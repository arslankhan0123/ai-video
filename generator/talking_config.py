"""
Config for the 60-second Urdu FUNNY talking-toddler short.
VARIED version: every clip is a DIFFERENT place + style, with random funny talk.

Veo 3.1 makes 8-second clips, so a 60s video is 8 segments stitched together.
The toddler SPEAKS, so we keep Veo's native audio (its Urdu voice + lip-sync).

The character is an original toddler (not based on any real person/video).

NOTE on consistency vs variety:
  USE_IMAGE_REFERENCE = True  -> one locked portrait is the first frame of every
    clip, so the FACE is identical... but so is the scene (all clips look the
    same). Use only if you want a fixed talking-head.
  USE_IMAGE_REFERENCE = False -> each clip renders its own place/style from text
    (what you want for variety). The face may vary slightly between clips; that's
    the trade-off for different locations.
"""

import os

from . import config  # reuse ASPECT_RATIO, FPS, VEO_MODEL, VEO_EXTRA_CONFIG

# Final length (seconds). 8 x 8s = 64s -> trimmed to 60s.
TARGET_SECONDS = 60

# Optional very-quiet music bed under the voice (linear gain).
TALKING_MUSIC_GAIN = 0.05

# --- Title / YouTube metadata --------------------------------------------- #
# When True, the title/description/tags are auto-generated from the toddler's
# lines (via a Gemini text model). The output .mp4 is named after the title.
AUTO_TITLE = True
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")

# Fallbacks used if auto-generation is off or fails.
VIDEO_TITLE = "Chhota Bacha, Bara Attitude 😂 | Funny Urdu Baby #Shorts"
VIDEO_DESCRIPTION = (
    "A tiny toddler with a very big attitude takes on the world — in Urdu. 😂 "
    "#Shorts #funny #baby #urdu"
)
VIDEO_TAGS = ["funny baby", "urdu comedy", "cute baby", "shorts",
              "funny shorts", "desi baby", "viral shorts", "comedy"]

# YouTube upload defaults (used with `python talk.py --upload`).
YT_PRIVACY = "private"   # "private" | "unlisted" | "public"
YT_CATEGORY = "24"       # 24 = Entertainment

# --- Image reference ------------------------------------------------------- #
# OFF so each clip gets its own place/style (variety). Turn on only for a fixed
# single-location talking head.
USE_IMAGE_REFERENCE = False
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3-pro-image")
PORTRAIT_FILE = "character/toddler.png"
CHARACTER_PORTRAIT_PROMPT = (
    "Ultra-photorealistic portrait photograph of an adorable chubby South Asian "
    "toddler boy about 2 years old: round face, big expressive dark-brown eyes, "
    "full rosy cheeks, soft lifelike baby skin, short dark hair, a small black "
    "nazar dot on the forehead, wearing a colorful printed shirt, cute grumpy "
    "expression. Plain soft studio background. Shot on a cinema camera, natural "
    "light, shallow depth of field, true-to-life realism, vertical 9:16. No text."
)

# --------------------------------------------------------------------------- #
# Character identity — reused in every clip so the SAME kind of toddler appears,
# while each scene sets its own place and style.
# --------------------------------------------------------------------------- #
TALKING_CHARACTER = (
    "An adorable, chubby real South Asian toddler boy about 2 years old, round "
    "face, big expressive dark-brown eyes, full rosy cheeks, soft lifelike baby "
    "skin, short dark hair, a small black nazar dot on the forehead, wearing a "
    "colorful printed shirt. Hilariously expressive with exaggerated grown-up "
    "expressions and little hand gestures, like a tiny adult who thinks he's in "
    "charge. Ultra-photorealistic, lifelike real human toddler, cinematic, "
    "9:16 vertical. Smooth lively motion and natural lip-sync. No on-screen "
    "text, no captions, no subtitles, no logos."
)

SPEECH_DIRECTION = (
    "A cute little toddler voice speaking Urdu, funny and confident, accurate "
    "lip-sync, matching ambient sound for the location, no background music."
)

