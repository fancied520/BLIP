import csv
import re
import argparse
from pathlib import Path


def tokenize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.split()


def simple_f1(pred: str, ref: str) -> float:
    pred_tokens = set(tokenize(pred))
    ref_tokens = set(tokenize(ref))

    if not pred_tokens or not ref_tokens:
        return 0.0

    overlap = len(pred_tokens & ref_tokens)
    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def best_f1_against_refs(pred: str, refs: list[str]):
    valid_refs = [r for r in refs if isinstance(r, str) and r.strip()]
    if not valid_refs:
        return 0.0, ""

    scores = [(simple_f1(pred, ref), ref) for ref in valid_refs]
    best_score, best_ref = max(scores, key=lambda x: x[0])
    return best_score, best_ref


def load_results(csv_file: str):
    rows = []
    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            refs = [
                row.get("human_caption_1", ""),
                row.get("human_caption_2", ""),
                row.get("human_caption_3", ""),
                row.get("human_caption_4", ""),
                row.get("human_caption_5", ""),
            ]
            best_f1, best_ref = best_f1_against_refs(row.get("blip_caption", ""), refs)

            rows.append({
                "image_name": row.get("image_name", ""),
                "blip_caption": row.get("blip_caption", ""),
                "human_caption_1": row.get("human_caption_1", ""),
                "human_caption_2": row.get("human_caption_2", ""),
                "human_caption_3": row.get("human_caption_3", ""),
                "human_caption_4": row.get("human_caption_4", ""),
                "human_caption_5": row.get("human_caption_5", ""),
                "best_f1": round(best_f1, 4),
                "best_ref": best_ref,
            })
    return rows


def save_csv(rows, output_file: str):
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Select good / medium / bad samples by simple token-level F1.")
    parser.add_argument("--input-file", type=str, default="results/results.csv")
    parser.add_argument("--output-dir", type=str, default="results/sample_selection")
    parser.add_argument("--num-good", type=int, default=5)
    parser.add_argument("--num-medium", type=int, default=10)
    parser.add_argument("--num-bad", type=int, default=15)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_results(args.input_file)
    if not rows:
        print("No rows found.")
        return

    rows_sorted = sorted(rows, key=lambda x: x["best_f1"], reverse=True)

    total = len(rows_sorted)
    print(f"Total rows: {total}")

    # 好样本：直接取前 num_good 个
    good_samples = rows_sorted[:args.num_good]

    # 差样本：直接取后 num_bad 个
    bad_samples = rows_sorted[-args.num_bad:]

    # 中样本：从中间附近取 num_medium 个
    mid_start = max(0, total // 2 - args.num_medium // 2)
    mid_end = mid_start + args.num_medium
    medium_samples = rows_sorted[mid_start:mid_end]

    save_csv(rows_sorted, output_dir / "all_with_best_f1.csv")
    save_csv(good_samples, output_dir / "good_samples.csv")
    save_csv(medium_samples, output_dir / "medium_samples.csv")
    save_csv(bad_samples, output_dir / "bad_samples.csv")

    print(f"Saved:")
    print(f"- {output_dir / 'all_with_best_f1.csv'}")
    print(f"- {output_dir / 'good_samples.csv'}")
    print(f"- {output_dir / 'medium_samples.csv'}")
    print(f"- {output_dir / 'bad_samples.csv'}")


if __name__ == "__main__":
    main()