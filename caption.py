from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import argparse


MODEL_NAME = "Salesforce/blip-image-captioning-base"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading model on {DEVICE}...")
processor = BlipProcessor.from_pretrained(MODEL_NAME)
model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME).to(DEVICE)
model.eval()


def generate_caption(image_path: str) -> str:
    """
    Generate a caption for a single image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Generated caption.
    """
    image = Image.open(image_path).convert("RGB")

    inputs = processor(images=image, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=20)

    caption = processor.decode(output[0], skip_special_tokens=True).strip()
    return caption


def main():
    parser = argparse.ArgumentParser(description="Generate image caption using BLIP.")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    args = parser.parse_args()

    caption = generate_caption(args.image_path)
    print(caption)


if __name__ == "__main__":
    main()