"""
Auto-generate a YouTube title, description, and tags from the video's content
(the toddler's Urdu lines), using a Gemini text model.

Falls back to the defaults in talking_config.py if generation fails.
"""

import json
import os
import re


def generate_metadata(segments, model=None):
    """Return {'title', 'description', 'tags'} generated from the dialogue."""
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment or .env.")

    client = genai.Client(api_key=api_key)
    model = model or os.getenv("TEXT_MODEL", "gemini-2.5-flash")

    lines = "\n".join(f"- {s['urdu']}" for s in segments)
    prompt = (
        "These are the Urdu lines spoken by a cute, funny toddler character in a "
        "60-second vertical YouTube Short (comedy):\n"
        f"{lines}\n\n"
        "Create catchy metadata for this Short. Return ONLY a compact JSON object "
        "(no markdown, no code fences) with exactly these keys:\n"
        '  "title": a catchy YouTube Shorts title, max 70 characters, Urdu/English '
        "mix is fine, may include one emoji, and should end with #Shorts;\n"
        '  "description": 1-2 friendly sentences about the video;\n'
        '  "tags": an array of 8 short lowercase tags (no # symbol).'
    )

    resp = client.models.generate_content(model=model, contents=prompt)
    text = (getattr(resp, "text", None) or "").strip()

    # Strip code fences if the model added them.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()

    data = json.loads(text)
    # Basic shape guard.
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    tags = data.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    if not title:
        raise ValueError("No title produced")
    return {"title": title, "description": description, "tags": [str(t) for t in tags]}
