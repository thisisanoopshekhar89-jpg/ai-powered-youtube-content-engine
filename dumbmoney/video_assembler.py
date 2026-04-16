import os
import subprocess
import requests
import struct
import wave
import random
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

STAGE_IMG  = Path(r"C:\Users\ASUS\whattheworld\assets\stage\stage_background_916.png")
BULL_DIR   = Path(r"C:\Users\ASUS\whattheworld\assets\characters\bull\bull_v2")
BEAR_DIR   = Path(r"C:\Users\ASUS\whattheworld\assets\characters\bear\bear_v2")
OUTPUT_DIR = Path(r"C:\Users\ASUS\whattheworld\output\full_scene")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FPS         = 24
WIDTH       = 1080
HEIGHT      = 1920
BULL_H      = int(HEIGHT * 0.40)
BEAR_H      = int(HEIGHT * 0.40)
BULL_X      = "W*0.03"
BULL_Y      = "(H-h)*0.68"
BEAR_X      = "W*0.48"
BEAR_Y      = "(H-h)*0.68"
STAGE_CROP  = 80

THRESH_OPEN = 800
THRESH_WIDE = 2000
THRESH_LOUD = 5000

APPROVED = {
    "adbhuta", "arms_crossed", "bhayanaka", "exaggerated_laugh",
    "excited_arms_up", "facepalm", "hasya", "karuna", "mic_drop",
    "mouth_closed", "mouth_half", "mouth_open", "neutral", "pointing",
    "raudra", "shanta", "shringara", "smug", "thinking", "vira"
}

BULL_IDLE_POOL     = ["shanta", "smug", "thinking", "shringara"]
BEAR_IDLE_POOL     = ["neutral", "arms_crossed", "thinking", "shanta"]
BULL_REACTION_POOL = ["adbhuta", "bhayanaka", "facepalm"]
BEAR_REACTION_POOL = ["smug", "adbhuta", "arms_crossed"]
BLINK_FRAMES       = [("neutral", 2), ("neutral", 2), ("neutral", 2)]

VOICES = {
    "BULL":      {"id": "knQkMIFmYkJlzJUlOm2V", "stability": 0.40, "similarity_boost": 0.85, "style": 0.60},
    "BEAR":      {"id": "HqxxwYOPFQpV9Ci1kok7", "stability": 0.80, "similarity_boost": 0.90, "style": 0.15},
    "ANNOUNCER": {"id": "NZvlub2kymSacYmGIL4J", "stability": 0.75, "similarity_boost": 0.85, "style": 0.20},
}

SCENE = [
    {"character": "BULL", "expression": "excited_arms_up",   "dialogue": "The market dropped TWO percent today. And I am HERE for it!"},
    {"character": "BULL", "expression": "vira",              "dialogue": "This is a HEALTHY correction. Buy. The. Dip."},
    {"character": "BEAR", "expression": "neutral",           "dialogue": "Consumer debt is at four point two trillion dollars."},
    {"character": "BEAR", "expression": "pointing",          "dialogue": "That is not a correction. That is a warning."},
    {"character": "BULL", "expression": "adbhuta",           "dialogue": "Wait... FOUR POINT TWO trillion?"},
    {"character": "BULL", "expression": "thinking",          "dialogue": "BUT... this is actually GREAT for the market."},
    {"character": "BEAR", "expression": "arms_crossed",      "dialogue": "No. It is not."},
    {"character": "BEAR", "expression": "smug",              "dialogue": "And yet... here we are. Again."},
    {"character": "BULL", "expression": "exaggerated_laugh", "dialogue": "I cannot be stopped!"},
    {"character": "BEAR", "expression": "smug",              "dialogue": "You will be stopped. I have the data."},
    {"character": "BEAR", "expression": "neutral",           "dialogue": "Like. And subscribe. Bear does not ask twice."},
]


def run(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ❌ {label}: {r.stderr[-200:]}")
        return False
    return True


def get_duration(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path)
    ], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 2.0


