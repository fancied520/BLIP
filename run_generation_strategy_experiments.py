from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


DEFAULT_STRATEGIES: Dict[str, Dict] = {
    "baseline": {
        "max_new_tokens": 20,
        "num_beams": 1,
    },
    "exp1_longer": {
        "max_new_tokens": 30,
        "num_beams": 1,
    },
    "exp2_beam5": {
        "max_new_tokens": 30,
        "num_beams": 5,
        "early_stopping": True,
    },
}


def normalize_text(text: str) -> List[str]:
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [tok for tok in text.split() if tok]
    return tokens



def simple_f1(pred: str, ref: str) -> float:
    pred_set = set(normalize_text(pred))
    ref_set = set(normalize_text(ref))

    if not pred_set or not ref_set:
        return 0.0

    overlap = len(pred_set & ref_set)
    if overlap == 0:
        return 0.0

    precision = overlap / len(pred_set)
    recall = overlap / len(ref_set)
    return 2 * precision * recall / (precision + recall)



def best_f1_against_refs(pred: str, refs: List[str]) -> Tuple[float, str]:
    best_score = 0.0
    best_ref = ""
    for ref in refs:
        if pd.isna(ref) or not str(ref).strip():
            continue
        score = simple_f1(pred, str(ref))
        if score > best_score:
            best_score = score
            best_ref = str(ref)
    return best_score, best_ref



def detect_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"



def load_sample_table(sample_csv: Path, full_results_csv: Path | None = None) -> pd.DataFrame:
    df = pd.read_csv(sample_csv)

    if "image_name" not in df.columns:
        raise ValueError(f"{sample_csv} 中缺少 image_name 列")

    human_cols = [c for c in df.columns if c.startswith("human_caption_")]
    if human_cols:
        return df

    if full_results_csv is None or not full_results_csv.exists():
        raise ValueError(
            "样本表中没有 human_caption_1~5，且未找到可用于补充的完整 results.csv"
        )

    full_df = pd.read_csv(full_results_csv)
    needed_cols = ["image_name"] + [c for c in full_df.columns if c.startswith("human_caption_")]
    full_df = full_df[needed_cols].drop_duplicates(subset=["image_name"])
    df = df.merge(full_df, on="image_name", how="left")
    return df



def generate_caption(
    image_path: Path,
    processor: BlipProcessor,
    model: BlipForConditionalGeneration,
    device: str,
    strategy: Dict,
) -> str:
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(**inputs, **strategy)

    caption = processor.decode(output_ids[0], skip_special_tokens=True)
    return caption.strip()



def main() -> None:
    parser = argparse.ArgumentParser(description="Run BLIP decoding-strategy experiments on final samples.")
    parser.add_argument(
        "--sample_csv",
        type=str,
        default="results/final_samples/final_all_samples.csv",
        help="最终代表样本 CSV 路径",
    )
    parser.add_argument(
        "--full_results_csv",
        type=str,
        default="results/results.csv",
        help="全量结果表路径，用于补充 human captions",
    )
    parser.add_argument(
        "--image_dir",
        type=str,
        default="data/images",
        help="图片目录",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results/strategy_experiments",
        help="实验结果输出目录",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="Salesforce/blip-image-captioning-base",
        help="Hugging Face 模型名",
    )
    args = parser.parse_args()

    sample_csv = Path(args.sample_csv)
    full_results_csv = Path(args.full_results_csv)
    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_sample_table(sample_csv=sample_csv, full_results_csv=full_results_csv)
    human_cols = [c for c in df.columns if c.startswith("human_caption_")]

    device = detect_device()
    print(f"Loading model on {device}...")
    processor = BlipProcessor.from_pretrained(args.model_name)
    model = BlipForConditionalGeneration.from_pretrained(args.model_name).to(device)
    model.eval()

    long_rows = []
    wide_rows = []

    print(f"Total samples: {len(df)}")
    print(f"Strategies: {list(DEFAULT_STRATEGIES.keys())}")

    for idx, row in df.iterrows():
        image_name = row["image_name"]
        image_path = image_dir / image_name
        if not image_path.exists():
            print(f"[WARN] 图片不存在，跳过: {image_path}")
            continue

        refs = [str(row[c]) for c in human_cols if c in row and not pd.isna(row[c])]
        group_value = row["group"] if "group" in row else row.get("category", "")

        per_image_record = {
            "image_name": image_name,
            "group": group_value,
        }
        for c in human_cols:
            per_image_record[c] = row.get(c, "")

        print(f"[{idx + 1}/{len(df)}] {image_name}")

        for strategy_name, strategy_cfg in DEFAULT_STRATEGIES.items():
            caption = generate_caption(
                image_path=image_path,
                processor=processor,
                model=model,
                device=device,
                strategy=strategy_cfg,
            )
            best_f1, best_ref = best_f1_against_refs(caption, refs)

            long_rows.append(
                {
                    "image_name": image_name,
                    "group": group_value,
                    "strategy": strategy_name,
                    "generated_caption": caption,
                    "best_f1": round(best_f1, 4),
                    "best_match_ref": best_ref,
                    **{c: row.get(c, "") for c in human_cols},
                }
            )

            per_image_record[f"{strategy_name}_caption"] = caption
            per_image_record[f"{strategy_name}_best_f1"] = round(best_f1, 4)

            print(f"    - {strategy_name}: {caption} | best_f1={best_f1:.4f}")

        wide_rows.append(per_image_record)

    long_df = pd.DataFrame(long_rows)
    wide_df = pd.DataFrame(wide_rows)

    long_csv = output_dir / "strategy_results_long.csv"
    wide_csv = output_dir / "strategy_results_wide.csv"
    summary_csv = output_dir / "strategy_summary.csv"

    long_df.to_csv(long_csv, index=False, encoding="utf-8-sig")
    wide_df.to_csv(wide_csv, index=False, encoding="utf-8-sig")

    if not long_df.empty:
        summary_df = (
            long_df.groupby(["strategy", "group"], dropna=False)["best_f1"]
            .agg(["count", "mean", "median", "max", "min"])
            .reset_index()
            .sort_values(["group", "mean"], ascending=[True, False])
        )
    else:
        summary_df = pd.DataFrame(columns=["strategy", "group", "count", "mean", "median", "max", "min"])

    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")

    print("\nDone.")
    print(f"Saved long results to: {long_csv}")
    print(f"Saved wide results to: {wide_csv}")
    print(f"Saved summary to: {summary_csv}")


if __name__ == "__main__":
    main()
