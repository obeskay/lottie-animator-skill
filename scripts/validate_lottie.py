#!/usr/bin/env python3
"""Dependency-free Lottie JSON smoke test."""
from __future__ import annotations
import json
import sys
from pathlib import Path

REQUIRED = ("v", "fr", "ip", "op", "w", "h", "layers")

def validate(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot parse JSON: {exc}"]
    errors = [f"missing top-level key: {key}" for key in REQUIRED if key not in data]
    for key in ("fr", "ip", "op", "w", "h"):
        if key in data and not isinstance(data[key], (int, float)):
            errors.append(f"{key} must be numeric")
    if data.get("fr", 0) <= 0: errors.append("fr must be greater than 0")
    if data.get("op", 0) <= data.get("ip", 0): errors.append("op must be greater than ip")
    if not isinstance(data.get("layers"), list): errors.append("layers must be an array")
    return errors

def main() -> int:
    paths = [Path(arg) for arg in sys.argv[1:]] or sorted(Path("examples").glob("*.json"))
    failed = False
    for path in paths:
        errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {path}\n" + "\n".join(f"  - {error}" for error in errors))
        else:
            print(f"OK   {path}")
    return int(failed or not paths)

if __name__ == "__main__":
    raise SystemExit(main())
