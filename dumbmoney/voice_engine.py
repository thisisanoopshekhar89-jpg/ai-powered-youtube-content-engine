# ============================================================
# THE DUMB MONEY CLUB — VOICE ENGINE v2
# Bull:      knQkMIFmYkJlzJUlOm2V
# Bear:      HqxxwYOPFQpV9Ci1kok7
# Announcer: knQkMIFmYkJlzJUlOm2V (Bull's voice — warm, energetic)
# These never change.
# ============================================================

import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_URL     = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

CHARACTER_VOICES = {
    "BULL": {
        "voice_id":          "knQkMIFmYkJlzJUlOm2V",
        "model":             "eleven_multilingual_v2",
        "stability":         0.40,
        "similarity_boost":  0.85,
        "style":             0.60,
        "use_speaker_boost": True
    },
    "BEAR": {
        "voice_id":          "HqxxwYOPFQpV9Ci1kok7",
        "model":             "eleven_multilingual_v2",
        "stability":         0.80,
        "similarity_boost":  0.90,
        "style":             0.15,
        "use_speaker_boost": True
    },
    "ANNOUNCER": {
        "voice_id":          "knQkMIFmYkJlzJUlOm2V",
        "model":             "eleven_multilingual_v2",
        "stability":         0.55,
        "similarity_boost":  0.85,
        "style":             0.45,
        "use_speaker_boost": True
    }
}


def generate_voice(character, text, output_file, retries=3):
    if not text or not text.strip():
        print(f"  ⚠️  Empty text for {character} — skipping")
        return False

    char_upper = character.upper()
    if char_upper not in CHARACTER_VOICES:
        print(f"  ❌ Unknown character: {character}")
        return False

    voice   = CHARACTER_VOICES[char_upper]
    url     = ELEVEN_URL.format(voice_id=voice["voice_id"])
    headers = {
        "xi-api-key":   ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text":     text.strip(),
        "model_id": voice["model"],
        "voice_settings": {
            "stability":         voice["stability"],
            "similarity_boost":  voice["similarity_boost"],
            "style":             voice["style"],
            "use_speaker_boost": voice["use_speaker_boost"]
        }
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                out = Path(output_file)
                out.parent.mkdir(parents=True, exist_ok=True)
                with open(out, "wb") as f:
                    f.write(response.content)

                # Verify file is valid
                if out.stat().st_size < 1000:
                    print(f"  ⚠️  {character} audio too small — retrying")
                    out.unlink()
                    time.sleep(2)
                    continue

                print(f"  ✅ {char_upper} [{out.stem}] — {out.stat().st_size // 1024}KB")
                return True

            elif response.status_code == 429:
                wait = 10 * attempt
                print(f"  ⏳ Rate limited — waiting {wait}s (attempt {attempt}/{retries})")
                time.sleep(wait)
                continue

            else:
                print(f"  ❌ ElevenLabs error for {character}: {response.text[:200]}")
                return False

        except requests.exceptions.Timeout:
            print(f"  ⏳ Timeout — retrying ({attempt}/{retries})")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"  ❌ Voice generation failed for {character}: {e}")
            return False

    print(f"  ❌ {character} failed after {retries} attempts")
    return False


if __name__ == "__main__":
    print("🎙️  VOICE ENGINE TEST")
    print("=" * 40)

    os.makedirs("audio/test", exist_ok=True)

    tests = [
        ("ANNOUNCER", "Ladies and gentlemen... The Dumb Money Club.", "audio/test/announcer_test.mp3"),
        ("BULL",      "This is actually GREAT for the market. Trust me. BUY THE DIP.",  "audio/test/bull_test.mp3"),
        ("BEAR",      "Consumer debt is at four point two trillion dollars. That is not great.", "audio/test/bear_test.mp3"),
    ]

    for char, text, path in tests:
        print(f"\n  Testing {char}...")
        generate_voice(char, text, path)

    print("\n✅ Done. Check audio/test/ folder.")