# --------------------------------------------------------------------------- #
# 8 funny beats — each a DIFFERENT place + style + camera, with random funny
# Urdu talk. Original, family-friendly. Edit freely.
# --------------------------------------------------------------------------- #
SEGMENTS = [
    {
        "id": 1,
        "scene": ("PLACE: a busy, colorful South Asian street bazaar in warm "
                  "afternoon light, documentary realism. The toddler stands with "
                  "arms crossed, grumpy serious face. Camera: slow push-in, lively "
                  "crowd bokeh behind him."),
        "urdu": "دیکھو، مجھے بھوک لگی ہے، اور بھوکے آدمی سے کوئی پنگا نہیں لیتا۔",
    },
    {
        "id": 2,
        "scene": ("PLACE: inside a bright, colorful toy shop packed with toys on "
                  "shelves, playful vibrant lighting. The toddler spreads both arms "
                  "wide gesturing at all the toys, eyes sparkling greedily. Camera: "
                  "quick energetic reveal of the shelves."),
        "urdu": "یہ سارے کھلونے مجھے چاہئیں۔ سارے کے سارے۔ اور ہاں، ادھار بالکل نہیں چلے گا۔",
    },
    {
        "id": 3,
        "scene": ("PLACE: a sunny green park, the toddler sitting on a swing gently "
                  "swinging, cheerful bright daylight, soft bokeh trees. He gestures "
                  "philosophically. Camera: gentle side tracking with the swing."),
        "urdu": "زندگی اس جھولے کی طرح ہے، کبھی اوپر، کبھی نیچے، مگر میں ہر حال میں اسٹائل میں رہتا ہوں۔",
    },
    {
        "id": 4,
        "scene": ("PLACE: a cozy warm home kitchen, the toddler in a high chair "
                  "dramatically pushing away a plate of vegetables with a disgusted "
                  "pout, soft warm indoor light. Camera: medium close-up."),
        "urdu": "سبزی؟ نہیں بھئی۔ میں نے اپنے وکیل سے بات کر لی ہے، یہ تو بالکل غیر قانونی ہے۔",
    },
    {
        "id": 5,
        "scene": ("PLACE: a rooftop at golden-hour sunset over a South Asian city, "
                  "cinematic warm orange light, gentle breeze. The toddler stands "
                  "like a wise old elder, hands behind his back. Camera: slow "
                  "cinematic orbit."),
        "urdu": "سنو نوجوانو، میں نے اپنی دو سال کی زندگی میں جو دیکھا ہے، وہ تم نے سوچا بھی نہیں ہوگا۔",
    },
    {
        "id": 6,
        "scene": ("PLACE: the back seat of a moving auto-rickshaw, blurred city "
                  "street rushing past the open side, dynamic daytime. The toddler "
                  "throws his hands up complaining about the traffic. Camera: "
                  "handheld, lively motion."),
        "urdu": "یہ ٹریفک تو روز کا تماشا ہے۔ میں تو کہتا ہوں رکشہ مجھے چلانے دو، منٹوں میں پہنچا دوں۔",
    },
    {
        "id": 7,
        "scene": ("PLACE: a traditional sweets (mithai) shop with trays of colorful "
                  "sweets, warm inviting glow. The toddler has a little sweet-syrup "
                  "on his cheeks and hides one hand behind his back with fake "
                  "innocence. Camera: slow push-in on his guilty face."),
        "urdu": "یہ مٹھائی میں نے نہیں کھائی۔ منہ پر لگی ہے؟ جی نہیں، وہ کوئی ثبوت نہیں ہے۔",
    },
    {
        "id": 8,
        "scene": ("PLACE: a cozy living room in the evening with soft warm lamp "
                  "light and a blurred sofa behind. The toddler points confidently "
                  "at the camera with a big cheeky grin, then a satisfied nod like "
                  "dropping the mic. Camera: steady close-up."),
        "urdu": "تو یاد رکھنا، گھر کا اصل باس کون ہے؟ بالکل ٹھیک پہچانا، میں۔",
    },
]


def segment_prompt(seg: dict) -> str:
    """Assemble the full Veo prompt for one funny talking segment."""
    return (
        f"{TALKING_CHARACTER} {seg['scene']} "
        f'He looks at the camera and says, in Urdu: "{seg["urdu"]}". '
        f"{SPEECH_DIRECTION}"
    )
