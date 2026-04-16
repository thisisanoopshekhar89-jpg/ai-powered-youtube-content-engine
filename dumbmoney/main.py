# ============================================================
# THE DUMB MONEY CLUB — MASTER PIPELINE v33
# Bull argues. Bear corrects. Daily. Forever.
# python main.py
#
# v33:
# + Single CTA at end — Bear only on Story 5
# + Bull CTA removed from Story 5 (was doubling up)
# + Outro dialogue removed — jingle slide only, no talking
# + Result: Story 5 closer → Bear CTA → outro jingle. Clean.
# ============================================================

import os
import json
import shutil
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR      = Path(__file__).parent.parent
ASSETS        = BASE_DIR / "assets"
OUTPUT        = BASE_DIR / "output"
INTRO_VID     = ASSETS / "stage" / "introtoclub.mp4"
JINGLE        = ASSETS / "sounds" / "jingle.mp3"
JINGLE_OUTRO  = ASSETS / "sounds" / "jingleoutro.mp3"
MEMORY_FILE   = OUTPUT / "episode_memory.json"

EPISODE_DATE  = datetime.now().strftime('%Y%m%d')
EPISODE_DIR   = OUTPUT / "episodes" / EPISODE_DATE
EPISODE_DIR.mkdir(parents=True, exist_ok=True)

INTRO_MAX_DUR      = 12.0
ANNOUNCER_DELAY_MS = 2000

FIXED_ANNOUNCER = (
    "Ladies and gentlemen... The Dumb Money Club. "
    "Smart money. Stupid world. Let's go."
)


# ============================================================
# HELPERS
# ============================================================

def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {"episodes": data.get("episodes", [])}
        if isinstance(data, list):
            return {"episodes": data}
        return data
    return {"episodes": []}


def save_memory(memory, script):
    stories = script.get("stories", script.get("segments", []))
    bear_verdict = ""
    for story in stories:
        if story.get("id") == "the_closer":
            for beat in story.get("argument", []):
                if beat.get("character") == "BEAR" and beat.get("beat") == "THEREFORE":
                    bear_verdict = beat.get("dialogue", "")
            if not bear_verdict:
                bear_verdict = story.get("bear", {}).get("dialogue", "")

    episodes = memory.get("episodes", [])
    if isinstance(episodes, dict):
        episodes = list(episodes.values())

    episodes.append({
        "date":             EPISODE_DATE,
        "title":            script.get("title", ""),
        "episode_thread":   script.get("episode_thread", ""),
        "bull_wrong_about": script.get("episode_seed", "")[:150],
        "bear_verdict":     bear_verdict[:200],
        "btc_price":        None,
        "topics":           [s.get("id", "") for s in stories]
    })
    episodes = episodes[-30:]
    memory["episodes"] = episodes
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)
    print(f"  💾 Memory saved — {len(episodes)} episodes")


def ffmpeg(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ❌ {label}: {r.stderr[-400:]}")
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
        return 5.0


def check_audio(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries",
        "stream=codec_type", "-of", "csv=p=0", str(path)
    ], capture_output=True, text=True)
    return "audio" in r.stdout


def normalize(src, dst):
    return ffmpeg([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        str(dst)
    ], "normalize")


# ============================================================
# INTRO
# ============================================================

