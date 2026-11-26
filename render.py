#!/usr/bin/env python3
"""Draw THE WORLD TODAY for Thursday 26 November 2026 (1024x1024 PNG).

A code-drawn newspaper front page: masthead, a lead story on the
Houthis' claimed Ras Tanura strike and Brent over $94, two second
stories (the deepening AI rout, five Russian jets hit at Savasleyka),
a markets strip, a 30-item digest and a footer ticker — 39 verified
stories, listed in news-20261126-shortlist.md.

Flat shapes and type only; no photographs, no copied images.
Deterministic: running it twice writes identical bytes.
"""

import math
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 28
INNER = PAGE - 2 * MARGIN

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (249, 245, 234)
INK = (22, 22, 22)
MUTED = (102, 97, 86)
RULE = (198, 192, 178)
CARDLINE = (205, 199, 185)
RED = (172, 32, 22)
BLUE = (26, 74, 132)
GREEN = (16, 102, 86)
PURPLE = (88, 56, 138)
OCHRE = (164, 98, 0)
ROSE = (146, 38, 88)
TEAL = (43, 107, 119)
NIGHT = (30, 32, 38)
DUSK = (233, 176, 92)
SKY = (214, 228, 240)
FLAME = (226, 110, 30)

KIND_COLOUR = {
    "WORLD": RED,
    "US": BLUE,
    "TECH": PURPLE,
    "ASIA": OCHRE,
    "SPORT": ROSE,
    "CLIMATE": GREEN,
    "EUROPE": TEAL,
}

DIGEST = [
    ("WORLD", "Third tanker and an LNG carrier hit mines off Hormuz, Iran says."),
    ("WORLD", "US tells its citizens to leave Iran immediately."),
    ("WORLD", "Hormuz crude flows down 31% to an eight-week low."),
    ("WORLD", "OPEC+ meets Sunday to decide 2027 output policy."),
    ("US", "Fed Beige Book: modest growth, wage gains, price pressure."),
    ("US", "Trump spares Thanksgiving turkeys Liberty and Liberty."),
    ("TECH", "Nvidia's Huang resigned 12 Nov; Kress is interim chief."),
    ("TECH", "US tightens remote AI chip access; B300 GPUs seek buyers."),
    ("TECH", "FCC lets SpaceX put 1,000,000 data centres in space."),
    ("WORLD", "Israeli judges urge dropping top charges v Netanyahu."),
    ("WORLD", "Israel kills a new Hamas internal security chief."),
    ("WORLD", "Melania helps reunite nine more children with families."),
    ("EUROPE", "EU hunts for a new ECB chief as Lagarde resigns."),
    ("EUROPE", "Russia's military budget surges; EU budget advances."),
    ("EUROPE", "Norway court voids climate-disputed oil licences."),
    ("WORLD", "At least 30 killed in Cairo fuel-tanker fire."),
    ("WORLD", "At least 30 killed in attacks in Nigeria's Niger State."),
    ("ASIA", "Rioters burn at least 100 Grameen Bank branches."),
    ("ASIA", "North Korea orders Swiss office in Pyongyang shut."),
    ("ASIA", "India marks Constitution Day; Rs15,000cr package for Nepal."),
    ("ASIA", "India urges human control over AI in warfare."),
    ("ASIA", "Pakistan's first astronaut reaches China's space station."),
    ("ASIA", "Sheikh Hasina seeks return to Bangladesh on 16 Dec."),
    ("WORLD", "Hera heads to inspect the asteroid-test crater."),
    ("WORLD", "Kenya clears last Ebola patient; DRC toll tops 5,300."),
    ("WORLD", "Australia apologises to LGBTQ service members."),
    ("WORLD", "ECOWAS sets 2027 date for its regional security force."),
    ("SPORT", "1,220 players register for the IPL 2027 auction."),
    ("SPORT", "Gukesh faces Sindarov in the World Chess Championship."),
    ("SPORT", "Sooryavanshi smashes 204 off 53 balls v UAE."),
]

