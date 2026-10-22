#!/usr/bin/env python3
"""
60-second Urdu talking-character short.

Veo 3.1 makes 8s clips, so this generates 8 talking segments (each with one
Urdu line, spoken + lip-synced by Veo) and stitches them into one ~60s video.

Examples:
    python talk.py --dry-run                 # print prompts, spend nothing
    python talk.py --only-segment 1          # render just segment 1 (cheap test)
    python talk.py                           # full 60s build
    python talk.py --skip-video --music "music/bed.mp3"   # re-stitch only
"""

import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from generator import talking_config as tcfg
from generator import veo_client, ffmerge, imagegen


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description="Generate the 60s Urdu talking short.")
    p.add_argument("--root", default=here)
    p.add_argument("--only-segment", type=int, default=None,
                   help="Render just this segment id (1-8) for a cheap test.")
    p.add_argument("--skip-video", action="store_true",
                   help="Reuse existing clips in talking_clips/ (no Veo calls).")
    p.add_argument("--music", default=None, help="Optional quiet music bed file.")
    p.add_argument("--no-image", action="store_true",
                   help="Skip the reference portrait (text-to-video only).")
    p.add_argument("--new-portrait", action="store_true",
                   help="Regenerate the reference portrait even if one exists.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print prompts only; no API calls.")
    args = p.parse_args()

    clips_dir = os.path.join(args.root, "talking_clips")
    out_dir = os.path.join(args.root, "output")
    os.makedirs(clips_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # --- Reference portrait: one realistic face used for every clip --------- #
    image_path = None
    if tcfg.USE_IMAGE_REFERENCE and not args.no_image and not args.dry_run:
        portrait = os.path.join(args.root, tcfg.PORTRAIT_FILE)
        os.makedirs(os.path.dirname(portrait), exist_ok=True)
        if args.new_portrait or not os.path.exists(portrait):
            print(f"Generating reference portrait ({tcfg.IMAGE_MODEL}) ...")
            try:
                imagegen.generate_portrait(
                    tcfg.CHARACTER_PORTRAIT_PROMPT, portrait, model=tcfg.IMAGE_MODEL
                )
            except Exception as e:
                print(f"  ! portrait generation failed ({e}); "
                      f"continuing without a reference image.")
                portrait = None
        else:
            print(f"Using existing portrait: {portrait}")
        image_path = portrait if portrait and os.path.exists(portrait) else None

    segments = tcfg.SEGMENTS
    if args.only_segment:
        segments = [s for s in segments if s["id"] == args.only_segment]
        if not segments:
            print(f"No segment with id {args.only_segment}")
            sys.exit(1)

    clip_paths = []
    try:
        for seg in segments:
            sid = seg["id"]
            cpath = os.path.join(clips_dir, f"seg_{sid}.mp4")
            clip_paths.append(cpath)
            prompt = tcfg.segment_prompt(seg)

            if args.dry_run:
                print(f"\n[DRY RUN] Segment {sid} prompt:\n{prompt}")
                continue
            if args.skip_video and os.path.exists(cpath):
                print(f"Segment {sid}: reusing {cpath}")
                continue
            print(f"Segment {sid}: generating talking clip ...")
            veo_client.generate_scene(prompt, cpath, image_path=image_path)

        if args.dry_run:
            print("\n[DRY RUN] No API calls made.")
            return
        if args.only_segment:
            print(f"\nDone. Clip: {clip_paths[0]} — check it, then run `python talk.py`.")
            return

        # Need all 8 clips present to assemble the full video.
        all_paths = [os.path.join(clips_dir, f"seg_{s['id']}.mp4")
                     for s in tcfg.SEGMENTS]
        missing = [p for p in all_paths if not os.path.exists(p)]
        if missing:
            print(f"ERROR: missing clips: {missing}", file=sys.stderr)
            sys.exit(1)

        music = args.music
        if not music:
            music_dir = os.path.join(args.root, "music")
            if os.path.isdir(music_dir):
                cands = [os.path.join(music_dir, f) for f in sorted(os.listdir(music_dir))
                         if f.lower().endswith((".mp3", ".wav", ".m4a", ".aac"))]
                music = cands[0] if cands else None

        out_path = os.path.join(out_dir, "urdu_talk_final.mp4")
        ffmerge.assemble_talking(
            all_paths, out_path, music_path=music,
            max_seconds=tcfg.TARGET_SECONDS, music_gain=tcfg.TALKING_MUSIC_GAIN,
        )
        print(f"\nAll done. Output: {out_path}")
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
