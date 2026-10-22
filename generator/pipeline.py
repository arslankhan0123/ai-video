"""
Orchestrates the whole thing: generate clips -> narration -> assemble.

Folder layout created under the project root:
    clips/     scene_1.mp4 ... scene_8.mp4   (from Veo)
    vo/        vo_1.mp3     ... vo_8.mp3      (narration)
    sfx/       your sound-effect files
    music/     your music track(s)
    output/    hidden_world_final.mp4
"""

import os

from . import config, veo_client, tts, assemble


def _ensure_dirs(root):
    paths = {
        "clips": os.path.join(root, "clips"),
        "vo": os.path.join(root, "vo"),
        "sfx": os.path.join(root, "sfx"),
        "music": os.path.join(root, "music"),
        "output": os.path.join(root, "output"),
    }
    for p in paths.values():
        os.makedirs(p, exist_ok=True)
    return paths


def run(root, only_scene=None, skip_video=False, skip_vo=False,
        tts_engine=None, music_file=None, dry_run=False):
    paths = _ensure_dirs(root)

    scenes = config.SCENES
    if only_scene:
        scenes = [s for s in scenes if s["id"] == only_scene]
        if not scenes:
            raise ValueError(f"No scene with id {only_scene}")

    video_paths, vo_paths = {}, {}

    # ----- 1. Video clips (Veo 3) ----------------------------------------- #
    for scene in scenes:
        sid = scene["id"]
        vpath = os.path.join(paths["clips"], f"scene_{sid}.mp4")
        video_paths[sid] = vpath
        prompt = config.full_prompt(scene)

        if dry_run:
            print(f"[DRY RUN] Scene {sid} Veo prompt:\n{prompt}\n")
            continue
        if skip_video and os.path.exists(vpath):
            print(f"Scene {sid}: reusing existing {vpath}")
            continue
        print(f"Scene {sid}: generating video ...")
        veo_client.generate_scene(prompt, vpath)

    # ----- 2. Narration (TTS) --------------------------------------------- #
    for scene in scenes:
        sid = scene["id"]
        opath = os.path.join(paths["vo"], f"vo_{sid}.mp3")
        vo_paths[sid] = opath
        text = scene["narration"]

        if dry_run:
            print(f"[DRY RUN] Scene {sid} narration: {text}")
            continue
        if skip_vo and os.path.exists(opath):
            print(f"Scene {sid}: reusing existing {opath}")
            continue
        print(f"Scene {sid}: synthesizing narration ...")
        tts.synthesize(text, opath, engine=tts_engine)

    if dry_run:
        print("\n[DRY RUN] No API calls made, no files generated. "
              "Remove --dry-run to produce the video.")
        return None

    if only_scene:
        print(f"\nDone with scene {only_scene}. "
              f"Clip: {video_paths[only_scene]}")
        print("Run without --only-scene to build the full video.")
        return video_paths[only_scene]

    # ----- 3. Assemble ----------------------------------------------------- #
    music_path = music_file
    if not music_path:
        # pick the first file in music/ if present
        music_dir = paths["music"]
        candidates = [os.path.join(music_dir, f) for f in sorted(os.listdir(music_dir))
                      if f.lower().endswith((".mp3", ".wav", ".m4a", ".aac"))]
        music_path = candidates[0] if candidates else None
    if not music_path:
        print("Note: no music file found in music/ — exporting without a music bed.")

    out_path = os.path.join(paths["output"], "hidden_world_final.mp4")
    assemble.assemble(video_paths, vo_paths, paths["sfx"], music_path, out_path)
    return out_path
