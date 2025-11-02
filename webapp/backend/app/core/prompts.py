"""
Prompt definitions for graduation photo generation
Free tier: 5 fixed prompts
Premium tier: Random 5 from extended bank
"""

# Free tier prompts (always the same 5)
FREE_TIER_PROMPTS = {
    "P0_Apple_Studio": {
        "id": "P0_Apple_Studio",
        "name": "Apple Studio Portrait",
        "description": "High-end studio portrait with graduation attire",
        "prompt": "Transform this photo into a high-end studio portrait with graduation attire. "
                 "Maintain the person's exact facial features, skin tone, and identity. "
                 "Add professional graduation gown, hood, and cap matching the university style shown in the reference. "
                 "Use clean, minimalist background with soft, even studio lighting. "
                 "Photorealistic, sharp focus, professional photography quality."
    },
    "P2_Grad_Parametric": {
        "id": "P2_Grad_Parametric",
        "name": "University-Specific Regalia",
        "description": "Traditional graduation portrait with accurate university regalia",
        "prompt": "Identity-preserving edit: Add graduation regalia to this portrait while keeping the person's face completely unchanged. "
                 "Use the reference image to match the exact gown color, hood design, and cap style for {university} {degree_level}. "
                 "Professional photography lighting, natural pose, clean background. "
                 "Photorealistic texture on fabric, accurate academic dress details."
    },
    "P5_Editorial_Soft": {
        "id": "P5_Editorial_Soft",
        "name": "Editorial Soft Style",
        "description": "Soft, editorial-style graduation portrait",
        "prompt": "Editorial portrait with soft cinematic grading. Add graduation attire (gown, hood, cap) "
                 "while preserving the person's facial identity completely. "
                 "Soft natural light, shallow depth of field, film photography aesthetic. "
                 "Muted color palette, elegant composition, professional yet approachable feel."
    },
    "P6_HighKey_WhiteBG": {
        "id": "P6_HighKey_WhiteBG",
        "name": "High-Key White Background",
        "description": "Bright, professional white background graduation photo",
        "prompt": "High-key studio portrait with pure white background. "
                 "Add graduation gown, hood, and cap while maintaining exact facial features and identity. "
                 "Bright, even lighting with no harsh shadows. Clean, professional look perfect for announcements and LinkedIn. "
                 "Sharp focus, photorealistic details, commercial photography quality."
    },
    "P7_LowKey_BlackBG": {
        "id": "P7_LowKey_BlackBG",
        "name": "Low-Key Black Background",
        "description": "Dramatic graduation portrait with black background",
        "prompt": "Low-key studio portrait with dramatic black background. "
                 "Add graduation attire while preserving the person's identity. "
                 "Dramatic side lighting creating depth and dimension. "
                 "Elegant, sophisticated aesthetic with strong contrast. "
                 "Professional photography, sharp details, cinematic quality."
    }
}

