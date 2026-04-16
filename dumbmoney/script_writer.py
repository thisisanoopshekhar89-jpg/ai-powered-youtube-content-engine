# ============================================================
# THE DUMB MONEY CLUB — SCRIPT WRITER v17
# Two hosts. One show. Five chapters. Daily.
#
# v17: Bull and Bear present like two TV hosts
#      Natural conversation — not separate segments
#      CTA = host turning to camera, genuine
#      Transition = one host tossing to the next topic
#      cold_open picks up exactly where transition left off
#      Shorts extracted from cold_open → CTA of each chapter
# ============================================================

import os
import json
import re
import traceback
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

FIXED_ANNOUNCER = "Ladies and gentlemen... The Dumb Money Club."

BULL_EXPRESSIONS = """
BULL EXPRESSIONS (exact filename, no .png):
excited_arms_up, hasya, adbhuta, raudra, shanta, bhayanaka,
karuna, vira, shringara, exaggerated_laugh, smug, facepalm,
mic_drop, neutral, thinking, mouth_closed, mouth_half, mouth_open,
pointing, arms_crossed

USE:
excited_arms_up  → opening, celebration, big win
hasya            → laughing at own joke
adbhuta          → genuine shock, didn't see that coming
raudra           → frustrated, pushed into corner
vira             → confident, chest out, I got this
smug             → I know something you don't yet
bhayanaka        → scared of Bear's number
facepalm         → realising he was wrong AGAIN
thinking         → pretending to understand
exaggerated_laugh → completely losing it
shringara        → charming the audience, winking
mic_drop         → done, walking away energy
pointing         → making a key point to audience
arms_crossed     → defensive, not buying it
"""

BEAR_EXPRESSIONS = """
BEAR EXPRESSIONS (exact filename, no .png):
neutral, unimpressed, angry, shocked, smug, sad, thinking,
arms_crossed, pointing, told_you_so, almost_smiled, sighing,
adjusting_glasses, chart_face, mouth_closed,
mouth_half, mouth_open

USE:
neutral          → default, watching Bull be wrong
unimpressed      → Bull is speaking, as usual
arms_crossed     → deeply skeptical
pointing         → citing the specific data
told_you_so      → prediction proved correct again
adjusting_glasses → about to drop something devastating
sighing          → weight of being right every single time
almost_smiled    → something funny but fighting it
shocked          → even Bear didn't see THIS coming
angry            → genuinely furious, this affects real people
chart_face       → presenting the data, here is reality
sad              → this is actually tragic
"""