def build_intro(output_path, announcer_audio=None):
    if not INTRO_VID.exists():
        print(f"  ⚠️  Intro video not found: {INTRO_VID}")
        return False

    print("  🎬 Building intro...")
    use_dur = INTRO_MAX_DUR

    scaled = EPISODE_DIR / "intro_scaled.mp4"
    ok = ffmpeg([
        "ffmpeg", "-y",
        "-i", str(INTRO_VID),
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", "24", "-an",
        "-t", str(use_dur),
        str(scaled)
    ], "scale_intro")

    if not ok or not scaled.exists():
        print("  ❌ Could not scale intro")
        return False

    if announcer_audio and Path(announcer_audio).exists() and JINGLE.exists():
        ann_dur = get_duration(announcer_audio)
        print(f"  📢 Announcer: {ann_dur:.1f}s (starts at 2s)")

        ok = ffmpeg([
            "ffmpeg", "-y",
            "-i", str(scaled),
            "-stream_loop", "-1", "-i", str(JINGLE),
            "-i", str(announcer_audio),
            "-filter_complex",
            f"[1:a]aresample=44100,atrim=0:{use_dur},asetpts=PTS-STARTPTS,"
            f"volume='if(lt(t,2),0.5,0.15)':eval=frame[jingle];"
            f"[2:a]aresample=44100,adelay={ANNOUNCER_DELAY_MS}|{ANNOUNCER_DELAY_MS},"
            f"asetpts=PTS-STARTPTS,volume=0.9[ann];"
            f"[jingle][ann]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[a]",
            "-map", "0:v", "-map", "[a]",
            "-r", "24", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-t", str(use_dur),
            str(output_path)
        ], "intro_full")

    elif JINGLE.exists():
        ok = ffmpeg([
            "ffmpeg", "-y",
            "-i", str(scaled),
            "-stream_loop", "-1", "-i", str(JINGLE),
            "-filter_complex",
            f"[1:a]aresample=44100,atrim=0:{use_dur},asetpts=PTS-STARTPTS,volume=0.5[a]",
            "-map", "0:v", "-map", "[a]",
            "-r", "24", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-t", str(use_dur),
            str(output_path)
        ], "intro_jingle_only")
    else:
        shutil.copy(str(scaled), str(output_path))
        ok = True

    if ok and Path(output_path).exists():
        dur = get_duration(output_path)
        print(f"  ✅ Intro: {dur:.1f}s | Audio: {'✅' if check_audio(output_path) else '❌'}")
        return True

    print("  ❌ Intro failed")
    return False


# ============================================================
# OUTRO — jingle slide only, no talking
# ============================================================

def build_outro(output_path):
    print("  🎬 Building outro...")
    outro_audio = JINGLE_OUTRO if JINGLE_OUTRO.exists() else JINGLE

    if not outro_audio.exists():
        dur = 5.0
        return ffmpeg([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=black:size=1080x1920:duration={dur}:rate=24",
            "-vf", "drawtext=text='THE DUMB MONEY CLUB':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", "-t", str(dur),
            str(output_path)
        ], "outro_silent")

    dur = get_duration(outro_audio)
    print(f"  🎵 Outro: {dur:.1f}s — jingle + slide, no talking")

    ok = ffmpeg([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:size=1080x1920:duration={dur}:rate=24",
        "-i", str(outro_audio),
        "-filter_complex",
        f"[0:v]drawtext=text='THE DUMB MONEY CLUB':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-140,"
        f"drawtext=text='Smart Money. Stupid World.':fontsize=38:fontcolor=gray:x=(w-text_w)/2:y=(h-text_h)/2-50,"
        f"drawtext=text='New episode daily':fontsize=30:fontcolor=darkgray:x=(w-text_w)/2:y=(h-text_h)/2+20[v];"
        f"[1:a]aresample=44100,volume=0.85[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-t", str(dur), str(output_path)
    ], "outro_full")

    if ok and Path(output_path).exists():
        print(f"  ✅ Outro: {get_duration(output_path):.1f}s")
    return ok


