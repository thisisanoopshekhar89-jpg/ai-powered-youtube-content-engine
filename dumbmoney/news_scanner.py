# ============================================================
# THE DUMB MONEY CLUB — NEWS SCANNER v9
#
# 5 CHAPTERS:
# CH1 — GLOBAL NEWS    (war/crisis/election)
# CH2 — NAME SAID WHAT (named person + quote/action)
# CH3 — MARKET UPDATE  (stocks/economy + crypto prices)
# CH4 — VIRAL/MEME/AI  (AI/startup/tech)
# CH5 — THE CLOSER     (philosophical — Claude writes it)
#
# v9: Relaxed person slot — wider names, 15 candidates,
#     blocks only live updates + negotiations + pure crypto
# ============================================================

import os
import json
import re
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY    = os.getenv("NEWSAPI_KEY")
REDDIT_HEADERS  = {"User-Agent": "DumbMoneyClub/1.0"}
TODAY           = datetime.now().strftime("%Y-%m-%d")
YESTERDAY       = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# ============================================================
# NAMED PEOPLE — wide list for CH2
# ============================================================
NAMED_PEOPLE = [
    # Political leaders
    "trump", "donald trump", "modi", "narendra modi",
    "putin", "vladimir putin", "xi jinping", "zelensky",
    "macron", "sunak", "scholz", "erdogan", "netanyahu",
    "biden", "harris", "vance", "jd vance",
    # Tech / Business
    "elon musk", "musk", "bezos", "jeff bezos",
    "zuckerberg", "mark zuckerberg", "sam altman", "altman",
    "pichai", "sundar pichai", "tim cook", "cook",
    "nadella", "satya nadella", "warren buffett", "buffett",
    "ray dalio", "soros", "bill gates", "gates",
    # Finance / Economic
    "jerome powell", "powell", "janet yellen", "yellen",
    "fed chair", "treasury secretary", "imf chief",
    # Generic authority
    "white house", "kremlin", "pentagon said",
    "president said", "prime minister said", "governor said",
    "ceo said", "ceo announced", "minister said",
    "senator said", "secretary said", "fed said",
    "said today", "announced today", "warned today",
    "declared today", "signed today"
]

# ============================================================
# EXCLUSION SETS
# ============================================================

CRYPTO_TERMS = {
    "bitcoin", "btc", "bnb", "ethereum", "eth", "crypto",
    "blockchain", "nft", "defi", "altcoin", "meme coin",
    "cryptocurrency", "coinbase", "binance", "web3", "solana",
    "dogecoin", "ripple", "xrp", "tether", "stablecoin"
}

SPACE_TERMS = {
    "spacex", "static fire", "starship", "rocket test",
    "nasa launch", "falcon 9", "space launch", "orbital",
    "reentry", "booster catch", "space station", "iss",
    "moon mission", "mars mission", "artemis", "blue origin",
    "rocket lab", "virgin galactic", "engine test",
    "booster test", "rocket firing", "launch pad"
}

SOFT_TERMS = {
    "museum", "historic site", "heritage site", "tourism",
    "niagara", "landmark", "monument", "gallery", "exhibition",
    "liminal", "horror game", "backrooms", "creepypasta",
    "gaming", "video game", "movie", "film", "tv show",
    "celebrity gossip", "award show", "entertainment",
    "sports score", "ballroom", "renovation", "remodel"
}

# Only block the clearest non-person news from person slot
PERSON_BLOCKLIST = {
    "live updates", "live blog", "breaking news update",
    "fail to agree", "fails to agree", "failed to agree",
    "negotiations stall", "talks collapse", "no deal reached",
    "iran nuclear", "us iran talks", "peace negotiations",
    "iranian nuclear", "nuclear agreement"
}

