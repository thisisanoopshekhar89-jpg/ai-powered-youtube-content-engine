# ============================================================
# THE DUMB MONEY CLUB — SOUND ENGINE
# Generates all sound effects via ElevenLabs Sound Effects API
# Intro jazz, audience reactions, Buck's piano sting
# Runs once to build the library, then reuses forever
# ============================================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

# ============================================================
# SOUND LIBRARY
# These are generated ONCE and saved permanently
# Every episode reuses the same files
# ============================================================

SOUND_LIBRARY = {
    "intro_jazz": {
        "prompt": "upbeat jazz club intro music, vintage 1950s comedy club, brass and piano, energetic, 4 seconds",
        "duration": 4.0,
        "path": "assets/sounds/intro_jazz.mp3"
    },
    "bull_entrance": {
        "prompt": "comedic trumpet fanfare, upbeat and silly, 2 seconds",
        "duration": 2.0,
        "path": "assets/sounds/bull_entrance.mp3"
    },
    "bear_entrance": {
        "prompt": "low dramatic trombone sound, slow and serious, 2 seconds",
        "duration": 2.0,
        "path": "assets/sounds/bear_entrance.mp3"
    },
    "audience_laugh": {
        "prompt": "live comedy club audience laughing, genuine reaction, medium intensity, 2 seconds",
        "duration": 2.0,
        "path": "assets/sounds/audience_laugh.mp3"
    },
    "audience_groan": {
        "prompt": "live comedy club audience groaning, disappointed reaction, 2 seconds",
        "duration": 2.0,
        "path": "assets/sounds/audience_groan.mp3"
    },
    "audience_ooh": {
        "prompt": "live comedy club audience ooh reaction, surprised, 1 second",
        "duration": 1.0,
        "path": "assets/sounds/audience_ooh.mp3"
    },
    "audience_applause": {
        "prompt": "live comedy club audience applause, warm, 3 seconds",
        "duration": 3.0,
        "path": "assets/sounds/audience_applause.mp3"
    },
    "piano_note": {
        "prompt": "single deep piano note, dramatic, resonant, fading, 2 seconds",
        "duration": 2.0,
        "path": "assets/sounds/piano_note.mp3"
    },
    "jazz_ambience": {
        "prompt": "quiet jazz club background ambience, soft piano and bass, intimate, looping, 10 seconds",
        "duration": 10.0,
        "path": "assets/sounds/jazz_ambience.mp3"
    },
    "lights_out": {
        "prompt": "electrical click and hum, stage lights switching off, silence falling, 1 second",
        "duration": 1.0,
        "path": "assets/sounds/lights_out.mp3"
    },
    "outro_jazz": {
        "prompt": "jazz club outro music, vintage, warm, fading out, 4 seconds",
        "duration": 4.0,
        "path": "assets/sounds/outro_jazz.mp3"
    }
}


def generate_sound_effect(name, config):
    """Generate one sound effect via ElevenLabs Sound Effects API."""
    output_path = config["path"]

    if os.path.exists(output_path):
        print(f"   ✅ Already exists: {name}")
        return True

    print(f"   🎵 Generating: {name}...")

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": config["prompt"],
        "duration_seconds": config["duration"],
        "prompt_influence": 0.3
    }

    try:
        r = requests.post(
            ELEVENLABS_API_BASE + "/sound-generation",
            headers=headers,
            json=payload,
            timeout=30
        )

        if r.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(r.content)
            print(f"   ✅ Saved: {output_path}")
            return True
        else:
            print(f"   ❌ Failed {name}: {r.status_code} — {r.text[:100]}")
            return False

    except Exception as e:
        print(f"   ❌ Error {name}: {e}")
        return False


def build_sound_library():
    """
    Generate all sound effects and save permanently.
    Only generates files that don't exist yet.
    Safe to run multiple times.
    """
    print("\n🎵 SOUND ENGINE — THE DUMB MONEY CLUB")
    print("=" * 50)
    print("Building permanent sound library...")
    print()

    os.makedirs("assets/sounds", exist_ok=True)

    generated = 0
    skipped = 0
    failed = 0

    for name, config in SOUND_LIBRARY.items():
        if os.path.exists(config["path"]):
            print(f"   ✅ Already exists: {name}")
            skipped += 1
        else:
            success = generate_sound_effect(name, config)
            if success:
                generated += 1
            else:
                failed += 1

    print()
    print("=" * 50)
    print(f"✅ Generated: {generated}")
    print(f"⏭️  Skipped (already exist): {skipped}")
    if failed:
        print(f"❌ Failed: {failed}")
    print("Sound library ready.")
    return generated + skipped


def check_sound_library():
    """Check which sounds exist and which are missing."""
    print("\n🔍 Sound library status:")
    missing = []
    for name, config in SOUND_LIBRARY.items():
        if os.path.exists(config["path"]):
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name} — MISSING")
            missing.append(name)
    return missing


if __name__ == "__main__":
    build_sound_library()