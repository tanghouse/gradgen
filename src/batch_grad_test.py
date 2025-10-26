# batch_grad_test.py
import os, re, json, csv, argparse, time, shutil, hashlib, datetime
from pathlib import Path
from typing import List, Dict

from PIL import Image
from tqdm import tqdm

# ---- Optional engines (use Vertex by default) ----
try:
    from vertexai import init as vertex_init
    from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
except Exception:
    GenerativeModel = None

try:
    from google import genai
    from google.genai import types as gtypes
except Exception:
    genai = None
    gtypes = None

CONTROL_SUFFIX = (
    "Use the provided 'Design Board' image ONLY as a reference for gown/hood/cap style and colors; "
    "do not display the board itself. Preserve the person's identity and facial geometry. "
    "Photo-real textures and natural skin detail. Return ONE image only (finished portrait). "
    "--no text, watermarks, logos."
)

def load_prompts(path: Path) -> Dict[str, str]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    # Enhance: append the control suffix to all prompts that are graduation or portrait edits
    enhanced = {}
    for k, v in obj.items():
        # Add suffix to all; remove if you want to keep originals 1:1
        enhanced[k] = (v.rstrip() + "\n\n" + CONTROL_SUFFIX)
    return enhanced

def list_portraits(root: Path, limit: int = 0) -> List[Path]:
    exts = (".jpg",".jpeg",".png",".webp")
    items = sorted([p for p in root.rglob("*") if p.suffix.lower() in exts])
    return items[:limit] if limit else items

def list_boards(boards_glob: str, limit: int = 0) -> List[Path]:
    items = sorted(Path().glob(boards_glob))
    return items[:limit] if limit else items

def board_meta(p: Path):
    # Expect templates/<University>/<Level>/board.png
    parts = p.parts
    uni, lvl = "Unknown University", "Unknown"
    if len(parts) >= 3:
        # try to parse .../templates/<University>/<Level>/board.png
        try:
            idx = parts.index("templates")
            if len(parts) > idx+2:
                uni = parts[idx+1]
                lvl = parts[idx+2]
        except ValueError:
            # fallback: take parent folders
            uni = p.parent.parent.name
            lvl = p.parent.name
    return uni, lvl

# -------------- Engines --------------
def ensure_vertex():
    if GenerativeModel is None:
        raise RuntimeError("Vertex AI not installed. pip install google-cloud-aiplatform vertexai")

def ensure_genai():
    if genai is None or gtypes is None:
        raise RuntimeError("google-genai not installed. pip install google-genai")

def mime_for(p: Path) -> str:
    ext = p.suffix.lower()
    if ext == ".png": return "image/png"
    if ext == ".webp": return "image/webp"
    return "image/jpeg"

def call_vertex(project: str, location: str, model_name: str, selfie: Path, board: Path, prompt: str) -> bytes:
    ensure_vertex()
    vertex_init(project=project, location=location)
    model = GenerativeModel(model_name)
    parts = [
        Part.from_data(mime_type=mime_for(selfie), data=selfie.read_bytes()),
        Part.from_data(mime_type=mime_for(board),  data=board.read_bytes()),
        prompt
    ]
    resp = model.generate_content(
        parts,
        generation_config=GenerationConfig(
            response_modalities=["IMAGE"],
            # temperature etc. can be added here to sweep
        )
    )
    for cand in resp.candidates:
        for prt in cand.content.parts:
            if getattr(prt, "inline_data", None) and getattr(prt.inline_data, "data", None):
                return prt.inline_data.data
    raise RuntimeError("Vertex returned no image data")

def call_genai(api_key: str, model: str, selfie: Path, board: Path, prompt: str) -> bytes:
    ensure_genai()
    client = genai.Client(api_key=api_key)
    def part(p: Path):
        return gtypes.Part.from_bytes(data=p.read_bytes(), mime_type=mime_for(p))
    contents = [part(selfie), part(board), prompt]
    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=gtypes.GenerateContentConfig(response_modalities=["Image"])
    )
    cand = resp.candidates[0]
    for prt in cand.content.parts:
        inline = getattr(prt, "inline_data", None)
        if inline and getattr(inline, "data", None):
            return inline.data
    if hasattr(resp, "binary") and resp.binary:
        return resp.binary
    raise RuntimeError("GenAI returned no image data")

