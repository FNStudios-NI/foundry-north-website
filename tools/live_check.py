# live_check.py: read the live site and the domain's other answers, and say
# PASS or FAIL for each.
#
# What it is for
#   Going live is his act in Cloudflare. This tool reads what a visitor and
#   a mail server would see afterwards, and checks it, one line per check:
#     - the bare address and www. each answer 200 with the page (the body
#       holds "Foundry North" and id="contact"); a redirect from one to the
#       other that ends in 200 with the page passes;
#     - the link preview: the page's og:title, og:description and og:image
#       are there, and the og:image address answers 200 with an image type;
#     - the mail and the names left untouched still match the readings of
#       14 Oct (docs/brief.md § Facts): the three Zoho MX records, the SPF
#       text, portal. answering 200 and pick. answering 404.
#   Each line reads PASS <check> · <what it read>, or
#   FAIL <check> · <what it read> · expected <what>. The last line is
#   LIVE: PASS (exit 0) or LIVE: FAIL <n> (exit 1).
#
# Why the rule exists
#   The switch of the address must change the website and nothing else: his
#   email runs on the same domain. Reading every answer after the switch,
#   the same way each time, shows both at once, and a script does that more
#   surely than a person clicking about.
#
# How to run it (from the project's top folder)
#   python tools/live_check.py
#   python tools/live_check.py --base <url>   (the page checks read <url>
#   instead, e.g. the private preview or the tests' local server)
#
# Python 3 standard library only. DNS is read over DNS-over-HTTPS from
# Cloudflare (JSON), so no nslookup is needed. It reads; it never writes.

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DOMAIN = "foundrynorthstudios.co.uk"
PAGES = [f"https://{DOMAIN}/", f"https://www.{DOMAIN}/"]
DOH = "https://cloudflare-dns.com/dns-query"
# The readings of 14 Oct (docs/brief.md § Facts).
MX = [(10, "mx.zoho.eu"), (20, "mx2.zoho.eu"), (50, "mx3.zoho.eu")]
SPF = "v=spf1 include:zoho.eu include:_spf-eu.ionos.com ~all"
UNTOUCHED = [(f"https://portal.{DOMAIN}/", 200), (f"https://pick.{DOMAIN}/", 404)]


def fetch(url, accept=None):
    """The tool's one network step: GET url, following redirects.
    Returns (status or None, content type, body text, final url or the error)."""
    headers = {"User-Agent": "foundry-north-live-check/1"}
    if accept:
        headers["Accept"] = accept
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read().decode("utf-8", "replace"), e.geturl()
    except (urllib.error.URLError, OSError) as e:
        return None, "", "", str(getattr(e, "reason", e))


def page_checks(pages):
    """One check per page address, then the link preview of the first page that answered."""
    results, found = [], None
    for url in pages:
        status, _, body, final = fetch(url)
        read = f"{status} from {final}" if status else f"no answer ({final})"
        has_page = "Foundry North" in body and 'id="contact"' in body
        if status == 200 and not has_page:
            read += ", without the page"
        results.append((status == 200 and has_page, f"page {url}", read,
                        '200 with the page ("Foundry North" and id="contact")'))
        if status == 200 and has_page and found is None:
            found = (body, final)
    results.append(preview_check(found))
    return results


def og(body, prop):
    """The content of <meta property="og:<prop>">, or None."""
    for tag in re.findall(r"<meta\b[^>]*>", body, re.I):
        if re.search(rf"""property\s*=\s*["']og:{prop}["']""", tag, re.I):
            m = re.search(r"""content\s*=\s*["']([^"']*)["']""", tag, re.I)
            return m.group(1) if m else None
    return None


def preview_check(found):
    expected = "og:title, og:description and og:image, the image 200 with an image type"
    if found is None:
        return (False, "preview", "no page to read", expected)
    body, final = found
    tags = {p: og(body, p) for p in ("title", "description", "image")}
    missing = [f"og:{p}" for p, v in tags.items() if not v]
    if missing:
        return (False, "preview", f"missing {', '.join(missing)}", expected)
    image = urllib.parse.urljoin(final, tags["image"])
    status, ctype, _, _ = fetch(image)
    ok = status == 200 and ctype.startswith("image/")
    return (ok, "preview", f"og:image {image} answered {status} {ctype}".rstrip(), expected)


def dns(name, rtype):
    """The answers' data for name and rtype, read over DNS-over-HTTPS, or None."""
    query = urllib.parse.urlencode({"name": name, "type": rtype})
    status, _, body, _ = fetch(f"{DOH}?{query}", accept="application/dns-json")
    if status != 200:
        return None
    try:
        reply = json.loads(body)
    except ValueError:
        return None
    return [a["data"] for a in reply.get("Answer", []) if a.get("type") == {"MX": 15, "TXT": 16}[rtype]]


def mx_check():
    data = dns(DOMAIN, "MX")
    expected = ", ".join(f"{h} ({p})" for p, h in MX)
    if data is None:
        return (False, "mx", "no DNS answer", expected)
    found = []
    for d in data:
        pref, _, host = d.partition(" ")
        found.append((int(pref) if pref.isdigit() else 0, host.rstrip(".").lower()))
    found.sort()
    read = ", ".join(f"{h} ({p})" for p, h in found) or "none"
    return (found == MX, "mx", read, expected)


def spf_check():
    data = dns(DOMAIN, "TXT")
    if data is None:
        return (False, "spf", "no DNS answer", SPF)
    # A TXT answer is one or more quoted strings; join them into one text.
    texts = ["".join(re.findall(r'"((?:[^"\\]|\\.)*)"', d)) or d for d in data]
    spf = [t for t in texts if t.startswith("v=spf1")]
    read = " | ".join(spf) or "no SPF text"
    return (spf == [SPF], "spf", read, SPF)


def untouched_checks():
    results = []
    for url, want in UNTOUCHED:
        status, _, _, final = fetch(url)
        read = f"{status} from {final}" if status else f"no answer ({final})"
        name = urllib.parse.urlparse(url).hostname.split(".")[0] + "."
        results.append((status == want, name, read, str(want)))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read the live site and the domain's other answers.")
    parser.add_argument("--base", help="point the page checks at this address instead")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # the "·" prints in a Windows code page
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    results = page_checks([args.base] if args.base else PAGES)
    results += [mx_check(), spf_check()] + untouched_checks()
    for ok, check, read, expected in results:
        print(f"PASS {check} · {read}" if ok else f"FAIL {check} · {read} · expected {expected}")
    failed = sum(1 for r in results if not r[0])
    print("LIVE: PASS" if not failed else f"LIVE: FAIL {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
