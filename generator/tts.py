"""
Narrator voiceover generation.

Two engines:
  - "edge"       : edge-tts, free, no API key. Default.
  - "elevenlabs" : higher quality, needs ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID.

Each produces one mp3 per scene so lines can be placed exactly on the timeline.
"""

import asyncio
import os

from . import config


def synthesize(text: str, out_path: str, engine: str = None) -> str:
    engine = (engine or config.TTS_ENGINE or "edge").lower()
    if engine == "elevenlabs":
        return _elevenlabs(text, out_path)
    return _edge(text, out_path)


# --------------------------------------------------------------------------- #
# edge-tts  (free)
# --------------------------------------------------------------------------- #
def _edge(text: str, out_path: str) -> str:
    try:
        import edge_tts  # noqa
    except ImportError as e:
        raise RuntimeError(
            "edge-tts is not installed. Run: pip install edge-tts"
        ) from e

    async def _run():
        import edge_tts
        communicate = edge_tts.Communicate(
            text, voice=config.EDGE_VOICE, rate=config.EDGE_RATE
        )
        await communicate.save(out_path)

    asyncio.run(_run())
    print(f"  ✓ narration (edge) → {out_path}")
    return out_path


# --------------------------------------------------------------------------- #
# ElevenLabs  (paid, higher quality)
# --------------------------------------------------------------------------- #
def _elevenlabs(text: str, out_path: str) -> str:
    try:
        from elevenlabs.client import ElevenLabs  # noqa
    except ImportError as e:
        raise RuntimeError(
            "elevenlabs is not installed. Run: pip install elevenlabs"
        ) from e

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("Set ELEVENLABS_API_KEY in your environment or .env.")
    if not config.ELEVENLABS_VOICE_ID:
        raise RuntimeError(
            "Set ELEVENLABS_VOICE_ID in your .env to a deep male voice id."
        )

    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        voice_id=config.ELEVENLABS_VOICE_ID,
        model_id=config.ELEVENLABS_MODEL,
        text=text,
        output_format="mp3_44100_128",
    )
    with open(out_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    print(f"  ✓ narration (elevenlabs) → {out_path}")
    return out_path