# -------------- Runner --------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portraits_root", default="data/raw_portraits")
    ap.add_argument("--prompts_file",  default="prompts.json")
    ap.add_argument("--boards_glob",   default="templates/*/*/board.png",
                    help="glob to find design boards (University/Level/board.png)")
    ap.add_argument("--engine", choices=["vertex","genai"], default="vertex")
    ap.add_argument("--vertex_project", default="", help="GCP project (Vertex)")
    ap.add_argument("--vertex_location", default="us-central1", help="GCP region (Vertex)")
    ap.add_argument("--genai_model", default="gemini-2.5-flash-image", help="Public Gemini model (if using genai)")
    ap.add_argument("--out_root", default="experiments")
    ap.add_argument("--limit_portraits", type=int, default=0)
    ap.add_argument("--limit_prompts",  type=int, default=0)
    ap.add_argument("--limit_boards",   type=int, default=0)
    args = ap.parse_args()

    # Load prompts (enhanced)
    prompts = load_prompts(Path(args.prompts_file))
    prompt_items = list(prompts.items())
    if args.limit_prompts: prompt_items = prompt_items[:args.limit_prompts]

    portraits = list_portraits(Path(args.portraits_root), args.limit_portraits)
    boards    = list_boards(args.boards_glob, args.limit_boards)

    if not portraits:
        raise SystemExit(f"No portraits found in {args.portraits_root}")
    if not boards:
        raise SystemExit(f"No boards found via glob: {args.boards_glob}")

    run_id = datetime.datetime.now().strftime("run_%Y%m%d-%H%M%S")
    run_dir = Path(args.out_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = open(run_dir / "manifest.csv", "w", newline="", encoding="utf-8")
    w = csv.writer(manifest)
    w.writerow(["university","level","portrait","prompt_id","engine","model","output_path"])

    # Iterate
    for board in tqdm(boards, desc="Boards"):
        uni, lvl = board_meta(board)
        for selfie in tqdm(portraits, desc=f"{uni}__{lvl}", leave=False):
            # per-portrait folder under this board
            portrait_key = selfie.stem
            for pid, ptxt in prompt_items:
                prompt_text = ptxt  # already enhanced with control suffix
                # Output dir:
                out_dir = run_dir / f"{uni}__{lvl}" / portrait_key / pid
                out_dir.mkdir(parents=True, exist_ok=True)

                # Copy inputs for easy review
                selfie_copy = out_dir / selfie.name
                board_copy  = out_dir / "board.png"
                if not selfie_copy.exists(): shutil.copy2(selfie, selfie_copy)
                if not board_copy.exists():  shutil.copy2(board,  board_copy)

                # Save resolved prompt + meta
                (out_dir / "prompt.txt").write_text(prompt_text, encoding="utf-8")
                meta = {
                    "university": uni, "level": lvl, "portrait": selfie.name,
                    "prompt_id": pid, "engine": args.engine,
                    "model": args.genai_model if args.engine=="genai" else "gemini-2.5-flash-image",
                    "vertex_project": args.vertex_project, "vertex_location": args.vertex_location
                }
                (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

                # Generate
                try:
                    if args.engine == "vertex":
                        if not args.vertex_project:
                            raise RuntimeError("Vertex mode needs --vertex_project")
                        img_bytes = call_vertex(args.vertex_project, args.vertex_location,
                                                "gemini-2.5-flash-image", selfie, board, prompt_text)
                    else:
                        api_key = os.getenv("GEMINI_API_KEY") or ""
                        if not api_key:
                            raise RuntimeError("Set GEMINI_API_KEY for genai engine")
                        img_bytes = call_genai(api_key, args.genai_model, selfie, board, prompt_text)

                    out_path = out_dir / "output.png"
                    out_path.write_bytes(img_bytes)
                    # quick sanity open
                    Image.open(out_path).load()

                    w.writerow([uni, lvl, selfie.name, pid, args.engine,
                                meta["model"], str(out_path)])
                except Exception as e:
                    (out_dir / "error.txt").write_text(str(e), encoding="utf-8")

                time.sleep(0.1)
    manifest.close()
    print(f"\nDone. Review: {run_dir}\nCSV: {run_dir/'manifest.csv'}")
if __name__ == "__main__":
    main()
