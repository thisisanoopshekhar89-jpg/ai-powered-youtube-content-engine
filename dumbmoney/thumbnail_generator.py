# ============================================================
# THE DUMB MONEY CLUB — THUMBNAIL GENERATOR v1
# Auto-generates YouTube thumbnails from script data
# 1280x720 — YouTube standard
# Called automatically from main.py after script is written
# ============================================================

import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE_DIR   = Path(__file__).parent.parent
ASSETS     = BASE_DIR / "assets"
BULL_DIR   = ASSETS / "characters" / "bull" / "bull_v2"
BEAR_DIR   = ASSETS / "characters" / "bear" / "bear_v2"
OUTPUT_DIR = BASE_DIR / "output" / "thumbnails"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Thumbnail dimensions — YouTube standard
WIDTH  = 1280
HEIGHT = 720

# Expression to use per chapter type
CHAPTER_EXPRESSIONS = {
    "global_news":   {"bull": "adbhuta",      "bear": "adjusting_glasses"},
    "name_said_what":{"bull": "exaggerated_laugh", "bear": "told_you_so"},
    "market_update": {"bull": "excited_arms_up",   "bear": "chart_face"},
    "viral_moment":  {"bull": "hasya",         "bear": "almost_smiled"},
    "the_closer":    {"bull": "thinking",      "bear": "neutral"},
}

# Background colors per chapter
CHAPTER_COLORS = {
    "global_news":    "#1a1a2e",   # deep navy
    "name_said_what": "#16213e",   # dark blue
    "market_update":  "#0f3460",   # rich blue
    "viral_moment":   "#1b1b2f",   # deep purple
    "the_closer":     "#0d0d0d",   # near black
}

# Accent colors per chapter
ACCENT_COLORS = {
    "global_news":    "#e94560",   # red
    "name_said_what": "#f5a623",   # amber
    "market_update":  "#00d4aa",   # teal
    "viral_moment":   "#a855f7",   # purple
    "the_closer":     "#f59e0b",   # gold
}


def get_png(character, expression):
    """Get character PNG — fallback to neutral if not found."""
    d    = BULL_DIR if character == "BULL" else BEAR_DIR
    path = d / f"{expression}.png"
    if path.exists():
        return path
    return d / "neutral.png"


def load_font(size, bold=False):
    """Load a font — tries common Windows fonts, falls back to default."""
    font_paths = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/ariblk.ttf",   # Arial Black
        "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
        "C:/Windows/Fonts/arial.ttf",
        "C:/Users/ASUS/AppData/Local/Microsoft/Windows/Fonts/Poppins-SemiBold.ttf",
    ]
    for fp in font_paths:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()


def draw_text_with_shadow(draw, text, position, font, color, shadow_color="#000000", shadow_offset=4):
    """Draw text with drop shadow for readability."""
    x, y = position
    # Shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    draw.text((x - shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    draw.text((x + shadow_offset, y - shadow_offset), text, font=font, fill=shadow_color)
    draw.text((x - shadow_offset, y - shadow_offset), text, font=font, fill=shadow_color)
    # Main text
    draw.text((x, y), text, font=font, fill=color)


