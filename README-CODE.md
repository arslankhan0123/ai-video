# The Hidden World — Python Generator

A complete pipeline that generates the 8 Veo 3 clips, synthesizes the narrator
voiceover, and assembles the final vertical (9:16) YouTube Short automatically.

```
Ai Video/
├── main.py                 ← run this
├── requirements.txt
├── .env.example            ← copy to .env and add your keys
├── generator/
│   ├── config.py           ← all scenes, prompts, narration, mix levels
│   ├── veo_client.py       ← Veo 3 calls
│   ├── tts.py              ← narration (edge-tts / ElevenLabs)
│   ├── assemble.py         ← stitching + mixing (MoviePy/ffmpeg)
│   └── pipeline.py         ← orchestration
├── clips/    (auto)        ← generated scene_1.mp4 … scene_8.mp4
├── vo/       (auto)        ← generated vo_1.mp3 … vo_8.mp3
├── sfx/                    ← put 3 sound effects here (see below)
├── music/                 ← put your music track here
└── output/   (auto)        ← hidden_world_final.mp4
```

## Setup (one time)

1. **Install Python 3.10+** and **ffmpeg** (MoviePy needs it).
   - ffmpeg on Windows: download from ffmpeg.org and add its `bin` to PATH,
     or `winget install Gyan.FFmpeg`.
2. In this folder:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and paste your **GEMINI_API_KEY**.
   (Veo 3 may require a paid Google tier — that's on your account.)
4. Drop a music file into `music/` and 3 sound effects into `sfx/` named:
   `whoosh_portal.mp3`, `impact_boom.mp3`, `light_swell.mp3`.
   (Sources: YouTube Audio Library, Pixabay. Optional — it runs without them.)

## Run it

```bash
# 1. Preview everything, spend nothing:
python main.py --dry-run

# 2. Test ONE scene first (recommended before the full run):
python main.py --only-scene 1

# 3. Full build (free narration + your music):
python main.py --music "music/epic.mp3"

# 4. Re-stitch without regenerating (after you tweak audio):
python main.py --skip-video --skip-vo --music "music/epic.mp3"
```

The final file lands at `output/hidden_world_final.mp4`, ready to upload as a
Short (keep it ≤ 60s, add #Shorts).

## Editing the story
Everything creative lives in `generator/config.py`:
- `SCENES` — change any prompt, narration line, or SFX.
- `CHARACTER_BLOCK` — change the main character's look (stays consistent).
- `MUSIC_GAIN`, `NARRATION_GAIN`, etc. — tweak the mix.
- `VEO_MODEL` / `VEO_EXTRA_CONFIG` — switch Veo model or add config fields.

## Honest limitations
- **Costs money:** Veo 3 generation runs on your Google account and credits.
- **Model names drift:** if Veo returns a "model not found" error, update
  `VEO_MODEL` in `config.py` to the current name from Google's Veo docs.
- **Character consistency** isn't guaranteed across clips even with the shared
  character block — re-run a scene (`--only-scene N`) if Kai's face drifts.
- The `--dry-run` and `--only-scene 1` modes exist so you can validate the flow
  and one clip cheaply before committing to the full 8-scene render.
```
