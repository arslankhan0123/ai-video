"""
Final assembly with MoviePy (ffmpeg under the hood).

For each scene we:
  - load the Veo clip and lower its ambient audio,
  - lay the narrator line on top,
  - optionally drop an SFX accent.
Then we concatenate all scenes and mix a music bed across the whole thing,
and export a vertical 1080x1920 mp4.

Requires:
    pip install "moviepy>=2.1,<3"
    ffmpeg installed and on PATH.
"""

import os

from . import config


def _import_moviepy():
    try:
        from moviepy import (  # noqa
            VideoFileClip, AudioFileClip, CompositeAudioClip,
            concatenate_videoclips,
        )
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            'MoviePy 2.x is required. Run: pip install "moviepy>=2.1,<3" '
            "and make sure ffmpeg is installed."
        ) from e
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips,
    )
    return VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips


def _scaled(clip, gain):
    """Volume-scale an audio/video clip across MoviePy 2.x variants."""
    if hasattr(clip, "with_volume_scaled"):
        return clip.with_volume_scaled(gain)
    # fallback for older naming
    return clip.volumex(gain)  # type: ignore[attr-defined]


def build_scene_clip(scene, video_path, vo_path, sfx_dir):
    """Return a MoviePy video clip for one scene with its audio mixed in."""
    (VideoFileClip, AudioFileClip, CompositeAudioClip, _concat) = _import_moviepy()

    video = VideoFileClip(video_path)

    audio_layers = []
    # 1) Veo's own ambient audio, quietened (may be absent on some clips).
    if video.audio is not None:
        audio_layers.append(_scaled(video.audio, config.AMBIENT_GAIN))

    # 2) Narrator line for this scene.
    if vo_path and os.path.exists(vo_path):
        vo = _scaled(AudioFileClip(vo_path), config.NARRATION_GAIN)
        audio_layers.append(vo)

    # 3) Optional SFX accent at a given offset.
    sfx_name = scene.get("sfx")
    if sfx_name:
        sfx_path = os.path.join(sfx_dir, sfx_name)
        if os.path.exists(sfx_path):
            sfx = _scaled(AudioFileClip(sfx_path), config.SFX_GAIN)
            sfx = sfx.with_start(scene.get("sfx_at", 0))
            audio_layers.append(sfx)

    if audio_layers:
        mixed = CompositeAudioClip(audio_layers)
        video = video.with_audio(mixed)
    return video


def assemble(video_paths, vo_paths, sfx_dir, music_path, out_path):
    """
    video_paths : dict {scene_id: path}
    vo_paths    : dict {scene_id: path or None}
    """
    (VideoFileClip, AudioFileClip, CompositeAudioClip,
     concatenate_videoclips) = _import_moviepy()

    clips = []
    for scene in config.SCENES:
        sid = scene["id"]
        vpath = video_paths.get(sid)
        if not vpath or not os.path.exists(vpath):
            raise FileNotFoundError(f"Missing video for scene {sid}: {vpath}")
        clips.append(build_scene_clip(scene, vpath, vo_paths.get(sid), sfx_dir))

    print("  → concatenating scenes ...")
    final = concatenate_videoclips(clips, method="compose")

    # Music bed across the whole video, if provided.
    if music_path and os.path.exists(music_path):
        print("  → adding music bed ...")
        music = AudioFileClip(music_path)
        # Trim music to the video length.
        if music.duration > final.duration:
            music = music.subclipped(0, final.duration)
        music = _scaled(music, config.MUSIC_GAIN)
        base = final.audio
        if base is not None:
            final = final.with_audio(CompositeAudioClip([base, music]))
        else:
            final = final.with_audio(music)

    print(f"  → exporting {out_path} (this takes a while) ...")
    final.write_videofile(
        out_path,
        fps=config.FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )
    print(f"  ✓ final video → {out_path}")
    return out_path


def assemble_talking(clip_paths, out_path, music_path=None,
                     max_seconds=60, music_gain=0.06):
    """
    Concatenate talking-character clips KEEPING their native audio (the spoken
    Urdu), trim to `max_seconds`, optionally lay a very quiet music bed, export.
    """
    (VideoFileClip, AudioFileClip, CompositeAudioClip,
     concatenate_videoclips) = _import_moviepy()

    clips = [VideoFileClip(p) for p in clip_paths]  # audio kept by default
    print("  → concatenating talking segments ...")
    final = concatenate_videoclips(clips, method="compose")

    if final.duration > max_seconds:
        final = final.subclipped(0, max_seconds)

    if music_path and os.path.exists(music_path):
        print("  → adding quiet music bed under the voice ...")
        music = AudioFileClip(music_path)
        if music.duration > final.duration:
            music = music.subclipped(0, final.duration)
        music = _scaled(music, music_gain)
        base = final.audio
        final = final.with_audio(
            CompositeAudioClip([base, music]) if base is not None else music
        )

    print(f"  → exporting {out_path} ...")
    final.write_videofile(
        out_path,
        fps=config.FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )
    print(f"  ✓ final video → {out_path}")
    return out_path