def generate_voice(character, text, path):
    v = VOICES.get(character, VOICES["BULL"])
    url     = f"https://api.elevenlabs.io/v1/text-to-speech/{v['id']}"
    headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
    data    = {
        "text":     text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability":         v["stability"],
            "similarity_boost":  v["similarity_boost"],
            "style":             v["style"],
            "use_speaker_boost": True
        }
    }
    r = requests.post(url, json=data, headers=headers)
    if r.status_code != 200:
        print(f"  ❌ Voice: {r.text[:150]}")
        return False
    with open(path, "wb") as f:
        f.write(r.content)
    return True


def mp3_to_wav(mp3_path, wav_path):
    return run(["ffmpeg", "-y", "-i", str(mp3_path), str(wav_path)], "mp3_to_wav")


def get_amplitude_per_frame(wav_path, duration, fps=24):
    try:
        with wave.open(str(wav_path), 'r') as wf:
            n_channels = wf.getnchannels()
            sampwidth  = wf.getsampwidth()
            framerate  = wf.getframerate()
            n_frames   = wf.getnframes()
            raw        = wf.readframes(n_frames)

        fmt     = f"{n_frames * n_channels}h" if sampwidth == 2 else f"{n_frames * n_channels}b"
        samples = struct.unpack(fmt, raw)

        if n_channels == 2:
            samples = [abs(samples[i] + samples[i+1]) // 2
                      for i in range(0, len(samples), 2)]
        else:
            samples = [abs(s) for s in samples]

        spf     = framerate / fps
        total_f = int(duration * fps)
        return [max(samples[int(f*spf):int((f+1)*spf)] or [0]) for f in range(total_f)]

    except Exception as e:
        print(f"  ⚠️  Amplitude: {e}")
        return None


def get_png(character, name):
    d          = BULL_DIR if character == "BULL" else BEAR_DIR
    name_clean = name.lower().strip().replace(" ", "_")

    if name_clean in APPROVED:
        p = d / f"{name_clean}.png"
        if p.exists():
            return p

    for f in d.glob("*.png"):
        if f.stem.lower() == name_clean and f.stem.lower() in APPROVED:
            return f

    # Fallback to neutral
    p = d / "neutral.png"
    if p.exists():
        return p

    files = list(d.glob("*.png"))
    return files[0] if files else None


def composite_both(bull_expr, bear_expr, out_path):
    bull_png = get_png("BULL", bull_expr)
    bear_png = get_png("BEAR", bear_expr)
    if not bull_png or not bear_png:
        return False
    cmd = [
        "ffmpeg", "-y",
        "-i", str(STAGE_IMG),
        "-i", str(bull_png),
        "-i", str(bear_png),
        "-filter_complex",
        f"[1:v]scale=-1:{BULL_H}[bull];"
        f"[2:v]scale=-1:{BEAR_H}[bear];"
        f"[0:v]scale={WIDTH}:{HEIGHT},"
        f"crop={WIDTH}:{HEIGHT-STAGE_CROP}:0:0,"
        f"pad={WIDTH}:{HEIGHT}:0:0:color=black[bg];"
        f"[bg][bull]overlay={BULL_X}:{BULL_Y}[s1];"
        f"[s1][bear]overlay={BEAR_X}:{BEAR_Y}",
        "-frames:v", "1", "-q:v", "2",
        str(out_path)
    ]
    return run(cmd, "composite")


def frame_clip(frame_path, n_frames, out_path):
    duration = max(n_frames / FPS, 0.1)
    return run([
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(FPS),
        "-i", str(frame_path),
        "-c:v", "libx264", "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
        "-r", str(FPS),
        str(out_path)
    ], "frame_clip")


def get_comp(b_expr, r_expr, comp_cache, work_dir):
    key = f"{b_expr}__{r_expr}"
    if key not in comp_cache:
        p = work_dir / f"comp_{key[:60]}.jpg"
        if composite_both(b_expr, r_expr, p):
            comp_cache[key] = p
    return comp_cache.get(key)


def safe_expr(expr):
    return expr if expr in APPROVED else "neutral"


