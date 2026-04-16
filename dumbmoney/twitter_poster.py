# ============================================================
# THE DUMB MONEY CLUB — TWITTER/X POSTER
# Posts daily episode + 5 shorts automatically
# Uses OAuth 1.0a — needs Read and Write permissions
# ============================================================

import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_clients():
    try:
        import tweepy

        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
            wait_on_rate_limit=True
        )

        auth = tweepy.OAuth1UserHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET"),
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Verify credentials
        me = client.get_me()
        if me and me.data:
            print(f"✅ Twitter connected: @{me.data.username}")
        return client, api

    except ImportError:
        print("❌ tweepy not installed — pip install tweepy")
        return None, None
    except Exception as e:
        print(f"❌ Twitter connection failed: {e}")
        return None, None


def post_episode(script, youtube_url, shorts=None):
    print("\n🐦 POSTING TO TWITTER/X...")
    print("=" * 50)

    client, api = get_clients()
    if not client:
        return None

    title     = script.get("title", "The Dumb Money Club")
    thread    = script.get("episode_thread", "")
    stories   = script.get("stories", script.get("segments", []))

    # ── MAIN TWEET ─────────────────────────────────────────
    # Get Bear's philosophical closer
    bear_closer = ""
    for story in stories:
        if story.get("id") == "the_closer":
            for beat in story.get("argument", []):
                if beat.get("character") == "BEAR":
                    bear_closer = beat.get("dialogue", "")
                    break

    if not bear_closer:
        # Fallback to any Bear line from closer
        for story in stories:
            if story.get("id") == "the_closer":
                bear_closer = story.get("bear", {}).get("dialogue", "")
                break

    # Build main tweet
    if bear_closer:
        tweet = f"🐻 \"{bear_closer[:180]}\"\n\n"
    else:
        tweet = f"🎬 {title}\n\n"

    tweet += f"🐂 Bull disagrees. As always.\n\n"
    tweet += f"📺 {youtube_url}\n\n"
    tweet += f"#DumbMoneyClub #Finance #Bitcoin #Markets #Comedy"

    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    try:
        response = client.create_tweet(text=tweet)
        tweet_id = response.data["id"]
        print(f"✅ Main tweet: https://x.com/i/web/status/{tweet_id}")
    except Exception as e:
        print(f"❌ Main tweet failed: {e}")
        return None

    time.sleep(3)

    # ── THREAD — 5 story hooks as replies ──────────────────
    story_tweets = []
    for i, story in enumerate(stories[:5]):
        short     = story.get("short", {})
        hook      = short.get("hook", story.get("hook", ""))
        insight   = short.get("insight", "")
        punchline = short.get("punchline", "")

        if not hook:
            continue

        story_tweet = f"{hook}\n\n{insight[:100] if insight else ''}"
        if punchline:
            story_tweet += f"\n\n{punchline[:80]}"
        story_tweet += f"\n\n#DumbMoneyClub"

        if len(story_tweet) > 280:
            story_tweet = story_tweet[:277] + "..."

        try:
            r = client.create_tweet(
                text=story_tweet,
                in_reply_to_tweet_id=tweet_id
            )
            tweet_id = r.data["id"]
            story_tweets.append(tweet_id)
            print(f"  ✅ Thread {i+1}: {hook[:50]}")
            time.sleep(2)
        except Exception as e:
            print(f"  ⚠️  Thread {i+1} failed: {e}")

    # ── SHORTS — post as separate tweets ───────────────────
    if shorts and api:
        print(f"\n📱 Posting {len(shorts)} shorts...")
        for i, short in enumerate(shorts[:5]):
            short_file = short.get("file", "")
            if not Path(short_file).exists():
                print(f"  ⚠️  Short {i+1} file not found")
                continue

            try:
                short_data    = short.get("data", {})
                hook          = short_data.get("hook", f"Short {i+1}")
                caption       = short_data.get("caption", hook)
                tweet_text    = f"{hook}\n\n{caption[:100]}\n\n#DumbMoneyClub #Shorts #Finance"

                if len(tweet_text) > 280:
                    tweet_text = tweet_text[:277] + "..."

                print(f"  📤 Uploading short {i+1}: {Path(short_file).name}")

                # Upload video
                media = api.media_upload(
                    filename=str(short_file),
                    media_category="tweet_video"
                )
                media_id = media.media_id

                # Wait for processing
                print(f"  ⏳ Processing media...")
                for attempt in range(15):
                    try:
                        status = api.get_media_upload_status(media_id)
                        state  = status.processing_info.get("state", "succeeded")
                        if state == "succeeded":
                            break
                        elif state == "failed":
                            raise Exception("Media processing failed")
                        progress = status.processing_info.get("progress_percent", 0)
                        print(f"  ⏳ {progress}%...")
                        time.sleep(3)
                    except AttributeError:
                        break

                client.create_tweet(
                    text=tweet_text,
                    media_ids=[str(media_id)]
                )
                print(f"  ✅ Short {i+1} posted: {hook[:40]}")
                time.sleep(5)

            except Exception as e:
                print(f"  ⚠️  Short {i+1} failed: {e}")

    print(f"\n✅ Twitter/X posting complete")
    return tweet_id


if __name__ == "__main__":
    # Test with dummy data
    print("🐦 Testing Twitter connection...")

    test_script = {
        "title": "The Dumb Money Club — Test",
        "episode_thread": "Today everything went wrong and Bull thinks it's fine.",
        "stories": [
            {
                "id": "the_closer",
                "short": {"hook": "Bear said something tonight.", "insight": "Test insight."},
                "bear": {"dialogue": "I said this in 2023. Here is the chart."},
                "argument": [
                    {
                        "character": "BEAR",
                        "dialogue": "The people making the rules are not living by them. Remember that."
                    }
                ]
            }
        ],
        "segments": []
    }

    post_episode(
        script      = test_script,
        youtube_url = "https://youtube.com/@DumbMoneyClub2026",
        shorts      = []
    )