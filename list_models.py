#!/usr/bin/env python3
"""
List the models YOUR Gemini API key can access, and highlight the ones that
support video generation (Veo). Use this to get the exact model string to put
in .env as VEO_MODEL.

Run:
    python list_models.py
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from google import genai
except ImportError:
    print("google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API key. Set GEMINI_API_KEY in your environment or .env.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# Try to list base models; fall back to a plain list if the arg isn't supported.
try:
    models = list(client.models.list(config={"query_base": True}))
except Exception:
    models = list(client.models.list())

video_models = []
print("\n=== All models available to your key ===")
for m in models:
    name = getattr(m, "name", str(m))
    actions = getattr(m, "supported_actions", None) \
        or getattr(m, "supported_generation_methods", None) or []
    actions_str = ", ".join(actions) if actions else "(unknown)"
    print(f"  {name}   [{actions_str}]")

    lname = str(name).lower()
    is_video = "veo" in lname or any(
        a for a in actions
        if "video" in a.lower() or "predictlongrunning" in a.lower()
    )
    if is_video:
        video_models.append(name)

print("\n=== Likely VIDEO (Veo) models — use one of these as VEO_MODEL ===")
if video_models:
    for name in video_models:
        # strip the "models/" prefix if present; config.py accepts either form
        print(f"  {name.split('/')[-1]}")
    print("\nPut your chosen one in .env, e.g.:")
    print(f"  VEO_MODEL={video_models[0].split('/')[-1]}")
else:
    print("  None found. Your key/tier may not have Veo access yet.")
    print("  Check https://ai.google.dev/gemini-api/docs/video for current access.")
