# Tests for live_check.py, with no network. The page checks read a small
# page served by http.server on 127.0.0.1; the DNS checks read recorded
# answers through a stub of the tool's one fetch function. A guard here
# fails any connection that is not to 127.0.0.1.
#   python -B -m pytest tools/tests/test_live_check.py -q

import http.server
import importlib.util
import json
import os
import socket
import threading

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("live_check", os.path.join(HERE, "..", "live_check.py"))
live_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live_check)

LOCAL = ("127.0.0.1", "localhost")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Fail any connection, or name lookup, that is not to 127.0.0.1."""
    connect, getaddrinfo = socket.socket.connect, socket.getaddrinfo

    def guarded_connect(self, address):
        if isinstance(address, tuple) and address[0] not in LOCAL:
            raise AssertionError(f"network connection in a test: {address}")
        return connect(self, address)

    def guarded_getaddrinfo(host, *args, **kwargs):
        if host not in LOCAL:
            raise AssertionError(f"network lookup in a test: {host}")
        return getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)


PAGE = """<!doctype html><html><head><title>Foundry North</title>
<meta property="og:title" content="Foundry North">
<meta property="og:description" content="Your own mini studio.">
{image}</head><body><h1>Foundry North</h1><section id="contact"></section></body></html>"""
IMAGE = '<meta property="og:image" content="/og.png">'


class Handler(http.server.BaseHTTPRequestHandler):
    routes = {
        "/good/": (200, "text/html", PAGE.format(image=IMAGE)),
        "/no-image/": (200, "text/html", PAGE.format(image="")),
        "/broken/": (500, "text/html", "<h1>Internal Server Error</h1>"),
        "/og.png": (200, "image/png", "\x89PNG"),
    }

    def do_GET(self):
        status, ctype, body = self.routes.get(self.path, (404, "text/html", "not here"))
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture
def site():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def doh(rtype, *data):
    """A Cloudflare DNS-over-HTTPS JSON answer, as it read on 14 Oct."""
    code = {"MX": 15, "TXT": 16}[rtype]
    return json.dumps({"Status": 0, "Answer": [
        {"name": live_check.DOMAIN, "type": code, "TTL": 300, "data": d} for d in data]})


MX_14_OCT = doh("MX", "10 mx.zoho.eu.", "20 mx2.zoho.eu.", "50 mx3.zoho.eu.")
TXT_14_OCT = doh("TXT", '"v=spf1 include:zoho.eu include:_spf-eu.ionos.com ~all"')


def stub_fetch(monkeypatch, mx=MX_14_OCT, txt=TXT_14_OCT):
    """Recorded answers for DNS, portal. and pick.; the local server for the rest."""
    real = live_check.fetch

    def fetch(url, accept=None):
        if url.startswith(live_check.DOH):
            assert accept == "application/dns-json"
            return 200, "application/dns-json", mx if "type=MX" in url else txt, url
        if url.startswith("https://portal."):
            return 200, "text/html", "<title>Workspace</title>", url
        if url.startswith("https://pick."):
            return 404, "text/html", "There is nothing at this link.", url
        return real(url, accept)

    monkeypatch.setattr(live_check, "fetch", fetch)


def by_name(results):
    return {check: ok for ok, check, _, _ in results}


def test_good_page_passes(site):
    results = live_check.page_checks([site + "/good/"])
    assert by_name(results) == {f"page {site}/good/": True, "preview": True}


def test_missing_og_image_fails(site):
    ok, check, read, _ = live_check.page_checks([site + "/no-image/"])[-1]
    assert (ok, check) == (False, "preview")
    assert "og:image" in read


def test_500_fails(site):
    results = live_check.page_checks([site + "/broken/"])
    assert by_name(results) == {f"page {site}/broken/": False, "preview": False}
    assert results[0][2].startswith("500")


def test_14_oct_answers_pass(monkeypatch):
    stub_fetch(monkeypatch)
    assert by_name([live_check.mx_check(), live_check.spf_check()] + live_check.untouched_checks()) == {
        "mx": True, "spf": True, "portal.": True, "pick.": True}


def test_changed_mx_fails(monkeypatch):
    stub_fetch(monkeypatch, mx=doh("MX", "10 mx.zoho.eu.", "20 mx2.zoho.eu.", "50 mx.other.example."))
    ok, check, read, _ = live_check.mx_check()
    assert (ok, check) == (False, "mx")
    assert "mx.other.example" in read


def test_changed_spf_fails(monkeypatch):
    stub_fetch(monkeypatch, txt=doh("TXT", '"v=spf1 include:zoho.eu ~all"'))
    ok, check, _, _ = live_check.spf_check()
    assert (ok, check) == (False, "spf")


def test_main_prints_one_line_per_check(site, monkeypatch, capsys):
    stub_fetch(monkeypatch)
    assert live_check.main(["--base", site + "/good/"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split(" · ")[0] for line in lines] == [
        f"PASS page {site}/good/", "PASS preview", "PASS mx", "PASS spf", "PASS portal.", "PASS pick.", "LIVE: PASS"]


def test_main_counts_failures(site, monkeypatch, capsys):
    stub_fetch(monkeypatch, txt=doh("TXT", '"v=spf1 -all"'))
    assert live_check.main(["--base", site + "/broken/"]) == 1
    lines = capsys.readouterr().out.splitlines()
    assert "FAIL spf · v=spf1 -all · expected " + live_check.SPF in lines
    assert lines[-1] == "LIVE: FAIL 3"
