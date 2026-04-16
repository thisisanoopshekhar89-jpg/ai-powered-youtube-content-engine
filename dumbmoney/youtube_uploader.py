# ============================================================
# THE DUMB MONEY CLUB — YOUTUBE UPLOADER v3
# Full episode + 5 individually named shorts
# Curiosity gap titles — proven by channel data
# Full SEO per video
# ============================================================

import os
import json
import time
import pickle
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent


def get_youtube_service():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        SCOPES = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]

        token_path = BASE_DIR / "assets" / "youtube_token.pickle"
        creds_path = BASE_DIR / "youtube_credentials.json"
        creds      = None

        if token_path.exists():
            with open(token_path, "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not creds_path.exists():
                    print("  ❌ youtube_credentials.json not found")
                    return None
                flow  = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "wb") as f:
                pickle.dump(creds, f)

        service = build("youtube", "v3", credentials=creds)
        print("  ✅ YouTube API connected")
        return service

    except ImportError:
        print("  ❌ YouTube libraries not installed")
        print("     pip install google-api-python-client google-auth-oauthlib")
        return None
    except Exception as e:
        print(f"  ❌ YouTube connection failed: {e}")
        return None


def upload_video(service, video_path, title, description, tags,
                 thumbnail_path=None, is_short=False):
    if not Path(video_path).exists():
        print(f"  ❌ File not found: {video_path}")
        return None

    try:
        from googleapiclient.http import MediaFileUpload

        body = {
            "snippet": {
                "title":                title[:100],
                "description":          description[:4900],
                "tags":                 tags[:15],
                "categoryId":           "25",
                "defaultLanguage":      "en",
                "defaultAudioLanguage": "en"
            },
            "status": {
                "privacyStatus":           "public",
                "madeForKids":             False,
                "selfDeclaredMadeForKids": False
            }
        }

        size_mb = Path(video_path).stat().st_size / 1024 / 1024
        print(f"  📤 {Path(video_path).name} ({size_mb:.1f} MB)")
        print(f"     {title[:70]}")

        media   = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024
        )
        request = service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  ⏳ {int(status.progress() * 100)}%")

        video_id = response["id"]
        url      = f"https://youtube.com/watch?v={video_id}"
        print(f"  ✅ Live: {url}")

        if thumbnail_path and Path(thumbnail_path).exists():
            try:
                from googleapiclient.http import MediaFileUpload as MFU
                service.thumbnails().set(
                    videoId=video_id,
                    media_body=MFU(str(thumbnail_path), mimetype="image/jpeg")
                ).execute()
                print("  ✅ Thumbnail set")
            except Exception as e:
                print(f"  ⚠️  Thumbnail failed: {e}")

        return video_id

    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        return None


def pin_comment(service, video_id, comment):
    try:
        service.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {"textOriginal": comment}
                    }
                }
            }
        ).execute()
        print("  📌 Comment pinned")
    except Exception as e:
        print(f"  ⚠️  Pin failed: {e}")


# ============================================================
# EPISODE DESCRIPTION — full SEO with chapters
# ============================================================

def build_episode_description(script, seo):
    """Full YouTube description with chapters and SEO."""
    desc = seo.get("description", "")

    thread = script.get("episode_thread", "")
    if thread:
        desc += f"\n\n{thread}"

    stories = script.get("stories", script.get("segments", []))
    if stories:
        desc += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nCHAPTERS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += "0:00 Intro — The Dumb Money Club\n"
        seg_time = 120
        for i, story in enumerate(stories):
            mins  = (i * seg_time) // 60
            secs  = (i * seg_time) % 60
            title = story.get("title", f"Story {i+1}")
            desc += f"{mins}:{secs:02d} {title}\n"

    desc += (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "THE DUMB MONEY CLUB\n"
        "Smart money. Stupid world.\n"
        "New episode every day.\n\n"
        "🐂 Bull believes everything is fine.\n"
        "🐻 Bear has the charts.\n\n"
        "Bull is always wrong. Bear is always right.\n"
        "The comedy is watching Bull figure it out in real time.\n\n"
        "#DumbMoneyClub #Finance #Comedy #Bitcoin #BTC #BNB #Gold "
        "#Markets #News #Money #Economy #Investing #Stocks #Crypto"
    )

    return desc


# ============================================================
# SHORT TITLE — curiosity gap format
# Based on channel data — unfinished sentences win every time
# Top performers: "America owes $10 trillion. Gue..." (438 views)
#                 "A woman just won $2 million and she's NOT..." (288)
#                 "Trump says war ends in weeks. Your petrol bill..." (233)
# ============================================================

