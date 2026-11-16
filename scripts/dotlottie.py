#!/usr/bin/env python3
"""Pack Lottie JSON into a .lottie archive, and get it back out.

A .lottie (dotLottie) file is a zip: a manifest plus one or more Lottie JSON
animations, often a quarter of the size of the JSON. Players such as
dotlottie-web, dotlottie-ios and dotlottie-android load it directly.

    python3 scripts/dotlottie.py pack success-check.json -o success.lottie
    python3 scripts/dotlottie.py pack a.json b.json -o set.lottie   # several in one file
    python3 scripts/dotlottie.py unpack downloaded.lottie -o out/    # one JSON per animation
    python3 scripts/dotlottie.py info downloaded.lottie

`pack` writes the version 2 layout (animations under a/). `unpack` reads both
version 1 (animations/, images/) and version 2 (a/, i/), and folds any image
assets into the JSON as data URIs, so what comes out renders and lints alone.
The linter and recolor.py read .lottie files through `read_lottie`.

Exit codes: 0 done, 2 bad invocation or unreadable archive.
Dependency-free. Python 3.8+.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
import zipfile
from zipfile import BadZipFile
from pathlib import Path

GENERATOR = "lottie-animator"
ANIMATION_DIRS = ("a/", "animations/")
IMAGE_DIRS = ("i/", "images/")


def _check_id(anim_id):
    # ids become file names on unpack, so nothing that can climb out of the folder
    if not anim_id or re.search(r"[/\\\x00]", anim_id) or anim_id.strip(".") == "":
        raise ValueError("animation id %r cannot be a file name" % anim_id)
    return anim_id


def _animation_ids(zf):
    names = zf.namelist()
    try:
        manifest = json.loads(zf.read("manifest.json"))
        ids = [entry["id"] for entry in manifest.get("animations", [])]
    except (KeyError, ValueError, TypeError, AttributeError):
        ids = []
    if not ids:  # no usable manifest: take whatever animations sit directly in a/ or animations/
        ids = [Path(n).stem for n in names if n.startswith(ANIMATION_DIRS) and n.endswith(".json") and n.count("/") == 1]
    return [_check_id(str(i)) for i in ids]


def _read_member(zf, candidates):
    names = set(zf.namelist())
    for name in candidates:
        if name in names:
            return zf.read(name)
    return None


def _inline_images(zf, doc):
    for asset in doc.get("assets", []):
        filename = asset.get("p")
        if not isinstance(filename, str) or asset.get("e") == 1 or filename.startswith("data:"):
            continue
        folder = str(asset.get("u") or "").strip("/")
        candidates = [folder + "/" + filename if folder else filename]
        candidates += [d + filename for d in IMAGE_DIRS]
        data = _read_member(zf, candidates)
        if data is None:
            continue  # leave the reference; the linter will report the missing asset
        mime = mimetypes.guess_type(filename)[0] or "image/png"
        asset.update(u="", e=1, p="data:%s;base64,%s" % (mime, base64.b64encode(data).decode("ascii")))
    return doc


def read_archive(path):
    """Every animation in a .lottie as {id: Lottie dict}, images inlined."""
    with zipfile.ZipFile(path) as zf:
        animations = {}
        for anim_id in _animation_ids(zf):
            raw = _read_member(zf, [d + anim_id + ".json" for d in ANIMATION_DIRS])
            if raw is None:
                raise ValueError("manifest lists %r but the archive has no JSON for it" % anim_id)
            doc = json.loads(raw)
            if not isinstance(doc, dict):
                raise ValueError("%r is not a Lottie animation" % anim_id)
            animations[anim_id] = _inline_images(zf, doc)
    if not animations:
        raise ValueError("no animations inside %s" % path)
    return animations


def read_lottie(path):
    """A Lottie dict from a .json or the first animation of a .lottie."""
    path = Path(path)
    if path.suffix.lower() == ".lottie":
        return next(iter(read_archive(path).values()))
    return json.loads(path.read_text(encoding="utf-8"))


def write_archive(docs, out):
    """docs: {id: Lottie dict}. Writes a version 2 .lottie."""
    for anim_id, doc in docs.items():
        _check_id(anim_id)
        if not isinstance(doc, dict):
            raise ValueError("%s is not a Lottie animation" % anim_id)
        for asset in doc.get("assets", []):
            if isinstance(asset.get("p"), str) and asset.get("e") != 1 and not asset["p"].startswith("data:"):
                raise ValueError(
                    "%s references the external image %r; embed it as a data URI first" % (anim_id, asset["p"])
                )
    manifest = {
        "version": "2",
        "generator": GENERATOR,
        "animations": [{"id": anim_id} for anim_id in docs],
    }
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, separators=(",", ":")))
        for anim_id, doc in docs.items():
            zf.writestr("a/%s.json" % anim_id, json.dumps(doc, separators=(",", ":"), ensure_ascii=False))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pack, unpack or inspect .lottie (dotLottie) archives.")
    sub = parser.add_subparsers(dest="command", required=True)
    pack = sub.add_parser("pack", help="Lottie JSON files into one .lottie")
    pack.add_argument("inputs", nargs="+")
    pack.add_argument("-o", "--out", help="output path (default: first input with .lottie)")
    unpack = sub.add_parser("unpack", help="a .lottie into one JSON per animation")
    unpack.add_argument("input")
    unpack.add_argument("-o", "--out", default=".", help="output directory (default: here)")
    info = sub.add_parser("info", help="list the animations in a .lottie")
    info.add_argument("input")
    args = parser.parse_args(argv)

    try:
        if args.command == "pack":
            docs = {}
            for name in args.inputs:
                if Path(name).stem in docs:
                    raise ValueError("two inputs are named %s; animation ids must differ" % Path(name).stem)
                docs[Path(name).stem] = json.loads(Path(name).read_text(encoding="utf-8"))
            out = Path(args.out or Path(args.inputs[0]).with_suffix(".lottie"))
            write_archive(docs, out)
            size = sum(Path(n).stat().st_size for n in args.inputs)
            print("%s  %d animation%s, %d -> %d bytes" % (
                out, len(docs), "" if len(docs) == 1 else "s", size, out.stat().st_size))
            return 0
        animations = read_archive(args.input)
    except (OSError, ValueError, BadZipFile) as error:
        print("dotlottie: %s" % error, file=sys.stderr)
        return 2

    for anim_id, doc in animations.items():
        fr = doc.get("fr") or 0
        seconds = (doc.get("op", 0) - doc.get("ip", 0)) / fr if fr else 0
        line = "%s  %sx%s  %.2f s  %d layers" % (anim_id, doc.get("w"), doc.get("h"), seconds, len(doc.get("layers", [])))
        if args.command == "unpack":
            target = Path(args.out) / (anim_id + ".json")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(doc, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
            line += "  -> %s" % target
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
