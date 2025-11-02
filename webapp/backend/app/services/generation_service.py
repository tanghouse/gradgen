import os
import json
from pathlib import Path
from typing import Optional, Dict, List
from PIL import Image
from app.core.config import settings
from app.core.prompts import (
    get_free_tier_prompts,
    get_random_premium_prompts,
    get_prompt_by_id,
    format_prompt
)
from app.services.watermark_service import add_watermark_to_image

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


class GenerationService:
    """Service for generating graduation portraits using Google Gemini."""

    def __init__(self):
        if genai is None or gtypes is None:
            raise RuntimeError("google-genai not installed. pip install google-genai")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> dict:
        """Load prompts from prompts.json."""
        prompts_path = Path(__file__).parent.parent.parent / "prompts.json"
        if not prompts_path.exists():
            # Fallback to default prompts
            return {
                "P2": "Identity-preserving edit. Keep the subject unchanged except wardrobe. "
                      "Dress the subject in official graduation regalia shown in the design board. "
                      "Ultra photo-real, true-to-color textiles."
            }

        with open(prompts_path, 'r', encoding='utf-8') as f:
            obj = json.load(f)

        # Enhance prompts with control suffix and create simple aliases
        enhanced = {}
        for k, v in obj.items():
            full_text = v.rstrip() + "\n\n" + CONTROL_SUFFIX
            # Add with full key
            enhanced[k] = full_text
            # Also add with simple P0-P7 key for backward compatibility
            # e.g., "P2_Grad_Parametric" -> also available as "P2"
            if k.startswith("P") and "_" in k:
                simple_key = k.split("_")[0]
                enhanced[simple_key] = full_text

        return enhanced

    def _mime_for(self, path: Path) -> str:
        """Get MIME type for image file."""
        ext = path.suffix.lower()
        if ext == ".png":
            return "image/png"
        if ext == ".webp":
            return "image/webp"
        return "image/jpeg"

    def generate_portrait(
        self,
        selfie_path: Path,
        board_path: Path,
        prompt_id: str = "P2",
        custom_prompt: str = None
    ) -> bytes:
        """
        Generate a graduation portrait using Gemini.

        Args:
            selfie_path: Path to the input portrait photo
            board_path: Path to the design board (gown reference)
            prompt_id: Prompt ID to use (default P2)
            custom_prompt: Override prompt text (optional)

        Returns:
            bytes: Generated image data
        """
        if custom_prompt:
            prompt = custom_prompt
        elif prompt_id not in self.prompts:
            raise ValueError(f"Unknown prompt ID: {prompt_id}")
        else:
            prompt = self.prompts[prompt_id]

        # Create parts for Gemini
        def part(p: Path):
            return gtypes.Part.from_bytes(
                data=p.read_bytes(),
                mime_type=self._mime_for(p)
            )

        contents = [part(selfie_path), part(board_path), prompt]

        # Call Gemini API
        resp = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=gtypes.GenerateContentConfig(response_modalities=["Image"])
        )

        # Extract image data
        cand = resp.candidates[0]
        for prt in cand.content.parts:
            inline = getattr(prt, "inline_data", None)
            if inline and getattr(inline, "data", None):
                return inline.data

        if hasattr(resp, "binary") and resp.binary:
            return resp.binary

        raise RuntimeError("Gemini API returned no image data")

    def get_board_path(self, university: str, degree_level: str) -> Optional[Path]:
        """
        Get the path to the design board for a university and degree level.

        Args:
            university: University name
            degree_level: Degree level (e.g., "Bachelors", "Masters", "PhD")

        Returns:
            Path to board.png or None if not found
        """
        templates_root = Path(__file__).parent.parent.parent / "templates"
        board_path = templates_root / university / degree_level / "board.png"

        if board_path.exists():
            return board_path

        return None

    def list_available_universities(self) -> list[dict]:
        """List all available universities and their degree levels."""
        templates_root = Path(__file__).parent.parent.parent / "templates"

        if not templates_root.exists():
            return []

        universities = []
        for uni_dir in sorted(templates_root.iterdir()):
            if not uni_dir.is_dir():
                continue

            levels = []
            for level_dir in sorted(uni_dir.iterdir()):
                if level_dir.is_dir() and (level_dir / "board.png").exists():
                    levels.append(level_dir.name)

            if levels:
                universities.append({
                    "name": uni_dir.name,
                    "degree_levels": levels
                })

        return universities

    def get_prompts_for_tier(self, tier: str, university: str = "", degree_level: str = "") -> Dict:
        """
        Get prompts based on tier (free or premium)

        Args:
            tier: "free" or "premium"
            university: University name for parametric prompts
            degree_level: Degree level for parametric prompts

        Returns:
            Dictionary of prompts {prompt_id: prompt_data}
        """
        if tier == "free":
            prompts = get_free_tier_prompts()
        elif tier == "premium":
            prompts = get_random_premium_prompts(count=5)
        else:
            raise ValueError(f"Invalid tier: {tier}")

        # Format prompts with university details if needed
        formatted_prompts = {}
        for prompt_id, prompt_data in prompts.items():
            prompt_text = prompt_data["prompt"]

            # Format parametric prompts
            if "{university}" in prompt_text or "{degree_level}" in prompt_text:
                prompt_text = format_prompt(prompt_text, university, degree_level)

            # Add control suffix
            prompt_text = prompt_text.rstrip() + "\n\n" + CONTROL_SUFFIX

            formatted_prompts[prompt_id] = {
                **prompt_data,
                "prompt": prompt_text
            }

        return formatted_prompts

    def generate_batch_portraits(
        self,
        selfie_path: Path,
        board_path: Path,
        tier: str,
        university: str = "",
        degree_level: str = ""
    ) -> List[Dict]:
        """
        Generate multiple portraits using tier-appropriate prompts

        Args:
            selfie_path: Path to input photo
            board_path: Path to design board
            tier: "free" or "premium"
            university: University name
            degree_level: Degree level

        Returns:
            List of dicts with {prompt_id, image_bytes, is_watermarked}
        """
        prompts = self.get_prompts_for_tier(tier, university, degree_level)
        results = []

        for prompt_id, prompt_data in prompts.items():
            try:
                # Generate image with formatted prompt
                image_bytes = self.generate_portrait(
                    selfie_path=selfie_path,
                    board_path=board_path,
                    prompt_id=prompt_id,
                    custom_prompt=prompt_data["prompt"]
                )

                # Apply watermark if free tier
                is_watermarked = (tier == "free")
                if is_watermarked:
                    image_bytes = add_watermark_to_image(
                        image_bytes=image_bytes,
                        tier="free",
                        position="bottom_right"
                    )

                results.append({
                    "prompt_id": prompt_id,
                    "prompt_name": prompt_data["name"],
                    "image_bytes": image_bytes,
                    "is_watermarked": is_watermarked,
                    "success": True,
                    "error": None
                })

            except Exception as e:
                results.append({
                    "prompt_id": prompt_id,
                    "prompt_name": prompt_data["name"],
                    "image_bytes": None,
                    "is_watermarked": False,
                    "success": False,
                    "error": str(e)
                })

        return results


generation_service = GenerationService()
