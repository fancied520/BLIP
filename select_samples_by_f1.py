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


def best_f1_against_refs(pred: str, refs):
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


def save_csv(rows, output_file: Path):
    if not rows:
        print(f"[Warning] No rows to save: {output_file}")
        return

    fieldnames = list(rows[0].keys())
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Select candidate pools for good / medium / bad samples by simple token-level F1."
    )
    parser.add_argument("--input-file", type=str, default="results/results.csv")
    parser.add_argument("--output-dir", type=str, default="results/sample_selection")

    # 候选池大小，而不是最终样本数
    parser.add_argument("--num-good-candidates", type=int, default=20)
    parser.add_argument("--num-medium-candidates", type=int, default=30)
    parser.add_argument("--num-bad-candidates", type=int, default=30)

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

    # 1. 好候选：取前若干高分样本
    good_candidates = rows_sorted[:args.num_good_candidates]

    # 2. 差候选：取后若干低分样本
    bad_candidates = rows_sorted[-args.num_bad_candidates:]

    # 3. 中候选：从中间区域取更大的候选池
    mid_center = total // 2
    half_window = args.num_medium_candidates // 2
    mid_start = max(0, mid_center - half_window)
    mid_end = min(total, mid_start + args.num_medium_candidates)

    # 防止接近尾部时长度不够
    if mid_end - mid_start < args.num_medium_candidates:
        mid_start = max(0, mid_end - args.num_medium_candidates)

    medium_candidates = rows_sorted[mid_start:mid_end]

    # 保存
    save_csv(rows_sorted, output_dir / "all_with_best_f1.csv")
    save_csv(good_candidates, output_dir / "good_candidates.csv")
    save_csv(medium_candidates, output_dir / "medium_candidates.csv")
    save_csv(bad_candidates, output_dir / "bad_candidates.csv")

    print("Saved:")
    print(f"- {output_dir / 'all_with_best_f1.csv'}")
    print(f"- {output_dir / 'good_candidates.csv'}")
    print(f"- {output_dir / 'medium_candidates.csv'}")
    print(f"- {output_dir / 'bad_candidates.csv'}")

    print("\nNext step:")
    print("Please manually review these candidate pools, then create:")
    print("- final_good_samples.csv   (5 samples)")
    print("- final_medium_samples.csv (10 samples)")
    print("- final_bad_samples.csv    (15 samples)")


if __name__ == "__main__":
    main()