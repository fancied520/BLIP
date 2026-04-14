from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from PIL import Image, UnidentifiedImageError
from transformers import BlipForConditionalGeneration, BlipProcessor

MODEL_NAME = "Salesforce/blip-image-captioning-base"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an image caption with BLIP."
    )
    parser.add_argument("image_path", help="Path to the input image file.")
    return parser.parse_args()


def load_image(image_path: Path) -> Image.Image:
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    if not image_path.is_file():
        raise FileNotFoundError(f"Path is not a file: {image_path}")

    try:
        return Image.open(image_path).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError(
            f"Unable to read image file: {image_path}. Please provide a valid JPG or PNG."
        ) from exc
    except OSError as exc:
        raise ValueError(f"Failed to open image: {image_path}") from exc


def load_model() -> tuple[BlipProcessor, BlipForConditionalGeneration, torch.device]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    try:
        processor = BlipProcessor.from_pretrained(MODEL_NAME)
        model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)
    except Exception as exc:
        raise RuntimeError(
            "Failed to load BLIP model. Check your network connection, Hugging Face access, "
            "or local cache, then try again."
        ) from exc

    model.to(device)
    model.eval()
    return processor, model, device


def generate_caption(image_path: Path) -> str:
    image = load_image(image_path)
    processor, model, device = load_model()

    inputs = processor(images=image, return_tensors="pt")
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=30)

    return processor.decode(output[0], skip_special_tokens=True).strip()


def main() -> int:
    args = parse_args()
    image_path = Path(args.image_path).expanduser().resolve()

    try:
        caption = generate_caption(image_path)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    print(caption)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

