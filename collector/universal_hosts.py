"""Host exclusions for universal discovery and verification."""
from contextlib import contextmanager
from urllib.parse import urlsplit

EXCLUDED_DOMAINS = ('smartrecruiters.com', 'smartrecruiterscareers.com', 'ashbyhq.com')


def excluded_host(host):
    host = (host or '').lower().rstrip('.')
    return any(host == domain or host.endswith('.' + domain) for domain in EXCLUDED_DOMAINS)


def excluded_url(url):
    return excluded_host(urlsplit(url or '').hostname)


@contextmanager
def universal_host_scope(client):
    previous = getattr(client, 'universal_host_scope', False)
    client.universal_host_scope = True
    try:
        yield
    finally:
        if previous:
            client.universal_host_scope = previous
        else:
            del client.universal_host_scope