SKIP_KEYWORDS = [
    "fashion", "celebrity", "red carpet", "award show", "dating",
    "married", "divorce", "baby shower", "hairstyle", "outfit",
    "makeup", "influencer", "reality tv", "kardashian", "taylor swift",
    "horoscope", "lottery winner", "nand shortage", "silicon motion",
    "memory chip", "static fire", "engine test", "booster test",
    "museum", "historic site", "heritage", "tourism", "niagara",
    "liminal horror", "backrooms", "creepypasta", "horror game",
    "video game", "movie review", "film review", "box office",
    "sports score", "match result", "cricket score", "nba score"
]

HIGH_VALUE_KEYWORDS = [
    "billion", "trillion", "million", "crash", "collapse",
    "record high", "record low", "ban", "sanctions", "historic",
    "unprecedented", "crisis", "rate hike", "rate cut", "tariff",
    "inflation", "recession", "discovery", "breakthrough",
    "percent", "%", "$", "said", "announced", "warned", "declared",
    "artificial intelligence", "AI", "startup", "funding", "viral"
]

# ============================================================
# NEWSAPI QUERIES
# ============================================================

QUERIES = {
    "global": (
        '("war" OR "invasion" OR "military offensive" OR "sanctions imposed" '
        'OR "election results" OR "protest crackdown" OR "famine" '
        'OR "earthquake kills" OR "flood kills" OR "pandemic" '
        'OR "nuclear threat" OR "refugee crisis" OR "ceasefire" '
        'OR "coup" OR "economic crisis" OR "civilians killed" '
        'OR "airstrike" OR "people killed") '
        'NOT ("crypto" OR "bitcoin" OR "BTC" OR "SpaceX" OR "rocket" '
        'OR "museum" OR "historic site" OR "heritage" OR "tourism" '
        'OR "live updates" OR "live blog" OR "negotiations")'
    ),
    "person": (
        '("Trump" OR "Elon Musk" OR "Modi" OR "Putin" '
        'OR "Xi Jinping" OR "Powell" OR "Bezos" '
        'OR "Zuckerberg" OR "Sam Altman" OR "Biden" '
        'OR "Vance" OR "Yellen" OR "Netanyahu" OR "Zelensky" '
        'OR "Macron" OR "White House" OR "Fed chair" '
        'OR "executive order" OR "tariff" OR "CEO fired" '
        'OR "president signed" OR "minister warned") '
        'NOT ("crypto" OR "bitcoin" OR "SpaceX" OR "museum" '
        'OR "ballroom" OR "renovation" OR "live updates" '
        'OR "live blog" OR "iran nuclear" OR "nuclear talks" '
        'OR "peace negotiations" OR "failed to agree")'
    ),
    "market": (
        '("S&P 500" OR "Federal Reserve" OR "interest rate" '
        'OR "inflation rate" OR "recession" OR "GDP" '
        'OR "oil price" OR "earnings" OR "Wall Street" '
        'OR "nasdaq" OR "dow jones" OR "jobs report" '
        'OR "unemployment" OR "retail inflation" OR "stock market" '
        'OR "market crash" OR "market rally") '
        'NOT ("crypto" OR "bitcoin" OR "BTC" OR "SpaceX")'
    ),
    "viral": (
        '("AI" OR "ChatGPT" OR "artificial intelligence" '
        'OR "startup raised" OR "new app" OR "robot" '
        'OR "scientists discovered" OR "study finds" '
        'OR "researchers found" OR "went viral" '
        'OR "social media" OR "tech company" '
        'OR "funding round" OR "product launch" OR "AI model") '
        'NOT ("crypto" OR "bitcoin" OR "BTC" OR "blockchain" '
        'OR "SpaceX" OR "rocket" OR "starship" '
        'OR "stock market" OR "S&P" OR "wall street" '
        'OR "horror" OR "gaming" OR "movie" OR "film" '
        'OR "museum" OR "historic" OR "heritage" '
        'OR "NAND" OR "negotiations" OR "live updates")'
    ),
    "crypto": (
        '("Bitcoin" OR "BTC" OR "BNB" OR "Ethereum" OR "crypto" '
        'OR "blockchain" OR "DeFi" OR "NFT" OR "cryptocurrency" '
        'OR "ETF bitcoin" OR "crypto regulation")'
    )
}