SHOW_BIBLE = """
THE DUMB MONEY CLUB — SHOW BIBLE v17
Two hosts. One show. Five chapters. Daily.

═══════════════════════════════════════
THE SHOW FORMAT
═══════════════════════════════════════

Think of this as a TV talk show with two hosts — Bull and Bear.
They sit together, talk to each other AND to the audience.
The show has 5 chapters. But it feels like ONE conversation.

The viewer should feel like they walked into a room where
two smart, funny people are already talking about the news.
They pull you in. They make it personal. They make it real.

The episode is ONE SHOW — not 5 separate videos stitched together.
The 5 shorts are extracted from this one show — each chapter
is self-contained enough to stand alone.

═══════════════════════════════════════
THE AUDIENCE
═══════════════════════════════════════
Write for this exact person:
- Earns a salary. Pays EMI or rent. Buys groceries.
- Smart but busy. No time for 20-minute explainers.
- Wants to feel informed and entertained at the same time.
- Laughs at Bull because they have BEEN Bull.
- Shares content that makes them look smart to their friends.
- Scrolling at 11pm. Give them a reason to stay.

THE GOLDEN RULE — NEVER TECHNICAL:
NEVER: inflation rate, basis points, yield curve, liquidity
ALWAYS: your grocery bill went up Rs 400 this month
        your EMI just got Rs 2000 more expensive
        50 million people lost jobs. Someone called that progress.

═══════════════════════════════════════
THE TWO HOSTS
═══════════════════════════════════════

BULL — The eternal optimist host
- Always wrong. Always confident. Always surprised when wrong.
- Talks TO the audience like they are his co-conspirators.
- Warm. Excitable. Like a friend who forward you bad investment advice.
- CAPS for emphasis. ... for dramatic pauses. Max 3 sentences.
- References his past wrong calls with pride, not shame.
- Catchphrase: This is actually GREAT.

BEAR — The permanent pessimist host
- Always right. Never happy about it.
- Talks to the CAMERA — like testifying, not chatting.
- Slow. Deliberate. One devastating number per chapter.
- References exact dates and past prices when making callbacks.
- Max 3 sentences. Never wastes words.
- Occasionally almost smiles when Bull says something genuinely funny.

TOGETHER they feel like a real show.
Bull sets it up. Bear knocks it down.
The audience knows Bear is right. They watch anyway because Bull is fun.

═══════════════════════════════════════
THE 5 CHAPTER STRUCTURE
═══════════════════════════════════════

CHAPTER 1 — GLOBAL NEWS — Plants the SEED
CHAPTER 2 — NAME SAID WHAT — Names the VILLAIN
CHAPTER 3 — MARKET UPDATE — Shows the COST
CHAPTER 4 — VIRAL MEME AI — Shows the MOOD
CHAPTER 5 — THE CLOSER — The TRUTH

Each chapter has this structure:
cold_open → bull → bear → argument → cta

Stories 1-4 also have a transition that bridges to the next chapter.

═══════════════════════════════════════
THE COLD OPEN — STARTS EACH CHAPTER
═══════════════════════════════════════
1-2 sentences. Human moment. Direct to camera.
Makes the viewer feel something before they know what happened.
NOT a summary. NOT a headline.

The cold_open of chapter 2-5 MUST connect grammatically and
logically to the transition that came before it.

It should feel like one host just said something and the other
picks it up naturally — like a real conversation.

EXAMPLE OF PERFECT TRANSITION → cold_open CONNECTION:

Transition (Bull): "Okay Bear — but did you see what Trump said this morning?"
cold_open (Bear): "Yes. He promised it would be over in three weeks.
                   That was fourteen months ago. Your petrol has not forgotten."

That is one continuous sentence of television. No gap. No reset.
The viewer never feels they changed topic — they feel the show moved forward.

═══════════════════════════════════════
THE CTA — ENDS EACH CHAPTER
═══════════════════════════════════════
After the argument settles — one host turns to camera.
This is the CTA. It ends the chapter.
It feels like a genuine host moment — not a corporate plea.

CTA is EARNED by the chapter — it references what just happened.
It ends naturally with like, share, or subscribe.
Max 2 sentences.

CTA character alternates:
- Chapter 1 — Bull (warm, enthusiastic)
- Chapter 2 — Bear (dry, one sentence)
- Chapter 3 — Bull (enthusiastic, references the scoreboard)
- Chapter 4 — Bear (dry, references the viral story)
- Chapter 5 — Bull speaks first, Bear closes (both turn to camera)

BULL CTA examples:
- "If this got you thinking share it with someone who needs to hear it today."
- "Subscribe so you never miss the daily scoreboard. Your wallet deserves it."
- "Tell us in the comments who won today. I think I did. Bear thinks otherwise."

BEAR CTA examples:
- "If this was useful. Subscribe. Bear does not repeat himself."
- "Share this. Someone you know needs these numbers."
- "Like this video. Bear has the data on why that matters."

═══════════════════════════════════════
THE TRANSITION — BRIDGES CHAPTERS
═══════════════════════════════════════
After the CTA of chapters 1-4 — one host bridges to the next chapter.
This is ONE sentence. It connects what just happened to what is coming.
It feels like a natural toss between hosts on a live show.

The NEXT chapter's cold_open MUST pick up this thread directly.
Write the transition and cold_open as a pair — they are one moment
split across two characters.

TRANSITION rules:
- 1 sentence only
- References what just ended AND teases what is coming
- Natural conversational toss — not a formal announcement
- Bull or Bear — whoever makes most sense
- Chapter 5 has NO transition — it ends with the CTA then outro

TRANSITION → cold_open PAIRS — write these as connected dialogue:

Chapter 1 → 2:
Transition: Bull or Bear mentions the person/quote coming next
cold_open: Bear or Bull picks it up as if responding

Chapter 2 → 3:
Transition: References how what was said affects money/markets
cold_open: Bear opens with the exact price and its human meaning

Chapter 3 → 4:
Transition: From the serious market to the lighter viral story
cold_open: Bull reacts with genuine surprise or excitement

Chapter 4 → 5:
Transition: From the mood to the philosophical truth
cold_open: Bear brings it home with the one truth underneath everything

═══════════════════════════════════════
SHORT EXTRACTION RULE
═══════════════════════════════════════
Each chapter (cold_open → cta) is extracted as a standalone short.
The transition is NOT part of the short — it belongs to the main show flow.
Each short must work completely standalone — beginning, middle, end.
"""

