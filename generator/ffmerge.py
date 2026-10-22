"""
Robust video stitching using ffmpeg directly (no MoviePy).

Why: Veo clips can differ slightly in size/SAR/fps, and composing those in
MoviePy produces glitchy merges. Here every clip is first normalized to the
exact same format, then concatenated with the ffmpeg concat demuxer, which is
the reliable, standard way to join clips cleanly.

Requires ffmpeg + ffprobe on PATH.
"""

import os
import subprocess
import tempfile


def _run(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed:\n" + " ".join(cmd) + "\n" + proc.stderr[-2000:]
        )
    return proc


def _has_audio(path):
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return bool(proc.stdout.strip())


def normalize_clip(src, dst, w=1080, h=1920, fps=30):
    """Re-encode one clip to a uniform format, padding to WxH and ensuring audio."""
    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
    )
    if _has_audio(src):
        cmd = [
            "ffmpeg", "-y", "-i", src, "-vf", vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            dst,
        ]
    else:
        # Clip has no audio track — add silent stereo so concat stays in sync.
        cmd = [
            "ffmpeg", "-y", "-i", src,
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            dst,
        ]
    _run(cmd)
    return dst


def _concat(norm_paths, dst):
    listfile = dst + ".txt"
    with open(listfile, "w", encoding="utf-8") as f:
        for p in norm_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    try:
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
              "-i", listfile, "-c", "copy", dst])
    finally:
        if os.path.exists(listfile):
            os.remove(listfile)
    return dst


def _trim(src, dst, seconds):
    _run([
        "ffmpeg", "-y", "-i", src, "-t", str(seconds),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", dst,
    ])
    return dst


def _add_music(video, music, dst, gain=0.06):
    _run([
        "ffmpeg", "-y", "-i", video, "-stream_loop", "-1", "-i", music,
        "-filter_complex",
        f"[1:a]volume={gain}[m];"
        f"[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-shortest", dst,
    ])
    return dst


def assemble_talking(clip_paths, out_path, music_path=None,
                     max_seconds=60, music_gain=0.06, fps=30):
    """
    Normalize -> concat -> trim -> (optional) quiet music bed. Keeps the clips'
    native audio (the spoken Urdu). Returns out_path.
    """
    for p in clip_paths:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing clip: {p}")

    with tempfile.TemporaryDirectory() as tmp:
        print("  → normalizing clips to 1080x1920 ...")
        norm = []
        for i, p in enumerate(clip_paths, 1):
            n = os.path.join(tmp, f"norm_{i:02d}.mp4")
            normalize_clip(p, n, fps=fps)
            norm.append(n)

        print("  → concatenating ...")
        joined = os.path.join(tmp, "joined.mp4")
        _concat(norm, joined)

        trimmed = os.path.join(tmp, "trimmed.mp4")
        _trim(joined, trimmed, max_seconds)

        if music_path and os.path.exists(music_path):
            print("  → adding quiet music bed under the voice ...")
            _add_music(trimmed, music_path, out_path, gain=music_gain)
        else:
            # move/copy trimmed to final
            _run(["ffmpeg", "-y", "-i", trimmed, "-c", "copy", out_path])

    print(f"  ✓ final video → {out_path}")
    return out_path