# Premium tier prompt bank (random 5 selected from these)
PREMIUM_TIER_PROMPT_BANK = {
    "Classic_UK_Graduation": {
        "id": "Classic_UK_Graduation",
        "name": "Classic UK Graduation",
        "description": "Traditional British university graduation style",
        "prompt": "Traditional UK university graduation portrait. "
                 "Formal academic dress with accurate British university regalia. "
                 "Classic pose, professional setting, timeless composition. "
                 "Preserve exact facial features and identity. "
                 "Professional photography, natural lighting, prestigious aesthetic."
    },
    "American_College_Style": {
        "id": "American_College_Style",
        "name": "American College Style",
        "description": "US-style college graduation photo",
        "prompt": "American college graduation portrait. "
                 "US-style cap and gown with tassel. "
                 "Bright, optimistic feel with campus-inspired background. "
                 "Maintain person's complete facial identity. "
                 "Professional yet friendly aesthetic, natural smile encouraged."
    },
    "Vintage_Academic": {
        "id": "Vintage_Academic",
        "name": "Vintage Academic",
        "description": "Classic vintage academic portrait style",
        "prompt": "Vintage academic portrait with film photography aesthetic. "
                 "Traditional graduation attire, sepia or muted color tones. "
                 "Classic composition inspired by historical university portraits. "
                 "Preserve facial identity completely. "
                 "Timeless, elegant, sophisticated quality."
    },
    "Golden_Hour_Outdoor": {
        "id": "Golden_Hour_Outdoor",
        "name": "Golden Hour Outdoor",
        "description": "Outdoor graduation photo at golden hour",
        "prompt": "Outdoor graduation portrait during golden hour. "
                 "Warm, natural sunlight creating a glowing effect. "
                 "Add graduation gown and cap while maintaining identity. "
                 "University campus or elegant outdoor setting. "
                 "Professional yet natural feel, celebration aesthetic."
    },
    "Corporate_Professional": {
        "id": "Corporate_Professional",
        "name": "Corporate Professional",
        "description": "LinkedIn-ready professional graduation portrait",
        "prompt": "Corporate-professional graduation portrait optimized for LinkedIn. "
                 "Clean, professional background (neutral or subtle gradient). "
                 "Graduation attire with polished, business-appropriate presentation. "
                 "Maintain exact facial features and professional demeanor. "
                 "Perfect for professional networking, sharp and clear."
    },
    "Candid_Celebration": {
        "id": "Candid_Celebration",
        "name": "Candid Celebration",
        "description": "Natural, joyful celebration moment",
        "prompt": "Candid graduation celebration portrait capturing genuine joy. "
                 "Natural expression of achievement and happiness. "
                 "Graduation attire in a celebratory context. "
                 "Preserve person's identity and authentic emotion. "
                 "Photojournalistic style, natural lighting, genuine moment."
    },
    "Formal_Yearbook": {
        "id": "Formal_Yearbook",
        "name": "Formal Yearbook Style",
        "description": "Traditional yearbook-style graduation photo",
        "prompt": "Formal yearbook graduation portrait. "
                 "Traditional pose and framing used in university yearbooks. "
                 "Clean background, even lighting, professional composition. "
                 "Graduation gown and cap with formal presentation. "
                 "Maintain exact facial features, classic timeless style."
    },
    "Artistic_Portrait": {
        "id": "Artistic_Portrait",
        "name": "Artistic Portrait",
        "description": "Creative, artistic graduation portrait",
        "prompt": "Artistic graduation portrait with creative composition. "
                 "Unique angle, dramatic lighting, or artistic background. "
                 "Graduation attire presented in an elevated, artistic way. "
                 "Preserve person's identity while adding creative flair. "
                 "Gallery-worthy quality, distinctive and memorable."
    },
    "Family_Heirloom": {
        "id": "Family_Heirloom",
        "name": "Family Heirloom",
        "description": "Timeless portrait suitable for family keepsake",
        "prompt": "Timeless graduation portrait suitable as family heirloom. "
                 "Classic composition and lighting that will remain elegant for decades. "
                 "Traditional graduation attire, dignified pose. "
                 "Preserve exact facial features and character. "
                 "Museum-quality, archival aesthetic, enduring style."
    },
    "Modern_Minimal": {
        "id": "Modern_Minimal",
        "name": "Modern Minimalist",
        "description": "Contemporary minimalist graduation portrait",
        "prompt": "Modern minimalist graduation portrait. "
                 "Clean lines, simple composition, contemporary aesthetic. "
                 "Graduation attire with modern, uncluttered presentation. "
                 "Maintain person's identity with modern styling. "
                 "Instagram-worthy, clean, elegant simplicity."
    },
    "Dramatic_Chiaroscuro": {
        "id": "Dramatic_Chiaroscuro",
        "name": "Dramatic Chiaroscuro",
        "description": "Dramatic lighting with strong light/shadow contrast",
        "prompt": "Dramatic graduation portrait using chiaroscuro lighting technique. "
                 "Strong contrast between light and shadow. "
                 "Graduation regalia with dramatic, sculptural lighting. "
                 "Preserve facial features while creating depth and drama. "
                 "Fine art photography quality, Renaissance-inspired."
    },
    "Soft_Natural_Light": {
        "id": "Soft_Natural_Light",
        "name": "Soft Natural Light",
        "description": "Gentle, flattering natural window light",
        "prompt": "Graduation portrait with soft, flattering natural window light. "
                 "Gentle illumination creating a warm, approachable feel. "
                 "Graduation attire with relaxed, natural presentation. "
                 "Maintain exact facial identity. "
                 "Professional yet personal, inviting aesthetic."
    },
    "Urban_Contemporary": {
        "id": "Urban_Contemporary",
        "name": "Urban Contemporary",
        "description": "Modern urban setting graduation photo",
        "prompt": "Contemporary graduation portrait in urban setting. "
                 "Modern city background or architectural elements. "
                 "Graduation gown and cap with current, stylish presentation. "
                 "Preserve person's identity with modern edge. "
                 "Fresh, current, urban professional aesthetic."
    },
    "Heritage_Tradition": {
        "id": "Heritage_Tradition",
        "name": "Heritage & Tradition",
        "description": "Traditional graduation celebrating heritage",
        "prompt": "Traditional graduation portrait celebrating academic heritage. "
                 "Formal academic regalia with emphasis on ceremonial tradition. "
                 "Dignified, respectful composition honoring educational achievement. "
                 "Maintain person's complete identity. "
                 "Prestigious, formal, time-honored aesthetic."
    },
    "Joyful_Candid": {
        "id": "Joyful_Candid",
        "name": "Joyful & Candid",
        "description": "Spontaneous, joyful graduation moment",
        "prompt": "Spontaneous, joyful graduation portrait capturing pure happiness. "
                 "Natural laugh or genuine smile in graduation attire. "
                 "Authentic moment of achievement and celebration. "
                 "Preserve person's authentic expression and features. "
                 "Warm, genuine, heartfelt quality."
    }
}

# Helper functions
def get_free_tier_prompts() -> dict:
    """Get the 5 fixed free tier prompts"""
    return FREE_TIER_PROMPTS

def get_random_premium_prompts(count: int = 5) -> dict:
    """Get random prompts from premium tier bank"""
    import random
    all_premium_ids = list(PREMIUM_TIER_PROMPT_BANK.keys())
    selected_ids = random.sample(all_premium_ids, min(count, len(all_premium_ids)))
    return {pid: PREMIUM_TIER_PROMPT_BANK[pid] for pid in selected_ids}

def get_prompt_by_id(prompt_id: str) -> dict:
    """Get a specific prompt by ID from either tier"""
    if prompt_id in FREE_TIER_PROMPTS:
        return FREE_TIER_PROMPTS[prompt_id]
    if prompt_id in PREMIUM_TIER_PROMPT_BANK:
        return PREMIUM_TIER_PROMPT_BANK[prompt_id]
    return None

def format_prompt(prompt_template: str, university: str = "", degree_level: str = "") -> str:
    """Format prompt template with university and degree level"""
    return prompt_template.format(
        university=university or "this university",
        degree_level=degree_level or "degree"
    )
