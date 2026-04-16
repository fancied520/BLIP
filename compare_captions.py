from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


DEFAULT_CAPTIONS_FILE = Path("data/captions.txt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Look up all human-written captions for one image in Flickr8k captions.txt."
    )
    parser.add_argument(
        "image_name",
        help="Image file name, for example: 1000268201_693b08cb0e.jpg",
    )
    parser.add_argument(
        "--captions-file",
        default=str(DEFAULT_CAPTIONS_FILE),
        help="Path to captions.txt (default: data/captions.txt)",
    )
    return parser.parse_args()


def load_captions(captions_file: Path) -> dict[str, list[str]]:
    if not captions_file.exists():
        raise FileNotFoundError(f"Captions file not found: {captions_file}")
    if not captions_file.is_file():
        raise FileNotFoundError(f"Path is not a file: {captions_file}")

    captions_map: dict[str, list[str]] = {}

    try:
        with captions_file.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)

            for row_num, row in enumerate(reader, start=1):
                if not row:
                    continue

                if len(row) < 2:
                    raise ValueError(
                        f"Invalid format in {captions_file} at line {row_num}: {row}"
                    )

                image_name = row[0].strip()
                caption = ",".join(row[1:]).strip()

                if not image_name or not caption:
                    continue

                captions_map.setdefault(image_name, []).append(caption)

    except OSError as exc:
        raise RuntimeError(f"Failed to read captions file: {captions_file}") from exc

    return captions_map


def main() -> int:
    args = parse_args()
    image_name = args.image_name.strip()
    captions_file = Path(args.captions_file).expanduser().resolve()

    try:
        captions_map = load_captions(captions_file)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    captions = captions_map.get(image_name)

    if not captions:
        print(f"No captions found for image: {image_name}", file=sys.stderr)
        return 1

    print(f"Image: {image_name}")
    print(f"Found {len(captions)} caption(s):")
    print()

    for i, caption in enumerate(captions, start=1):
        print(f"{i}. {caption}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())