# ============================================================
# HELPERS
# ============================================================

def is_non_english(title):
    if not title:
        return True
    non_ascii = sum(1 for c in title if ord(c) > 127)
    return non_ascii > len(title) * 0.2


def is_low_quality(title, desc=""):
    text = (title + " " + (desc or "")).lower()
    for kw in SKIP_KEYWORDS:
        if kw in text:
            return True
    if len(title) < 20:
        return True
    if "[Removed]" in title or "removed" in title.lower():
        return True
    if is_non_english(title):
        return True
    return False


def contains_any(text, terms):
    text = text.lower()
    return any(t in text for t in terms)


def has_named_person(title, desc=""):
    text = (title + " " + (desc or "")).lower()
    return any(p in text for p in NAMED_PEOPLE)


def is_person_story(title, desc=""):
    """
    Valid person story:
    - Has a named person OR authority figure
    - NOT a live update / negotiations story
    """
    text = (title + " " + (desc or "")).lower()
    if not has_named_person(title, desc):
        return False, "no named person"
    if contains_any(text, PERSON_BLOCKLIST):
        return False, "blocked (live update/negotiations)"
    if contains_any(text, CRYPTO_TERMS):
        return False, "crypto story"
    return True, "ok"


def titles_overlap(t1, t2):
    stops = {
        "the","a","an","is","in","on","at","to","of","and","or",
        "for","with","as","by","—","-","that","this","was","are",
        "its","it","be","has","have","had","will","would","could"
    }
    w1 = set(t1.lower().split()) - stops
    w2 = set(t2.lower().split()) - stops
    return len(w1 & w2) > 3


def score_story(title, desc=""):
    text = (title + " " + (desc or "")).lower()
    score = 0
    for kw in HIGH_VALUE_KEYWORDS:
        if kw in text:
            score += 2
    numbers = re.findall(r'\d+\.?\d*[%$BMKTbmkt]?', text)
    score += min(len(numbers), 6)
    return score


def fetch_newsapi(query_key, exclude_titles=None):
    """Fetch single best story."""
    if not NEWS_API_KEY:
        return None

    exclude_titles = exclude_titles or []
    params = {
        "q":        QUERIES[query_key],
        "from":     YESTERDAY,
        "to":       TODAY,
        "language": "en",
        "sortBy":   "relevancy",
        "pageSize": 20,
        "apiKey":   NEWS_API_KEY
    }

    try:
        r        = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        articles = r.json().get("articles", [])
        best     = None
        best_s   = -1

        for a in articles:
            title = a.get("title", "")
            desc  = a.get("description", "") or ""

            if is_low_quality(title, desc):
                continue
            if any(titles_overlap(title, u) for u in exclude_titles):
                continue

            s = score_story(title, desc)
            if s > best_s:
                best_s = s
                best = {
                    "title":       title,
                    "description": desc,
                    "source":      a.get("source", {}).get("name", ""),
                    "url":         a.get("url", ""),
                    "published":   a.get("publishedAt", ""),
                    "score":       s
                }
        return best

    except Exception as e:
        print(f"    ❌ NewsAPI ({query_key}): {e}")
        return None


