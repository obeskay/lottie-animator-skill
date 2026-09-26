#!/usr/bin/env python3
"""List and replace the colours in any Lottie file.

Bringing a downloaded animation into a brand palette is mostly finding every
place a colour hides: static and animated fills and strokes, gradient stops,
solid layers. Missing one leaves a stray swatch of the old palette.

    python3 scripts/recolor.py in.json --list
    python3 scripts/recolor.py in.json --map "#FF5A5F=#C8522B" --map "#222222=#1E1B18" -o out.json

`--list` prints each colour with how often it is used and by which layers, so
the mapping can be decided by role (the ink, the accent, the surface) rather
than guessed. Colours are compared at 8-bit precision. Exit codes: 0 done,
1 a --map colour was not found in the file, 2 bad invocation.

Dependency-free. Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HEX = "0123456789ABCDEF"


def to_hex(rgb):
    return "#" + "".join("%02X" % max(0, min(255, round(v * 255))) for v in rgb[:3])


def parse_hex(text):
    value = text.strip().lstrip("#").upper()
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6 or any(ch not in HEX for ch in value):
        raise ValueError("expected #RRGGBB, got %r" % text)
    return "#" + value


def _rgb(hex_color):
    return [round(int(hex_color[i:i + 2], 16) / 255.0, 4) for i in (1, 3, 5)]


def colour_slots(doc):
    """Yield (layer name, getter, setter) for every colour in the document."""
    def colour_values(prop):
        # A colour property is static [r, g, b, a] or keyframes whose s/e hold one.
        if not isinstance(prop, dict):
            return
        k = prop.get("k")
        if prop.get("a") and isinstance(k, list):
            for key in k:
                for field in ("s", "e"):
                    if isinstance(key, dict) and isinstance(key.get(field), list) and len(key[field]) >= 3:
                        yield key[field]
        elif isinstance(k, list) and len(k) >= 3 and all(isinstance(v, (int, float)) for v in k):
            yield k

    def gradient_values(g):
        # Stops are packed as offset, r, g, b for each of p stops, then alpha pairs.
        if not isinstance(g, dict) or not isinstance(g.get("k"), dict):
            return
        count = g.get("p", 0)
        prop = g["k"]
        arrays = [key.get(f) for key in prop.get("k", []) if isinstance(key, dict) for f in ("s", "e")] \
            if prop.get("a") else [prop.get("k")]
        for values in arrays:
            if isinstance(values, list):
                for stop in range(count):
                    yield values, 4 * stop + 1

    def walk(node, name):
        if isinstance(node, dict):
            if node.get("ty") in (0, 1, 2, 3, 4, 5) and "ks" in node:
                name = node.get("nm", name)
            if node.get("ty") in ("fl", "st"):
                for values in colour_values(node.get("c")):
                    yield name, values, 0
            if node.get("ty") in ("gf", "gs"):
                for values, offset in gradient_values(node.get("g")):
                    yield name, values, offset
            # Text documents keep fill and stroke colour as fc / sc arrays.
            for field in ("fc", "sc"):
                if isinstance(node.get(field), list) and len(node[field]) >= 3:
                    yield name, node[field], 0
            for key, value in node.items():
                if key != "c" or node.get("ty") not in ("fl", "st"):
                    yield from walk(value, name)
        elif isinstance(node, list):
            for value in node:
                yield from walk(value, name)

    yield from walk(doc, doc.get("nm", "?"))


def solid_layers(doc):
    for layer in _all_layers(doc):
        if layer.get("ty") == 1 and isinstance(layer.get("sc"), str):
            yield layer


def _all_layers(doc):
    yield from doc.get("layers", [])
    for asset in doc.get("assets", []):
        yield from asset.get("layers", []) or []


def inventory(doc):
    usage = defaultdict(lambda: {"count": 0, "layers": set()})
    for name, values, offset in colour_slots(doc):
        entry = usage[to_hex(values[offset:offset + 3])]
        entry["count"] += 1
        entry["layers"].add(name)
    for layer in solid_layers(doc):
        entry = usage[parse_hex(layer["sc"])]
        entry["count"] += 1
        entry["layers"].add(layer.get("nm", "solid"))
    return usage


def recolor(doc, mapping):
    """Replace colours in place. Returns the set of source colours that were found."""
    found = set()
    for _, values, offset in colour_slots(doc):
        source = to_hex(values[offset:offset + 3])
        if source in mapping:
            values[offset:offset + 3] = _rgb(mapping[source])
            found.add(source)
    for layer in solid_layers(doc):
        source = parse_hex(layer["sc"])
        if source in mapping:
            layer["sc"] = mapping[source].lower()
            found.add(source)
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description="List or replace the colours in a Lottie file.")
    parser.add_argument("input")
    parser.add_argument("--list", action="store_true", help="print the colours in use and exit")
    parser.add_argument("--map", action="append", default=[], metavar="#OLD=#NEW",
                        help="replace one colour; repeat for more")
    parser.add_argument("-o", "--out", help="output path (default: overwrite the input)")
    args = parser.parse_args(argv)

    try:
        doc = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print("recolor: cannot read %s: %s" % (args.input, error), file=sys.stderr)
        return 2

    if args.list or not args.map:
        usage = inventory(doc)
        for colour, entry in sorted(usage.items(), key=lambda item: -item[1]["count"]):
            layers = ", ".join(sorted(entry["layers"]))
            print("%s  %3d use%s  %s" % (colour, entry["count"], " " if entry["count"] == 1 else "s", layers))
        if not usage:
            print("no colours found")
        return 0

    try:
        mapping = {}
        for pair in args.map:
            old, new = pair.split("=", 1)
            mapping[parse_hex(old)] = parse_hex(new)
    except ValueError as error:
        print("recolor: %s" % error, file=sys.stderr)
        return 2

    found = recolor(doc, mapping)
    out = Path(args.out or args.input)
    out.write_text(json.dumps(doc, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    missing = sorted(set(mapping) - found)
    print("recolor: %d colour%s replaced -> %s" % (len(found), "" if len(found) == 1 else "s", out))
    if missing:
        print("recolor: not in the file: %s (run --list)" % ", ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
