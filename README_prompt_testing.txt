Prompt Testing Starter (Graduation Portraits)

Folder structure suggestion
---------------------------
data/
  raw_portraits/
    unsplash/...
    pexels/...
    pixabay/...
  outputs/
    {model}/{prompt_id}/{image_id}_{seed}.jpg
meta/
  prompt_test_plan.csv
  prompts.json
  ratings/

How to run a batch
------------------
1) Collect 10–20 test portraits (released for commercial use), record source_url and license in CSV.
2) Choose 5–10 prompts from prompts.json (start with P0, P1, P2, P6).
3) Fix a seed and model parameters for reproducibility.
4) Run the matrix: images × prompts (and, if needed, × models).
5) Save outputs to the path convention above and log each run in prompt_test_plan.csv.
6) Human review: score each output on 1–5 for face_fidelity, attire_accuracy, lighting_realism, background_quality, artifacts (lower is better), and overall.
7) Keep comments on failure modes (e.g., hood color wrong, cap angle off, skin over-smoothed).

Rating rubric (1–5)
-------------------
- Face fidelity: likeness to source face (pose, identity, skin texture).
- Attire accuracy: gown/hood/cap correctness vs. university design board (folds, color bands, trim).
- Lighting realism: natural highlights/shadows, no HDR/AI sheen.
- Background quality: clean gradient/separation, no halos or seams.
- Artifacts (low is good): warped features, duplicate tassels, color bleeding, odd hands/ears.
- Overall: judgment call after considering the above.

Licensing checklist
-------------------
- Prefer Unsplash License or Pexels License; record the source URL.
- Flickr: filter to CC0 or CC BY and record exact license and author.
- Avoid research-only datasets (FFHQ/CelebA/LFW) for anything beyond internal, non-commercial testing.

