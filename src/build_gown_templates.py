import os, re, argparse, time, csv
from pathlib import Path
from typing import Optional, List

from PIL import Image
from tqdm import tqdm

# ---- Public Gemini client (optional) ----
try:
    from google import genai
    from google.genai import types as gtypes
except Exception:
    genai = None
    gtypes = None

# ---- Vertex AI (recommended) ----
try:
    from vertexai import init as vertex_init
    from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
except Exception:
    GenerativeModel = None

PROMPT_TEMPLATE = """You are a graphic designer. From the provided graduation photo(s), create ONE composite image (PNG, white background) formatted as a clean moodboard that contains only:
- GOWN (robe) — isolated, background removed
- HOOD (colored hood/stole) — isolated, background removed
- CAP (mortarboard with tassel) — isolated, background removed

Layout requirements
- Canvas: 1600×900, white background.
- Place the three items as separate panels with subtle drop shadows and consistent scaling:
  - Left: Gown (largest)
  - Top-right: Hood
  - Bottom-right: Cap
- Add small, clean labels “Gown”, “Hood”, “Cap” under each item (sans-serif, black).
- Add a small header at top-left: “{university} — {level} Template”.

Rules
- Use the best photo angles available: if both front and back are provided, use front for Gown & Cap, back for Hood.
- Remove all background and people; preserve original fabric colours, folds, edging and hood colours.
- Return ONE PNG image only (the finished moodboard). No text in the response besides the single PNG output.
"""

def build_prompt(university: str, level: str) -> str:
    return PROMPT_TEMPLATE.format(university=university, level=level)

# --------- pick sources: first JPG + robust -set-1 matcher ----------
# Matches set 1 with flexible separators and leading zeros, without catching set-11 or set-13:
# Examples matched: "-set-1", "-set1", "-set_01", " set 1 ", "-set-1-1" (still indicates it's a set-1 variant)
RX_SET1 = re.compile(r"(?i)(?:^|[^0-9])set[-_ ]*0*1(?:[^0-9]|$)")

