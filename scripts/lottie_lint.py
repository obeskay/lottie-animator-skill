#!/usr/bin/env python3
"""Lint a Lottie JSON file for structural, timing, and motion-quality defects.

Dependency-free. Python 3.8+.

Usage:
    python3 scripts/lottie_lint.py animation.json
    python3 scripts/lottie_lint.py examples/            # every .json inside
    python3 scripts/lottie_lint.py a.json --json        # machine-readable
    python3 scripts/lottie_lint.py a.json --strict      # warnings fail the run

Exit code 0 when nothing above the failure threshold is reported.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ERROR = "error"
WARN = "warn"
INFO = "info"

_SEVERITY_ORDER = {ERROR: 0, WARN: 1, INFO: 2}

# Layer type ids from the Lottie specification.
LAYER_TYPES = {
    0: "precomp",
    1: "solid",
    2: "image",
    3: "null",
    4: "shape",
    5: "text",
    6: "audio",
    13: "camera",
}

REQUIRED_DOC_KEYS = ("v", "fr", "ip", "op", "w", "h", "layers")
NUMERIC_DOC_KEYS = ("fr", "ip", "op", "w", "h")

# Properties whose absence makes a player drop the entire layer: the file
# loads, reports no error, and paints nothing. Each entry below was verified
# by removing the property from a working animation and rendering the result.
SHAPE_REQUIRED = {
    "sh": ("ks",),                     # path
    "rc": ("p", "s", "r"),             # rectangle
    "el": ("p", "s"),                  # ellipse
    "sr": ("p", "r", "pt", "or", "os"),  # polystar
    "fl": ("c", "o"),                  # fill
    "st": ("c", "o", "w"),             # stroke
    "gf": ("s", "e", "g", "o"),        # gradient fill
    "gs": ("s", "e", "g", "o", "w"),   # gradient stroke
    "tr": ("o",),                      # shape transform
    "tm": ("s", "e", "o"),             # trim path
    "rp": ("c", "o", "tr"),            # repeater
}

# Required by the specification, but lottie-web supplies a default rather than
# failing. Other players are not guaranteed to be as forgiving, so these are
# reported as warnings instead of being ignored.
# Fill rule (fl.r) is deliberately absent: almost every real Lottie omits it and
# the default is correct, so warning about it is noise rather than signal.
SHAPE_RECOMMENDED = {
    "gf": ("t",),                          # gradient type; defaults to linear
    "gs": ("t",),
    "tr": ("a", "p", "s", "r"),            # default to identity
}

# A star (sy == 1) also needs the inner radius pair; a polygon (sy == 2) does not.
STAR_REQUIRED = ("ir", "is")

SHAPE_NAMES = {
    "sh": "path", "rc": "rectangle", "el": "ellipse", "sr": "polystar",
    "fl": "fill", "st": "stroke", "gf": "gradient fill", "gs": "gradient stroke",
    "tr": "transform", "tm": "trim path", "rp": "repeater", "gr": "group",
}


class Finding:
    """A single lint result."""

    __slots__ = ("code", "severity", "where", "message", "hint")

    def __init__(self, code, severity, where, message, hint=""):
        self.code = code
        self.severity = severity
        self.where = where
        self.message = message
        self.hint = hint

    def as_dict(self):
        return {
            "code": self.code,
            "severity": self.severity,
            "where": self.where,
            "message": self.message,
            "hint": self.hint,
        }


class Linter:
    def __init__(self, data, loop=None, source_name="", allow_static=False):
        self.data = data
        self.findings = []
        self.stats = {}
        self.linear_properties = []
        self.allow_static = allow_static
        # Loop closure only matters if the animation is meant to loop. A rocket
        # launch is allowed to end somewhere other than where it started.
        self.loop = self.detect_loop(source_name) if loop is None else loop

    def detect_loop(self, source_name=""):
        """Guess loop intent from the composition or file name."""
        haystack = "%s %s" % (self.data.get("nm") or "", source_name)
        return any(
            word in haystack.lower()
            for word in ("loop", "loader", "loading", "spinner", "pulse", "idle", "cycle")
        )

    # -- reporting ---------------------------------------------------------
    def add(self, code, severity, where, message, hint=""):
        self.findings.append(Finding(code, severity, where, message, hint))

    # -- entry point -------------------------------------------------------
    def run(self):
        if not isinstance(self.data, dict):
            self.add(
                "LT000", ERROR, "$", "top level must be a JSON object",
                "A Lottie file is a single object, not an array or scalar.",
            )
            return self.findings
        self.check_document()
        self.check_assets()
        self.check_layers()
        self.check_motion_presence()
        self.report_linear_easing()
        self.findings = _collapse(self.findings)
        self.findings.sort(key=lambda f: (_SEVERITY_ORDER[f.severity], f.code, f.where))
        return self.findings

    # -- document ----------------------------------------------------------
    def check_document(self):
        data = self.data
        for key in REQUIRED_DOC_KEYS:
            if key not in data:
                self.add(
                    "LT001", ERROR, "$", "missing required top-level key: %s" % key,
                    "Players read this field directly; without it the file will not load.",
                )
        for key in NUMERIC_DOC_KEYS:
            if key in data and not isinstance(data[key], (int, float)) or isinstance(data.get(key), bool):
                if key in data:
                    self.add("LT002", ERROR, "$.%s" % key, "%s must be numeric" % key)

        fr = _num(data.get("fr"))
        ip = _num(data.get("ip"))
        op = _num(data.get("op"))
        w = _num(data.get("w"))
        h = _num(data.get("h"))

        if fr is not None and fr <= 0:
            self.add("LT003", ERROR, "$.fr", "fr must be greater than 0")
        elif fr is not None and fr > 120:
            self.add(
                "LT004", WARN, "$.fr", "fr is %g; above 120 wastes file size" % fr,
                "30 or 60 covers every real playback target.",
            )
        if ip is not None and op is not None and op <= ip:
            self.add("LT005", ERROR, "$.op", "op (%g) must be greater than ip (%g)" % (op, ip))
        for key, val in (("w", w), ("h", h)):
            if val is not None and val <= 0:
                self.add("LT006", ERROR, "$.%s" % key, "%s must be greater than 0" % key)

        if "layers" in self.data and not isinstance(self.data["layers"], list):
            self.add("LT007", ERROR, "$.layers", "layers must be an array")
        elif isinstance(self.data.get("layers"), list) and not self.data["layers"]:
            self.add("LT008", ERROR, "$.layers", "layers is empty; nothing will render")

        if fr and ip is not None and op is not None and op > ip:
            duration = (op - ip) / fr
            self.stats["duration_s"] = round(duration, 3)
            self.stats["frames"] = op - ip
            if duration < 0.1:
                self.add(
                    "LT009", WARN, "$", "duration is %.3fs; too short to read" % duration,
                    "Sub-100ms motion registers as a glitch, not an animation.",
                )
            elif duration > 30:
                self.add(
                    "LT010", WARN, "$", "duration is %.1fs; very long for a Lottie" % duration,
                )
        if not data.get("nm"):
            self.add(
                "LT011", INFO, "$.nm", "composition has no name",
                "Named compositions are easier to debug in a player.",
            )
        if data.get("ddd"):
            self.add(
                "LT012", WARN, "$.ddd", "3D flag is on; most web players ignore 3D layers",
                "Set ddd to 0 unless you are targeting a renderer with 3D support.",
            )

    # -- assets ------------------------------------------------------------
    def check_assets(self):
        assets = self.data.get("assets")
        if assets is None:
            return
        if not isinstance(assets, list):
            self.add("AS001", ERROR, "$.assets", "assets must be an array")
            return
        seen = {}
        for index, asset in enumerate(assets):
            if not isinstance(asset, dict):
                self.add("AS002", ERROR, "$.assets[%d]" % index, "asset must be an object")
                continue
            aid = asset.get("id")
            if aid is None:
                self.add("AS003", ERROR, "$.assets[%d]" % index, "asset has no id")
                continue
            if aid in seen:
                self.add(
                    "AS004", ERROR, "$.assets[%d]" % index,
                    "duplicate asset id %r (also at index %d)" % (aid, seen[aid]),
                )
            seen[aid] = index

        referenced = set()
        _collect_refids(self.data.get("layers"), referenced)
        for asset in assets:
            if isinstance(asset, dict) and "layers" in asset:
                _collect_refids(asset.get("layers"), referenced)
        for aid, index in seen.items():
            if aid not in referenced:
                self.add(
                    "AS005", WARN, "$.assets[%d]" % index,
                    "asset %r is never referenced; it only adds file size" % aid,
                )
        for ref, where in referenced_pairs(self.data):
            if ref not in seen:
                self.add(
                    "AS006", ERROR, where, "refId %r does not match any asset" % ref,
                    "The layer will render as empty.",
                )

    # -- layers ------------------------------------------------------------
    def check_layers(self):
        layers = self.data.get("layers")
        if not isinstance(layers, list):
            return
        comp_ip = _num(self.data.get("ip")) or 0
        comp_op = _num(self.data.get("op"))
        self.stats["layers"] = len(layers)

        by_ind = {}
        for index, layer in enumerate(layers):
            if not isinstance(layer, dict):
                self.add("LY001", ERROR, "$.layers[%d]" % index, "layer must be an object")
                continue
            ind = layer.get("ind")
            if ind is not None:
                if ind in by_ind:
                    self.add(
                        "LY002", ERROR, "$.layers[%d].ind" % index,
                        "duplicate layer ind %r (also at index %d)" % (ind, by_ind[ind]),
                        "Parenting resolves by ind; duplicates make it ambiguous.",
                    )
                by_ind[ind] = index

        for index, layer in enumerate(layers):
            if isinstance(layer, dict):
                self.check_layer(index, layer, comp_ip, comp_op, by_ind, layers)

    def check_layer(self, index, layer, comp_ip, comp_op, by_ind, layers):
        where = "$.layers[%d]" % index
        name = layer.get("nm")
        label = "%s (%s)" % (where, name) if name else where

        ty = layer.get("ty")
        if ty is None:
            self.add("LY003", ERROR, where + ".ty", "layer has no type")
        elif ty not in LAYER_TYPES:
            self.add("LY004", WARN, where + ".ty", "unknown layer type %r" % ty)

        # The defect that renders a layer invisible while the JSON still parses.
        # st matters as much as ip/op: the playhead is compared against
        # (frame - st), and an undefined st makes that comparison NaN, so the
        # layer is hidden at every frame. Verified by rendering.
        missing = [k for k in ("ip", "op", "st") if k not in layer]
        if missing:
            self.add(
                "LY005", ERROR, where,
                "%s missing %s; the layer will not render"
                % (label, " and ".join(missing)),
                "Players compare the playhead against the layer's ip/op offset by "
                "st. Any of them undefined makes the comparison fail at every "
                'frame and the layer silently disappears. Set ip/op to the visible '
                'range and st to 0 unless the layer is time-shifted.',
            )
        else:
            lip = _num(layer.get("ip"))
            lop = _num(layer.get("op"))
            if lip is None or lop is None:
                self.add("LY006", ERROR, where, "%s has non-numeric ip/op" % label)
            else:
                if lop <= lip:
                    self.add(
                        "LY007", ERROR, where,
                        "%s has op (%g) <= ip (%g); it is never visible" % (label, lop, lip),
                    )
                elif comp_op is not None and (lip >= comp_op or lop <= comp_ip):
                    self.add(
                        "LY008", ERROR, where,
                        "%s lives outside the composition range [%g, %g)" % (label, comp_ip, comp_op),
                        "Nothing in this layer will ever be on screen.",
                    )

        if not name:
            self.add(
                "LY009", INFO, where + ".nm", "layer %d has no name" % index,
                "Names are what make a 12-layer file debuggable.",
            )
        if layer.get("hd"):
            self.add("LY010", WARN, where + ".hd", "%s is hidden" % label)

        parent = layer.get("parent")
        if parent is not None:
            if parent not in by_ind:
                self.add(
                    "LY011", ERROR, where + ".parent",
                    "%s is parented to ind %r, which does not exist" % (label, parent),
                )
            else:
                cycle = self._parent_cycle(index, layers, by_ind)
                if cycle:
                    self.add(
                        "LY012", ERROR, where + ".parent",
                        "parenting cycle: %s" % " -> ".join(str(c) for c in cycle),
                        "A parent chain must terminate; a loop hangs or breaks the renderer.",
                    )

        if ty == 4:
            shapes = layer.get("shapes")
            if not isinstance(shapes, list) or not shapes:
                self.add(
                    "LY013", ERROR, where + ".shapes",
                    "%s is a shape layer with no shapes" % label,
                )
            else:
                self._check_paintable(shapes, where + ".shapes", label)
                self._check_occluded(shapes, where + ".shapes", label)
                self._check_shape_items(shapes, where + ".shapes", label)

        ks = layer.get("ks")
        if not isinstance(ks, dict):
            self.add("LY014", ERROR, where + ".ks", "%s has no transform (ks)" % label)
        else:
            self._check_opacity(ks, where, label)

        self._check_properties(layer, where, label, comp_ip, comp_op)

    def _parent_cycle(self, start_index, layers, by_ind):
        seen = []
        index = start_index
        for _ in range(len(layers) + 1):
            if index in seen:
                return seen[seen.index(index):] + [index]
            seen.append(index)
            parent = layers[index].get("parent")
            if parent is None or parent not in by_ind:
                return None
            index = by_ind[parent]
        return seen

    def _check_paintable(self, shapes, where, label):
        """A shape layer with only geometry and no fill or stroke paints nothing."""
        kinds = set()
        _collect_shape_types(shapes, kinds)
        if not kinds & {"fl", "st", "gf", "gs"}:
            self.add(
                "LY015", WARN, where,
                "%s has no fill or stroke; the geometry is invisible" % label,
                "Add a fill (fl) or stroke (st) item to the shape group.",
            )

    def _check_occluded(self, shapes, where, label):
        """A group hidden underneath an opaque sibling renders, then disappears.

        Lottie paints the FIRST item of a `shapes` array on top. Authoring a
        character front-to-back — the way layer panels in most editors read —
        puts the face plate above the eyes, and every feature is drawn and then
        covered by an opaque ellipse. Nothing is malformed, so every structural
        check passes and the canvas is simply wrong. This repository shipped
        exactly that defect in `panda-loader.json` for two releases.

        Only certain occlusion is reported. A group has to be opaque, static
        and unrotated to count as a coverer, and the covered geometry has to
        fall inside the *inscribed* box of the covering shape, never merely its
        bounding box — an ellipse leaves its corners visible.
        """
        groups = [
            (index, item) for index, item in enumerate(shapes)
            if isinstance(item, dict) and item.get("ty") == "gr"
        ]
        if len(groups) < 2:
            return

        described = []
        for index, group in groups:
            described.append((index, group, _group_footprint(group)))

        for above_pos, (above_index, above, above_fp) in enumerate(described):
            if above_fp is None or above_fp.solid is None:
                continue
            for below_index, below, below_fp in described[above_pos + 1:]:
                if below_fp is None or below_fp.extent is None:
                    continue
                if not _contains(above_fp.solid, below_fp.extent):
                    continue
                self.add(
                    "SH004", WARN, "%s[%d]" % (where, below_index),
                    "%s: %s is completely covered by %s, painted above it"
                    % (
                        label,
                        _brief(below.get("nm") or "group %d" % below_index, 28),
                        _brief(above.get("nm") or "group %d" % above_index, 28),
                    ),
                    "Lottie paints the first item of a shapes array on top, so "
                    "this group renders and is then hidden. If it was authored "
                    "back-to-front, reverse the order of the groups.",
                )

    def _check_shape_items(self, node, where, label):
        """Walk shape items and confirm each carries the properties its type needs."""
        if isinstance(node, list):
            for index, item in enumerate(node):
                self._check_shape_items(item, "%s[%d]" % (where, index), label)
            return
        if not isinstance(node, dict):
            return

        ty = node.get("ty")
        if isinstance(ty, str) and ty in SHAPE_REQUIRED:
            label = SHAPE_NAMES.get(ty, ty)
            name = _brief(node.get("nm") or ty, 24)
            required = list(SHAPE_REQUIRED[ty])
            if ty == "sr" and node.get("sy", 1) == 1:
                required.extend(STAR_REQUIRED)
            # A skew angle without its axis blanks the layer; the axis alone is fine.
            if ty == "tr" and "sk" in node:
                required.append("sa")

            missing = [key for key in required if key not in node]
            if missing:
                self.add(
                    "SH001", ERROR, where,
                    "%s %s is missing %s" % (label, name, ", ".join(missing)),
                    "Players throw while building this item and then drop the entire "
                    "layer without reporting an error: the file loads and paints "
                    "nothing. Every %s needs %s." % (label, ", ".join(required)),
                )

            advisory = [
                key for key in SHAPE_RECOMMENDED.get(ty, ()) if key not in node
            ]
            if advisory:
                self.add(
                    "SH003", WARN, where,
                    "%s %s is missing %s" % (label, name, ", ".join(advisory)),
                    "The specification requires this. lottie-web substitutes a "
                    "default, but other players are not guaranteed to.",
                )
        elif isinstance(ty, str) and ty not in SHAPE_NAMES and ty not in ("mm", "gr"):
            self.add("SH002", WARN, where, "unknown shape item type %r" % ty)

        if isinstance(node.get("it"), list):
            self._check_shape_items(node["it"], where + ".it", label)

    def _check_opacity(self, ks, where, label):
        opacity = ks.get("o")
        if not isinstance(opacity, dict):
            return
        values = _property_values(opacity)
        if values and all(_scalar(v) == 0 for v in values):
            self.add(
                "LY016", ERROR, where + ".ks.o",
                "%s has opacity 0 for its whole life; it is invisible" % label,
                "The file will validate and render nothing. Check the opacity keyframes.",
            )

    # -- properties --------------------------------------------------------
    def _check_properties(self, layer, base, label, comp_ip, comp_op):
        lip = _num(layer.get("ip"))
        lop = _num(layer.get("op"))
        if lip is None:
            lip = comp_ip
        if lop is None:
            lop = comp_op
        for path, prop in _walk_properties(layer, base):
            self._check_property(path, prop, label, lip, lop)

    def _check_property(self, path, prop, label, lip, lop):
        # Easing handles belong to individual keyframes, never to the property
        # that holds them. Misplaced handles do not degrade gracefully: the
        # player throws mid-render and the whole frame comes out blank.
        misplaced = [key for key in ("i", "o", "t", "s", "h") if key in prop]
        if misplaced:
            self.add(
                "KF011", ERROR, path,
                "keyframe field(s) %s sit on the property instead of inside a keyframe"
                % ", ".join(repr(k) for k in misplaced),
                "Move them into the keyframe object they belong to, e.g. "
                'k[0]["o"] rather than the property\'s "o". A player hitting this '
                "aborts the render pass, so every layer in the file goes blank.",
            )

        if prop.get("a") != 1:
            return
        keyframes = prop.get("k")
        if not isinstance(keyframes, list) or not keyframes:
            self.add("KF001", ERROR, path, "animated property has no keyframes")
            return
        if not all(isinstance(kf, dict) for kf in keyframes):
            self.add(
                "KF002", ERROR, path,
                "animated property (a=1) holds a static value",
                "Set a to 0 for a constant value, or supply a keyframe array.",
            )
            return

        self.stats["animated_properties"] = self.stats.get("animated_properties", 0) + 1

        times = []
        for i, kf in enumerate(keyframes):
            t = _num(kf.get("t"))
            if t is None:
                self.add("KF003", ERROR, "%s.k[%d]" % (path, i), "keyframe has no time (t)")
                continue
            times.append(t)

        for i in range(1, len(times)):
            if times[i] <= times[i - 1]:
                self.add(
                    "KF004", ERROR, "%s.k[%d]" % (path, i),
                    "keyframe times must strictly increase (t=%g after t=%g)"
                    % (times[i], times[i - 1]),
                    "Out-of-order keyframes make playback jump or freeze.",
                )
                break

        if len(keyframes) == 1:
            self.add(
                "KF005", WARN, path,
                "animated property has a single keyframe; nothing moves",
                "Either add a second keyframe or set a to 0.",
            )

        if times and lop is not None and lip is not None:
            if all(t >= lop for t in times) or all(t < lip for t in times):
                self.add(
                    "KF006", WARN, path,
                    "all keyframes fall outside the layer range [%g, %g)" % (lip, lop),
                    "This motion never plays.",
                )

        # Easing handles: x must stay inside [0,1] or the curve is not a function
        # of time. y may overshoot -- that is what produces a bounce.
        linear = 0
        for i, kf in enumerate(keyframes[:-1]):
            if kf.get("h"):  # hold keyframe: no interpolation by design
                continue
            if kf.get("i") is None or kf.get("o") is None:
                linear += 1
            for handle in ("i", "o"):
                spec = kf.get(handle)
                if spec is None:
                    continue
                for axis in ("x", "y"):
                    for value in _as_list(spec.get(axis)):
                        v = _num(value)
                        if v is None:
                            self.add(
                                "KF008", ERROR, "%s.k[%d].%s.%s" % (path, i, handle, axis),
                                "easing handle must be numeric",
                            )
                        elif axis == "x" and not 0 <= v <= 1:
                            self.add(
                                "KF009", ERROR, "%s.k[%d].%s.x" % (path, i, handle),
                                "easing handle x is %g; must be within [0, 1]" % v,
                                "Only y may overshoot 1 (that is how you get a bounce).",
                            )

        if linear:
            self.linear_properties.append(path)

        self._check_loop_closure(path, keyframes, times, label, lip, lop)

    def _check_loop_closure(self, path, keyframes, times, label, lip, lop):
        """A looping property must end where it started or the wrap will jump."""
        if not self.loop or len(keyframes) < 2 or lop is None or lip is None or not times:
            return
        spans_comp = times[0] <= lip and times[-1] >= lop - 1
        if not spans_comp:
            return
        first = keyframes[0].get("s")
        last = keyframes[-1].get("s")
        if last is None:
            last = keyframes[-2].get("e", keyframes[-1].get("s"))
        if first is None or last is None:
            return
        # A full turn is a closed loop: 0deg and 360deg are the same pose.
        if _is_rotation(path) and _turns_full_circle(first, last):
            return
        if not _values_close(first, last):
            self.add(
                "KF010", WARN, path,
                "loop does not close: starts at %s, ends at %s"
                % (_brief(first), _brief(last)),
                "The wrap from the last frame to the first will visibly jump. Match the "
                "first and last values, or shorten the loop to where they do match.",
            )

    def report_linear_easing(self):
        """One summary beats one finding per keyframe; this is a taste note."""
        count = len(self.linear_properties)
        if not count:
            return
        total = self.stats.get("animated_properties", count)
        shown = ", ".join(self.linear_properties[:3])
        if count > 3:
            shown += ", +%d more" % (count - 3)
        severity = WARN if total and count == total else INFO
        self.add(
            "KF007", severity, "$",
            "%d of %d animated properties interpolate linearly" % (count, total),
            "Linear motion reads as mechanical. Entrances want an ease-out, exits an "
            "ease-in, loops an ease-in-out. Affected: %s" % shown,
        )

    # -- whole-file motion -------------------------------------------------
    def check_motion_presence(self):
        if self.allow_static:
            return
        layers = self.data.get("layers")
        if not isinstance(layers, list) or not layers:
            return
        if self.stats.get("animated_properties"):
            return
        uses_frame_switching = any(
            isinstance(layer, dict)
            and _num(layer.get("ip")) is not None
            and _num(layer.get("op")) is not None
            and (_num(layer.get("op")) - _num(layer.get("ip")))
            < (_num(self.data.get("op")) or 0) - (_num(self.data.get("ip")) or 0)
            for layer in layers
        )
        if uses_frame_switching:
            return
        self.add(
            "MQ001", ERROR, "$", "no animated properties; this is a static image",
            "Every property has a=0. Animate at least one of position, scale, "
            "rotation, opacity, or a trim path.",
        )


# -- helpers ---------------------------------------------------------------
def _collapse(findings):
    """The same defect repeated 32 times is one thing to fix, not 32."""
    grouped = {}
    order = []
    for finding in findings:
        key = (finding.code, finding.message)
        if key not in grouped:
            grouped[key] = [finding, 1]
            order.append(key)
        else:
            grouped[key][1] += 1
    out = []
    for key in order:
        finding, count = grouped[key]
        if count > 1:
            finding.where = "%s (and %d more)" % (finding.where, count - 1)
            finding.message = "%s  [x%d]" % (finding.message, count)
        out.append(finding)
    return out


def _num(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _scalar(value):
    if isinstance(value, list):
        return _scalar(value[0]) if value else None
    return _num(value)


def _property_values(prop):
    """Every value a property takes, static or keyframed."""
    if prop.get("a") == 1:
        keyframes = prop.get("k")
        if not isinstance(keyframes, list):
            return []
        out = []
        for kf in keyframes:
            if isinstance(kf, dict) and "s" in kf:
                out.append(kf["s"])
        return out
    return [prop.get("k")]


def _is_property(node):
    """A Lottie property is an object with an integer animated flag and a value."""
    return (
        isinstance(node, dict)
        and "k" in node
        and isinstance(node.get("a"), int)
        and not isinstance(node.get("a"), bool)
    )


def _walk_properties(node, path):
    """Yield (json_path, property) for every animatable property under node."""
    if _is_property(node):
        yield path, node
        return
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _walk_properties(value, "%s.%s" % (path, key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk_properties(value, "%s[%d]" % (path, index))


def _collect_refids(node, out):
    if isinstance(node, dict):
        if isinstance(node.get("refId"), str):
            out.add(node["refId"])
        for value in node.values():
            _collect_refids(value, out)
    elif isinstance(node, list):
        for value in node:
            _collect_refids(value, out)


def referenced_pairs(data):
    """(refId, json_path) for every reference, so misses can be located."""
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            if isinstance(node.get("refId"), str):
                out.append((node["refId"], path + ".refId"))
            for key, value in node.items():
                walk(value, "%s.%s" % (path, key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, "%s[%d]" % (path, index))

    walk(data.get("layers"), "$.layers")
    return out


class _Footprint:
    """What a shape group definitely paints, and how far it definitely reaches.

    `solid` is the largest axis-aligned box the group is guaranteed to fill
    with an opaque colour, or None when that cannot be established. `extent`
    is the box outside which the group certainly paints nothing.
    """

    __slots__ = ("solid", "extent")

    def __init__(self, solid, extent):
        self.solid = solid
        self.extent = extent


def _static(prop):
    """The value of a property that never animates, else None."""
    if not isinstance(prop, dict) or prop.get("a") == 1:
        return None
    return prop.get("k")


def _static_pair(prop):
    value = _static(prop)
    if not isinstance(value, list) or len(value) < 2:
        return None
    x, y = _num(value[0]), _num(value[1])
    return None if x is None or y is None else (x, y)


def _translation_only(group):
    """Offset of a group whose transform is a pure, static translation.

    Anything else — animated, scaled, rotated or skewed — returns None, which
    takes the group out of the check entirely rather than guessing at its
    footprint.
    """
    tr = None
    for item in group.get("it") or []:
        if isinstance(item, dict) and item.get("ty") == "tr":
            tr = item
    if tr is None:
        return (0.0, 0.0)

    opacity = _static(tr.get("o"))
    if _scalar(opacity) is not None and _scalar(opacity) < 100:
        return None
    for key in ("r", "rz", "sk", "sa"):
        if key in tr:
            angle = _scalar(_static(tr.get(key)))
            if angle is None or abs(angle) > 0.01:
                return None
    if "s" in tr:
        scale = _static_pair(tr.get("s"))
        if scale is None or abs(scale[0] - 100) > 0.01 or abs(scale[1] - 100) > 0.01:
            return None

    position = _static_pair(tr.get("p")) if "p" in tr else (0.0, 0.0)
    anchor = _static_pair(tr.get("a")) if "a" in tr else (0.0, 0.0)
    if position is None or anchor is None:
        return None
    return (position[0] - anchor[0], position[1] - anchor[1])


def _group_footprint(group):
    if not isinstance(group, dict) or not isinstance(group.get("it"), list):
        return None
    offset = _translation_only(group)
    if offset is None:
        return None

    items = group["it"]
    # A nested group could paint anywhere; refuse to reason about it.
    if any(isinstance(i, dict) and i.get("ty") == "gr" for i in items):
        return None

    opaque_fill = False
    stroke_reach = 0.0
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("ty") == "fl":
            alpha = _scalar(_static(item.get("o")))
            if alpha is not None and alpha >= 100:
                opaque_fill = True
        elif item.get("ty") in ("st", "gs"):
            width = _scalar(_static(item.get("w")))
            if width is None:
                return None          # unknown reach; do not bound this group
            stroke_reach = max(stroke_reach, width / 2.0)
        elif item.get("ty") in ("rp",):
            return None              # a repeater clones geometry elsewhere

    boxes = []
    inscribed = []
    for item in items:
        if not isinstance(item, dict):
            continue
        ty = item.get("ty")
        if ty not in ("el", "rc"):
            if ty in ("sh", "sr"):
                return None          # arbitrary path: no cheap, safe bounds
            continue
        centre = _static_pair(item.get("p"))
        size = _static_pair(item.get("s"))
        if centre is None or size is None:
            return None
        cx, cy = centre[0] + offset[0], centre[1] + offset[1]
        hw, hh = abs(size[0]) / 2.0, abs(size[1]) / 2.0
        boxes.append((cx - hw - stroke_reach, cy - hh - stroke_reach,
                      cx + hw + stroke_reach, cy + hh + stroke_reach))
        if ty == "el":
            # The largest axis-aligned box inside an ellipse.
            inscribed.append((cx - hw * 0.7071, cy - hh * 0.7071,
                              cx + hw * 0.7071, cy + hh * 0.7071))
        else:
            radius = _scalar(_static(item.get("r"))) or 0.0
            inscribed.append((cx - hw + radius, cy - hh + radius,
                              cx + hw - radius, cy + hh - radius))

    if not boxes:
        return None
    extent = (min(b[0] for b in boxes), min(b[1] for b in boxes),
              max(b[2] for b in boxes), max(b[3] for b in boxes))
    # One shape is enough to cover; several would need a union, which is not
    # worth the risk of claiming solidity that is not there.
    solid = inscribed[0] if opaque_fill and len(inscribed) == 1 else None
    return _Footprint(solid, extent)


def _contains(outer, inner):
    return (
        outer[0] <= inner[0] and outer[1] <= inner[1]
        and outer[2] >= inner[2] and outer[3] >= inner[3]
    )


def _collect_shape_types(node, out):
    if isinstance(node, dict):
        if isinstance(node.get("ty"), str):
            out.add(node["ty"])
        for value in node.values():
            _collect_shape_types(value, out)
    elif isinstance(node, list):
        for value in node:
            _collect_shape_types(value, out)


def _is_rotation(path):
    """Transform rotation, in 2D (r) or on the z axis (rz)."""
    return path.endswith(".r") or path.endswith(".rz")


def _turns_full_circle(first, last, tolerance=0.5):
    a, b = _scalar(first), _scalar(last)
    if a is None or b is None:
        return False
    delta = abs(b - a)
    return delta >= 1 and abs(delta % 360) <= tolerance


def _values_close(a, b, tolerance=0.5):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tolerance
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(_values_close(x, y, tolerance) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return False
        return all(_values_close(a[k], b[k], tolerance) for k in a)
    return a == b


def _brief(value, limit=40):
    text = json.dumps(value, separators=(",", ":"))
    return text if len(text) <= limit else text[: limit - 1] + "…"


# -- cli -------------------------------------------------------------------
def collect_paths(args):
    paths = []
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.json")))
        else:
            paths.append(path)
    return paths


def lint_file(path, loop=None, allow_static=False):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [Finding("IO001", ERROR, str(path), "cannot read file: %s" % exc)], {}
    except json.JSONDecodeError as exc:
        return [
            Finding(
                "IO002", ERROR, "%s:%d" % (path, exc.lineno),
                "invalid JSON: %s" % exc.msg,
            )
        ], {}
    linter = Linter(data, loop=loop, source_name=path.name, allow_static=allow_static)
    return linter.run(), linter.stats


SYMBOL = {ERROR: "x", WARN: "!", INFO: "-"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Lint Lottie JSON for structural, timing, and motion defects."
    )
    parser.add_argument("paths", nargs="*", help="files or directories (default: examples/)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--strict", action="store_true", help="warnings fail the run")
    parser.add_argument("--quiet", action="store_true", help="only show failures")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="include info-level notes"
    )
    parser.add_argument(
        "--allow-static", action="store_true",
        help="accept a composition with no animation (e.g. fresh svg2lottie output)",
    )
    parser.add_argument(
        "--loop", dest="loop", action="store_true", default=None,
        help="check that looping properties close (auto-detected from the name)",
    )
    parser.add_argument(
        "--no-loop", dest="loop", action="store_false",
        help="skip loop-closure checks; the animation plays once",
    )
    args = parser.parse_args(argv)

    paths = collect_paths(args.paths) if args.paths else sorted(Path("examples").glob("*.json"))
    if not paths:
        print("no Lottie files found", file=sys.stderr)
        return 2

    threshold = WARN if args.strict else ERROR
    limit = _SEVERITY_ORDER[threshold]
    show = _SEVERITY_ORDER[INFO] if args.verbose else _SEVERITY_ORDER[WARN]
    report = []
    failed = False

    for path in paths:
        findings, stats = lint_file(path, loop=args.loop, allow_static=args.allow_static)
        blocking = [f for f in findings if _SEVERITY_ORDER[f.severity] <= limit]
        if blocking:
            failed = True
        report.append(
            {
                "file": str(path),
                "ok": not blocking,
                "stats": stats,
                "findings": [f.as_dict() for f in findings],
            }
        )
        if args.json:
            continue
        visible = [f for f in findings if _SEVERITY_ORDER[f.severity] <= show]
        hidden = len(findings) - len(visible)
        if not visible:
            if not args.quiet:
                print("PASS %s%s%s" % (path, _stats_suffix(stats), _hidden_suffix(hidden)))
            continue
        status = "FAIL" if blocking else "PASS"
        if args.quiet and not blocking:
            continue
        print("%s %s%s%s" % (status, path, _stats_suffix(stats), _hidden_suffix(hidden)))
        for finding in visible:
            print(
                "  %s %s  %s"
                % (SYMBOL[finding.severity], finding.code, finding.message)
            )
            print("      at %s" % finding.where)
            if finding.hint:
                print("      %s" % finding.hint)

    if args.json:
        print(json.dumps(report, indent=2))
    return 1 if failed else 0


def _hidden_suffix(hidden):
    return "  [%d note%s, -v]" % (hidden, "" if hidden == 1 else "s") if hidden else ""


def _stats_suffix(stats):
    if not stats:
        return ""
    bits = []
    if "layers" in stats:
        bits.append("%d layers" % stats["layers"])
    if "duration_s" in stats:
        bits.append("%gs" % stats["duration_s"])
    if "animated_properties" in stats:
        bits.append("%d animated props" % stats["animated_properties"])
    return "  (%s)" % ", ".join(bits) if bits else ""


if __name__ == "__main__":
    raise SystemExit(main())