def wrap_text_to_width(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels."""
    words  = text.split()
    lines  = []
    current = ""

    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        w    = bbox[2] - bbox[0]
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def generate_thumbnail(script, episode_date, story_index=None):
    """
    Generate thumbnail for the main episode.
    Uses the most impactful chapter (highest score) or specified story_index.
    Returns path to saved thumbnail.
    """
    stories = script.get("stories", script.get("segments", []))
    if not stories:
        print("  ⚠️  No stories for thumbnail")
        return None

    # Pick the story to feature — default to global_news or first story
    if story_index is not None and story_index < len(stories):
        story = stories[story_index]
    else:
        # Prefer global_news or name_said_what for main thumbnail
        story = stories[0]
        for s in stories:
            if s.get("id") in ["global_news", "name_said_what"]:
                story = s
                break

    story_id     = story.get("id", "global_news")
    thumbnail_text = script.get("seo", {}).get("thumbnail_text", "")

    if not thumbnail_text:
        # Fallback — use episode title
        thumbnail_text = script.get("title", "Smart Money. Stupid World.")

    # Clean text
    thumbnail_text = thumbnail_text.upper()

    # Get expressions and colors
    exprs      = CHAPTER_EXPRESSIONS.get(story_id, CHAPTER_EXPRESSIONS["global_news"])
    bg_color   = CHAPTER_COLORS.get(story_id, "#1a1a2e")
    accent     = ACCENT_COLORS.get(story_id, "#e94560")

    # ── Build canvas ──────────────────────────────────────────
    img  = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    # Gradient overlay — darker on left for text, lighter on right for character
    for x in range(WIDTH):
        alpha = int(180 * (1 - x / WIDTH))
        draw.line([(x, 0), (x, HEIGHT)], fill=(*_hex_to_rgb(bg_color), alpha))

    # ── Place Bear on RIGHT side ──────────────────────────────
    bear_expr = exprs["bear"]
    bear_path = get_png("BEAR", bear_expr)

    if bear_path.exists():
        bear_img = Image.open(bear_path).convert("RGBA")

        # Scale Bear to 65% of thumbnail height
        bear_h    = int(HEIGHT * 0.85)
        bear_ratio= bear_img.width / bear_img.height
        bear_w    = int(bear_h * bear_ratio)
        bear_img  = bear_img.resize((bear_w, bear_h), Image.LANCZOS)

        # Position — right side, bottom aligned
        bear_x = WIDTH - bear_w - 20
        bear_y = HEIGHT - bear_h - 10

        img.paste(bear_img, (bear_x, bear_y), bear_img)

    # ── Place Bull on RIGHT side (slightly behind Bear) ───────
    bull_expr = exprs["bull"]
    bull_path = get_png("BULL", bull_expr)

    if bull_path.exists():
        bull_img = Image.open(bull_path).convert("RGBA")

        # Scale Bull slightly smaller than Bear
        bull_h    = int(HEIGHT * 0.75)
        bull_ratio= bull_img.width / bull_img.height
        bull_w    = int(bull_h * bull_ratio)
        bull_img  = bull_img.resize((bull_w, bull_h), Image.LANCZOS)

        # Position — slightly left of Bear, bottom aligned
        bull_x = WIDTH - bear_w - bull_w + 60
        bull_y = HEIGHT - bull_h - 10

        img.paste(bull_img, (bull_x, bull_y), bull_img)

    # ── Accent bar on left edge ───────────────────────────────
    draw.rectangle([(0, 0), (12, HEIGHT)], fill=accent)

    # ── Channel name — top left ───────────────────────────────
    font_small  = load_font(32)
    channel_tag = "THE DUMB MONEY CLUB"
    draw.text((30, 28), channel_tag, font=font_small, fill=accent)

    # ── Main headline text — left side ────────────────────────
    font_large = load_font(96)
    font_med   = load_font(72)

    # Available width for text — left 55% of thumbnail
    text_max_w = int(WIDTH * 0.55)
    text_x     = 30

    # Try large font first, fall back to medium if too many lines
    lines = wrap_text_to_width(thumbnail_text, font_large, text_max_w, draw)

    if len(lines) > 3:
        lines = wrap_text_to_width(thumbnail_text, font_med, text_max_w, draw)
        font_use = font_med
        line_h   = 80
    else:
        font_use = font_large
        line_h   = 105

    # Center text block vertically
    total_h  = len(lines) * line_h
    text_y   = (HEIGHT - total_h) // 2 - 20

    for line in lines:
        draw_text_with_shadow(
            draw, line,
            (text_x, text_y),
            font_use,
            color="white",
            shadow_color="#000000",
            shadow_offset=5
        )
        text_y += line_h

    # ── Tagline below main text ───────────────────────────────
    font_tag = load_font(34)
    tagline  = "Smart Money. Stupid World."
    draw_text_with_shadow(
        draw, tagline,
        (text_x, text_y + 10),
        font_tag,
        color=accent,
        shadow_color="#000000",
        shadow_offset=3
    )

    # ── Bull/Bear label badges ────────────────────────────────
    # Bottom left
    font_badge = load_font(28)
    draw.rectangle([(30, HEIGHT - 60), (190, HEIGHT - 20)], fill=accent)
    draw.text((40, HEIGHT - 55), "🐂 BULL vs 🐻 BEAR", font=font_badge, fill="white")

    # ── Save ──────────────────────────────────────────────────
    out_path = OUTPUT_DIR / f"thumbnail_{episode_date}.jpg"
    img.convert("RGB").save(str(out_path), "JPEG", quality=95)
    print(f"  ✅ Thumbnail saved: {out_path.name}")
    return str(out_path)


def generate_short_thumbnail(script, episode_date, story_index, short_index):
    """
    Generate thumbnail for a specific short.
    Each short gets its own thumbnail based on its chapter.
    """
    stories = script.get("stories", script.get("segments", []))
    if story_index >= len(stories):
        return None

    story    = stories[story_index]
    story_id = story.get("id", "global_news")

    # Get short hook as text
    short_data = story.get("short", {})
    hook       = short_data.get("hook", story.get("hook", ""))

    # Take first 4-5 words for thumbnail
    words = hook.upper().split()
    text  = " ".join(words[:5])
    if len(words) > 5:
        text += "..."

    exprs    = CHAPTER_EXPRESSIONS.get(story_id, CHAPTER_EXPRESSIONS["global_news"])
    bg_color = CHAPTER_COLORS.get(story_id, "#1a1a2e")
    accent   = ACCENT_COLORS.get(story_id, "#e94560")

    img  = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    # Accent bar
    draw.rectangle([(0, 0), (12, HEIGHT)], fill=accent)

    # Character — use Bear for most shorts (more authoritative)
    char      = "BEAR" if story_id != "viral_moment" else "BULL"
    char_expr = exprs["bear"] if char == "BEAR" else exprs["bull"]
    char_path = get_png(char, char_expr)

    if char_path.exists():
        char_img   = Image.open(char_path).convert("RGBA")
        char_h     = int(HEIGHT * 0.90)
        char_ratio = char_img.width / char_img.height
        char_w     = int(char_h * char_ratio)
        char_img   = char_img.resize((char_w, char_h), Image.LANCZOS)
        char_x     = WIDTH - char_w - 10
        char_y     = HEIGHT - char_h
        img.paste(char_img, (char_x, char_y), char_img)

    # Text
    font_large = load_font(88)
    font_med   = load_font(64)
    text_max_w = int(WIDTH * 0.58)

    lines = wrap_text_to_width(text, font_large, text_max_w, draw)
    if len(lines) > 3:
        lines    = wrap_text_to_width(text, font_med, text_max_w, draw)
        font_use = font_med
        line_h   = 75
    else:
        font_use = font_large
        line_h   = 98

    total_h = len(lines) * line_h
    text_y  = (HEIGHT - total_h) // 2 - 20

    for line in lines:
        draw_text_with_shadow(draw, line, (30, text_y), font_use, "white", "#000000", 5)
        text_y += line_h

    # Shorts badge
    font_badge = load_font(30)
    draw.rectangle([(30, HEIGHT - 65), (170, HEIGHT - 20)], fill=accent)
    draw.text((40, HEIGHT - 58), "#SHORTS", font=font_badge, fill="white")

    # Save
    out_path = OUTPUT_DIR / f"thumbnail_{episode_date}_short{short_index+1}.jpg"
    img.convert("RGB").save(str(out_path), "JPEG", quality=95)
    print(f"  ✅ Short thumbnail {short_index+1}: {out_path.name}")
    return str(out_path)


def _hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_all_thumbnails(script, episode_date):
    """
    Generate main episode thumbnail + 5 short thumbnails.
    Called from main.py after script is written.
    Returns dict of thumbnail paths.
    """
    print("\n🖼️  Generating thumbnails...")

    thumbnails = {}

    # Main episode thumbnail
    main_thumb = generate_thumbnail(script, episode_date)
    if main_thumb:
        thumbnails["episode"] = main_thumb

    # Short thumbnails — one per story
    stories = script.get("stories", script.get("segments", []))
    for i, story in enumerate(stories):
        thumb = generate_short_thumbnail(script, episode_date, i, i)
        if thumb:
            thumbnails[f"short_{i+1}"] = thumb

    print(f"  ✅ {len(thumbnails)} thumbnails generated")
    return thumbnails


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    # Test with dummy script
    test_script = {
        "title": "America owes $10 trillion and nobody is talking about it",
        "seo": {
            "thumbnail_text": "America owes $10 trillion. Guess who pays."
        },
        "stories": [
            {
                "id": "global_news",
                "title": "Chapter 1 — America's $10 Trillion Problem",
                "hook": "America owes more than any country in history",
                "short": {
                    "hook": "America owes the planet 10 trillion dollars"
                }
            },
            {
                "id": "name_said_what",
                "title": "Chapter 2 — Trump Said WHAT??",
                "hook": "Trump said tariffs will make America rich",
                "short": {
                    "hook": "Trump said tariffs would lower your grocery bill"
                }
            },
            {
                "id": "market_update",
                "title": "Chapter 3 — Market Update",
                "hook": "Your money did something today",
                "short": {
                    "hook": "Bitcoin at 71 thousand dollars. Your groceries cost more."
                }
            },
            {
                "id": "viral_moment",
                "title": "Chapter 4 — AI Takes Another Job",
                "hook": "AI just replaced someone you know",
                "short": {
                    "hook": "This AI just did something that should scare you"
                }
            },
            {
                "id": "the_closer",
                "title": "Chapter 5 — The Closer",
                "hook": "Bear said something tonight",
                "short": {
                    "hook": "Bear said something true tonight"
                }
            }
        ]
    }

    date   = "20260408"
    thumbs = generate_all_thumbnails(test_script, date)
    print(f"\nGenerated: {list(thumbs.keys())}")
    print(f"Saved to: {OUTPUT_DIR}")