def fetch_newsapi_candidates(query_key, exclude_titles=None, max_results=15):
    """Fetch multiple candidates for manual filtering."""
    if not NEWS_API_KEY:
        return []

    exclude_titles = exclude_titles or []
    params = {
        "q":        QUERIES[query_key],
        "from":     YESTERDAY,
        "to":       TODAY,
        "language": "en",
        "sortBy":   "relevancy",
        "pageSize": 20,
        "apiKey":   NEWS_API_KEY
    }

    try:
        r        = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        articles = r.json().get("articles", [])
        results  = []

        for a in articles:
            title = a.get("title", "")
            desc  = a.get("description", "") or ""

            if is_low_quality(title, desc):
                continue
            if any(titles_overlap(title, u) for u in exclude_titles):
                continue

            results.append({
                "title":       title,
                "description": desc,
                "source":      a.get("source", {}).get("name", ""),
                "url":         a.get("url", ""),
                "published":   a.get("publishedAt", ""),
                "score":       score_story(title, desc)
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    except Exception as e:
        print(f"    ❌ NewsAPI candidates ({query_key}): {e}")
        return []


def fetch_crypto_prices():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids":                 "bitcoin,binancecoin,dogecoin,ethereum",
                "vs_currencies":       "usd",
                "include_24hr_change": "true"
            },
            timeout=10
        )
        data  = r.json()
        btc   = data.get("bitcoin",     {})
        bnb   = data.get("binancecoin", {})
        doge  = data.get("dogecoin",    {})
        eth   = data.get("ethereum",    {})
        btc_p = btc.get("usd", 0)
        btc_c = round(btc.get("usd_24h_change", 0), 2)
        bnb_p = bnb.get("usd", 0)
        bnb_c = round(bnb.get("usd_24h_change", 0), 2)
        sb    = "+" if btc_c >= 0 else ""
        sn    = "+" if bnb_c >= 0 else ""

        return {
            "title": f"BTC ${btc_p:,.0f} ({sb}{btc_c}%) | BNB ${bnb_p:,.0f} ({sn}{bnb_c}%)",
            "description": (
                f"Bitcoin at ${btc_p:,.0f}, {sb}{btc_c}% in 24 hours. "
                f"BNB at ${bnb_p:,.0f}, {sn}{bnb_c}% in 24 hours. "
                f"ETH at ${eth.get('usd',0):,.0f}. "
                f"DOGE at ${doge.get('usd',0):.4f}."
            ),
            "prices": {
                "btc":  btc_p, "bnb": bnb_p,
                "eth":  eth.get("usd", 0),
                "doge": doge.get("usd", 0),
                "gold": 3100
            },
            "source": "CoinGecko",
            "score":  8
        }
    except Exception as e:
        print(f"    ⚠️  CoinGecko: {e}")
        return {
            "title":       "Bitcoin and crypto markets update",
            "description": "BTC, BNB and major altcoins update.",
            "prices":      {"btc": 0, "bnb": 0, "gold": 3100},
            "source":      "fallback", "score": 3
        }


def fetch_reddit(subreddit, exclude_titles=None, banned_terms=None):
    exclude_titles = exclude_titles or []
    banned_terms   = banned_terms   or set()
    try:
        url   = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=20"
        r     = requests.get(url, headers=REDDIT_HEADERS, timeout=10)
        posts = r.json().get("data", {}).get("children", [])
        for post in posts:
            p     = post.get("data", {})
            title = p.get("title", "")
            if p.get("score", 0) < 300 or p.get("stickied"):
                continue
            if is_low_quality(title):
                continue
            if contains_any(title, banned_terms):
                continue
            if any(titles_overlap(title, u) for u in exclude_titles):
                continue
            return {
                "title":       title,
                "description": f"Trending on r/{subreddit} — {p.get('num_comments',0)} comments",
                "source":      f"r/{subreddit}",
                "score":       4
            }
        return None
    except:
        return None


def fetch_google_trends():
    try:
        url    = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        r      = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', r.text)
        return [t.strip() for t in titles[1:6]]
    except:
        return []


# ============================================================
# MAIN SCANNER
# ============================================================

