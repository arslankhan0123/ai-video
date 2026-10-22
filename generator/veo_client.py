"""
Veo 3 video generation via the Google Gen AI SDK (google-genai).

Each scene prompt is sent to Veo, which returns a long-running operation. We
poll until it's done, then download the resulting mp4.

Requires:
    pip install google-genai
    GEMINI_API_KEY in your environment (or .env)

Note: Veo access/billing and exact model names are set by Google and may change.
If a call fails with a model-not-found or permission error, check Google's
current Veo documentation and update VEO_MODEL / VEO_EXTRA_CONFIG in config.py.
"""

import os
import time

from . import config


def _client():
    try:
        from google import genai  # noqa
    except ImportError as e:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install google-genai"
        ) from e

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No API key found. Set GEMINI_API_KEY in your environment or .env file."
        )
    from google import genai
    return genai.Client(api_key=api_key)


def _build_config():
    """Assemble the GenerateVideosConfig from config.py settings."""
    from google.genai import types

    fields = dict(
        aspect_ratio=config.ASPECT_RATIO,
        number_of_videos=1,
    )
    # Pass through any extra, version-specific fields the user opted into.
    for key, value in (config.VEO_EXTRA_CONFIG or {}).items():
        fields[key] = value
    return types.GenerateVideosConfig(**fields)


def generate_scene(prompt: str, out_path: str, image_path: str = None,
                   poll_seconds: int = 10, timeout_seconds: int = 600) -> str:
    """
    Generate a single clip from `prompt` and save it to `out_path`.
    If `image_path` is given, it's used as a reference/first frame
    (image-to-video) so the character stays consistent.
    Returns the output path. Raises on failure or timeout.
    """
    client = _client()
    cfg = _build_config()

    kwargs = dict(model=config.VEO_MODEL, prompt=prompt, config=cfg)
    if image_path:
        from google.genai import types
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
        kwargs["image"] = types.Image(image_bytes=img_bytes, mime_type=mime)
        print(f"  → submitting to Veo ({config.VEO_MODEL}) with reference image ...")
    else:
        print(f"  → submitting to Veo ({config.VEO_MODEL}) ...")

    operation = client.models.generate_videos(**kwargs)

    waited = 0
    while not operation.done:
        if waited >= timeout_seconds:
            raise TimeoutError(
                f"Veo generation timed out after {timeout_seconds}s for {out_path}"
            )
        time.sleep(poll_seconds)
        waited += poll_seconds
        print(f"  → still rendering... ({waited}s)")
        operation = client.operations.get(operation)

    response = getattr(operation, "response", None)
    videos = getattr(response, "generated_videos", None) if response else None
    if not videos:
        raise RuntimeError(
            f"Veo returned no video for this prompt. Full operation: {operation}"
        )

    generated = videos[0]
    # Download the file bytes, then save locally.
    client.files.download(file=generated.video)
    generated.video.save(out_path)
    print(f"  ✓ saved {out_path}")
    return out_path
