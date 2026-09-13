"""motion.py is what generators are told to use, so its promises are pinned.

A token that emits a bare keyframe would reintroduce the KF012 freeze in every
file written with it; a house curve with overshoot would quietly undo the
taste defaults.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from motion import EASE, squircle, track  # noqa: E402


class MotionTokensTest(unittest.TestCase):
    def test_track_never_emits_a_bare_keyframe(self):
        for name in list(EASE) + ["hold"]:
            keys = track((0, 0, name), (10, 50, name), (20, 100))["k"]
            for key in keys[:-1]:
                self.assertTrue(key.get("h") or ("o" in key and "i" in key), (name, key))

    def test_house_curves_do_not_overshoot(self):
        for name, ((x1, y1), (x2, y2)) in EASE.items():
            self.assertTrue(0 <= x1 <= 1 and 0 <= x2 <= 1, name)
            if name != "playful":
                self.assertTrue(0 <= y1 <= 1 and 0 <= y2 <= 1, name)

    def test_squircle_is_closed_centred_and_stays_in_bounds(self):
        shape = squircle(100, 60, 10)
        self.assertTrue(shape["c"])
        self.assertEqual(len(shape["v"]), 8)
        self.assertAlmostEqual(sum(v[0] for v in shape["v"]), 0, places=6)
        self.assertAlmostEqual(sum(v[1] for v in shape["v"]), 0, places=6)
        for (x, y), (ox, oy), (ix, iy) in zip(shape["v"], shape["o"], shape["i"]):
            for px, py in ((x + ox, y + oy), (x + ix, y + iy)):
                self.assertTrue(abs(px) <= 50 and abs(py) <= 30, (px, py))


if __name__ == "__main__":
    unittest.main()
