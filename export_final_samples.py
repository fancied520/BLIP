import csv
import shutil
import argparse
from pathlib import Path


FINAL_GOOD = [
    "1119418776_58e4b93eac.jpg",
    "1235681222_819231767a.jpg",
    "143237785_93f81b3201.jpg",
    "1662261486_db967930de.jpg",
    "2786299623_a3c48bd318.jpg",
]

FINAL_MEDIUM = [
    "2686432878_0697dbc048.jpg",
    "2692635048_16c279ff9e.jpg",
    "2696636252_91ef1491ea.jpg",
    "2705793985_007cc703fb.jpg",
    "2709648336_15455e60b2.jpg",
    "2710563762_06d48329d7.jpg",
    "2710698257_2e4ca8dd44.jpg",
    "2714878018_1593c38d69.jpg",
    "2723477522_d89f5ac62b.jpg",
    "2766291711_4e13a2b594.jpg",
]

FINAL_BAD = [
    "2043520315_4a2c782c90.jpg",
    "299612419_b55fe32fea.jpg",
    "3247168324_c45eaf734d.jpg",
    "118187095_d422383c81.jpg",
    "2529205842_bdcb49d65b.jpg",
    "2367318629_b60cf4c4b3.jpg",
    "133189853_811de6ab2a.jpg",
    "1030985833_b0902ea560.jpg",
    "109738916_236dc456ac.jpg",
    "2500567791_101d5ddee3.jpg",
    "3209620285_edfc479392.jpg",
    "3217266166_4e0091860b.jpg",
    "3271252073_0a1b9525fc.jpg",
    "3362592729_893e26b806.jpg",
    "3532782283_341f0381a3.jpg",
]


def load_csv_as_dict(csv_file: Path):
    rows = {}
    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_name = row.get("image_name", "").strip()
            if image_name:
                rows[image_name] = row
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


def collect_rows(selected_names, source_rows, category):
    collected = []
    missing = []

    for name in selected_names:
        if name in source_rows:
            row = dict(source_rows[name])
            row["category"] = category
            collected.append(row)
        else:
            missing.append(name)

    return collected, missing


def copy_images(selected_names, images_dir: Path, dst_dir: Path):
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing = []

    for name in selected_names:
        src = images_dir / name
        dst = dst_dir / name
        if src.exists():
            shutil.copy2(src, dst)
            copied += 1
        else:
            missing.append(name)

    return copied, missing


def main():
    parser = argparse.ArgumentParser(description="Export final representative samples and images.")
    parser.add_argument("--good-csv", type=str, default="results/sample_selection/good_candidates.csv")
    parser.add_argument("--medium-csv", type=str, default="results/sample_selection/medium_candidates.csv")
    parser.add_argument("--bad-csv", type=str, default="results/sample_selection/bad_candidates.csv")
    parser.add_argument("--images-dir", type=str, default="data/images")
    parser.add_argument("--output-dir", type=str, default="results/final_samples")
    args = parser.parse_args()

    good_csv = Path(args.good_csv)
    medium_csv = Path(args.medium_csv)
    bad_csv = Path(args.bad_csv)
    images_dir = Path(args.images_dir)
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    good_rows_dict = load_csv_as_dict(good_csv)
    medium_rows_dict = load_csv_as_dict(medium_csv)
    bad_rows_dict = load_csv_as_dict(bad_csv)

    final_good_rows, missing_good_rows = collect_rows(FINAL_GOOD, good_rows_dict, "good")
    final_medium_rows, missing_medium_rows = collect_rows(FINAL_MEDIUM, medium_rows_dict, "medium")
    final_bad_rows, missing_bad_rows = collect_rows(FINAL_BAD, bad_rows_dict, "bad")

    # 保存最终 CSV
    save_csv(final_good_rows, output_dir / "final_good_samples.csv")
    save_csv(final_medium_rows, output_dir / "final_medium_samples.csv")
    save_csv(final_bad_rows, output_dir / "final_bad_samples.csv")

    all_rows = final_good_rows + final_medium_rows + final_bad_rows
    save_csv(all_rows, output_dir / "final_all_samples.csv")

    # 复制图片
    copied_good, missing_good_imgs = copy_images(FINAL_GOOD, images_dir, output_dir / "good")
    copied_medium, missing_medium_imgs = copy_images(FINAL_MEDIUM, images_dir, output_dir / "medium")
    copied_bad, missing_bad_imgs = copy_images(FINAL_BAD, images_dir, output_dir / "bad")

    print("Done.")
    print(f"Saved CSVs to: {output_dir}")
    print(f"Copied good images   : {copied_good}")
    print(f"Copied medium images : {copied_medium}")
    print(f"Copied bad images    : {copied_bad}")

    all_missing_rows = missing_good_rows + missing_medium_rows + missing_bad_rows
    all_missing_imgs = missing_good_imgs + missing_medium_imgs + missing_bad_imgs

    if all_missing_rows:
        print("\n[Warning] These selected rows were not found in candidate CSVs:")
        for name in all_missing_rows:
            print("-", name)

    if all_missing_imgs:
        print("\n[Warning] These selected images were not found in image folder:")
        for name in all_missing_imgs:
            print("-", name)


if __name__ == "__main__":
    main()