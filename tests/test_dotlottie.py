"""dotLottie archives: a .lottie must round-trip, lint and recolour like JSON.

The layout written here (manifest version 2, animations under a/) was checked
against the dotlottie-web player when the tool was added; these tests pin the
archive shape and the round trip so a later edit cannot drift from it.
"""
import base64
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from dotlottie import read_archive, read_lottie, write_archive  # noqa: E402

DOT = REPO / "scripts" / "dotlottie.py"
LINT = REPO / "scripts" / "lottie_lint.py"
RECOLOR = REPO / "scripts" / "recolor.py"
CHECK = REPO / "examples" / "success-check.json"
PNG = base64.b64decode(  # 1x1 transparent PNG
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)


class DotLottieTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.doc = json.loads(CHECK.read_text(encoding="utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_pack_writes_version_2_layout_and_round_trips(self):
        out = self.dir / "check.lottie"
        result = run(DOT, "pack", CHECK, "-o", out)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(out) as zf:
            manifest = json.loads(zf.read("manifest.json"))
            self.assertEqual(manifest["version"], "2")
            self.assertEqual(manifest["animations"], [{"id": "success-check"}])
            self.assertIn("a/success-check.json", zf.namelist())
        self.assertEqual(read_lottie(out), self.doc)
        self.assertLess(out.stat().st_size, CHECK.stat().st_size)

    def test_unpack_reads_version_1_and_inlines_images(self):
        doc = dict(self.doc, assets=[{"id": "img_0", "w": 1, "h": 1, "u": "/images/", "p": "dot.png", "e": 0}])
        archive = self.dir / "old.lottie"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"version": "1", "animations": [{"id": "old"}]}))
            zf.writestr("animations/old.json", json.dumps(doc))
            zf.writestr("images/dot.png", PNG)
        result = run(DOT, "unpack", archive, "-o", self.dir / "out")
        self.assertEqual(result.returncode, 0, result.stderr)
        asset = json.loads((self.dir / "out" / "old.json").read_text())["assets"][0]
        self.assertEqual(asset["e"], 1)
        self.assertEqual(base64.b64decode(asset["p"].split(",", 1)[1]), PNG)

    def test_several_animations_in_one_archive(self):
        out = self.dir / "set.lottie"
        write_archive({"one": self.doc, "two": self.doc}, out)
        self.assertEqual(list(read_archive(out)), ["one", "two"])

    def test_ids_that_climb_out_of_the_folder_are_refused(self):
        archive = self.dir / "evil.lottie"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"version": "2", "animations": [{"id": "../../x"}]}))
            zf.writestr("a/../../x.json", json.dumps(self.doc))
        result = run(DOT, "unpack", archive, "-o", self.dir / "out")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.dir / "x.json").exists())

    def test_external_images_are_refused_on_pack(self):
        doc = dict(self.doc, assets=[{"id": "img_0", "u": "images/", "p": "a.png", "e": 0}])
        with self.assertRaises(ValueError):
            write_archive({"x": doc}, self.dir / "x.lottie")

    def test_linter_reads_lottie_files_and_rejects_corrupt_ones(self):
        out = self.dir / "check.lottie"
        write_archive({"success-check": self.doc}, out)
        self.assertEqual(run(LINT, out, "--strict").returncode, 0)
        bad = self.dir / "bad.lottie"
        bad.write_bytes(b"not a zip")
        result = run(LINT, bad)
        self.assertEqual(result.returncode, 1)
        self.assertIn("IO003", result.stdout)

    def test_recolor_lists_and_rewrites_a_lottie(self):
        src = self.dir / "check.lottie"
        write_archive({"success-check": self.doc}, src)
        listing = run(RECOLOR, src, "--list")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        first = listing.stdout.split()[0]
        out = self.dir / "recoloured.lottie"
        result = run(RECOLOR, src, "--map", "%s=#123456" % first, "-o", out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("#123456", run(RECOLOR, out, "--list").stdout)


if __name__ == "__main__":
    unittest.main()