TICKER = [
    "US ARMY: IOWA BLAST A 'HUGE SUCCESS'",
    "GHANA UNVEILS HERITAGE BANKNOTES",
    "KENYA WINS 293,600 SAUDI JOBS",
    "5.7 QUAKE OFF ANTARCTICA",
    "BEARS KILL 37 IN RUSSIA THIS YEAR",
    "WARSAW TEEN HELD OVER SCHOOL PLOT",
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    """Greedy word wrap into lines no wider than width."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def rule(d, x0, y, x1, colour=RULE, thick=1):
    for k in range(thick):
        d.line([(x0, y + k), (x1, y + k)], fill=colour)


def centre(d, cx, y, text, fnt, colour=INK):
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=colour)


def draw_masthead(d):
    title = font(SERIF_B, 62)
    centre(d, PAGE / 2, 24, "THE WORLD TODAY", title, INK)
    rule(d, MARGIN, 94, PAGE - MARGIN, INK, 2)
    dateline = font(SANS_B, 14)
    centre(
        d,
        PAGE / 2,
        102,
        "THURSDAY 26 NOVEMBER 2026  \u00b7  WORLD EDITION  \u00b7  39 STORIES",
        dateline,
        INK,
    )
    rule(d, MARGIN, 124, PAGE - MARGIN, INK, 1)


def refinery_scene(d, x0, y0, x1, y1):
    """Flat drawing of a refinery at dusk: towers, flare stack, smoke."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    # low sun behind the towers
    d.ellipse([x1 - 58, y0 + 12, x1 - 24, y0 + 46], fill=DUSK)
    # ground band
    d.rectangle([x0, y0 + 118, x1, y1], fill=(52, 58, 64))
    # distillation towers of different heights
    for tx, th, tw in [(x0 + 16, 66, 26), (x0 + 52, 84, 22), (x0 + 84, 58, 30)]:
        d.rectangle([tx, y0 + 118 - th, tx + tw, y0 + 118], fill=(38, 40, 46))
        d.rectangle([tx - 3, y0 + 118 - th - 6, tx + tw + 3, y0 + 118 - th], fill=(38, 40, 46))
    # storage tanks
    for tx in (x0 + 128, x0 + 168):
        d.ellipse([tx, y0 + 88, tx + 34, y0 + 100], fill=(222, 222, 214))
        d.rectangle([tx, y0 + 94, tx + 34, y0 + 118], fill=(222, 222, 214))
    # flare stack with flame
    fx = x1 - 34
    d.rectangle([fx - 5, y0 + 34, fx + 5, y0 + 118], fill=(38, 40, 46))
    d.polygon(
        [(fx - 12, y0 + 34), (fx + 12, y0 + 34), (fx, y0 + 6)],
        fill=FLAME,
    )
    d.ellipse([fx - 7, y0 + 20, fx + 7, y0 + 34], fill=(240, 170, 60))
    # smoke puffs drifting left from the flare
    for sx, sy, sr in [(fx - 26, y0 + 22, 9), (fx - 46, y0 + 14, 12), (fx - 70, y0 + 8, 10)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(238, 238, 232))
    # caption strip
    cap = font(SANS_B, 11)
    d.text((x0 + 10, y1 - 16), "RAS TANURA, SAUDI ARABIA", font=cap, fill=(255, 255, 255))


def lead_block(d):
    x0, x1 = MARGIN, MARGIN + 660
    y = 138
    kick = font(SANS_B, 15)
    d.text((x0, y), "GULF WAR \u00b7 OIL", font=kick, fill=RED)
    head = font(SERIF_B, 32)
    d.text((x0, y + 24), "Brent tops $94 as Houthis claim", font=head, fill=INK)
    d.text((x0, y + 60), "strike on Ras Tanura refinery", font=head, fill=INK)
    deck = font(SANS_R, 15)
    yy = y + 100
    for line in wrap(
        d,
        "Riyadh says it shot down four drones over the kingdom's largest "
        "refinery; the claim of a hit is unconfirmed. WTI rose 2% to $83.68.",
        deck,
        x1 - x0,
    ):
        d.text((x0, yy), line, font=deck, fill=INK)
        yy += 20
    body = font(SANS_R, 13)
    yy += 8
    for line in wrap(
        d,
        "The Houthis also struck Saudi Red Sea ports, and a third tanker "
        "and an LNG carrier hit mines in the Strait of Hormuz, where crude "
        "flows are down 31%. The US told its citizens to leave Iran at once.",
        body,
        x1 - x0,
    ):
        d.text((x0, yy), line, font=body, fill=MUTED)
        yy += 17
    refinery_scene(d, 712, 138, PAGE - MARGIN, 328)


def story_card(d, x0, x1, y0, y1, tag, tint, headlines, body_text, graphic):
    d.rectangle([x0, y0, x1, y1], outline=CARDLINE, width=1)
    d.rectangle([x0, y0, x1, y0 + 4], fill=tint)
    kick = font(SANS_B, 13)
    d.text((x0 + 12, y0 + 12), tag, font=kick, fill=tint)
    head = font(SERIF_B, 23)
    yy = y0 + 34
    for line in headlines:
        d.text((x0 + 12, yy), line, font=head, fill=INK)
        yy += 28
    body = font(SANS_R, 12)
    for line in wrap(d, body_text, body, x1 - x0 - 24):
        d.text((x0 + 12, yy), line, font=body, fill=MUTED)
        yy += 16
    graphic(d, x0, x1, yy, y1)


def market_chart(d, x0, x1, y_top, y_bot):
    """Vertical bars: two falls, two rallies (DOW is in the strip)."""
    vals = [("NASDAQ", -4.0), ("TAIEX", -4.8), ("BRENT", 3.5), ("WTI", 2.0)]
    lab = font(SANS_B, 10)
    num = font(SANS_B, 10)
    n = len(vals)
    slot = (x1 - x0 - 24) / n
    base = y_bot - 14
    span = base - (y_top + 2)
    for i, (name, v) in enumerate(vals):
        cx = x0 + 12 + slot * i + slot / 2
        hgt = max(6, abs(v) / 5.0 * span)
        col = GREEN if v > 0 else RED
        d.rectangle([cx - 15, base - hgt, cx + 15, base], fill=col)
        vt = f"{'+' if v > 0 else ''}{v}%"
        vw = d.textlength(vt, font=num)
        if hgt >= 16:
            # value sits inside the bar, in white
            d.text((cx - vw / 2, base - hgt + 3), vt, font=num, fill=(255, 255, 255))
        else:
            d.text((cx - vw / 2, base - hgt - 13), vt, font=num, fill=col)
        nw = d.textlength(name, font=lab)
        d.text((cx - nw / 2, base + 3), name, font=lab, fill=MUTED)


def jets_stat(d, x0, x1, y_top, y_bot):
    big = font(SERIF_B, 30)
    small = font(SANS_B, 11)
    label = "5 jets hit"
    d.text((x0 + 12, y_top + 2), label, font=big, fill=RED)
    gap = d.textlength(label, font=big)
    d.text((x0 + 12 + gap + 12, y_top + 14), "3 MiG-31s, 2 Su-34s", font=small, fill=INK)
    d.text((x0 + 12, y_top + 40), "88 OF 112 DRONES DOWN  \u00b7  POLAND SEEKS NO-FLY ZONE",
           font=small, fill=MUTED)


def second_row(d):
    y0, y1 = 340, 510
    story_card(
        d, MARGIN, MARGIN + 476, y0, y1,
        "MARKETS \u00b7 AI ROUT", RED,
        ["Nasdaq sinks nearly 4%", "as the AI rout deepens"],
        "Taiwan's Taiex fell 1,927 points on a US plan for 15% tariffs "
        "on its goods; US markets shut for Thanksgiving.",
        market_chart,
    )
    story_card(
        d, MARGIN + 492, PAGE - MARGIN, y0, y1,
        "UKRAINE WAR", BLUE,
        ["Five Russian jets hit", "at Savasleyka airbase"],
        "Kyiv says three MiG-31s and two Su-34s were hit overnight, and "
        "Poland asked NATO to shoot down Russian missiles over Ukraine.",
        jets_stat,
    )


def strip_line(d):
    fnt = font(SANS_B, 14)
    centre(
        d, PAGE / 2, 520,
        "BRENT $94.61 +3.5%  \u00b7  WTI $83.68 +2%  \u00b7  NASDAQ \u22124%  \u00b7  "
        "TAIEX 38,195 \u22124.8%  \u00b7  DOW CLOSED \u2014 THANKSGIVING",
        fnt, INK,
    )
    rule(d, MARGIN, 546, PAGE - MARGIN, INK, 1)


def digest_block(d):
    head = font(SANS_B, 14)
    d.text((MARGIN, 558), "THE DAY IN BRIEF", font=head, fill=INK)
    rule(d, MARGIN + 150, 566, PAGE - MARGIN, RULE, 1)
    tag_fnt = font(SANS_B, 11)
    txt_fnt = font(SANS_R, 11)
    col_w = 476
    halves = (DIGEST[:15], DIGEST[15:])
    for ci, items in enumerate(halves):
        x = MARGIN + ci * (col_w + 16)
        y = 584
        for tag, text in items:
            col = KIND_COLOUR[tag]
            d.text((x, y), tag, font=tag_fnt, fill=col)
            tw = d.textlength(tag + "  ", font=tag_fnt)
            line = text
            while d.textlength(line, font=txt_fnt) > col_w - tw and len(line) > 10:
                line = line.rsplit(" ", 1)[0]
            d.text((x + tw, y), line, font=txt_fnt, fill=INK)
            y += 24


def footer_bar(d):
    d.rectangle([MARGIN, 950, PAGE - MARGIN, 998], fill=NIGHT)
    fnt = font(SANS_B, 11)
    top = "  \u00b7  ".join(TICKER[:3])
    bot = "  \u00b7  ".join(TICKER[3:])
    centre(d, PAGE / 2, 958, top, fnt, (236, 233, 225))
    centre(d, PAGE / 2, 976, bot, fnt, (236, 233, 225))


def render(out_path):
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    lead_block(d)
    second_row(d)
    strip_line(d)
    digest_block(d)
    footer_bar(d)
    img.save(out_path, "PNG")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
