"""SVG path data to cubic bezier segments.

Every command is reduced to cubics, because that is the only curve Lottie
stores. Arcs are split into <=90 degree pieces before conversion, which keeps
the error below a rounding artefact at icon scale.

Dependency-free. Python 3.8+.
"""
from __future__ import annotations

import math
import re

NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
COMMAND = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]")

# How many arguments each command consumes per repetition.
ARITY = {
    "M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4,
    "Q": 4, "T": 2, "A": 7, "Z": 0,
}


class PathError(ValueError):
    """The path data cannot be parsed."""


def tokenize(data):
    """Split path data into (command, [numbers]) pairs."""
    tokens = []
    index = 0
    length = len(data)
    while index < length:
        char = data[index]
        if char.isspace() or char == ",":
            index += 1
            continue
        if not COMMAND.match(char):
            raise PathError("unexpected character %r at position %d" % (char, index))
        command = char
        index += 1
        numbers = []
        while index < length:
            match = NUMBER.match(data, index)
            if not match:
                if data[index].isspace() or data[index] == ",":
                    index += 1
                    continue
                break
            numbers.append(float(match.group()))
            index = match.end()
        tokens.append((command, numbers))
    return tokens


def _chunks(values, size):
    if size == 0:
        yield []
        return
    if len(values) % size:
        raise PathError(
            "expected a multiple of %d arguments, got %d" % (size, len(values))
        )
    for start in range(0, len(values), size):
        yield values[start:start + size]


def parse_path(data):
    """Convert path data into subpaths of cubic segments.

    Returns a list of subpaths. Each subpath is
    ``{"segments": [(p0, c1, c2, p3), ...], "closed": bool}``.
    """
    subpaths = []
    segments = []
    closed = False
    start = (0.0, 0.0)
    current = (0.0, 0.0)
    previous_cubic_control = None
    previous_quad_control = None
    previous_command = None

    def flush():
        nonlocal segments, closed
        if segments:
            subpaths.append({"segments": segments, "closed": closed})
        segments = []
        closed = False

    for command, numbers in tokenize(data):
        upper = command.upper()
        relative = command.islower()
        if upper not in ARITY:
            raise PathError("unsupported command %r" % command)

        if upper == "Z":
            if segments and current != start:
                segments.append((current, current, start, start))
            closed = True
            current = start
            flush()
            previous_command = upper
            continue

        # A moveto with extra coordinate pairs implies lineto for the rest.
        groups = list(_chunks(numbers, ARITY[upper]))
        if not groups:
            raise PathError("command %r has no arguments" % command)

        for position, args in enumerate(groups):
            if upper == "M":
                if position == 0:
                    flush()
                    current = _point(args, current, relative)
                    start = current
                else:
                    target = _point(args, current, relative)
                    segments.append(_line(current, target))
                    current = target
                previous_cubic_control = previous_quad_control = None
            elif upper == "L":
                target = _point(args, current, relative)
                segments.append(_line(current, target))
                current = target
                previous_cubic_control = previous_quad_control = None
            elif upper == "H":
                x = args[0] + (current[0] if relative else 0)
                target = (x, current[1])
                segments.append(_line(current, target))
                current = target
                previous_cubic_control = previous_quad_control = None
            elif upper == "V":
                y = args[0] + (current[1] if relative else 0)
                target = (current[0], y)
                segments.append(_line(current, target))
                current = target
                previous_cubic_control = previous_quad_control = None
            elif upper == "C":
                c1 = _point(args[0:2], current, relative)
                c2 = _point(args[2:4], current, relative)
                target = _point(args[4:6], current, relative)
                segments.append((current, c1, c2, target))
                previous_cubic_control = c2
                previous_quad_control = None
                current = target
            elif upper == "S":
                # The first control point mirrors the previous curve's second.
                if previous_command in ("C", "S") and previous_cubic_control:
                    c1 = _reflect(previous_cubic_control, current)
                else:
                    c1 = current
                c2 = _point(args[0:2], current, relative)
                target = _point(args[2:4], current, relative)
                segments.append((current, c1, c2, target))
                previous_cubic_control = c2
                previous_quad_control = None
                current = target
            elif upper == "Q":
                control = _point(args[0:2], current, relative)
                target = _point(args[2:4], current, relative)
                segments.append(_quadratic(current, control, target))
                previous_quad_control = control
                previous_cubic_control = None
                current = target
            elif upper == "T":
                if previous_command in ("Q", "T") and previous_quad_control:
                    control = _reflect(previous_quad_control, current)
                else:
                    control = current
                target = _point(args[0:2], current, relative)
                segments.append(_quadratic(current, control, target))
                previous_quad_control = control
                previous_cubic_control = None
                current = target
            elif upper == "A":
                rx, ry, rotation, large_arc, sweep = args[0:5]
                target = _point(args[5:7], current, relative)
                segments.extend(
                    arc_to_cubics(current, rx, ry, rotation, large_arc, sweep, target)
                )
                previous_cubic_control = previous_quad_control = None
                current = target
            previous_command = upper

    flush()
    return subpaths


def _point(args, current, relative):
    if relative:
        return (args[0] + current[0], args[1] + current[1])
    return (args[0], args[1])


def _reflect(control, origin):
    return (2 * origin[0] - control[0], 2 * origin[1] - control[1])


def _line(a, b):
    """A straight line as a cubic whose controls sit on the endpoints."""
    return (a, a, b, b)


