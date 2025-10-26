import argparse
import csv
import datetime as dt
import json
import random
from pathlib import Path
from typing import Dict, List, Optional

# ---------- Helpers ----------
def find_latest_run(experiments_root: Path) -> Path:
    runs = [p for p in experiments_root.iterdir() if p.is_dir()]
    if not runs:
        raise SystemExit(f"No runs found under {experiments_root}")
    # latest by modified time
    runs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[0]

def load_meta(fldr: Path) -> Dict:
    m = fldr / "meta.json"
    if m.exists():
        try:
            return json.loads(m.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)

def collect_rows(run_dir: Path, include_prompt_text: bool = True) -> List[Dict]:
    """
    Walk the run directory and collect one row per output.png
    Expected structure:
      run_dir/<University>__<Level>/<portrait>/<PromptID>/output.png
    """
    rows: List[Dict] = []
    for out_png in run_dir.rglob("output.png"):
        leaf = out_png.parent
        try:
            prompt_id = leaf.name
            portrait   = leaf.parent.name
            uni_level  = leaf.parent.parent.name
            if "__" in uni_level:
                university, level = uni_level.split("__", 1)
            else:
                university, level = uni_level, "Unknown"
        except Exception:
            # Skip weird paths
            continue

        # Gather other artifacts
        board = leaf / "board.png"
        prompt_txt = leaf / "prompt.txt"
        selfie = None
        # pick any non-board png/jpg in leaf as selfie (heuristic)
        for p in leaf.iterdir():
            if p.name.lower() in ("output.png","board.png","prompt.txt","meta.json","error.txt"):
                continue
            if p.suffix.lower() in (".jpg",".jpeg",".png",".webp"):
                selfie = p
                break

        meta = load_meta(leaf)
        engine = meta.get("engine", "")
        model  = meta.get("model", "")
        board_rel   = str(board.name) if not board.exists() else "board.png"  # inside folder
        selfie_rel  = selfie.name if selfie else ""
        prompt_text = prompt_txt.read_text(encoding="utf-8") if (include_prompt_text and prompt_txt.exists()) else ""

        row = {
            "item_id": f"{university}::{level}::{portrait}::{prompt_id}",
            "university": university,
            "level": level,
            "portrait": portrait,
            "prompt_id": prompt_id,
            "engine": engine,
            "model": model,
            "folder": str(leaf),
            "output_path": "output.png",
            "selfie_path": selfie_rel,
            "board_path": board_rel,
            "prompt_txt_path": "prompt.txt" if prompt_txt.exists() else "",
            "prompt_txt": prompt_text,
            # Blank ratings for humans:
            "face_identity_1to5": "",
            "hood_color_1to5": "",
            "gown_detail_1to5": "",
            "cap_quality_1to5": "",
            "layout_labels_1to5": "",
            "artifacts_1to5": "",
            "overall_1to10": "",
            "keep_retry": "",  # Keep / Retry / Reject
            "comments": "",
        }
        rows.append(row)
    return rows

def write_csv(rows: List[Dict], out_csv: Path):
    if not rows:
        raise SystemExit("No rows to write (did you point to the correct run folder?)")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def split_csv(rows: List[Dict], n: int) -> List[List[Dict]]:
    if n <= 1:
        return [rows]
    chunks = [[] for _ in range(n)]
    for i, r in enumerate(rows):
        chunks[i % n].append(r)
    return chunks

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser(description="Build marking CSV for human raters.")
    ap.add_argument("--experiments_root", default="experiments", help="Root folder containing run_* dirs")
    ap.add_argument("--run_dir", default="", help="Specific run dir; if empty, pick latest under experiments_root")
    ap.add_argument("--out_dir", default="eval_sheets", help="Where to write CSV(s)")
    ap.add_argument("--seed", type=int, default=42, help="Shuffle seed for row order")
    ap.add_argument("--group_by_portrait", action="store_true",
                    help="Keep items of the same portrait grouped together (shuffles groups, not rows)")
    ap.add_argument("--num_splits", type=int, default=1, help="Write N split CSVs for raters")
    ap.add_argument("--include_prompt_text", action="store_true", help="Include prompt text column")
    args = ap.parse_args()

    exp_root = Path(args.experiments_root)
    if args.run_dir:
        run_dir = Path(args.run_dir)
    else:
        run_dir = find_latest_run(exp_root)

    print(f"Using run: {run_dir}")

    rows = collect_rows(run_dir, include_prompt_text=args.include_prompt_text)

    # Shuffle
    random.seed(args.seed)
    if args.group_by_portrait:
        # group then shuffle groups for better UX
        buckets: Dict[str, List[Dict]] = {}
        for r in rows:
            buckets.setdefault(r["portrait"], []).append(r)
        groups = list(buckets.values())
        for g in groups:
            random.shuffle(g)
        random.shuffle(groups)
        rows = [r for g in groups for r in g]
    else:
        random.shuffle(rows)

    # Write CSV(s)
    out_base = Path(args.out_dir)
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    if args.num_splits > 1:
        chunks = split_csv(rows, args.num_splits)
        out_files = []
        for i, chunk in enumerate(chunks, start=1):
            out_csv = out_base / f"marking_sheet_{ts}_part{i:02d}_of_{args.num_splits}.csv"
            write_csv(chunk, out_csv)
            out_files.append(out_csv)
        print("Wrote:", *map(str, out_files), sep="\n  ")
    else:
        out_csv = out_base / f"marking_sheet_{ts}.csv"
        write_csv(rows, out_csv)
        print("Wrote:", out_csv)

if __name__ == "__main__":
    main()