def build_beat(beat, audio_path, duration, out_path, comp_cache, work_dir):
    character  = beat["character"]
    expression = safe_expr(beat["expression"])
    total_f    = int(duration * FPS)
    is_bull    = character == "BULL"

    idle_expr     = safe_expr(random.choice(BULL_IDLE_POOL if not is_bull else BEAR_IDLE_POOL))
    reaction_expr = safe_expr(random.choice(BULL_REACTION_POOL if is_bull else BEAR_REACTION_POOL))

    # Pre-composite all needed frames
    needed_speaker = [expression, "mouth_open", "mouth_half", "mouth_closed", "neutral"]
    needed_idle    = [idle_expr, reaction_expr, "neutral"]

    if is_bull:
        for e in needed_speaker:
            get_comp(safe_expr(e), idle_expr, comp_cache, work_dir)
        for e in needed_idle:
            get_comp(expression, safe_expr(e), comp_cache, work_dir)
    else:
        for e in needed_speaker:
            get_comp(idle_expr, safe_expr(e), comp_cache, work_dir)
        for e in needed_idle:
            get_comp(safe_expr(e), expression, comp_cache, work_dir)

    # Copy audio locally
    local_audio = work_dir / f"audio_{out_path.stem}.mp3"
    if not local_audio.exists():
        shutil.copy(str(audio_path), str(local_audio))

    wav_path = work_dir / f"temp_{out_path.stem}.wav"
    mp3_to_wav(local_audio, wav_path)
    amplitudes = get_amplitude_per_frame(wav_path, duration, FPS)

    def amp_to_speaker(f_idx, amp):
        if f_idx < int(0.1 * FPS):
            return expression
        if amp is None or amp < THRESH_OPEN:
            return expression
        elif amp < THRESH_WIDE:
            return "mouth_half"
        else:
            return "mouth_open"

    blink_at1     = total_f // 3
    blink_at2     = (total_f * 2) // 3
    blink_count   = 0
    reaction_done = False
    reaction_at   = total_f // 2

    if amplitudes:
        max_amp = max(amplitudes)
        if max_amp > THRESH_LOUD:
            reaction_at = amplitudes.index(max_amp)

    seq       = []
    prev_comp = None
    count     = 0
    frames    = amplitudes if amplitudes else [0] * total_f

    for f_idx in range(total_f):
        amp = frames[f_idx] if f_idx < len(frames) else 0

        # Blink 1
        if blink_count == 0 and f_idx >= blink_at1 and amp < THRESH_OPEN:
            if prev_comp and count > 0:
                seq.append((prev_comp, count))
                prev_comp = None
                count     = 0
            for bn, bf in BLINK_FRAMES:
                c = get_comp(expression, bn, comp_cache, work_dir) if is_bull \
                    else get_comp(bn, expression, comp_cache, work_dir)
                if c:
                    seq.append((c, bf))
            blink_count += 1
            continue

        # Reaction flash at peak
        if not reaction_done and f_idx >= reaction_at and amp > THRESH_WIDE:
            if prev_comp and count > 0:
                seq.append((prev_comp, count))
                prev_comp = None
                count     = 0
            c = get_comp(expression, reaction_expr, comp_cache, work_dir) if is_bull \
                else get_comp(reaction_expr, expression, comp_cache, work_dir)
            if c:
                seq.append((c, 3))
            reaction_done = True
            continue

        # Blink 2
        if blink_count == 1 and f_idx >= blink_at2 and amp < THRESH_OPEN:
            if prev_comp and count > 0:
                seq.append((prev_comp, count))
                prev_comp = None
                count     = 0
            for bn, bf in BLINK_FRAMES:
                c = get_comp(expression, bn, comp_cache, work_dir) if is_bull \
                    else get_comp(bn, expression, comp_cache, work_dir)
                if c:
                    seq.append((c, bf))
            blink_count += 1
            continue

        # Normal frame
        spk = amp_to_speaker(f_idx, amp)
        c   = get_comp(safe_expr(spk), idle_expr, comp_cache, work_dir) if is_bull \
              else get_comp(idle_expr, safe_expr(spk), comp_cache, work_dir)
        if not c:
            continue

        if c == prev_comp:
            count += 1
        else:
            if prev_comp and count > 0:
                seq.append((prev_comp, count))
            prev_comp = c
            count     = 1

    if prev_comp and count > 0:
        seq.append((prev_comp, count))

    if not seq:
        return False

    clips_dir = work_dir / f"clips_{out_path.stem}"
    clips_dir.mkdir(exist_ok=True)
    clip_files = []

    for ci, (frame_p, fcount) in enumerate(seq):
        if fcount < 1:
            continue
        cp = clips_dir / f"c{ci:03d}.mp4"
        if frame_clip(frame_p, fcount, cp):
            clip_files.append(cp)

    if not clip_files:
        return False

    silent = work_dir / f"silent_{out_path.stem}.mp4"
    lst    = work_dir / f"lst_{out_path.stem}.txt"
    with open(lst, "w") as f:
        for c in clip_files:
            f.write(f"file '{c}'\n")
    if not run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(lst), "-c", "copy", str(silent)], "concat"):
        return False

    return run([
        "ffmpeg", "-y",
        "-i", str(silent),
        "-i", str(local_audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-af", "aresample=44100,volume=1.0",
        "-shortest",
        str(out_path)
    ], "mux")


def main():
    print("\n🎭 THE DUMB MONEY CLUB")
    print("Bull + Bear — v2 characters")
    print("=" * 50)

    if not STAGE_IMG.exists():
        print(f"❌ Stage not found: {STAGE_IMG}")
        return

    bull_count = len(list(BULL_DIR.glob("*.png")))
    bear_count = len(list(BEAR_DIR.glob("*.png")))
    print(f"🐂 Bull PNGs: {bull_count} | 🐻 Bear PNGs: {bear_count}")

    if bull_count == 0 or bear_count == 0:
        print("❌ Missing character PNGs")
        return

    work_dir  = OUTPUT_DIR / "work"
    beats_dir = OUTPUT_DIR / "beats"
    audio_dir = OUTPUT_DIR / "audio"
    work_dir.mkdir(exist_ok=True)
    beats_dir.mkdir(exist_ok=True)
    audio_dir.mkdir(exist_ok=True)

    comp_cache  = {}
    beat_videos = []

    for i, beat in enumerate(SCENE):
        char     = beat["character"]
        expr     = beat.get("expression", "neutral")
        dialogue = beat.get("dialogue", "")

        print(f"\n[{i+1:02d}] {char} [{expr}]")
        print(f"     \"{dialogue[:65]}\"")

        preset     = beat.get("audio_file", "")
        audio_path = audio_dir / f"beat_{i:02d}.mp3"

        if preset and Path(preset).exists() and not audio_path.exists():
            shutil.copy(preset, audio_path)
            print(f"  🎙️  Audio copied")
        elif not audio_path.exists():
            print(f"  🎙️  Generating voice...")
            if not generate_voice(char, dialogue, audio_path):
                continue
        else:
            print(f"  🎙️  Reusing audio")

        if not audio_path.exists():
            continue

        dur = get_duration(audio_path)
        print(f"  ⏱️  {dur:.1f}s")

        beat_path = beats_dir / f"beat_{i:02d}.mp4"
        beat_data = {"character": char, "expression": expr, "dialogue": dialogue}

        if build_beat(beat_data, audio_path, dur, beat_path, comp_cache, work_dir):
            beat_videos.append(beat_path)
            print(f"  ✅ Done")
        else:
            print(f"  ❌ Failed")

    if not beat_videos:
        print("\n❌ Nothing generated")
        return

    print(f"\n🔗 Assembling {len(beat_videos)} beats...")
    final = OUTPUT_DIR / "dmc_bull_bear.mp4"
    lst   = OUTPUT_DIR / "final.txt"
    with open(lst, "w") as f:
        for v in beat_videos:
            f.write(f"file '{v}'\n")

    if run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(lst), "-c", "copy", str(final)], "final"):
        size_mb = final.stat().st_size / 1024 / 1024
        print(f"\n✅ COMPLETE")
        print(f"📹 {final}")
        print(f"   {size_mb:.1f} MB")


if __name__ == "__main__":
    main()