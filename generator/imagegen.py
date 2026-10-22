"""
Generate a single high-quality, photorealistic character portrait with a
Gemini image model, to use as the reference image for every Veo clip.

This locks the character's face so all 8 clips show the same realistic toddler.

Requires google-genai + GEMINI_API_KEY. Image model is configurable; run
list_models.py to see what your key supports (e.g. gemini-3-pro-image,
nano-banana-pro-preview, gemini-2.5-flash-image).
"""

import base64
import os


def generate_portrait(prompt, out_path, model=None):
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment or .env.")

    client = genai.Client(api_key=api_key)
    model = model or os.getenv("IMAGE_MODEL", "gemini-3-pro-image")

    # Some image models want response_modalities set; try with, fall back without.
    resp = None
    try:
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
    except Exception:
        resp = client.models.generate_content(model=model, contents=prompt)

    for cand in getattr(resp, "candidates", None) or []:
        content = getattr(cand, "content", None)
        for part in (getattr(content, "parts", None) or []):
            inline = getattr(part, "inline_data", None)
            data = getattr(inline, "data", None) if inline else None
            if data:
                if isinstance(data, str):
                    data = base64.b64decode(data)
                with open(out_path, "wb") as f:
                    f.write(data)
                print(f"  ✓ portrait → {out_path}")
                return out_path

    raise RuntimeError(
        f"{model} returned no image. Try a different IMAGE_MODEL "
        f"(run list_models.py to see options)."
    )
