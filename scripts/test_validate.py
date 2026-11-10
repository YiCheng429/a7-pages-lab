import tempfile
import unittest
from pathlib import Path
from validate import check

HTML = """<!doctype html><html><head>
<link rel="stylesheet" href="/a7-pages-lab/assets/ledger.css">
</head><body><h1>Release ledger</h1>
<a href="#activity">Activity</a><a href="./version.txt">Version</a>
<section id="activity"><h2>Recent activity</h2>
<!--START_SECTION:activity--><ol><li>Fixture event</li></ol><!--END_SECTION:activity-->
</section></body></html>"""


class GateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name).resolve()
        (self.site / "assets").mkdir()
        (self.site / "assets/ledger.css").write_text("body{}", encoding="utf-8")
        (self.site / "version.txt").write_text("a" * 40 + "/123/1\n", encoding="utf-8")

    def result(self, html):
        (self.site / "index.html").write_text(html, encoding="utf-8")
        return check(self.site, "/a7-pages-lab")

    def test_valid_home(self):
        self.assertEqual(self.result(HTML), [])

    def test_missing_target(self):
        bad = HTML.replace("</section>", '<a href="./__missing-release-gate__.html">Test</a></section>')
        self.assertIn("broken local link: ./__missing-release-gate__.html", " ".join(self.result(bad)))

    def test_missing_markers(self):
        self.assertIn("markers", " ".join(self.result(HTML.replace("<!--END_SECTION:activity-->", ""))))

    def test_missing_anchor(self):
        self.assertIn("missing anchor", " ".join(self.result(HTML.replace('href="#activity"', 'href="#absent"'))))

    def test_missing_version(self):
        (self.site / "version.txt").unlink()
        self.assertIn("identify a SHA", " ".join(self.result(HTML)))


if __name__ == "__main__":
    unittest.main()
