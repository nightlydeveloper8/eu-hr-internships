"""Scoped JKS inventory and project-specific Talentech application checks."""
import re
from contextlib import contextmanager
from urllib.parse import parse_qs, urljoin, urlsplit

from .adapters import _record
from .applications import checked_document
from .classify import canonical_url
from .public_sources import PublicInventory
from .universal import Document

HOST = "www.jks.dk"
ATS = "candidate.hr-manager.net"
INDEXES = tuple("https://www.jks.dk/" + path for path in (
    "om-jks/job-i-jks", "for-vikarer/esbjerg", "for-vikarer/odense"))
DETAIL = re.compile(r"/jobs/[a-z0-9-]+-([0-9]+)$")
CITIES = ("Esbjerg", "Odense", "Vejle", "Fredericia", "Slagelse", "Randers", "Hobro", "Frederikshavn")
FORM = "/ApplicationForm/SinglePageApplicationForm.aspx"
SOURCE = dict(id="jks-dk-internships", employer="JKS", adapter="jks-index",
              application_check="jks-talentech", enabled=False, staging_only=True,
              rollout_approved=False, ownership_scope="reviewed-hosts",
              require_employer_identity=True, allowed_hosts=[HOST, ATS],
              career_url=INDEXES[0], target_countries=["DK"], max_requests=24, collection_seconds=120)


def norm(text):
    return " ".join(text.casefold().split()).strip(" -")


def job_url(url):
    parsed = urlsplit(canonical_url(url))
    if parsed.netloc == HOST and not parsed.query:
        return DETAIL.fullmatch(parsed.path)
    return None


def project_url(url, project):
    parsed = urlsplit(canonical_url(url))
    query = parse_qs(parsed.query, keep_blank_values=True)
    keys = {"projectid", "cid", "departmentid", "mediaid", "skipadvertisement"}
    return (parsed.netloc == ATS and parsed.path in {"/ApplicationInit.aspx", FORM}
            and query.get("ProjectId") == [project] and query.get("cid") == ["1601"]
            and len({key.lower() for key in query}) == len(query)
            and all(key.lower() in keys and len(values) == 1 for key, values in query.items()))


@contextmanager
def scope(client, allowed):
    previous = getattr(client, "redirect_scope_allowed", None)

    def permitted(url):
        safe = canonical_url(url)
        return ((previous is None or previous(safe))
                and (allowed(safe) or safe in {"https://" + host + "/robots.txt" for host in (HOST, ATS)}))

    client.redirect_scope_allowed = permitted
    try:
        yield
    finally:
        if previous is None:
            del client.redirect_scope_allowed
        else:
            client.redirect_scope_allowed = previous


def source_gate(source):
    """Fail closed until a separate, explicit JKS production rollout is approved."""
    if (not isinstance(source, dict)
            or any(source.get(key) != SOURCE[key] for key in (
                "id", "employer", "adapter", "application_check", "career_url",
                "target_countries", "ownership_scope", "require_employer_identity"))
            or set(source.get("allowed_hosts", [])) != set(SOURCE["allowed_hosts"])
            or type(source.get("max_requests")) is not int
            or not 8 <= source["max_requests"] <= SOURCE["max_requests"]
            or type(source.get("collection_seconds")) is not int
            or not 40 <= source["collection_seconds"] <= SOURCE["collection_seconds"]):
        raise ValueError("JKS source is not in the reviewed identity, host or budget scope")
    if (source.get("enabled") is False and source.get("staging_only") is True
            and source.get("rollout_approved") is False):
        return "staging"
    if (source.get("enabled") is True and source.get("staging_only") is False
            and source.get("rollout_approved") is True
            and isinstance(source.get("rollout_authorization"), str)
            and len(source["rollout_authorization"].strip()) >= 10):
        return "production"
    raise ValueError("JKS activation requires separate explicit rollout approval")


def inventory(source, client):
    source_gate(source)
    postings = {}
    for index in INDEXES:
        with scope(client, lambda url: url == index):
            raw, _, final = client.request(index)
        if canonical_url(final) != index:
            raise ValueError("JKS inventory redirected")
        for href, _, _ in Document(raw, final).links:
            url = urljoin(index, href)
            p = urlsplit(url)
            if p.scheme != "https" or p.netloc != HOST or not DETAIL.fullmatch(p.path) or p.query:
                continue
            if "praktikant" in p.path and re.search(r"-(hr|rekruttering\w*)-", p.path):
                postings[DETAIL.fullmatch(p.path)[1]] = url

    rows, unknown = [], []
    for project, url in sorted(postings.items(), reverse=True)[:5]:
        with scope(client, lambda target: target == url):
            _, detail = checked_document(url, source, client)
        titles = {t for t in detail.h1 if "praktikant" in t.lower()}
        if len(titles) != 1:
            continue
        title = titles.pop()
        cities = [c for c in CITIES if re.search(r"\b" + c + r"\b", title, re.I)]
        if len(cities) != 1 or not re.search(r"\bHR\b|rekruttering", title, re.I):
            unknown.append(project)
            continue
        row = _record(source, project, title, cities[0] + ", Denmark", detail.text, url,
                      posting_identifier=project, country="DK", city=cities[0], language="da")
        row["inventory_evidence"] = "current-employer-index"
        rows.append(row)
    return PublicInventory(rows, dict(complete=False, closure_complete=False, status="partial",
                                      listed_projects=len(postings), unresolved_projects=unknown))


def application(record, source, client, doc):
    source_gate(source)
    from .verification import applicant_form

    project = str(record.get("posting_identifier") or "")
    match = job_url(doc.url)
    if (source.get("id") != SOURCE["id"] or set(source.get("allowed_hosts", [])) != set(SOURCE["allowed_hosts"])
            or source.get("adapter") != SOURCE["adapter"] or record.get("inventory_evidence") != "current-employer-index"
            or not match or match[1] != project or norm(record["title"]) not in {norm(t) for t in doc.h1}):
        raise ValueError("JKS vacancy identity mismatch")
    links = {urljoin(doc.url, href) for href, label, _ in doc.links if norm(label) == "søg stillingen"}
    if len(links) != 1:
        raise ValueError("Expected one JKS application destination")
    url = links.pop()
    if not project_url(url, project):
        raise ValueError("JKS tenant or project mismatch")
    with scope(client, lambda target: project_url(target, project)):
        raw, form = checked_document(url, source, client)
    words = norm(" ".join(form.body))
    if (not project_url(form.url, project) or urlsplit(form.url).path != FORM
            or norm(record["title"]) not in words or not applicant_form(raw, strict=True)
            or not all(label in words for label in ("fornavn", "efternavn", "e-mail"))):
        raise ValueError("Missing current, matching JKS application form")
    return dict(url=canonical_url(form.url), method="jks-talentech-same-project-form")
