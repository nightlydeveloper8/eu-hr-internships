"""Read-only JKS inventory and same-project form preview. No catalog writes."""
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import parse_qs, urljoin, urlsplit

from collector.classify import canonical_url
from collector.runtime import BudgetClient
from collector.universal import Document

INDEX = "https://www.jks.dk/om-jks/job-i-jks"
ATS = "candidate.hr-manager.net"
DETAIL = re.compile(r"/jobs/[a-z0-9-]+-([0-9]+)$")
CITIES = ("esbjerg", "odense", "vejle", "fredericia")
FORM = "/ApplicationForm/SinglePageApplicationForm.aspx"


def normalized(text):
    return " ".join(text.casefold().split()).strip(" -")


class ApplicantFields(HTMLParser):
    def __init__(self):
        super().__init__()
        self.names = set()
        self.in_form = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.in_form = True
        if self.in_form and tag == "input" and "disabled" not in attrs:
            if (attrs.get("type") or "text").lower() in {"text", "email", "file"}:
                self.names.add((attrs.get("name") or "").lower())

    def handle_endtag(self, tag):
        if tag == "form":
            self.in_form = False


def project_url(url, project):
    parsed = urlsplit(canonical_url(url))
    query = parse_qs(parsed.query)
    return (parsed.netloc == ATS and parsed.path in {"/ApplicationInit.aspx", FORM}
            and query.get("ProjectId") == [project] and query.get("cid") == ["1601"]
            and all(k.lower() in {"projectid", "cid", "departmentid", "mediaid", "skipadvertisement"}
                    for k in query))


def preview():
    client = BudgetClient(seconds=100, max_requests=18, delay=1)
    allowed = {INDEX}
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
    index, _ = page(INDEX)
    postings = {}
    for href, label, _ in index.links:
        url = urljoin(INDEX, href)
        parsed = urlsplit(url)
        match = DETAIL.fullmatch(parsed.path)
        if parsed.scheme == "https" and parsed.netloc == "www.jks.dk" and match and not parsed.query:
            if "praktikant" in parsed.path and re.search(r"-(hr|rekruttering\w*)-", parsed.path):
                postings[match[1]] = url

    proofs = []
    for project, url in sorted(postings.items())[:5]:
        allowed.add(url)
        active_project = project
        detail, _ = page(url)
        title = next((normalized(t) for t in detail.h1 if "praktikant" in t.lower()), "")
        cities = [c for c in CITIES if re.search(r"\b" + c + r"\b", title)]
        if len(cities) != 1 or not re.search(r"\bhr\b|rekruttering", title):
            continue
        links = {urljoin(url, h) for h, label, _ in detail.links if normalized(label) == "søg stillingen"}
        if len(links) != 1:
            continue
        apply = links.pop()
        if not project_url(apply, project):
            continue
        form, raw = page(apply)
        if urlsplit(form.url).path != FORM:
            continue
        fields = ApplicantFields()
        fields.feed(raw.decode("utf-8", "replace"))
        words = normalized(" ".join(form.body))
        if (title in words and "fornavn" in words and "efternavn" in words and "e-mail" in words
                and len(fields.names) >= 4):
            proofs.append(dict(country="DK", city=cities[0], title=title, project=project,
                               url=url, apply_url=form.url, checked_at=datetime.now(timezone.utc).isoformat()))
    return dict(inventory=INDEX, detected=len(postings), checked=min(len(postings), 5), proofs=proofs,
                requests=client.requests, bytes=client.bytes, closure_eligible=False)


if __name__ == "__main__":
    print(json.dumps(preview(), ensure_ascii=False, indent=2))
