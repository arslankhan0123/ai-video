"""
Configuration and scene data for "The Little Hero" short.

Edit the SCENES list to change prompts, narration, timings, or sound effects.
Everything else (keys, models, voices) is read from environment variables or
set here with safe defaults.
"""

import os

# --------------------------------------------------------------------------- #
# Global video settings
# --------------------------------------------------------------------------- #
ASPECT_RATIO = "9:16"          # vertical Short
FPS = 30
# Veo 3 produces 8-second clips. Keep scene durations at 8 unless your Veo
# version supports other lengths.
CLIP_SECONDS = 8

# Veo model. Model names change over time — if this 404s, run `list_models.py`
# to see the exact names YOUR key supports, then set VEO_MODEL in .env.
# Current Gemini API names (as of Oct 2026):
#   "veo-3.1-generate-preview"        (quality)
#   "veo-3.1-fast-generate-preview"   (faster / cheaper)
#   "veo-3.1-lite-generate-preview"   (lite)
VEO_MODEL = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")

# Only these two config fields are sent to Veo by default (widely supported).
# Put any extra, version-specific fields (e.g. person_generation, resolution,
# negative_prompt) here as a dict; they are passed through only if non-empty.
VEO_EXTRA_CONFIG = {
    # "person_generation": "allow_adult",
    # "resolution": "1080p",
}

# --------------------------------------------------------------------------- #
# Audio mix levels (linear gain; 1.0 = unchanged)
# --------------------------------------------------------------------------- #
AMBIENT_GAIN = 0.15     # Veo's own ambient/SFX audio, kept quiet under the VO
NARRATION_GAIN = 1.6    # narrator voiceover, pushed up so it's clearly audible
MUSIC_GAIN = 0.12       # music bed (~ -18 dB) under the narration
SFX_GAIN = 0.8          # accent sound effects

# --------------------------------------------------------------------------- #
# Voiceover (TTS) settings
# --------------------------------------------------------------------------- #
# Which TTS engine to use by default: "edge" (free, no key) or "elevenlabs".
TTS_ENGINE = os.getenv("TTS_ENGINE", "edge")

# edge-tts voice. Swap for the narration language:
#   English (light/friendly, good for comedy) : en-US-GuyNeural
#   English (deep/dramatic)                   : en-US-ChristopherNeural
#   Urdu (Pakistan)                           : ur-PK-AsadNeural
#   Hindi (India)                             : hi-IN-MadhurNeural
EDGE_VOICE = os.getenv("EDGE_VOICE", "en-US-GuyNeural")
EDGE_RATE = os.getenv("EDGE_RATE", "+2%")   # lively comedic pacing

# ElevenLabs: set ELEVENLABS_VOICE_ID in your .env to a deep male voice.
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

# --------------------------------------------------------------------------- #
# Reusable character block — prepended to every scene prompt so the main
# character stays visually consistent across all clips.
# (Original cute toddler character — not based on any specific real video.)
# --------------------------------------------------------------------------- #
CHARACTER_BLOCK = (
    "Character (keep identical in every shot): an adorable chubby South Asian "
    "toddler boy, about 2 to 3 years old, round face, full rosy cheeks, big "
    "expressive dark-brown eyes, short neat dark hair, wearing a colorful "
    "short-sleeve printed shirt and little blue jeans. Very cute, highly "
    "expressive face and body language. "
    "Style: hyperrealistic cinematic 3D animation, photoreal skin, hair and "
    "fabric detail, soft shallow depth of field, warm natural lighting, shot "
    "like a high-end animated short film, 9:16 vertical. "
    "No on-screen text, no captions, no subtitles, no logos. "
    "Ambient sound and gentle sound effects only; no spoken dialogue and no "
    "music in the clip."
)

