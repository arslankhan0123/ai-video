#!/usr/bin/env python3
"""
The Hidden World — one-command cinematic YouTube Short generator.

Examples:
    # See every prompt and narration line without spending any credits:
    python main.py --dry-run

    # Generate ONLY scene 1 (cheap test before committing to all 8):
    python main.py --only-scene 1

    # Full build, free narration (edge-tts), your music file:
    python main.py --music "music/epic.mp3"

    # Full build with ElevenLabs narration:
    python main.py --tts elevenlabs --music "music/epic.mp3"

    # Re-assemble using clips/VO already generated (no new API calls):
    python main.py --skip-video --skip-vo --music "music/epic.mp3"
"""

import argparse
import os
import sys

# Load .env if python-dotenv is available (optional convenience).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from generator import pipeline


def main():
    parser = argparse.ArgumentParser(description="Generate the Hidden World Short.")
    parser.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)),
                        help="Project root (defaults to this folder).")
    parser.add_argument("--only-scene", type=int, default=None,
                        help="Generate just this scene id (1-8) for testing.")
    parser.add_argument("--skip-video", action="store_true",
                        help="Reuse existing clips in clips/ instead of calling Veo.")
    parser.add_argument("--skip-vo", action="store_true",
                        help="Reuse existing narration in vo/.")
    parser.add_argument("--tts", choices=["edge", "elevenlabs"], default=None,
                        help="Voiceover engine (default from config / env).")
    parser.add_argument("--music", default=None,
                        help="Path to the music bed file.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print prompts and narration; make no API calls.")
    args = parser.parse_args()

    try:
        result = pipeline.run(
            root=args.root,
            only_scene=args.only_scene,
            skip_video=args.skip_video,
            skip_vo=args.skip_vo,
            tts_engine=args.tts,
            music_file=args.music,
            dry_run=args.dry_run,
        )
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if result:
        print(f"\nAll done. Output: {result}")


if __name__ == "__main__":
    main()
