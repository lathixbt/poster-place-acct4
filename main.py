#!/usr/bin/env python3
"""ORSOLIA — The Orchard That Grows Down from the Sky.

Entry program for make.fun competition
"the-poster-for-a-place-that-i-2-20261121-0539".

Copies the poster (entry.png, written next to this file) to
$MAKEFUN_OUTPUT_DIR/entry.png (fallback /output/entry.png),
validating size and dimensions first.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

MAX_BYTES = 1_048_576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024

POSTER_NAME = "entry.png"


def read_png_dimensions(path: Path) -> tuple[int, int]:
    """Read width/height from a PNG IHDR chunk (stdlib only)."""
    with open(path, "rb") as fh:
        header = fh.read(33)
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    if header[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def validate_poster(source: Path) -> tuple[int, int, int]:
    """Check the repo poster meets the competition limits.

    Returns (size_bytes, width, height). Raises SystemExit with a
    clear message when any limit is broken.
    """
    if not source.is_file():
        print(f"error: {POSTER_NAME} not found next to main.py", file=sys.stderr)
        raise SystemExit(1)

    size = source.stat().st_size
    if size > MAX_BYTES:
        print(f"error: {POSTER_NAME} is {size} bytes, over {MAX_BYTES}", file=sys.stderr)
        raise SystemExit(1)

    width, height = read_png_dimensions(source)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        print(
            f"error: {POSTER_NAME} is {width}x{height}, expected "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return size, width, height


def main() -> int:
    repo_dir = Path(__file__).resolve().parent
    source = repo_dir / POSTER_NAME
    size, width, height = validate_poster(source)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_path = Path(out_dir) / POSTER_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, out_path)

    # Round-trip check: output bytes must equal the repo poster bytes,
    # and the copied file must still read back as 1024x1024.
    if out_path.read_bytes() != source.read_bytes():
        print("error: round-trip mismatch, output differs from source", file=sys.stderr)
        return 1
    out_width, out_height = read_png_dimensions(out_path)
    if (out_width, out_height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        print(
            f"error: copied poster reads back as {out_width}x{out_height}",
            file=sys.stderr,
        )
        return 1

    print(f"wrote entry.png ({size} bytes, {width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
