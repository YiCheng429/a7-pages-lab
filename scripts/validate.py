"""Check the rendered homepage and its local targets before Pages upload."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit

START = "START_SECTION:activity"
END = "END_SECTION:activity"
SITE = "https://candidate.invalid"


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.comments = []
        self.headings = 0
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.headings += 1
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append((self.getpos()[0], attrs[key]))

    def handle_comment(self, value):
        self.comments.append(value.strip())


def check(root, base_path):
    home = root / "index.html"
    version = root / "version.txt"
    if not home.is_file():
        return ["index.html is missing; Jekyll did not render the homepage"]
    html = home.read_text(encoding="utf-8")
    page = Page(html)
    errors = []
    markers = [x for x in page.comments if x in (START, END)]
    if markers != [START, END] or "Recent activity" not in html or "activity" not in page.ids:
        errors.append("README activity markers or rendered activity section are missing or duplicated")
    if "{% include_relative" in html or page.headings != 1 or "<!doctype html>" not in html.lower():
        errors.append("Expected one rendered HTML homepage with exactly one h1")
    if not version.is_file() or not re.fullmatch(r"[a-f0-9]{40}/\d+/\d+\s*", version.read_text(encoding="utf-8")):
        errors.append("version.txt must identify a SHA, run ID and run attempt")
    base = "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"
    local_html = {home: page}
    for line, url in page.links:
        resolved = urlsplit(urljoin(SITE + base, url))
        if resolved.scheme not in ("http", "https") or resolved.netloc != "candidate.invalid":
            continue
        path = unquote(resolved.path)
        if not path.startswith(base):
            errors.append(f"index.html:{line}: local link outside Pages base {base}: {url}")
            continue
        target = (root / path.removeprefix(base)).resolve()
        if not target.is_relative_to(root):
            errors.append(f"index.html:{line}: target escapes candidate: {url}")
            continue
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            errors.append(f"index.html:{line}: broken local link: {url}")
        elif resolved.fragment and target.suffix == ".html":
            if target not in local_html:
                local_html[target] = Page(target.read_text(encoding="utf-8"))
            if unquote(resolved.fragment) not in local_html[target].ids:
                errors.append(f"index.html:{line}: missing anchor: {url}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    errors = check(args.site.resolve(), args.base_path)
    for error in errors:
        print(f"::error::{error}", file=sys.stderr)
    print("GATE BLOCKED: no artifact uploaded." if errors else
          "GATE PASSED: rendered README, local targets, and build identity verified.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