# --------------------------------------------------------------------------- #
# The 8 scenes. `start` is where the narration begins on the final timeline.
# `sfx` is an optional accent sound effect file (relative to the sfx/ folder)
# dropped at `sfx_at` seconds into that scene.
# --------------------------------------------------------------------------- #
SCENES = [
    {
        "id": 1,
        "start": 0,
        "prompt": (
            "The cute toddler boy stands alone in a busy, colorful South Asian "
            "street bazaar in warm afternoon light, looking around curiously at "
            "the crowd and stalls with a comically serious, determined little face. Suddenly a soft glowing doorway of golden-"
            "turquoise light shimmers into view down a quiet side alley; his eyes "
            "go wide with wonder and he toddles one small step toward it. Camera: "
            "slow gentle push-in, shallow depth of field, bustling market bokeh "
            "behind him. Lighting: warm golden hour with a soft magical glow from "
            "the doorway. Mood: curious, enchanting. Audio: lively market ambience, "
            "distant chatter, a soft magical shimmer."
        ),
        "narration": "Meet our hero. Two years old, zero fear, and absolutely no idea what he's getting into.",
        "sfx": "shimmer.mp3",
        "sfx_at": 2.0,
    },
    {
        "id": 2,
        "start": 8,
        "prompt": (
            "The toddler boy toddles through the glowing doorway and emerges into a "
            "magical hidden world: giant friendly glowing flowers, floating "
            "lanterns, soft waterfalls and sparkling fireflies, a dreamy pastel "
            "sky. He stops and gasps in delight, spinning slowly to take it all in, "
            "tiny arms raised. Camera: sweeping reveal rising and gently orbiting "
            "around him. Lighting: soft magical glow, warm and dreamy. Mood: "
            "breathtaking childlike wonder. Audio: gentle magical chimes, soft wind, "
            "distant sparkling tones."
        ),
        "narration": "He found a secret magical world. His reaction? Pure, unfiltered... whoa.",
        "sfx": None,
        "sfx_at": 0,
    },
    {
        "id": 3,
        "start": 16,
        "prompt": (
            "The toddler boy stands at the start of a wobbly little rope-and-plank "
            "bridge over a sparkling stream in the magical world. He hesitates, bites "
            "his lip nervously, then with a determined little face takes careful "
            "wobbling steps across, arms out for balance. Camera: low playful "
            "tracking beside his feet, tilting up to his focused face. Lighting: "
            "bright and warm with soft rim light. Mood: nervous but brave, endearing. "
            "Audio: creaking planks, trickling water, a soft suspenseful tinkle."
        ),
        "narration": "First challenge: a wobbly bridge. His master plan? Wobble harder and hope for the best.",
        "sfx": None,
        "sfx_at": 0,
    },
    {
        "id": 4,
        "start": 24,
        "prompt": (
            "The toddler boy reaches a glowing hollow tree; warm golden lights and "
            "floating sparkles swirl out as he approaches, reflecting in his wide "
            "eyes. He reaches out a tiny hand and touches a glowing orb; it pulses "
            "and lights up his delighted face. Camera: slow push-in on his aw-struck "
            "face, then soft rack focus to the glowing tree. Lighting: warm golden "
            "magical glow against soft shadow. Mood: wonder, discovery, joy. Audio: "
            "soft resonant hum, gentle sparkle, a rising magical tone."
        ),
        "narration": "Then he found the treasure. Naturally, he touched it. Of course he touched it.",
        "sfx": None,
        "sfx_at": 0,
    },
    {
        "id": 5,
        "start": 32,
        "prompt": (
            "The ground gives a little shake and the toddler boy trips and tumbles "
            "gently onto the soft glowing grass, his treasure orb rolling away; his "
            "lip quivers and his eyes well up with tears as soft petals and sparkles "
            "settle around him with a comically dramatic wobbling pout. Camera: slightly closer, tender low angle on his "
            "teary face. Lighting: dimmer and cooler, a sad soft blue. Mood: the sad "
            "little low point, tender. Audio: a soft stumble, a gentle sad chime, "
            "quiet wind."
        ),
        "narration": "And then... he fell. Cue the tears. This is the dramatic part, folks.",
        "sfx": "soft_thud.mp3",
        "sfx_at": 1.0,
    },
    {
        "id": 6,
        "start": 40,
        "prompt": (
            "The toddler boy sniffles, wipes his tears with the back of his little "
            "hand, takes a deep breath, and pushes himself up onto his feet with a "
            "determined, brave little face, tiny fists clenched. He steps forward "
            "again. Camera: low hero-angle slow push-in rising with him. Lighting: a "
            "warm shaft of light returns onto his determined face. Mood: tender, "
            "determined, the turning point. Audio: a soft sniffle, a gentle rising "
            "hopeful tone, a soft heartbeat-like pulse."
        ),
        "narration": "But this little guy does not quit. One deep breath... and he's back in business.",
        "sfx": None,
        "sfx_at": 0,
    },
    {
        "id": 7,
        "start": 48,
        "prompt": (
            "The toddler boy pushes open a big glowing round door with both tiny "
            "hands; brilliant warm golden light floods out and washes over him, a "
            "path of glowing stepping stones lighting up ahead. He breaks into a huge "
            "joyful giggling smile and toddles into the light. Camera: tracking behind "
            "him toward the glow, then a happy slow orbit. Lighting: radiant warm "
            "golden burst, soft lens flares. Mood: triumphant, joyful, uplifting. "
            "Audio: a soaring warm swell, a bright magical chime, happy sparkles."
        ),
        "narration": "He opened the giant door like a tiny boss. Honestly? Respect.",
        "sfx": "light_swell.mp3",
        "sfx_at": 1.0,
    },
    {
        "id": 8,
        "start": 56,
        "prompt": (
            "The toddler boy stands proudly on a small grassy hill overlooking the "
            "beautiful glowing magical world at golden dusk, a happy content smile on "
            "his face, gentle wind in his hair, holding his glowing orb. He looks up "
            "and beams. Camera: slow cinematic pull-back and crane-up revealing the "
            "vast dreamy world around him. Lighting: warm golden dusk, soft and "
            "hopeful, gentle god rays. Mood: peaceful, proud, heartwarming. Audio: "
            "gentle wind, soft warm ambient shimmer, a warm sustained tone fading out."
        ),
        "narration": "He came for snacks, probably. He left a legend. Never give up, little man.",
        "sfx": None,
        "sfx_at": 0,
    },
]


def full_prompt(scene: dict) -> str:
    """Character block + the scene's own prompt, as one Veo prompt."""
    return f"{CHARACTER_BLOCK}\n\n{scene['prompt']}"