def scan_daily_news():
    print("\n📡 DUMB MONEY CLUB — NEWS SCANNER v9")
    print("CH1:Global | CH2:Person | CH3:Market | CH4:Viral | CH5:Closer")
    print("=" * 55)
    print(f"📅 {datetime.now().strftime('%B %d, %Y — %I:%M %p')}\n")

    used   = []
    result = {}

    print("📰 Fetching...\n")

    # ── CH1: GLOBAL ────────────────────────────────────────
    print("  [CH1 GLOBAL]")
    story = fetch_newsapi("global", exclude_titles=used)
    if story:
        t = story["title"]
        d = story.get("description", "")
        if contains_any(t + " " + d, CRYPTO_TERMS | SPACE_TERMS | SOFT_TERMS):
            print(f"    ⚠️  Rejected: {t[:55]}")
            story = None
    if story:
        result["geo"] = story
        used.append(story["title"])
        print(f"    ✅ {story['title'][:65]}")
    else:
        post = fetch_reddit("worldnews", exclude_titles=used,
                            banned_terms=CRYPTO_TERMS | SPACE_TERMS | SOFT_TERMS)
        if post:
            result["geo"] = post
            used.append(post["title"])
            print(f"    ✅ {post['title'][:65]} (Reddit)")
        else:
            print(f"    ⚠️  No story found")

    # ── CH2: PERSON ────────────────────────────────────────
    print("\n  [CH2 PERSON]")
    # Fetch 15 candidates — pick first valid one
    candidates = fetch_newsapi_candidates("person", exclude_titles=used, max_results=15)
    person_story = None
    for c in candidates:
        valid, reason = is_person_story(c["title"], c.get("description", ""))
        if valid:
            person_story = c
            break
        else:
            print(f"    ⚠️  Skip ({reason}): {c['title'][:50]}")

    if person_story:
        result["trump"] = person_story
        used.append(person_story["title"])
        print(f"    ✅ {person_story['title'][:65]}")
    else:
        # Reddit fallback
        found = False
        for sub in ["politics", "worldnews", "news", "economy"]:
            post = fetch_reddit(sub, exclude_titles=used,
                                banned_terms=CRYPTO_TERMS | SOFT_TERMS | PERSON_BLOCKLIST)
            if post:
                valid, reason = is_person_story(post["title"])
                if valid:
                    result["trump"] = post
                    used.append(post["title"])
                    print(f"    ✅ {post['title'][:65]} (r/{sub})")
                    found = True
                    break
        if not found:
            print(f"    ⚠️  No person story found")

    # ── CH3: MARKET ────────────────────────────────────────
    print("\n  [CH3 MARKET]")
    story = fetch_newsapi("market", exclude_titles=used)
    if story:
        t = story["title"]
        d = story.get("description", "")
        if contains_any(t + " " + d, CRYPTO_TERMS | SPACE_TERMS):
            print(f"    ⚠️  Rejected: {t[:55]}")
            story = None
    if story:
        result["market"] = story
        used.append(story["title"])
        print(f"    ✅ {story['title'][:65]}")
    else:
        post = fetch_reddit("economics", exclude_titles=used,
                            banned_terms=CRYPTO_TERMS | SPACE_TERMS)
        if post:
            result["market"] = post
            used.append(post["title"])
            print(f"    ✅ {post['title'][:65]} (Reddit)")
        else:
            print(f"    ⚠️  No market story found")

    # ── CH4: VIRAL / MEME / AI ─────────────────────────────
    print("\n  [CH4 VIRAL]")
    story = fetch_newsapi("viral", exclude_titles=used)
    if story:
        t = story["title"]
        d = story.get("description", "")
        bad = CRYPTO_TERMS | SPACE_TERMS | SOFT_TERMS
        if contains_any(t + " " + d, bad):
            print(f"    ⚠️  Rejected: {t[:55]}")
            story = None
        if story and result.get("geo"):
            if titles_overlap(t, result["geo"]["title"]):
                print(f"    ⚠️  Duplicate of CH1: {t[:55]}")
                story = None
    if story:
        result["struggle"] = story
        used.append(story["title"])
        print(f"    ✅ {story['title'][:65]}")
    else:
        for sub in ["technology", "Futurology", "science",
                    "interestingasfuck", "todayilearned"]:
            post = fetch_reddit(sub, exclude_titles=used,
                                banned_terms=CRYPTO_TERMS | SPACE_TERMS | SOFT_TERMS)
            if post:
                result["struggle"] = post
                used.append(post["title"])
                print(f"    ✅ {post['title'][:65]} (r/{sub})")
                break
        else:
            print(f"    ⚠️  No viral story found")

    # ── CRYPTO PRICES ──────────────────────────────────────
    print("\n  [CRYPTO PRICES]")
    crypto = fetch_crypto_prices()
    crypto_news = fetch_newsapi("crypto", exclude_titles=used)
    if crypto_news:
        crypto["description"] += f" Latest: {crypto_news['title']}."
    result["crypto"] = crypto
    print(f"    ✅ {crypto['title'][:65]}")

    # ── GOOGLE TRENDS ──────────────────────────────────────
    trends = fetch_google_trends()
    if trends:
        result["trending"] = trends

    # ── PACKAGE ────────────────────────────────────────────
    package = {
        "date":     TODAY,
        "geo":      result.get("geo"),
        "trump":    result.get("trump"),
        "market":   result.get("market"),
        "struggle": result.get("struggle"),
        "crypto":   result.get("crypto"),
        "trending": result.get("trending"),
    }

    os.makedirs("output/news", exist_ok=True)
    path = f"output/news/scan_{TODAY}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(package, f, indent=2, ensure_ascii=False)

    found = sum(1 for k in ["geo","trump","market","struggle","crypto"]
                if package.get(k))
    print(f"\n✅ {found}/5 stories ready — {path}\n")
    return package


