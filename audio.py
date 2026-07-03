from pydub import AudioSegment
import os

CROSSFADE_MS = 800

def normalize(seg: AudioSegment, target_dbfs: float = -20.0) -> AudioSegment:
    change = target_dbfs - seg.dBFS
    return seg.apply_gain(change)

def load(path: str) -> AudioSegment | None:
    if path and os.path.exists(path):
        return AudioSegment.from_file(path)
    return None

def assemble_episode(
    raw_path: str,
    intro_path: str | None,
    outro_path: str | None,
    sponsor_path: str | None,
    output_path: str,
) -> tuple[float, int]:
    raw = normalize(AudioSegment.from_file(raw_path))
    intro = load(intro_path)
    outro = load(outro_path)
    sponsor = load(sponsor_path)

    if intro:
        intro = normalize(intro)

    if outro:
        outro = normalize(outro)

    if sponsor:
        sponsor = normalize(sponsor)
        midpoint = len(raw) // 2
        raw = raw[:midpoint] + sponsor + raw[midpoint:]

    parts = [p for p in [intro, raw, outro] if p is not None]

    final = parts[0]
    for part in parts[1:]:
        fade = min(CROSSFADE_MS, len(final), len(part))
        final = final.append(part, crossfade=fade)

    final = final.set_frame_rate(44100).set_channels(2)
    final.export(output_path, format="mp3", bitrate="192k")

    duration_seconds = len(final) / 1000.0
    file_size = os.path.getsize(output_path)
    return duration_seconds, file_size
