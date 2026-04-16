import os
import csv
import argparse
from collections import defaultdict

from caption import generate_caption


def load_human_captions(captions_file):
    image_to_captions = defaultdict(list)

    with open(captions_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            if len(row) < 2:
                continue

            image_name = row[0].strip()
            caption = row[1].strip()

            # 跳过表头，兼容 image,caption 或 image_name,caption
            if image_name.lower() in ["image", "image_name"] and caption.lower() == "caption":
                continue

            if not image_name or not caption:
                continue

            image_to_captions[image_name].append(caption)

    return image_to_captions


def main():
    parser = argparse.ArgumentParser(description="Run BLIP captioning on Flickr8k images in batch.")
    parser.add_argument("--captions-file", type=str, default="data/captions.txt")
    parser.add_argument("--images-dir", type=str, default="data/images")
    parser.add_argument("--output-file", type=str, default="results/results.csv")
    parser.add_argument("--limit", type=int, default=None, help="Only process first N images")
    args = parser.parse_args()

    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    image_to_captions = load_human_captions(args.captions_file)
    image_names = list(image_to_captions.keys())

    if args.limit is not None:
        image_names = image_names[:args.limit]

    total = len(image_names)
    print(f"Total images to process: {total}")

    with open(args.output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "image_name",
            "blip_caption",
            "human_caption_1",
            "human_caption_2",
            "human_caption_3",
            "human_caption_4",
            "human_caption_5",
        ])

        for idx, image_name in enumerate(image_names, start=1):
            image_path = os.path.join(args.images_dir, image_name)

            if not os.path.exists(image_path):
                print(f"[Warning] Image not found: {image_path}")
                continue

            try:
                blip_caption = generate_caption(image_path)
            except Exception as e:
                print(f"[Error] Failed on {image_name}: {e}")
                continue

            # 不直接修改原列表，避免副作用
            human_captions = image_to_captions[image_name][:5]
            human_captions = human_captions + [""] * (5 - len(human_captions))

            writer.writerow([
                image_name,
                blip_caption,
                human_captions[0],
                human_captions[1],
                human_captions[2],
                human_captions[3],
                human_captions[4],
            ])

            print(f"[{idx}/{total}] {image_name} -> {blip_caption}")

    print(f"\nDone. Results saved to: {args.output_file}")


if __name__ == "__main__":
    main()