def clean_title_text(text):
    """Remove chars that look bad in YouTube titles."""
    for ch in ["#", "|", "/", "\\", "<", ">", "*"]:
        text = text.replace(ch, "")
    return text.strip()


def build_short_title(short_data, episode_title, index):
    """
    Curiosity gap titles — cut before the reveal.
    Viewer must click to find out what happened.
    Format proven by channel top performers.
    """
    # Get best raw material from script
    hook      = clean_title_text(short_data.get("hook", ""))
    punchline = clean_title_text(short_data.get("punchline", ""))
    insight   = clean_title_text(short_data.get("insight", ""))
    conflict  = clean_title_text(short_data.get("conflict", ""))
    segment   = short_data.get("id") or short_data.get("segment") or ""

    # Pick the most human, specific line
    raw = hook or insight or conflict or punchline or episode_title

    # Cut the sentence at roughly halfway — never complete the thought
    def cut_at_half(text, min_words=5):
        words = text.split()
        if len(words) <= min_words:
            return text
        cut = max(min_words, len(words) // 2)
        return " ".join(words[:cut])

    # ── Curiosity gap by segment type ──────────────────────

    if segment in ["global_moment", "global_news"]:
        teaser = cut_at_half(raw, 5)
        title  = f"{teaser}... and nobody saw this coming"

    elif segment in ["name_said_what"]:
        teaser = cut_at_half(raw, 5)
        title  = f"{teaser}... Bear has the receipt"

    elif segment in ["market_today", "market_update"]:
        teaser = cut_at_half(raw, 5)
        title  = f"{teaser}... your wallet already knows"

    elif segment in ["viral_moment"]:
        teaser = cut_at_half(raw, 5)
        title  = f"{teaser}... Bear is not impressed"

    elif segment in ["the_closer"]:
        title  = "Bear said something tonight we cannot stop thinking about"

    else:
        teaser = cut_at_half(raw, 5)
        title  = f"{teaser}... Bull disagrees"

    # Add Shorts tag
    title = f"{title} #Shorts"

    # Enforce 100 char YouTube limit
    if len(title) > 100:
        title = title[:97] + "..."

    return title


# ============================================================
# SHORT DESCRIPTION — full SEO standalone
# ============================================================

def build_short_description(short_data, episode_title, youtube_url=""):
    """Full standalone description for each short."""
    hook      = short_data.get("hook", "")
    insight   = short_data.get("insight", "")
    punchline = short_data.get("punchline", "")
    caption   = short_data.get("caption", "")
    segment   = short_data.get("id") or short_data.get("segment") or ""

    desc = ""

    # Open with the hook — stops the scroll in description too
    if hook and len(hook) > 10:
        desc += f"{hook}\n\n"

    if insight and insight != hook:
        desc += f"{insight}\n\n"
    elif caption and caption != hook:
        desc += f"{caption}\n\n"

    if punchline and punchline not in [hook, insight, caption]:
        desc += f"{punchline}\n\n"

    desc += f"From today's episode: {episode_title}\n"

    if youtube_url:
        desc += f"Full episode: {youtube_url}\n"

    # Segment specific hashtags
    segment_tags = {
        "global_moment":  "#WorldNews #BreakingNews #GlobalEconomy",
        "name_said_what": "#Politics #WhatHeSaid #Viral",
        "market_today":   "#StockMarket #Bitcoin #Investing #BTC",
        "viral_moment":   "#AI #Tech #Viral #Startup #ChatGPT",
        "the_closer":     "#Motivation #Truth #Philosophy #Mindset",
    }
    extra_tags = segment_tags.get(segment, "#Finance #Money #News")

    desc += (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "THE DUMB MONEY CLUB\n"
        "Smart money. Stupid world. New episode daily.\n\n"
        "🐂 Bull is always wrong.\n"
        "🐻 Bear is always right.\n"
        "The comedy is watching Bull figure it out.\n\n"
        f"#DumbMoneyClub #Shorts #Finance #Comedy #Money {extra_tags}"
    )

    return desc


# ============================================================
# SHORT TAGS — segment specific
# ============================================================

def build_short_tags(short_data, base_tags):
    """Tags specific to each short segment."""
    segment = short_data.get("id") or short_data.get("segment") or ""
    tags    = list(base_tags)

    tag_map = {
        "global_moment":  ["worldnews", "breakingnews", "globaleconomy", "geopolitics"],
        "name_said_what": ["Trump", "Elon", "Modi", "viral", "politics", "saidwhat"],
        "market_today":   ["stockmarket", "investing", "SP500", "wallstreet", "BTC", "Bitcoin"],
        "viral_moment":   ["AI", "viral", "tech", "startup", "meme", "ChatGPT", "artificialintelligence"],
        "the_closer":     ["motivation", "mindset", "truth", "philosophy", "wisdom", "finance"],
    }

    extra = tag_map.get(segment, ["finance", "money", "news"])
    tags.extend(extra)

    return list(dict.fromkeys(tags))[:15]


# ============================================================
# MAIN UPLOAD
# ============================================================

def upload_episode(final_video, script, seo, episode_date, shorts=None):
    print(f"\n📺 YOUTUBE UPLOAD — {episode_date}")
    print("=" * 55)

    title       = seo.get("youtube_title", script.get("title", "The Dumb Money Club"))
    tags        = seo.get("tags", ["DumbMoneyClub", "finance", "comedy"])
    description = build_episode_description(script, seo)
    comment     = (
        f"🐻 Bear's closer today:\n\"{_get_bear_closer(script)}\"\n\n"
        f"Who won today? 🐂 Bull or 🐻 Bear? Tell us below 👇"
    )

    print(f"  📋 Title: {title[:65]}")
    print(f"  🏷️  Tags: {len(tags)}")

    service = get_youtube_service()

    if not service:
        _save_manifest(
            final_video, title, description,
            tags, comment, episode_date, shorts
        )
        return None

    # Upload main episode
    thumb_path = (
        BASE_DIR / "output" / "thumbnails" /
        f"thumbnail_{episode_date}.jpg"
    )

    video_id = upload_video(
        service        = service,
        video_path     = final_video,
        title          = title,
        description    = description,
        tags           = tags,
        thumbnail_path = str(thumb_path) if thumb_path.exists() else None
    )

    if not video_id:
        print("  ❌ Episode upload failed")
        return None

    pin_comment(service, video_id, comment)
    episode_url = f"https://youtube.com/watch?v={video_id}"

    # Upload 5 shorts with curiosity gap titles
    shorts_uploaded = []
    if shorts:
        print(f"\n  📱 Uploading {len(shorts)} shorts...")

        for i, short in enumerate(shorts):
            short_file = short.get("file", "")
            if not Path(short_file).exists():
                print(f"  ⚠️  Short {i+1} file not found")
                continue

            short_data  = short.get("data", {})
            short_title = build_short_title(short_data, title, i)
            short_desc  = build_short_description(short_data, title, episode_url)
            short_tags  = build_short_tags(short_data, tags)

            print(f"\n  📱 Short {i+1}: {short_title[:70]}")

            short_id = upload_video(
                service     = service,
                video_path  = short_file,
                title       = short_title,
                description = short_desc,
                tags        = short_tags,
                is_short    = True
            )

            if short_id:
                shorts_uploaded.append({
                    "id":    short_id,
                    "url":   f"https://youtube.com/watch?v={short_id}",
                    "title": short_title
                })

            time.sleep(3)

        print(f"\n  ✅ {len(shorts_uploaded)}/{len(shorts)} shorts uploaded")

    # Save upload log
    result = {
        "video_id":    video_id,
        "url":         episode_url,
        "title":       title,
        "date":        episode_date,
        "upload_time": datetime.now().isoformat(),
        "shorts":      shorts_uploaded
    }

    log_path = (
        BASE_DIR / "output" / "episodes" /
        episode_date / "upload_log.json"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n  ✅ EPISODE LIVE: {episode_url}")
    return result


def _get_bear_closer(script):
    """Get Bear's philosophical closer from the script."""
    stories = script.get("stories", script.get("segments", []))
    for story in reversed(stories):
        for beat in reversed(story.get("argument", [])):
            if beat.get("character") == "BEAR":
                return beat.get("dialogue", "")[:150]
    return script.get("outro", {}).get("bear_line", "Like and subscribe.")


def _save_manifest(video, title, description, tags, comment, date, shorts):
    """Save manifest for manual upload if OAuth fails."""
    manifest = {
        "video":       str(video),
        "title":       title,
        "description": description,
        "tags":        tags,
        "comment":     comment,
        "date":        date,
        "shorts":      [s.get("file", "") for s in (shorts or [])],
        "status":      "pending_manual_upload"
    }
    path = BASE_DIR / "output" / "episodes" / date / "upload_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  📝 Manifest saved: {path}")
    print("  ℹ️  Re-authenticate YouTube OAuth to enable auto-upload")


if __name__ == "__main__":
    print("YouTube Uploader v3 — The Dumb Money Club")
    print("Run python main.py to trigger upload pipeline")