def assemble_final(parts, output_path):
    valid = [p for p in parts if p and Path(p).exists()]
    if not valid:
        return False
    if len(valid) == 1:
        shutil.copy(valid[0], output_path)
        return True

    lst = EPISODE_DIR / "concat_final.txt"
    with open(lst, "w") as f:
        for p in valid:
            f.write(f"file '{p}'\n")

    return ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(lst),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        str(output_path)
    ], "final_concat")


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline():
    print()
    print("=" * 60)
    print("  THE DUMB MONEY CLUB — v33")
    print("  Bull argues. Bear corrects. Daily.")
    print(f"  {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 60)
    print()

    memory        = load_memory()
    past_episodes = memory.get("episodes", [])
    if isinstance(past_episodes, dict):
        past_episodes = list(past_episodes.values())

    print(f"📚 Memory: {len(past_episodes)} past episodes")
    if past_episodes:
        print(f"   Last: {past_episodes[-1].get('title','')[:50]}")
    print()

    # ── STEP 1: NEWS ───────────────────────────────────────────
    print("📰 STEP 1: Scanning news...")
    try:
        from news_scanner import scan_daily_news, pick_top_stories
        package = scan_daily_news()
        topics  = pick_top_stories(package)
        if not any(v for v in topics.values() if v):
            print("❌ No stories found")
            return None
        print(f"✅ {len([v for v in topics.values() if v])} stories ready\n")
    except Exception as e:
        print(f"❌ News: {e}")
        traceback.print_exc()
        return None

    # ── STEP 2: SCRIPT ─────────────────────────────────────────
    print("✍️  STEP 2: Writing script...")
    try:
        from script_writer import write_episode_script
        script = write_episode_script(
            topics,
            memory=past_episodes[-3:] if past_episodes else []
        )
        if not script:
            print("❌ Script failed")
            return None
        script_path = EPISODE_DIR / f"script_{EPISODE_DATE}.json"
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        print(f"✅ Script: {script.get('title','')[:60]}")
    except Exception as e:
        print(f"❌ Script: {e}")
        traceback.print_exc()
        return None

    # ── STEP 2b: THUMBNAILS ────────────────────────────────────
    print("\n🖼️  STEP 2b: Generating thumbnails...")
    thumbnails = {}
    try:
        from thumbnail_generator import generate_all_thumbnails
        thumbnails = generate_all_thumbnails(script, EPISODE_DATE)
        print(f"✅ {len(thumbnails)} thumbnails ready")
    except Exception as e:
        print(f"  ⚠️  Thumbnails failed: {e}")

    # ── STEP 3: VOICES ─────────────────────────────────────────
    print("\n🎙️  STEP 3: Generating voices...")
    try:
        from voice_engine import generate_voice

        audio_dir = EPISODE_DIR / "audio"
        audio_dir.mkdir(exist_ok=True)

        dialogue_beats = []
        order = 0

        # Announcer
        dialogue_beats.append({
            "order": order, "character": "ANNOUNCER",
            "scene": "intro", "expression": "neutral",
            "text": FIXED_ANNOUNCER, "beat_type": "announcer"
        })
        order += 1

        stories = script.get("stories", script.get("segments", []))
        for story_idx, story in enumerate(stories):
            story_id = story.get("id", "story")
            is_last  = (story_idx == len(stories) - 1)

            # cold_open
            cold_open = story.get("cold_open", {})
            cold_text = cold_open.get("dialogue", "")
            if cold_text:
                dialogue_beats.append({
                    "order": order, "character": cold_open.get("character", "BEAR"),
                    "scene": f"{story_id}_cold", "expression": cold_open.get("expression", "neutral"),
                    "text": cold_text, "beat_type": "cold_open", "story_id": story_id
                })
                order += 1

            # bull
            bull_line = story.get("bull", {}).get("dialogue", "")
            if bull_line:
                dialogue_beats.append({
                    "order": order, "character": "BULL",
                    "scene": story_id, "expression": story.get("bull", {}).get("expression", "neutral"),
                    "text": bull_line, "beat_type": "main", "story_id": story_id
                })
                order += 1

            # bear
            bear_line = story.get("bear", {}).get("dialogue", "")
            if bear_line:
                dialogue_beats.append({
                    "order": order, "character": "BEAR",
                    "scene": story_id, "expression": story.get("bear", {}).get("expression", "neutral"),
                    "text": bear_line, "beat_type": "main", "story_id": story_id
                })
                order += 1

            # argument
            for beat in story.get("argument", []):
                text = beat.get("dialogue", "")
                if text:
                    dialogue_beats.append({
                        "order": order, "character": beat.get("character", "BULL"),
                        "scene": f"{story_id}_arg", "expression": beat.get("expression", "neutral"),
                        "text": text, "beat_type": "argument", "story_id": story_id
                    })
                    order += 1

            # CTA
            # Stories 1-4: Bull or Bear CTA as written by script
            # Story 5 (the_closer): Bear only — "Bear does not ask twice"
            cta      = story.get("cta", {})
            cta_text = cta.get("dialogue", "")

            if story_id == "the_closer":
                # Story 5 — Bear CTA only from cta_bear field
                # Skip Bull's CTA to avoid doubling up
                bear_cta      = cta.get("cta_bear", {})
                bear_cta_text = bear_cta.get("dialogue", "")
                if bear_cta_text:
                    dialogue_beats.append({
                        "order": order, "character": "BEAR",
                        "scene": f"{story_id}_cta",
                        "expression": bear_cta.get("expression", "neutral"),
                        "text": bear_cta_text, "beat_type": "cta", "story_id": story_id
                    })
                    order += 1
                elif cta_text:
                    # Fallback — use whatever CTA text exists
                    dialogue_beats.append({
                        "order": order, "character": "BEAR",
                        "scene": f"{story_id}_cta",
                        "expression": cta.get("expression", "neutral"),
                        "text": cta_text, "beat_type": "cta", "story_id": story_id
                    })
                    order += 1
            else:
                # Stories 1-4 — standard CTA
                if cta_text:
                    dialogue_beats.append({
                        "order": order, "character": cta.get("character", "BULL"),
                        "scene": f"{story_id}_cta",
                        "expression": cta.get("expression", "shringara"),
                        "text": cta_text, "beat_type": "cta", "story_id": story_id
                    })
                    order += 1

            # Transition — main video only, NOT in short
            if not is_last:
                transition = story.get("transition", {})
                trans_text = transition.get("dialogue", "")
                if trans_text:
                    dialogue_beats.append({
                        "order": order, "character": transition.get("character", "BULL"),
                        "scene": f"{story_id}_transition",
                        "expression": transition.get("expression", "pointing"),
                        "text": trans_text, "beat_type": "transition", "story_id": story_id
                    })
                    order += 1

        # NO outro dialogue — jingle slide only
        # Story 5 Bear CTA is the final spoken word

        # Generate all voices
        audio_files = []
        for beat in dialogue_beats:
            if not beat.get("text"):
                continue
            out_path = audio_dir / f"{beat['order']:03d}_{beat['character']}_{beat['scene']}.mp3"
            if out_path.exists():
                print(f"  ⏭️  {beat['character']} [{beat['scene']}]")
            else:
                generate_voice(beat["character"], beat["text"], str(out_path))
            if out_path.exists():
                beat["audio_file"] = str(out_path)
                audio_files.append(beat)

        print(f"\n✅ {len(audio_files)} voice lines ready")

    except Exception as e:
        print(f"❌ Voice: {e}")
        traceback.print_exc()
        return None

    # ── STEP 4: VIDEO ──────────────────────────────────────────
    print("\n🎬 STEP 4: Assembling Bull + Bear video...")
    try:
        import video_assembler

        scene = []
        for beat in audio_files:
            if beat["character"] in ["BULL", "BEAR"] and beat.get("audio_file"):
                scene.append({
                    "character":  beat["character"],
                    "expression": beat.get("expression", "neutral"),
                    "dialogue":   beat["text"],
                    "audio_file": beat["audio_file"],
                    "beat_type":  beat.get("beat_type", "main"),
                    "story_id":   beat.get("story_id", "")
                })

        if not scene:
            print("❌ No scene beats")
            return None

        print(f"  🎭 {len(scene)} beats (incl. CTAs and transitions)")

        video_dir = EPISODE_DIR / "video"
        video_dir.mkdir(exist_ok=True)

        for d in ["work", "beats", "audio"]:
            p = video_dir / d
            if p.exists():
                shutil.rmtree(p)

        video_assembler.SCENE      = scene
        video_assembler.OUTPUT_DIR = video_dir
        video_assembler.main()

        raw_video = video_dir / "dmc_bull_bear.mp4"
        if not raw_video.exists():
            print("❌ Raw video not found")
            return None

        print(f"✅ Raw video | Audio: {'✅' if check_audio(raw_video) else '❌'}")

    except Exception as e:
        print(f"❌ Assembler: {e}")
        traceback.print_exc()
        return None

    # ── STEP 5: INTRO + OUTRO ──────────────────────────────────
    print("\n🎵 STEP 5: Building intro and outro...")

    intro_path = EPISODE_DIR / "intro_final.mp4"
    outro_path = EPISODE_DIR / "outro_final.mp4"
    main_norm  = EPISODE_DIR / "main_norm.mp4"

    announcer_audio = None
    for beat in audio_files:
        if beat["character"] == "ANNOUNCER":
            announcer_audio = beat.get("audio_file")
            break

    intro_ok = build_intro(intro_path, announcer_audio)
    outro_ok = build_outro(outro_path)

    print("  📐 Normalizing main video...")
    normalize(raw_video, main_norm)
    print(f"  ✅ Main | Audio: {'✅' if check_audio(main_norm) else '❌'}")

    # ── STEP 6: FINAL ASSEMBLY ─────────────────────────────────
    print("\n🔗 STEP 6: Final assembly...")

    final_video = EPISODE_DIR / f"dmc_{EPISODE_DATE}_final.mp4"

    parts = []
    if intro_ok and intro_path.exists():
        parts.append(intro_path)
    if main_norm.exists():
        parts.append(main_norm)
    elif raw_video.exists():
        parts.append(raw_video)
    if outro_ok and outro_path.exists():
        parts.append(outro_path)

    print(f"  🔗 Parts: {[Path(p).name for p in parts]}")
    ok = assemble_final(parts, final_video)

    if not ok or not final_video.exists():
        print("  ⚠️  Concat failed — copying raw")
        shutil.copy(raw_video, final_video)

    size_mb = final_video.stat().st_size / 1024 / 1024
    print(f"\n✅ Final: {final_video.name} | {size_mb:.1f} MB")

    # ── STEP 7: SHORTS — cold_open to end of CTA ───────────────
    print("\n✂️  STEP 7: Cutting 5 shorts (cold_open → CTA)...")
    shorts_dir = EPISODE_DIR / "shorts"
    shorts_dir.mkdir(exist_ok=True)

    shorts    = []
    stories   = script.get("stories", script.get("segments", []))
    beats_dir = EPISODE_DIR / "video" / "beats"

    # Build precise timing map from beat video durations
    beat_index = 0
    cursor     = 0.0
    story_map  = {}

    for beat in audio_files:
        char      = beat.get("character", "")
        beat_type = beat.get("beat_type", "")
        story_id  = beat.get("story_id", "")

        if char == "ANNOUNCER":
            continue

        beat_video = beats_dir / f"beat_{beat_index:02d}.mp4"
        duration   = get_duration(beat_video) if beat_video.exists() else get_duration(beat.get("audio_file", ""))

        if story_id not in story_map:
            story_map[story_id] = {"start": None, "cta_end": None, "trans_end": None}

        if beat_type == "cold_open" and story_map[story_id]["start"] is None:
            story_map[story_id]["start"] = cursor

        if beat_type == "cta":
            story_map[story_id]["cta_end"] = cursor + duration

        if beat_type == "transition":
            story_map[story_id]["trans_end"] = cursor + duration

        cursor     += duration
        beat_index += 1

    # Cut each short from cold_open → cta_end
    for i, story in enumerate(stories):
        story_id   = story.get("id", f"story_{i}")
        short_data = story.get("short", {})

        # Attach short thumbnail if available
        short_thumb_key = f"short_{i+1}"
        if short_thumb_key in thumbnails:
            short_data["thumbnail"] = thumbnails[short_thumb_key]

        timing = story_map.get(story_id, {})
        start  = timing.get("start")
        end    = timing.get("cta_end")

        if start is None or end is None:
            print(f"  ⚠️  Story {story_id} timing not found — skipping")
            continue

        dur = min(end - start, 59.0)
        if dur <= 0:
            print(f"  ⚠️  Story {story_id} zero duration — skipping")
            continue

        out = shorts_dir / f"short_{i+1}_{story_id}.mp4"

        ok = ffmpeg([
            "ffmpeg", "-y",
            "-i", str(main_norm),
            "-ss", str(start),
            "-t", str(dur),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            str(out)
        ], f"cut_short_{i+1}")

        if ok and out.exists():
            shorts.append({"file": str(out), "data": short_data})
            actual_dur = get_duration(out)
            print(f"  ✅ Short {i+1} [{story_id}]: {actual_dur:.1f}s | {start:.1f}s → {end:.1f}s")
        else:
            print(f"  ❌ Short {i+1} failed")

    print(f"✅ {len(shorts)} shorts ready")

    # ── STEP 8: MEMORY ─────────────────────────────────────────
    print("\n💾 STEP 8: Saving memory...")
    save_memory(memory, script)

    # ── STEP 8b: QC ────────────────────────────────────────────
    print("\n🔍 STEP 8b: Running QC...")
    try:
        from qc_bot import run_qc
        qc_passed = run_qc(script=script)
        if not qc_passed:
            print("❌ QC failed — upload blocked. Fix issues and re-run.")
            return None
    except Exception as e:
        print(f"  ⚠️  QC skipped: {e}")

    # ── STEP 9: YOUTUBE ────────────────────────────────────────
    print("\n📺 STEP 9: Uploading to YouTube...")
    yt_result = None
    try:
        from youtube_uploader import upload_episode as yt_upload
        yt_result = yt_upload(
            final_video  = final_video,
            script       = script,
            seo          = script.get("seo", {}),
            episode_date = EPISODE_DATE,
            shorts       = shorts
        )
    except Exception as e:
        print(f"  ⚠️  YouTube skipped: {e}")

    # ── STEP 10: TWITTER ───────────────────────────────────────
    print("\n🐦 STEP 10: Posting to Twitter/X...")
    try:
        from twitter_poster import post_episode as tweet_episode
        yt_url = ""
        if isinstance(yt_result, dict):
            yt_url = yt_result.get("url", "")
        if not yt_url:
            yt_url = "https://youtube.com/@DumbMoneyClub2026"
        tweet_episode(script, yt_url, shorts)
    except Exception as e:
        print(f"  ⚠️  Twitter skipped: {e}")

    # ── DONE ───────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("✅ EPISODE COMPLETE")
    print(f"📅 {datetime.now().strftime('%B %d, %Y')}")
    print(f"🎬 {script.get('title','')[:60]}")
    print(f"📁 {EPISODE_DIR}")
    print()
    print("  FILES:")
    print(f"  🎬 {final_video.name}")
    if thumbnails.get("episode"):
        print(f"  🖼️  {Path(thumbnails['episode']).name}")
    for s in shorts:
        print(f"  📱 {Path(s['file']).name}")
    print()
    print("  FLOW:")
    print("  Intro → Ch1 → Ch2 → Ch3 → Ch4 → Ch5 → Bear CTA → Outro jingle")
    print("=" * 60)
    print()

    return {
        "episode":    str(final_video),
        "shorts":     shorts,
        "script":     script,
        "date":       EPISODE_DATE,
        "thumbnails": thumbnails
    }


if __name__ == "__main__":
    run_pipeline()