def pick_sources(level_dir: Path) -> List[Path]:
    imgs = sorted([p for p in level_dir.glob("*.*")
                   if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")])
    if not imgs:
        return []

    # first JPG (preferred “front”)
    jpgs = [p for p in imgs if p.suffix.lower() in (".jpg", ".jpeg")]
    first_jpg = jpgs[0] if jpgs else imgs[0]

    # first file matching any set-1 style (on the stem, so the extension doesn't interfere)
    set1 = next((p for p in imgs if RX_SET1.search(p.stem)), None)

    sources = []
    if first_jpg:
        sources.append(first_jpg)
    if set1 and (not first_jpg or set1 != first_jpg):
        sources.append(set1)
    return sources

# ------------------ google-genai path ------------------
def genai_client():
    if genai is None:
        raise RuntimeError("google-genai is not installed. Try: pip install google-genai")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment")
    return genai.Client(api_key=key)

def genai_part(p: Path):
    if gtypes is None:
        raise RuntimeError("google-genai types not available")
    mime = "image/jpeg"
    if p.suffix.lower() == ".png": mime = "image/png"
    elif p.suffix.lower() == ".webp": mime = "image/webp"
    return gtypes.Part.from_bytes(data=p.read_bytes(), mime_type=mime)

def genai_make_board(client, model: str, images: List[Path], prompt: str) -> bytes:
    contents = [genai_part(p) for p in images] + [prompt]
    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=gtypes.GenerateContentConfig(response_modalities=["Image"])
    )
    cand = resp.candidates[0]
    for part in cand.content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and getattr(inline, "data", None):
            return inline.data
    if hasattr(resp, "binary") and resp.binary:
        return resp.binary
    t = getattr(resp, "text", "") or ""
    raise RuntimeError("No image bytes returned. " + (t[:200] + ("..." if len(t) > 200 else "")))

# ------------------ Vertex AI path (recommended) ------------------
def vertex_make_board(project: str, location: str, model_name: str, images: List[Path], prompt: str) -> bytes:
    if GenerativeModel is None:
        raise RuntimeError("vertexai is not installed. Try: pip install google-cloud-aiplatform vertexai")
    vertex_init(project=project, location=location)
    model = GenerativeModel(model_name)

    parts = []
    for p in images:
        mime = "image/jpeg"
        if p.suffix.lower() == ".png": mime = "image/png"
        elif p.suffix.lower() == ".webp": mime = "image/webp"
        parts.append(Part.from_data(mime_type=mime, data=p.read_bytes()))

    resp = model.generate_content(
        parts + [prompt],
        generation_config=GenerationConfig(
            response_mime_type=None,
            response_modalities=["IMAGE"],
        )
    )
    out_bytes = None
    for cand in resp.candidates:
        for prt in cand.content.parts:
            if getattr(prt, "inline_data", None) and getattr(prt.inline_data, "data", None):
                out_bytes = prt.inline_data.data
                break
        if out_bytes:
            break
    if not out_bytes:
        t = getattr(resp, "text", "") or ""
        raise RuntimeError("Vertex did not return image bytes. " + (t[:200] + ("..." if len(t) > 200 else "")))
    return out_bytes

# ------------------ pipeline ------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_root", default="output", help="Scraper output root")
    ap.add_argument("--out_root", default="templates", help="Where to write moodboards")
    ap.add_argument("--engine", choices=["vertex","genai"], default="genai",
                    help="'vertex' (recommended) or 'genai' (may be blocked in some regions)")
    ap.add_argument("--model", default="gemini-2.5-flash-image", help="Model name")
    ap.add_argument("--vertex_project", default="", help="GCP project (Vertex mode)")
    ap.add_argument("--vertex_location", default="us-central1", help="GCP region (Vertex mode)")
    ap.add_argument("--only_uni", default="", help="Process only this university folder name")
    ap.add_argument("--only_level", choices=["Masters","Bachelors",""], default="", help="Process only this level")
    ap.add_argument("--pause", type=float, default=0.2)
    args = ap.parse_args()

    in_root = Path(args.in_root)
    out_root = Path(args.out_root); out_root.mkdir(parents=True, exist_ok=True)

    if args.engine == "genai":
        client = genai_client()
    else:
        if not args.vertex_project:
            raise RuntimeError("Vertex mode requires --vertex_project (and optionally --vertex_location)")

    uni_dirs = [d for d in sorted(in_root.iterdir()) if d.is_dir()]
    if args.only_uni:
        uni_dirs = [d for d in uni_dirs if d.name == args.only_uni]
        if not uni_dirs:
            print(f"[info] No university folder matches: {args.only_uni}")
            return

    man_path = out_root / "moodboards_manifest.csv"
    with open(man_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["university","level","source_images","saved_board"])

        for uni_dir in tqdm(uni_dirs, desc="Universities"):
            levels = [args.only_level] if args.only_level else ["Masters","Bachelors"]
            for level in levels:
                if not level:
                    continue
                level_dir = uni_dir / level
                if not level_dir.exists():
                    continue

                sources = pick_sources(level_dir)
                if not sources:
                    continue

                out_dir = out_root / uni_dir.name / level
                out_dir.mkdir(parents=True, exist_ok=True)
                out_png = out_dir / "board.png"

                prompt = build_prompt(uni_dir.name, level)

                try:
                    if args.engine == "vertex":
                        img_bytes = vertex_make_board(
                            project=args.vertex_project,
                            location=args.vertex_location,
                            model_name=args.model,
                            images=sources,
                            prompt=prompt
                        )
                    else:
                        img_bytes = genai_make_board(
                            client=client,
                            model=args.model,
                            images=sources,
                            prompt=prompt
                        )
                    out_png.write_bytes(img_bytes)
                    Image.open(out_png).load()  # sanity check
                    w.writerow([uni_dir.name, level, ";".join([p.name for p in sources]), str(out_png)])
                except Exception as e:
                    print(f"[warn] {uni_dir.name}/{level} failed: {e}")

                time.sleep(args.pause)

    print(f"\nDone. Moodboards saved under: {out_root}\nManifest: {man_path}")

if __name__ == "__main__":
    main()