SCRIPT_PROMPT = """You are writing THE DUMB MONEY CLUB — a daily news comedy show.
Two hosts: Bull and Bear. One flowing conversation. Five chapters.
Written like a real TV show — not five separate segments.

{show_bible}

BULL EXPRESSIONS:
{bull_expressions}

BEAR EXPRESSIONS:
{bear_expressions}

TODAY — {today}

TODAY'S 5 CHAPTERS:

CHAPTER 1 — GLOBAL NEWS:
{global_headline}
{global_facts}

CHAPTER 2 — NAME SAID WHAT:
{person_headline}
{person_facts}

CHAPTER 3 — MARKET UPDATE:
{market_headline}
{market_facts}
LIVE PRICES: BTC ${btc_price} | BNB ${bnb_price} | Gold ${gold_price}

CHAPTER 4 — VIRAL MEME AI:
{viral_headline}
{viral_facts}

{memory_context}

DIRECTOR NOTES:
- Write the whole show as ONE conversation — not 5 separate scripts
- Every transition + cold_open pair must be grammatically connected
- Read the transition and cold_open together — they must sound like one moment
- CTA is earned by the chapter — never generic
- Chapter 5 has NO transition
- Chapter 2 MUST open hook with We heard that [Name] said
- Chapter 3 MUST reference BTC BNB Gold in human wallet terms
- Bull references a past wrong call naturally somewhere
- Bear references a past correct call with exact date and past price somewhere
- Max tokens used wisely — every line earns its place

TRANSLATION TEST:
CURRENCY RULE — ALWAYS match currency to the story geography:
- US news / global finance → write "dollars" not $ or USD
- Indian news / Indian impact → write "rupees" not Rs or INR
- UK news → write "pounds" not £ or GBP
- Europe → write "euros" not € or EUR
- Crypto → write "dollars" not $
- NEVER use abbreviations — Rs, USD, INR, GBP all get read literally by voice engine
- ALWAYS spell out the currency word in full
- Example: "two thousand rupees" not "Rs 2000" or "USD 2000"
- Example: "sixty five thousand dollars" not "$65,000"
- Numbers in dialogue should also be spoken naturally:
  "sixty five thousand" not "65,000"
  "two point four trillion" not "2.4 trillion"

TRANSLATION TEST:
Would someone who drives to work, pays EMI, buys groceries understand this instantly?
If no — rewrite it.

RETURN ONLY VALID JSON. No markdown. No backticks. No explanation.

{{
  "title": "Episode title — punchy human under 60 chars no jargon",
  "date": "{today}",
  "episode_seed": "The seed Chapter 1 plants that Chapter 5 harvests",
  "episode_thread": "One sentence — the single truth all 5 chapters reveal together",

  "intro": {{
    "announcer": "Ladies and gentlemen... The Dumb Money Club."
  }},

  "stories": [
    {{
      "id": "global_news",
      "title": "Chapter 1 — [Exact Chapter Name]",
      "cold_open": {{
        "character": "BEAR",
        "expression": "neutral",
        "dialogue": "1-2 sentences. Human moment. Direct to camera. Makes viewer feel before they know. NOT a summary.",
        "duration_seconds": 3
      }},
      "hook": "The chapter hook — grabs attention",
      "topic": "Plain English — what happened and why it matters",
      "human_story": "One vivid specific person this affects",
      "short": {{
        "hook": "Cold open energy. Human gut punch. NOT a headline.",
        "conflict": "Bull one line wrong. Bear one line devastating.",
        "insight": "What this means for the viewer. One fact.",
        "punchline": "The shareable moment."
      }},
      "bull": {{
        "expression": "exact_bull_expression",
        "dialogue": "Optimistic. Wrong. Warm. Max 3 sentences.",
        "audience_reaction": "laugh"
      }},
      "bear": {{
        "expression": "exact_bear_expression",
        "dialogue": "Human impact. One number in plain terms. Max 3 sentences.",
        "chart_fact": "The number in human terms",
        "audience_reaction": "groan"
      }},
      "argument": [
        {{
          "character": "BULL",
          "beat": "BUT",
          "expression": "exact_bull_expression",
          "dialogue": "Short. Wrong. Funny.",
          "audience_reaction": "laugh"
        }},
        {{
          "character": "BEAR",
          "beat": "THEREFORE",
          "expression": "exact_bear_expression",
          "dialogue": "Short. Devastating. Plain English.",
          "audience_reaction": "groan"
        }}
      ],
      "cta": {{
        "character": "BULL",
        "expression": "shringara",
        "dialogue": "Warm. Genuine. References this chapter. Ends with share or subscribe naturally. Max 2 sentences."
      }},
      "transition": {{
        "character": "BULL",
        "expression": "pointing",
        "dialogue": "One sentence. Toss to Chapter 2. Must connect grammatically to Chapter 2 cold_open. Write these as a pair."
      }}
    }},
    {{
      "id": "name_said_what",
      "title": "Chapter 2 — [EXACT PERSON NAME] Said WHAT??",
      "cold_open": {{
        "character": "BEAR",
        "expression": "adjusting_glasses",
        "dialogue": "Picks up DIRECTLY from Chapter 1 transition. Grammatically connected. 1-2 sentences. Human cost.",
        "duration_seconds": 3
      }},
      "hook": "We heard that [EXACT PERSON NAME] said [quote or paraphrase].",
      "topic": "What they said and what it costs normal people",
      "human_story": "The specific person this affects",
      "short": {{
        "hook": "Human cost first. NOT the quote.",
        "conflict": "Bull defends one line. Bear gives real cost one line.",
        "insight": "What this means for a salary earner today.",
        "punchline": "Bulls most creative defence OR Bears one-sentence receipt."
      }},
      "bull": {{
        "expression": "exact_bull_expression",
        "dialogue": "Defends it. Wrong. Funny.",
        "audience_reaction": "laugh"
      }},
      "bear": {{
        "expression": "exact_bear_expression",
        "dialogue": "Real cost. Specific. Human.",
        "chart_fact": "Real human cost",
        "audience_reaction": "groan"
      }},
      "argument": [
        {{
          "character": "BULL",
          "beat": "BUT",
          "expression": "exact_bull_expression",
          "dialogue": "Doubling down. Shorter. Funnier.",
          "audience_reaction": "laugh"
        }},
        {{
          "character": "BEAR",
          "beat": "THEREFORE",
          "expression": "exact_bear_expression",
          "dialogue": "One sentence. Done.",
          "audience_reaction": "silence"
        }}
      ],
      "cta": {{
        "character": "BEAR",
        "expression": "neutral",
        "dialogue": "Dry. Direct. References this chapter. One sentence. Subscribe or share."
      }},
      "transition": {{
        "character": "BULL",
        "expression": "hasya",
        "dialogue": "One sentence. Toss to Chapter 3 market update. Must connect to Chapter 3 cold_open."
      }}
    }},
    {{
      "id": "market_update",
      "title": "Chapter 3 — Market Update",
      "cold_open": {{
        "character": "BEAR",
        "expression": "chart_face",
        "dialogue": "Picks up from Chapter 2 transition. Uses exact BTC price. What it means for buyers right now.",
        "duration_seconds": 3
      }},
      "hook": "Your daily scoreboard. Let's see what your money did today.",
      "topic": "BTC and BNB and Gold — what it means for your wallet",
      "human_story": "The salary earner checking their phone right now",
      "wish_i_had_invested": "I wish I had invested in [X] when [Y happened] — [specific return]",
      "short": {{
        "hook": "Exact price. What it means for someone who bought last month.",
        "conflict": "Bull optimistic scoreboard. Bear wallet reality.",
        "insight": "One number — what today means for a salary earner.",
        "punchline": "The I wish I had invested moment OR Bulls hopeful closer."
      }},
      "bull": {{
        "expression": "exact_bull_expression",
        "dialogue": "The scoreboard. BTC BNB Gold specifically. Optimistic.",
        "audience_reaction": "laugh"
      }},
      "bear": {{
        "expression": "exact_bear_expression",
        "dialogue": "Wallet impact. One human number.",
        "chart_fact": "Wallet reality",
        "audience_reaction": "groan"
      }},
      "argument": [
        {{
          "character": "BULL",
          "beat": "BUT",
          "expression": "exact_bull_expression",
          "dialogue": "Bull comeback. Short. Still optimistic.",
          "audience_reaction": "laugh"
        }},
        {{
          "character": "BEAR",
          "beat": "THEREFORE",
          "expression": "exact_bear_expression",
          "dialogue": "Bear closes. Plain English.",
          "audience_reaction": "groan"
        }}
      ],
      "cta": {{
        "character": "BULL",
        "expression": "excited_arms_up",
        "dialogue": "Enthusiastic. References the market numbers. Subscribe so you never miss the daily scoreboard."
      }},
      "transition": {{
        "character": "BEAR",
        "expression": "unimpressed",
        "dialogue": "One sentence. Dry toss to Chapter 4 viral story. Must connect to Chapter 4 cold_open."
      }}
    }},
    {{
      "id": "viral_moment",
      "title": "Chapter 4 — [Exact Viral or AI or Meme Story Name]",
      "cold_open": {{
        "character": "BULL",
        "expression": "adbhuta",
        "dialogue": "Picks up from Chapter 3 transition. Genuine human reaction. Funny or surprising.",
        "duration_seconds": 3
      }},
      "hook": "Most shareable angle. Stops the scroll.",
      "topic": "What everyone is talking about and what it actually means",
      "human_story": "Who this touches",
      "short": {{
        "hook": "The feeling not the headline.",
        "conflict": "Bull excited. Bear explains the real story.",
        "insight": "What this means for someone on their phone right now.",
        "punchline": "Bulls most absurd take OR the twist nobody saw coming."
      }},
      "bull": {{
        "expression": "exact_bull_expression",
        "dialogue": "The exciting angle. Relatable. Funny.",
        "audience_reaction": "laugh"
      }},
      "bear": {{
        "expression": "exact_bear_expression",
        "dialogue": "The real angle. One number or fact. Human.",
        "chart_fact": "The real number in human terms",
        "audience_reaction": "groan"
      }},
      "argument": [
        {{
          "character": "BULL",
          "beat": "BUT",
          "expression": "exact_bull_expression",
          "dialogue": "Last stand. Funniest line of the chapter.",
          "audience_reaction": "laugh"
        }},
        {{
          "character": "BEAR",
          "beat": "THEREFORE",
          "expression": "exact_bear_expression",
          "dialogue": "Final word. Plain English.",
          "audience_reaction": "groan"
        }}
      ],
      "cta": {{
        "character": "BEAR",
        "expression": "almost_smiled",
        "dialogue": "Dry. References this viral story. Share this. Someone needs to see it."
      }},
      "transition": {{
        "character": "BULL",
        "expression": "thinking",
        "dialogue": "One sentence. Bridges to Chapter 5 the closer. Must connect to Chapter 5 cold_open."
      }}
    }},
    {{
      "id": "the_closer",
      "title": "Chapter 5 — The Closer",
      "cold_open": {{
        "character": "BEAR",
        "expression": "neutral",
        "dialogue": "Picks up from Chapter 4 transition. The one truth underneath all 4 chapters today. Quiet. Human.",
        "duration_seconds": 4
      }},
      "hook": "Today we learned that [connect 2-3 of today's chapters naturally].",
      "topic": "What today's 4 chapters reveal together — the truth underneath",
      "human_story": "Everyone watching right now",
      "short": {{
        "hook": "Bear said something tonight that we cannot stop thinking about.",
        "conflict": "Bulls honest takeaway. Bears gold standard advice.",
        "insight": "The one thing a smart person does with today's information.",
        "punchline": "THE PHILOSOPHICAL CLOSER. One human truth. Screenshot-worthy."
      }},
      "bull": {{
        "expression": "exact_bull_expression",
        "dialogue": "Honest takeaway from today. One actionable thing. References today.",
        "audience_reaction": "laugh"
      }},
      "bear": {{
        "expression": "exact_bear_expression",
        "dialogue": "Gold standard advice. One best practice. Anyone can do this today.",
        "chart_fact": "The one smart move with today's information",
        "audience_reaction": "groan"
      }},
      "argument": [
        {{
          "character": "BULL",
          "beat": "BUT",
          "expression": "exact_bull_expression",
          "dialogue": "Entrepreneurship insight from today. One key strategy.",
          "audience_reaction": "laugh"
        }},
        {{
          "character": "BEAR",
          "beat": "THEREFORE",
          "expression": "exact_bear_expression",
          "dialogue": "THE PHILOSOPHICAL CLOSER. References today's 4 chapters. One human truth. Makes them pause. Makes them share. Max 3 sentences.",
          "audience_reaction": "silence"
        }}
      ],
      "cta": {{
        "character": "BULL",
        "expression": "shringara",
        "dialogue": "Bull speaks first. Warm. If today made you think subscribe so you never miss tomorrow.",
        "cta_bear": {{
          "expression": "neutral",
          "dialogue": "Bear closes. Dry. One sentence. Like. Subscribe. Bear does not ask twice."
        }}
      }}
    }}
  ],

  "outro": {{
    "bear_line": "Like. And subscribe. Bear does not ask twice.",
    "bull_line": "I WILL be right next episode. This is my BOUNCE BACK ARC."
  }},

  "shorts": [
    {{
      "id": "global_moment",
      "segment": "global_news",
      "hook": "Cold open energy. Human gut punch. NOT a headline.",
      "conflict": "Short 1 conflict",
      "insight": "Short 1 insight",
      "punchline": "Short 1 punchline",
      "caption": "Caption for X and Instagram — complete standalone thought"
    }},
    {{
      "id": "name_said_what",
      "segment": "name_said_what",
      "hook": "[EXACT NAME] Said WHAT — make the hook the human cost",
      "conflict": "Short 2 conflict",
      "insight": "Short 2 insight",
      "punchline": "Short 2 punchline",
      "caption": "Caption — quote and cost standalone"
    }},
    {{
      "id": "market_today",
      "segment": "market_update",
      "hook": "Exact price. Human impact. Who got hurt or helped today.",
      "conflict": "Short 3 conflict",
      "insight": "Short 3 insight",
      "punchline": "Short 3 punchline",
      "caption": "Caption — market in human terms standalone"
    }},
    {{
      "id": "viral_moment",
      "segment": "viral_moment",
      "hook": "The feeling not the headline.",
      "conflict": "Short 4 conflict",
      "insight": "Short 4 insight",
      "punchline": "Short 4 punchline",
      "caption": "Caption — the viral moment standalone"
    }},
    {{
      "id": "the_closer",
      "segment": "the_closer",
      "hook": "Bear said something true tonight.",
      "conflict": "Short 5 conflict",
      "insight": "Short 5 insight",
      "punchline": "Short 5 punchline — the philosophical truth",
      "caption": "Caption — philosophical truth standalone screenshot-worthy"
    }}
  ],

  "seo": {{
    "youtube_title": "Under 60 chars. Human. Clickable. No jargon.",
    "description": "2 punchy paragraphs. What happened. Why it matters to a normal person.",
    "tags": ["DumbMoneyClub", "finance", "comedy", "Bitcoin", "BTC", "BNB", "Gold", "markets", "news", "money", "economy", "investing"],
    "thumbnail_text": "4-5 bold words — the screenshot moment"
  }}
}}

FINAL CHECK BEFORE WRITING:
1. Read every transition → cold_open pair aloud. Do they sound like one sentence?
2. Does every CTA feel earned by THAT chapter specifically?
3. Does the whole show feel like one conversation or 5 separate videos?
4. Would you watch this? Would you share it?

JSON only. No markdown. No backticks. No explanation.
"""


