#!/usr/bin/env python3
"""
60-second Urdu FUNNY talking-toddler short — 8 varied scenes, auto title,
optional YouTube upload.

Veo 3.1 makes 8s clips, so this generates 8 talking segments (each a different
place + funny Urdu line) and stitches them into one ~60s video. The output file
is named after an auto-generated title based on the video's content.

Examples:
    python talk.py --dry-run                   # print prompts, spend nothing
    python talk.py --only-segment 2            # render one clip (cheap test)
    python talk.py                             # full build -> output/<title>.mp4
    python talk.py --upload                    # build, then upload (private)
    python talk.py --upload --privacy public   # build, then upload public
    python talk.py --skip-video --upload       # re-stitch existing clips + upload
"""

import argparse
import os
import re
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from generator import talking_config as tcfg
from generator import veo_client, ffmerge, imagegen, titlegen


def safe_filename(title, fallback="funny-baby-short"):
    """Turn a title into a safe file name (keeps Urdu/English, drops emoji/symbols)."""
    name = re.sub(r"#\w+", "", title)                 # drop hashtags
    name = re.sub(r"[^\w \-]", "", name, flags=re.UNICODE).strip()
    name = re.sub(r"\s+", " ", name)[:80].strip()
    return name or fallback


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description="Generate the 60s Urdu funny toddler short.")
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
    p.add_argument("--no-auto-title", action="store_true",
                   help="Use the fallback title in config instead of generating one.")
    p.add_argument("--upload", action="store_true",
                   help="Upload the finished video to YouTube.")
    p.add_argument("--privacy", choices=["private", "unlisted", "public"],
                   default=tcfg.YT_PRIVACY, help="YouTube privacy (default: config).")
    p.add_argument("--dry-run", action="store_true",
                   help="Print prompts only; no API calls.")
    args = p.parse_args()

    clips_dir = os.path.join(args.root, "talking_clips")
    out_dir = os.path.join(args.root, "output")
    os.makedirs(clips_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # --- Optional reference portrait (off by default, for variety) ---------- #
    image_path = None
    if tcfg.USE_IMAGE_REFERENCE and not args.no_image and not args.dry_run:
        portrait = os.path.join(args.root, tcfg.PORTRAIT_FILE)
        os.makedirs(os.path.dirname(portrait), exist_ok=True)
        if args.new_portrait or not os.path.exists(portrait):
            print(f"Generating reference portrait ({tcfg.IMAGE_MODEL}) ...")
            try:
                imagegen.generate_portrait(
                    tcfg.CHARACTER_PORTRAIT_PROMPT, portrait, model=tcfg.IMAGE_MODEL)
            except Exception as e:
                print(f"  ! portrait generation failed ({e}); continuing without it.")
                portrait = None
        image_path = portrait if portrait and os.path.exists(portrait) else None

    segments = tcfg.SEGMENTS
    if args.only_segment:
        segments = [s for s in segments if s["id"] == args.only_segment]
        if not segments:
            print(f"No segment with id {args.only_segment}")
            sys.exit(1)

    try:
        # --- 1. Generate clips --------------------------------------------- #
        for seg in segments:
            sid = seg["id"]
            cpath = os.path.join(clips_dir, f"seg_{sid}.mp4")
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
            print(f"\nDone. Clip: talking_clips/seg_{args.only_segment}.mp4 — "
                  f"check it, then run `python talk.py`.")
            return

        # --- 2. Title / metadata ------------------------------------------- #
        title = tcfg.VIDEO_TITLE
        description = tcfg.VIDEO_DESCRIPTION
        tags = tcfg.VIDEO_TAGS
        if tcfg.AUTO_TITLE and not args.no_auto_title:
            print("Generating a title from the video's content ...")
            try:
                meta = titlegen.generate_metadata(tcfg.SEGMENTS, model=tcfg.TEXT_MODEL)
                title = meta["title"]
                description = meta["description"] or description
                tags = meta["tags"] or tags
                print(f"  ✓ title: {title}")
            except Exception as e:
                print(f"  ! title generation failed ({e}); using the default title.")

        # --- 3. Assemble --------------------------------------------------- #
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

        out_path = os.path.join(out_dir, safe_filename(title) + ".mp4")
        ffmerge.assemble_talking(
            all_paths, out_path, music_path=music,
            max_seconds=tcfg.TARGET_SECONDS, music_gain=tcfg.TALKING_MUSIC_GAIN)
        print(f"\nVideo ready: {out_path}")

        # --- 4. Upload ----------------------------------------------------- #
        if args.upload:
            from generator import youtube_upload
            desc = description if "#Shorts" in description else description + " #Shorts"
            youtube_upload.upload(
                out_path, title, desc, tags, root=args.root,
                privacy=args.privacy, category_id=tcfg.YT_CATEGORY)
        else:
            print("(Add --upload to publish this to YouTube.)")

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