def _quadratic(p0, control, p2):
    c1 = (p0[0] + 2.0 / 3.0 * (control[0] - p0[0]), p0[1] + 2.0 / 3.0 * (control[1] - p0[1]))
    c2 = (p2[0] + 2.0 / 3.0 * (control[0] - p2[0]), p2[1] + 2.0 / 3.0 * (control[1] - p2[1]))
    return (p0, c1, c2, p2)


def arc_to_cubics(start, rx, ry, rotation, large_arc, sweep, end):
    """Endpoint-parameterised arc to cubic segments (SVG spec F.6)."""
    if start == end:
        return []
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0:
        return [_line(start, end)]

    phi = math.radians(rotation % 360)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)

    dx = (start[0] - end[0]) / 2.0
    dy = (start[1] - end[1]) / 2.0
    x1 = cos_phi * dx + sin_phi * dy
    y1 = -sin_phi * dx + cos_phi * dy

    # Scale up radii that are too small to span the endpoints (spec F.6.6).
    lam = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if lam > 1:
        scale = math.sqrt(lam)
        rx *= scale
        ry *= scale

    denominator = rx * rx * y1 * y1 + ry * ry * x1 * x1
    numerator = rx * rx * ry * ry - denominator
    factor = 0.0 if numerator <= 0 else math.sqrt(numerator / denominator)
    if bool(large_arc) == bool(sweep):
        factor = -factor
    cx1 = factor * rx * y1 / ry
    cy1 = -factor * ry * x1 / rx

    cx = cos_phi * cx1 - sin_phi * cy1 + (start[0] + end[0]) / 2.0
    cy = sin_phi * cx1 + cos_phi * cy1 + (start[1] + end[1]) / 2.0

    theta = _angle(1.0, 0.0, (x1 - cx1) / rx, (y1 - cy1) / ry)
    delta = _angle((x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi

    # Cubic approximation degrades past a quarter turn, so subdivide.
    count = max(1, int(math.ceil(abs(delta) / (math.pi / 2))))
    step = delta / count
    alpha = 4.0 / 3.0 * math.tan(step / 4.0)

    segments = []
    current = start
    for index in range(count):
        angle1 = theta + index * step
        angle2 = angle1 + step
        p1 = _ellipse_point(cx, cy, rx, ry, cos_phi, sin_phi, angle1)
        p2 = _ellipse_point(cx, cy, rx, ry, cos_phi, sin_phi, angle2)
        d1 = _ellipse_derivative(rx, ry, cos_phi, sin_phi, angle1)
        d2 = _ellipse_derivative(rx, ry, cos_phi, sin_phi, angle2)
        c1 = (p1[0] + alpha * d1[0], p1[1] + alpha * d1[1])
        c2 = (p2[0] - alpha * d2[0], p2[1] - alpha * d2[1])
        target = end if index == count - 1 else p2
        segments.append((current, c1, c2, target))
        current = target
    return segments


def _ellipse_point(cx, cy, rx, ry, cos_phi, sin_phi, angle):
    x = rx * math.cos(angle)
    y = ry * math.sin(angle)
    return (cos_phi * x - sin_phi * y + cx, sin_phi * x + cos_phi * y + cy)


def _ellipse_derivative(rx, ry, cos_phi, sin_phi, angle):
    x = -rx * math.sin(angle)
    y = ry * math.cos(angle)
    return (cos_phi * x - sin_phi * y, sin_phi * x + cos_phi * y)


def _angle(ux, uy, vx, vy):
    dot = ux * vx + uy * vy
    magnitude = math.sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
    if magnitude == 0:
        return 0.0
    value = max(-1.0, min(1.0, dot / magnitude))
    angle = math.acos(value)
    if ux * vy - uy * vx < 0:
        angle = -angle
    return angle


def segments_to_lottie(subpath, transform=None, precision=3):
    """Convert one subpath into a Lottie bezier shape ({i, o, v, c})."""
    segments = subpath["segments"]
    closed = subpath["closed"]
    if not segments:
        return None

    apply = transform if transform else (lambda p: p)
    vertices = [apply(segments[0][0])]
    out_tangents = []
    in_tangents = [(0.0, 0.0)]

    for p0, c1, c2, p3 in segments:
        a, b, c, d = apply(p0), apply(c1), apply(c2), apply(p3)
        out_tangents.append((b[0] - a[0], b[1] - a[1]))
        vertices.append(d)
        in_tangents.append((c[0] - d[0], c[1] - d[1]))
    out_tangents.append((0.0, 0.0))

    # A closed path repeats its start point; fold that duplicate away and carry
    # the tangents across the seam so the join stays smooth.
    if closed and len(vertices) > 1 and _close(vertices[0], vertices[-1]):
        in_tangents[0] = in_tangents[-1]
        vertices.pop()
        out_tangents.pop()
        in_tangents.pop()

    rounder = lambda pair: [round(pair[0], precision), round(pair[1], precision)]
    return {
        "i": [rounder(t) for t in in_tangents],
        "o": [rounder(t) for t in out_tangents],
        "v": [rounder(v) for v in vertices],
        "c": bool(closed),
    }


def _close(a, b, tolerance=1e-6):
    return abs(a[0] - b[0]) <= tolerance and abs(a[1] - b[1]) <= tolerance


def bounds(subpaths, transform=None):
    """Bounding box over control points: (min_x, min_y, max_x, max_y)."""
    apply = transform if transform else (lambda p: p)
    xs, ys = [], []
    for subpath in subpaths:
        for segment in subpath["segments"]:
            for point in segment:
                x, y = apply(point)
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))