def pick_top_stories(package):
    seen = []
    top  = {}

    for key in ["geo", "trump", "market", "struggle"]:
        val = package.get(key)
        if not val or not isinstance(val, dict):
            continue

        title = val.get("title", "")
        desc  = val.get("description", "")

        if is_non_english(title):
            print(f"  ⚠️  [{key.upper()}] non-English — skipped")
            continue

        if any(titles_overlap(title, s) for s in seen):
            print(f"  ⚠️  [{key.upper()}] duplicate — skipped")
            continue

        if key in ["geo", "struggle"]:
            if contains_any(title + " " + desc, CRYPTO_TERMS):
                print(f"  ⚠️  [{key.upper()}] crypto in wrong slot — skipped")
                continue
            if contains_any(title + " " + desc, SPACE_TERMS):
                print(f"  ⚠️  [{key.upper()}] space in wrong slot — skipped")
                continue

        if key == "trump":
            valid, reason = is_person_story(title, desc)
            if not valid:
                print(f"  ⚠️  [TRUMP] invalid ({reason}) — skipped")
                continue

        top[key] = val
        seen.append(title)

    top["crypto"] = package.get("crypto")

    print("🎯 TODAY'S EPISODE:")
    print("=" * 55)
    labels = {
        "geo":      "CH1 GLOBAL  ",
        "trump":    "CH2 PERSON  ",
        "market":   "CH3 MARKET  ",
        "struggle": "CH4 VIRAL   ",
        "crypto":   "CH3 CRYPTO  ",
    }
    for key in ["geo", "trump", "market", "struggle", "crypto"]:
        val = top.get(key)
        if val and isinstance(val, dict):
            print(f"  [{labels[key]}] {val.get('title','')[:55]}")
        else:
            print(f"  [{labels[key]}] ⚠️  No story")

    print("\n  [CH5 CLOSER ] Philosophical — Claude from today's 4 stories")
    print()
    return top


if __name__ == "__main__":
    package = scan_daily_news()
    top     = pick_top_stories(package)