"""Read-only JKS inventory and same-project form preview. No catalog writes."""
import json
import re
from datetime import datetime, timezone
from urllib.parse import parse_qs, urljoin, urlsplit

from collector.classify import canonical_url
from collector.runtime import BudgetClient
from collector.verification import applicant_form, expired
from collector.universal import Document

INDEX = "https://www.jks.dk/om-jks/job-i-jks"
ATS = "candidate.hr-manager.net"
DETAIL = re.compile(r"/jobs/[a-z0-9-]+-([0-9]+)$")
OFFICES = ("esbjerg", "odense")
CITIES = ("esbjerg", "odense", "vejle", "fredericia", "slagelse", "randers", "hobro", "frederikshavn")
FORM = "/ApplicationForm/SinglePageApplicationForm.aspx"


def normalized(text):
    return " ".join(text.casefold().split()).strip(" -")


def project_url(url, project):
    parsed = urlsplit(canonical_url(url))
    query = parse_qs(parsed.query)
    return (parsed.netloc == ATS and parsed.path in {"/ApplicationInit.aspx", FORM}
            and query.get("ProjectId") == [project] and query.get("cid") == ["1601"]
            and all(k.lower() in {"projectid", "cid", "departmentid", "mediaid", "skipadvertisement"}
                    for k in query))


def preview():
    client = BudgetClient(seconds=100, max_requests=18, delay=1)
    inventories = [INDEX, *("https://www.jks.dk/for-vikarer/" + city for city in OFFICES)]
    allowed = set(inventories)
    active_project = None

    def scoped(url):
        url = canonical_url(url)
        if url in allowed:
            return True
        if urlsplit(url).path == "/robots.txt":
            return urlsplit(url).netloc in {"www.jks.dk", ATS}
        return bool(active_project and project_url(url, active_project))

    def page(url):
        if not scoped(url):
            raise ValueError("URL outside preview scope")
        raw, _, final = client.request(url)
        if not scoped(final):
            raise ValueError("Unreviewed destination")
        return Document(raw, final), raw

    client.redirect_scope_allowed = scoped
    postings = {}
    for inventory in inventories:
        index, _ = page(inventory)
        for href, label, _ in index.links:
            url = urljoin(inventory, href)
            parsed = urlsplit(url)
            match = DETAIL.fullmatch(parsed.path)
            if parsed.scheme == "https" and parsed.netloc == "www.jks.dk" and match and not parsed.query:
                if "praktikant" in parsed.path and re.search(r"-(hr|rekruttering\w*)-", parsed.path):
                    postings[match[1]] = url

    proofs = []
    unresolved = {}
    for project, url in sorted(postings.items(), reverse=True)[:5]:
        allowed.add(url)
        active_project = project
        detail, _ = page(url)
        title = next((normalized(t) for t in detail.h1 if "praktikant" in t.lower()), "")
        cities = [c for c in CITIES if re.search(r"\b" + c + r"\b", title)]
        unresolved[project] = dict(detail=url, stage="title/city", headings=detail.h1[:2])
        if len(cities) != 1 or not re.search(r"\bhr\b|rekruttering", title):
            continue
        # A missing intake date is allowed. Only a matching posting's own
        # structured deadline can establish expiry, never dates from related cards.
        stamp = datetime.now(timezone.utc).isoformat()
        if any(expired(post.get("validThrough"), stamp) for post in detail.jobposts()
               if normalized(post.get("title") or "") == title):
            unresolved[project]["stage"] = "expired deadline"
            continue
        links = {urljoin(url, h) for h, label, _ in detail.links if normalized(label) == "søg stillingen"}
        unresolved[project]["stage"] = "unique employer apply link"
        if len(links) != 1:
            continue
        apply = links.pop()
        unresolved[project]["stage"] = "employer tenant and project"
        if not project_url(apply, project):
            continue
        form, raw = page(apply)
        unresolved[project]["stage"] = "form destination"
        if urlsplit(form.url).path != FORM:
            continue
        form_valid = applicant_form(raw, strict=True)
        words = normalized(" ".join(form.body))
        unresolved[project].update(stage="title and candidate fields", same_title=title in words,
                                   candidate_labels=all(t in words for t in ("fornavn","efternavn","e-mail")),
                                   strict_applicant_form=form_valid)
        if (title in words and "fornavn" in words and "efternavn" in words and "e-mail" in words
                and form_valid):
            unresolved.pop(project)
            proofs.append(dict(country="DK", city=cities[0], title=title, project=project,
                               url=url, apply_url=form.url, checked_at=datetime.now(timezone.utc).isoformat()))
    return dict(inventories=inventories, detected=len(postings), checked=min(len(postings), 5), proofs=proofs,
                unresolved=unresolved, requests=client.requests, bytes=client.bytes, closure_eligible=False)


if __name__ == "__main__":
    print(json.dumps(preview(), ensure_ascii=False, indent=2))