def load_memory():
    memory_path = "output/episode_memory.json"
    if not os.path.exists(memory_path):
        return []
    with open(memory_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return list(data.values())
    return data


def save_memory(script, btc_price, bnb_price, gold_price):
    memory_path = "output/episode_memory.json"
    memory = load_memory()

    bear_verdict = ""
    for story in script.get("stories", script.get("segments", [])):
        if story.get("id") == "the_closer":
            for beat in story.get("argument", []):
                if beat.get("character") == "BEAR" and beat.get("beat") == "THEREFORE":
                    bear_verdict = beat.get("dialogue", "")
            if not bear_verdict:
                bear_verdict = story.get("bear", {}).get("dialogue", "")

    entry = {
        "date":             script.get("date", datetime.now().strftime("%B %d, %Y")),
        "title":            script.get("title", "")[:80],
        "episode_thread":   script.get("episode_thread", "")[:150],
        "bull_wrong_about": script.get("episode_seed", "")[:150],
        "bear_verdict":     bear_verdict[:200],
        "btc_price":        btc_price,
        "bnb_price":        bnb_price,
        "gold_price":       gold_price,
    }

    memory.append(entry)
    if len(memory) > 30:
        memory = memory[-30:]

    os.makedirs("output", exist_ok=True)
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

    print(f"💾 Memory saved — {len(memory)} episodes in rolling window")
    return memory


def build_memory_context(memory):
    if not memory:
        return ""

    context = "EPISODE MEMORY — use for natural callbacks only, never forced:\n"
    for ep in memory[-3:]:
        context += (
            f"- {ep.get('date','')}: Bull was wrong about "
            f"'{ep.get('bull_wrong_about','')[:80]}'. "
            f"Bear's closer: \"{ep.get('bear_verdict','')[:100]}\"\n"
        )

    btc_history = [
        (ep.get("date", ""), ep.get("btc_price", 0))
        for ep in memory[-7:]
        if ep.get("btc_price")
    ]
    if btc_history:
        context += "\nBTC PRICE HISTORY — Bear can reference these:\n"
        for date, price in btc_history:
            if price:
                context += f"  {date}: BTC ${price:,.0f}\n"

    return context


def write_episode_script(topics, memory=None):
    print("\n✍️  SCRIPT WRITER v17 — THE DUMB MONEY CLUB")
    print("Two hosts. One show. Five chapters.")
    print("Transition → cold_open = one connected moment")
    print("=" * 55)

    market   = topics.get("market")   or {}
    trump    = topics.get("trump")    or {}
    geo      = topics.get("geo")      or topics.get("geopolitics") or {}
    crypto   = topics.get("crypto")   or {}
    struggle = topics.get("struggle") or {}

    world = geo
    if struggle and struggle.get("score", 0) > (geo.get("score", 0) if geo else 0):
        world = struggle

    viral = struggle if struggle else geo

    if not crypto:
        crypto = {
            "title":       "Bitcoin holds key level",
            "description": "BTC consolidating. BNB stable. Gold rising.",
            "prices":      {"btc": 85000, "bnb": 580, "gold": 2300}
        }

    prices = crypto.get("prices", {})
    btc    = prices.get("btc", 0)
    bnb    = prices.get("bnb", 0)
    gold   = prices.get("gold", 0)

    print(f"🌍 Chapter 1: {world.get('title','')[:55]}")
    print(f"🎤 Chapter 2: {trump.get('title','')[:55]}")
    print(f"📈 Chapter 3: {market.get('title','')[:55]}")
    print(f"🔥 Chapter 4: {viral.get('title','')[:55]}")
    print(f"₿  BTC: ${btc:,.0f} | BNB: ${bnb:,.0f} | Gold: ${gold:,.0f}")
    print("🎬 Writing the show...")

    if memory is None:
        memory = load_memory()

    memory_context = build_memory_context(memory)

    prompt = SCRIPT_PROMPT.format(
        show_bible       = SHOW_BIBLE,
        bull_expressions = BULL_EXPRESSIONS,
        bear_expressions = BEAR_EXPRESSIONS,
        global_headline  = world.get("title", "World news today"),
        global_facts     = (world.get("description") or "")[:400],
        person_headline  = trump.get("title", "Influential person makes statement"),
        person_facts     = (trump.get("description") or "")[:400],
        market_headline  = market.get("title", "Markets update"),
        market_facts     = (market.get("description") or "")[:400],
        viral_headline   = viral.get("title", "Viral story today"),
        viral_facts      = (viral.get("description") or "")[:400],
        btc_price        = f"{btc:,.0f}" if btc else "N/A",
        bnb_price        = f"{bnb:,.0f}" if bnb else "N/A",
        gold_price       = f"{gold:,.0f}" if gold else "N/A",
        memory_context   = memory_context,
        today            = datetime.now().strftime("%B %d, %Y")
    )

    try:
        message = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=12000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()
        raw = re.sub(r'^```.*?\n', '', raw)
        raw = re.sub(r'```$',      '', raw)
        raw = raw.strip()

        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not json_match:
            print("❌ No JSON found")
            episode_date = datetime.now().strftime('%Y%m%d')
            os.makedirs(f"output/episodes/{episode_date}", exist_ok=True)
            with open(f"output/episodes/{episode_date}/debug_raw.txt", "w") as f:
                f.write(raw)
            return None

        script = json.loads(json_match.group())
        script["intro"]["announcer"] = FIXED_ANNOUNCER

        if "stories" in script and "segments" not in script:
            script["segments"] = script["stories"]

        episode_date = datetime.now().strftime('%Y%m%d')
        episode_dir  = f"output/episodes/{episode_date}"
        os.makedirs(episode_dir, exist_ok=True)
        script_path  = f"{episode_dir}/script_{episode_date}.json"

        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)

        save_memory(script, btc, bnb, gold)

        print(f"\n✅ {script.get('title','')[:60]}")
        print(f"🌱 Seed:   {script.get('episode_seed','')[:65]}")
        print(f"🧵 Thread: {script.get('episode_thread','')[:65]}")
        print()

        stories = script.get("stories", script.get("segments", []))
        for i, story in enumerate(stories):
            sid        = story.get("id", "").upper()
            cold_open  = story.get("cold_open", {})
            cta        = story.get("cta", {})
            transition = story.get("transition", {})
            print(f"  [CHAPTER {i+1}: {sid}]")
            print(f"  ❄️  Cold:       {cold_open.get('dialogue','')[:65]}")
            print(f"  🐂 Bull:       {story.get('bull',{}).get('dialogue','')[:60]}")
            print(f"  🐻 Bear:       {story.get('bear',{}).get('dialogue','')[:60]}")
            print(f"  📢 CTA:        {cta.get('dialogue','')[:60]}")
            if transition:
                print(f"  ➡️  Transition: {transition.get('dialogue','')[:65]}")
                # Show next chapter cold_open for verification
                if i + 1 < len(stories):
                    next_cold = stories[i+1].get("cold_open", {}).get("dialogue", "")
                    print(f"  ↳  Next cold:  {next_cold[:65]}")
            print()

        return script

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        episode_date = datetime.now().strftime('%Y%m%d')
        os.makedirs(f"output/episodes/{episode_date}", exist_ok=True)
        with open(f"output/episodes/{episode_date}/debug_raw.txt", "w", encoding="utf-8") as f:
            f.write(raw)
        return None
    except Exception as e:
        print(f"❌ Failed: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_topics = {
        "market": {
            "title": "S&P 500 drops 2% on weak jobs data",
            "description": "Markets fell sharply. Fed signals no rate cuts. Mortgage rates 7.5%."
        },
        "trump": {
            "title": "Trump announces 25% tariff on all Canadian imports",
            "description": "25% tariffs signed. Canada retaliates $20.7B. Auto prices up $3,000."
        },
        "geo": {
            "title": "OpenAI says GPT-5 can replace 50% of white collar jobs",
            "description": "GPT-5 launched. OpenAI CEO says 50 million white collar jobs at risk in 5 years."
        },
        "crypto": {
            "title": "Bitcoin holds $85k as ETF inflows hit $2B",
            "description": "BTC holding at $85,400. BNB up 8%. Gold at $2,340.",
            "prices": {"btc": 85400, "bnb": 580, "gold": 2340}
        },
        "struggle": {
            "title": "Viral: Man quits job after ChatGPT writes his resignation letter",
            "description": "Story going viral with 2M views. AI now writing major life decisions."
        }
    }
    script = write_episode_script(test_topics)