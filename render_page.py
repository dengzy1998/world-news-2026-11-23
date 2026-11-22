#!/usr/bin/env python3
"""Draw the Monday 23 November 2026 world-news front page, v1.

One 1024 by 1024 newspaper page holding 44 sourced stories from Monday
23 November 2026 (v1: the Asian morning plus US Sunday sport that falls
on Nov 23 in Asia/UTC; Europe and the Americas still to come): a big date masthead and kicker, region tabs with story
counts, a six-cell stat strip, a UTC/IST timeline, three illustrated lead
cards with flat drawn art, eight numbered grid cards with small art strips,
a dotted world map carrying numbered pins for stories 1-11, a two-column
list of 20 further stories, a DATE CHECK box naming older stories left
out on purpose, and a footer defining CLAIM and listing sources.
Rendering is deterministic: two runs write byte-identical files.
"""

import math
import os.path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "entry.png")

W = 1024
H = 1024
MARGIN = 16
CW = W - 2 * MARGIN

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

PAPER = (247, 243, 233)
INK = (24, 24, 24)
RED = (176, 28, 40)
GREY = (92, 90, 84)
FAINT = (196, 188, 164)
CARD = (252, 250, 244)
BODY = (50, 50, 48)

REGION_COLOUR = {
    "EUROPE": (31, 58, 95),
    "AMERICAS": (140, 44, 62),
    "ASIA-PACIFIC": (13, 110, 102),
    "MIDEAST": (196, 110, 20),
    "AFRICA": (62, 120, 44),
    "OCEANIA": (96, 62, 140),
    "WORLD": (96, 96, 96),
}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(pen, text, fnt, limit):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if pen.textlength(trial, font=fnt) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(pen, text, fnt, x, y, limit, leading, fill=INK, max_lines=None):
    rows = wrap(pen, text, fnt, limit)
    if max_lines and len(rows) > max_lines:
        rows = rows[:max_lines]
        tail = rows[-1]
        while tail and pen.textlength(tail + "...", font=fnt) > limit:
            tail = tail[:-1]
        rows[-1] = tail.rstrip() + "..."
    for row in rows:
        pen.text((x, y), row, font=fnt, fill=fill)
        y += leading
    return y


def centred(pen, text, fnt, y, fill=INK):
    wide = pen.textlength(text, font=fnt)
    pen.text(((W - wide) / 2, y), text, font=fnt, fill=fill)


def rule(pen, x0, x1, y, width=2, fill=INK):
    pen.line([(x0, y), (x1, y)], fill=fill, width=width)


# ------------------------------------------------------------------- stories

LEADS = [
    {
        "n": 1, "tag": "WELLINGTON - CRICKET", "region": "OCEANIA",
        "art": "cricket",
        "cap": "BASIN RESERVE - DAY 5, 119/2",
        "head": "Day Five: India Chase History in Wellington",
        "body": ("New Zealand resume on 119/2, still 233 behind after "
                 "India's record 720/9 declared - the highest Test total "
                 "on Kiwi soil. India need eight wickets for a first "
                 "Test win in NZ since 2009. "
                 "(NDTV, NZ Herald)"),
    },
    {
        "n": 2, "tag": "ANTALYA - CLIMATE", "region": "WORLD",
        "art": "summit",
        "cap": "ANTALYA - NO DEAL, FALLOUT MONDAY",
        "head": "COP31 Fallout: No Deal, and a $150m Question",
        "body": ("After Sunday's collapse - the EU rejected a "
                 "fossil-fuel-free text - Australia faces questions over "
                 "its ~$150m co-host bill as the PM's poll slides. "
                 "(Squiz, AAP)"),
    },
    {
        "n": 3, "tag": "CANBERRA - POLITICS", "region": "OCEANIA",
        "art": "parliament",
        "cap": "CANBERRA - NEWSPOLL, NOV 23",
        "head": "Albanese Trails Taylor as Preferred PM",
        "body": ("Newspoll: the PM falls behind the Coalition leader for "
                 "the first time; net approval hits a new low of -31. "
                 "Labor and One Nation tie on 27%; the Coalition on 22%. "
                 "(The Australian, AAP)"),
    },
]

# (number, tag, region, headline, body, art motif)
GRID = [
    (4, "MEXICO CITY - NFL", "AMERICAS",
     "First Sunday Night Football Outside the US",
     "The 8-1 49ers host the 7-2 Vikings at Estadio Banorte; "
     "kick-off 01:20 UTC. (NBC, DAZN)", "flag"),
    (5, "DALLAS - NFL", "AMERICAS",
     "Prescott's Five TDs Rout the Titans 51-30",
     "Dak Prescott throws for 325 yards and four TDs and runs in "
     "another as Dallas score on eight straight drives. (NBC)", "ball"),
    (6, "KANSAS CITY - NFL", "AMERICAS",
     "Chiefs Cruise 34-7 as Kelce Marks 100th at Arrowhead",
     "Mahomes throws for 324 yards and three TDs; Kelce catches "
     "two in his 100th home game. (NBC)", "trophy"),
    (7, "CHARLOTTE - NFL", "AMERICAS",
     "Panthers Edge Ravens 35-33 in Seven-Lead-Change Thriller",
     "A 37-yard field goal with 1:44 left seals it; Baltimore "
     "lose a sixth straight. (NBC)", "ball"),
    (8, "KYIV - WAR", "EUROPE",
     "Kyiv Region Mourns as Dymer Toll Rises to Three",
     "Nov 23 is a day of mourning after Sunday's drone strike on "
     "a five-storey block; 15 people still unreachable. (NV)", "missile"),
    (9, "CANBERRA - POLITICS", "OCEANIA",
     "Seven in 10 MPs Say Politics Harmed Their Mental Health",
     "A landmark survey finds most MPs report damage to their "
     "mental health; some had thoughts of suicide. (ABC)", "megaphone"),
    (10, "SYDNEY - AI", "OCEANIA",
     "Australia to Put AI Guardrails at Foreign Policy's Heart",
     "Foreign Minister Wong will warn AI is a national-security "
     "challenge in a major speech on Tuesday. (AAP)", "chip"),
    (11, "NEW DELHI - DIPLOMACY", "ASIA-PACIFIC",
     "Modi and Nepal's Shah Talk Energy and Rail Today",
     "The two PMs meet in Delhi on hydropower, energy and "
     "connectivity between the neighbours. (Mathrubhumi)", "deal"),
]

# (number, one-line story, region)
MORE = [
    (12, "Bills 26-9 Dolphins; Buffalo improve to 9-1. (Nov 23 Asia)", "AMERICAS"),
    (13, "Bears 21-13 Saints; Chicago move to 8-2. (Nov 23 Asia)", "AMERICAS"),
    (14, "Lions 31-21 Buccaneers; Detroit go 8-2. (Nov 23 Asia)", "AMERICAS"),
    (15, "Eagles 19-16 Steelers in Philadelphia. (Nov 23 Asia)", "AMERICAS"),
    (16, "Jets lead Chargers 10-3 at half-time; Broncos 10-0 Raiders. (live)", "AMERICAS"),
    (17, "NBA Sunday slate under way; Hawks lead Pistons. (live)", "AMERICAS"),
    (18, "Australia v England T20 at the MCG tonight; two debut. (fixture)", "OCEANIA"),
    (19, "JEE Main 2027 Session 1 registration closes today.", "ASIA-PACIFIC"),
    (20, "Delhi HC hears Krishi Bhawan mosque petitions today.", "ASIA-PACIFIC"),
    (21, "CAQM releases a report card on Delhi-NCR pollution measures.", "ASIA-PACIFIC"),
    (22, "India's oil and gas import bill up 60% to $16bn in Oct. (PPAC)", "ASIA-PACIFIC"),
    (23, "Samajwadi Party forms panel for 2027 UP seat-sharing talks.", "ASIA-PACIFIC"),
    (24, "Tamil Nadu seeks SC review of Karthigai Deepam order.", "ASIA-PACIFIC"),
    (25, "Maharashtra board orders Adani Renewable to stop Satara dig.", "ASIA-PACIFIC"),
    (26, "Non-coal mining clearance decentralised to states.", "ASIA-PACIFIC"),
    (27, "Keralam minister denies differences in state Cabinet.", "ASIA-PACIFIC"),
    (28, "Ladakh political dialogue to resume after Dec 15.", "ASIA-PACIFIC"),
    (29, "Parliament's final sitting week opens; gas, CGT on agenda. (AAP)", "OCEANIA"),
    (30, "Asia Power Index: Australia falls short as US power declines. (AAP)", "OCEANIA"),
    (31, "Schoolboy's 540km trek spotlights the bush health gap. (AAP)", "OCEANIA"),
    (32, "Keeping coal plants running raises blackout risk, cost. (AAP)", "OCEANIA"),
    (33, "Former NSW MP Rev Fred Nile dies aged 92. (Squiz)", "OCEANIA"),
    (34, "Two teens charged over fatal La Trobe St stabbing, Melbourne.", "OCEANIA"),
    (35, "Tokyo market shut for Labor Thanksgiving Day; Nikkei 56,437 Fri.", "ASIA-PACIFIC"),
    (36, "Google to invest $5m in IIT Kharagpur AI research. (Nov 23 brief.)", "ASIA-PACIFIC"),
    (37, "Modi opens AI centre at IIT Patna; Rs 400cr research park. (brief.)", "ASIA-PACIFIC"),
    (38, "India-EU free trade pact likely signed Dec 16 in Brussels. (brief.)", "ASIA-PACIFIC"),
    (39, "CJI calls for legal aid work, AI rules in law courses. (brief.)", "ASIA-PACIFIC"),
    (40, "Mahindra Last Mile Mobility eyes IPO in 18 months. (brief.)", "ASIA-PACIFIC"),
    (41, "Govt tightens terms for seven pre-NELP oil and gas blocks. (brief.)", "ASIA-PACIFIC"),
    (42, "Aluminium makers seek zero import duty ahead of Budget. (brief.)", "ASIA-PACIFIC"),
    (43, "West Bengal may review Class 11-12 semester exam pattern. (brief.)", "ASIA-PACIFIC"),
    (44, "NEET PG: 10,105 medical seats flagged as blocked. (brief.)", "ASIA-PACIFIC"),
]

STATS = [
    ("720/9", "India declared, highest Test total in NZ"),
    ("233", "runs New Zealand still trail by, 119/2"),
    ("51-30", "Cowboys rout the Titans in Dallas"),
    ("35-33", "Panthers edge Ravens, seven lead changes"),
    ("-31", "Albanese net approval, a new low"),
    ("01:20", "UTC: SNF kicks off in Mexico City"),
]

TIMELINE = ("TODAY IN TIME  |  03:31 IST Day 5 begins, Wellington  -  "
             "01:20 UTC 49ers v Vikings kick off, Mexico City  -  "
             "10:00 AEDT Final sitting week opens, Canberra  -  "
             "Evening AEDT Aus v England T20 at the MCG")

EXCLUDED_INTRO = ("These are NOT Sunday's news - older stories left out "
                  "on purpose:")
EXCLUDED = (
    "COP31's closing plenary and the collapse itself (Sun Nov 22; "
    "today's page carries Monday's fallout, story 2); "
    "Liverpool 4-0 Man Utd, Pochettino's debut rout (Nov 22); "
    "Verstappen wins the Las Vegas GP, 35 lead changes (Nov 21-22); "
    "South Korea's education minister quits over AI cheating (Nov 22); "
    "China slams the US FCC telecom ban (Nov 22); "
    "Indonesia candy-factory fire: 7 body bags, ~50 missing (Nov 21-22); "
    "Nigeria boat capsizes: 24 dead (Nov 20-21); "
    "Bahrain says Iran struck a civilian industrial site (Nov 21); "
    "Bangladesh: ~30 Awami League houses torched in Narail (Nov 20-22); "
    "Myanmar calls the ASEAN decision 'unfair' (Nov 21); "
    "Lisbon march over living costs (Nov 21); "
    "Sparta II cargo ship still burning off Finland (Nov 21); "
    "the Dymer drone strike itself (Nov 22; today's page carries the "
    "Nov 23 mourning day, story 8); "
    "Eisenkot-Netanyahu coalition talks resume (Nov 22); "
    "WSJ: Li Ming ran the Nvidia-chip network to China (Nov 21); "
    "NBA Saturday finals: Wembanyama 50, Knicks buzzer-beater (Nov 21); "
    "BepiColombo enters Mercury's orbit (Nov 21); "
    "Russia's Kyiv barrage and the Poland missile spillover (Nov 20).")

FOOTER = ("CLAIM = a claim as reported by the source named, not yet "
          "independently confirmed. v1 covers the Asian morning of Mon 23 Nov "
          "2026 plus US Sunday sport that falls on Nov 23 in Asia/UTC. "
          "Sources: NDTV, NZ Herald, The Squiz, AAP, ABC, Reuters, NBC, "
          "DAZN, The New Voice of Ukraine, Mathrubhumi, Jagran Josh, The "
          "Australian. All illustrations drawn for this page; no photographs.")

# (story number, longitude, latitude) for the map pins
PINS = {
    1: (174.8, -41.3), 2: (30.7, 36.9), 3: (149.1, -35.3),
    4: (-99.1, 19.4), 5: (-96.8, 32.8), 6: (-94.6, 39.1),
    7: (-80.8, 35.2), 8: (30.3, 50.8), 9: (149.1, -35.3),
    10: (151.2, -33.9), 11: (77.2, 28.6),
}

# ------------------------------------------------------- dotted world map

# Rough continent outlines (lon, lat), drawn from general geography.
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-95, 69), (-80, 73), (-65, 60),
     (-55, 52), (-60, 45), (-70, 42), (-75, 35), (-81, 26), (-90, 21),
     (-97, 16), (-105, 20), (-114, 28), (-122, 37), (-125, 48),
     (-135, 58), (-155, 58), (-165, 60)],
    [(-45, 60), (-30, 68), (-22, 70), (-30, 76), (-55, 80), (-58, 72)],
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -27), (-58, -35), (-65, -41), (-68, -52),
     (-71, -54), (-73, -44), (-72, -30), (-70, -19), (-77, -12),
     (-81, -5), (-80, 1)],
    [(-6, 35), (-10, 31), (-15, 27), (-17, 15), (-16, 11), (-11, 6),
     (-8, 4), (9, 4), (13, -2), (12, -6), (13, -12), (12, -18),
     (16, -28), (20, -35), (26, -34), (32, -29), (35, -24), (40, -16),
     (40, -10), (42, -2), (48, 11), (51, 12), (43, 12), (39, 21),
     (38, 28), (35, 31), (30, 31), (22, 33), (11, 34)],
    [(-10, 36), (-9, 43), (-2, 44), (-1, 48), (0, 50), (2, 51), (5, 53),
     (8, 57), (10, 59), (18, 56), (21, 55), (24, 58), (28, 59), (24, 62),
     (22, 65), (25, 68), (30, 70), (35, 66), (32, 60), (30, 55), (28, 50),
     (28, 46), (26, 44), (23, 40), (22, 37), (19, 40), (16, 38), (12, 44),
     (8, 44), (3, 42), (0, 39)],
    [(28, 41), (33, 42), (36, 45), (38, 50), (40, 55), (45, 62), (50, 69),
     (65, 69), (80, 70), (95, 72), (110, 73), (130, 72), (150, 70),
     (170, 66), (178, 65), (170, 60), (162, 56), (156, 51), (150, 45),
     (142, 40), (140, 35), (135, 33), (130, 31), (127, 38), (122, 38),
     (120, 32), (118, 25), (114, 22), (110, 20), (108, 12), (105, 8),
     (103, 2), (100, 6), (97, 15), (94, 17), (91, 22), (88, 22), (86, 20),
     (82, 17), (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25),
     (61, 25), (57, 26), (54, 26), (52, 29), (50, 29), (48, 30), (51, 24),
     (55, 24), (58, 22), (59, 22), (55, 17), (52, 15), (48, 14), (44, 12),
     (43, 13), (40, 20), (38, 25), (36, 30), (34, 31), (36, 36), (30, 36)],
    [(113, -22), (122, -17), (130, -12), (136, -12), (142, -11), (146, -16),
     (150, -22), (153, -27), (150, -37), (146, -39), (140, -38),
     (135, -35), (129, -32), (124, -33), (118, -35), (114, -30),
     (113, -25)],
    [(167, -45), (172, -42), (174, -39), (177, -38), (175, -41), (170, -44)],
]

ISLETS = [
    (-2, 53, 2.5, 3), (139, 37, 3, 4), (113, 0, 7, 2), (122, 13, 2, 4),
    (47, -19, 2, 5), (103, 1, 4, 2), (100, 14, 3, 4),
]


def on_land(lon, lat):
    for poly in LAND:
        inside = False
        last = len(poly) - 1
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[last]
            if ((y1 > lat) != (y2 > lat)) and (
                    lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1):
                inside = not inside
            last = i
        if inside:
            return True
    for clon, clat, rx, ry in ISLETS:
        if ((lon - clon) / rx) ** 2 + ((lat - clat) / ry) ** 2 <= 1:
            return True
    return False


def region_counts():
    tally = {}
    for lead in LEADS:
        tally[lead["region"]] = tally.get(lead["region"], 0) + 1
    for card in GRID:
        tally[card[2]] = tally.get(card[2], 0) + 1
    for item in MORE:
        tally[item[2]] = tally.get(item[2], 0) + 1
    return tally


# ------------------------------------------------------------------ sections

def paint_masthead(pen):
    small = font(SANS_B, 10)
    left = "THE WORLD IN ONE DAY"
    pen.text((MARGIN, 12), left, font=small, fill=INK)
    right = "44 STORIES - 5 REGIONS - ONE PAGE"
    tw = pen.textlength(right, font=small)
    pen.text((MARGIN + CW - tw, 12), right, font=small, fill=INK)
    centred(pen, "Monday 23 November 2026", font(SERIF_B, 40), 26)
    kick = font(SERIF, 13)
    centred(pen, "Day five in Wellington  -  COP31 fallout  -  Albanese trails Taylor",
            kick, 76, fill=RED)
    rule(pen, MARGIN, MARGIN + CW, 96, 3)
    rule(pen, MARGIN, MARGIN + CW, 100, 1)


def paint_tabs(pen, tally):
    order = ["EUROPE", "AMERICAS", "ASIA-PACIFIC", "MIDEAST", "WORLD",
             "OCEANIA"]
    y = 106
    fnt = font(SANS_B, 10)
    x = MARGIN
    for name in order:
        label = "%s %d" % (name, tally.get(name, 0))
        wdt = pen.textlength(label, font=fnt) + 16
        pen.rectangle([x, y, x + wdt, y + 19],
                      fill=REGION_COLOUR[name])
        tw = pen.textlength(label, font=fnt)
        pen.text((x + (wdt - tw) / 2, y + 4), label, font=fnt,
                 fill=(255, 255, 255))
        x += wdt + 4
    note = font(SANS_B, 9)
    s = "ALL STORIES: MON 23 NOV 2026, ANY TIME ZONE"
    tw = pen.textlength(s, font=note)
    pen.text((MARGIN + CW - tw, y + 5), s, font=note, fill=GREY)


def paint_stats(pen):
    y = 132
    gap = 6
    cell_w = (CW - gap * 5) / 6
    big = font(SERIF_B, 20)
    small = font(SANS, 8)
    for i, (num, label) in enumerate(STATS):
        x = MARGIN + i * (cell_w + gap)
        tw = pen.textlength(num, font=big)
        pen.text((x + (cell_w - tw) / 2, y), num, font=big, fill=RED)
        rows = wrap(pen, label, small, cell_w - 6)
        ly = y + 25
        for row in rows[:2]:
            tw = pen.textlength(row, font=small)
            pen.text((x + (cell_w - tw) / 2, ly), row, font=small, fill=INK)
            ly += 10
    rule(pen, MARGIN, MARGIN + CW, y + 46, 1, fill=FAINT)


def paint_timeline(pen):
    fnt = font(SANS_B, 9)
    tw = pen.textlength(TIMELINE, font=fnt)
    pen.text((MARGIN + (CW - tw) / 2, 184), TIMELINE, font=fnt, fill=INK)


# ------------------------------------------------------------- drawn artwork

def draw_globe(pen, cx, cy, r):
    pen.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 48, 96),
                outline=(255, 255, 255), width=2)
    pen.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                outline=(180, 200, 230), width=1)
    pen.line([(cx - r, cy), (cx + r, cy)], fill=(180, 200, 230), width=1)
    pen.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 0, 360,
            fill=(180, 200, 230), width=1)


def draw_lead_art(pen, kind, left, top, right, bottom):
    mid_y = (top + bottom) / 2
    if kind == "summit":
        pen.rectangle([left, top, right, bottom], fill=(16, 22, 44))
        for sx, sy in [(left + 30, top + 14), (left + 90, top + 8),
                       (left + 160, top + 18), (left + 240, top + 10),
                       (left + 290, top + 20)]:
            pen.ellipse([sx - 1, sy - 1, sx + 1, sy + 1],
                        fill=(255, 255, 255))
        draw_globe(pen, left + 62, mid_y + 4, 30)
        for i, col in enumerate([(0, 91, 187), (255, 255, 255),
                                 (206, 17, 38), (0, 122, 51),
                                 (255, 213, 0)]):
            fx = left + 120 + i * 38
            pen.rectangle([fx, mid_y - 14, fx + 28, mid_y + 8], fill=col,
                          outline=(255, 255, 255), width=1)
            pen.line([(fx + 2, mid_y + 8), (fx + 2, mid_y + 22)],
                     fill=(200, 200, 200), width=2)
        pen.text((left + 120, bottom - 16), "ANTALYA, TURKIYE",
                 font=font(SANS_B, 9), fill=(255, 255, 255))
    elif kind == "pentagon":
        pen.rectangle([left, top, right, bottom], fill=(214, 210, 198))
        pen.rectangle([left, top, right, top + 22], fill=(140, 170, 200))
        pen.ellipse([left + 28, top + 8, left + 34, top + 14],
                    fill=(255, 255, 255))
        cx = (left + right) / 2
        cy = mid_y + 6
        pts = []
        for k in range(5):
            ang = -math.pi / 2 + k * 2 * math.pi / 5
            pts.append((cx + 52 * math.cos(ang), cy + 34 * math.sin(ang)))
        pen.polygon(pts, fill=(120, 120, 118), outline=INK)
        pen.polygon([(cx - 26, cy - 8), (cx + 26, cy - 8),
                     (cx + 18, cy + 12), (cx - 18, cy + 12)],
                    fill=(200, 200, 198), outline=INK)
        pen.line([(cx + 62, top + 22), (cx + 62, mid_y + 26)],
                 fill=INK, width=2)
        pen.rectangle([cx + 62, top + 24, cx + 80, top + 34],
                      fill=RED, outline=INK)
    elif kind == "cricket":
        pen.rectangle([left, top, right, bottom], fill=(34, 110, 54))
        pen.rectangle([left, top, right, top + 26], fill=(120, 170, 210))
        pen.ellipse([right - 40, top + 6, right - 22, top + 24],
                    fill=(255, 240, 180))
        pen.rectangle([left + 60, mid_y - 6, right - 60, bottom - 8],
                      fill=(196, 164, 110))
        for sx in (left + 150, left + 156, left + 162):
            pen.line([(sx, mid_y + 14), (sx, mid_y + 30)],
                     fill=(255, 255, 255), width=3)
        pen.line([(left + 200, mid_y + 6), (left + 232, mid_y - 14)],
                 fill=(160, 110, 60), width=7)
        pen.ellipse([left + 238, mid_y - 18, left + 246, mid_y - 10],
                    fill=RED)
        pen.text((left + 10, bottom - 16), "NZ 119/2 - TRAIL 233",
                 font=font(SANS_B, 9), fill=(255, 255, 255))
    elif kind == "parliament":
        pen.rectangle([left, top, right, bottom], fill=(24, 48, 96))
        pen.rectangle([left, top, right, top + 24], fill=(120, 170, 210))
        pen.ellipse([right - 40, top + 6, right - 22, top + 24],
                    fill=(255, 240, 180))
        pen.rectangle([left + 60, mid_y - 2, right - 60, bottom - 6],
                      fill=(196, 190, 170))
        pen.polygon([(left + 120, mid_y - 24), (left + 160, mid_y - 2),
                     (left + 200, mid_y - 24)], fill=(150, 40, 50))
        pen.rectangle([left + 252, mid_y - 42, left + 254, mid_y - 2],
                      fill=(255, 255, 255), width=1)
        pen.rectangle([left + 254, mid_y - 42, left + 276, mid_y - 34],
                      fill=(0, 91, 187))
        pen.rectangle([left + 254, mid_y - 34, left + 276, mid_y - 28],
                      fill=(255, 255, 255))
        for cx in (left + 90, left + 130, left + 170, left + 210, left + 250):
            pen.rectangle([cx - 4, mid_y + 8, cx + 4, bottom - 10],
                          fill=(120, 118, 108))
        pen.text((left + 10, bottom - 16), "CANBERRA - NEWSPOLL",
                 font=font(SANS_B, 9), fill=(255, 255, 255))


def paint_leads(pen):
    y = 202
    gap = 8
    col_w = (CW - gap * 2) / 3
    pic_h = 92
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (col_w + gap)
        col = REGION_COLOUR[lead["region"]]
        pen.rectangle([x, y, x + col_w, y + 238], fill=CARD,
                      outline=FAINT, width=1)
        pen.rectangle([x, y, x + col_w, y + 5], fill=col)
        pen.rectangle([x + 6, y + 10, x + 30, y + 32], fill=RED)
        nf = font(SANS_B, 15)
        s = str(lead["n"])
        tw = pen.textlength(s, font=nf)
        pen.text((x + 18 - tw / 2, y + 12), s, font=nf,
                 fill=(255, 255, 255))
        pen.text((x + 36, y + 15), lead["tag"], font=font(SANS_B, 11),
                 fill=col)
        draw_lead_art(pen, lead["art"], x + 6, y + 36,
                      x + col_w - 6, y + 36 + pic_h)
        pen.rectangle([x + 6, y + 36 + pic_h, x + col_w - 6,
                       y + 50 + pic_h], fill=INK)
        cap = font(SANS_B, 8)
        tw = pen.textlength(lead["cap"], font=cap)
        pen.text((x + 6 + (col_w - 12 - tw) / 2, y + 39 + pic_h),
                 lead["cap"], font=cap, fill=(255, 255, 255))
        hy = para(pen, lead["head"], font(SERIF_B, 16), x + 6, y + 154,
                  col_w - 12, 19, max_lines=2)
        para(pen, lead["body"], font(SANS, 9), x + 6, hy + 3,
             col_w - 12, 12, fill=BODY, max_lines=4)

def draw_motif(pen, motif, left, top, right, bottom):
    """One small flat art strip for a grid card, plain shapes only."""
    mid_y = (top + bottom) / 2
    if motif == "card":
        pen.rectangle([left, top, right, bottom], fill=(24, 24, 32))
        pen.rectangle([left + 52, top + 4, left + 140, bottom - 4],
                      fill=(176, 28, 40), outline=(255, 255, 255), width=1)
        pen.rectangle([left + 52, top + 5, left + 140, top + 8],
                      fill=(255, 213, 0))
        pen.text((left + 60, mid_y - 2), "10%", font=font(SANS_B, 9),
                 fill=(255, 255, 255))
    elif motif == "flag":
        pen.rectangle([left, top, right, bottom], fill=(24, 48, 96))
        pen.rectangle([left + 40, top + 3, left + 96, bottom - 3],
                      fill=(206, 17, 38), outline=(255, 255, 255), width=1)
        pen.ellipse([left + 62, mid_y - 6, left + 74, mid_y + 6],
                    outline=(255, 255, 255), width=2)
        pen.rectangle([left + 116, top + 3, left + 172, bottom - 3],
                      fill=(255, 255, 255), outline=INK, width=1)
        pen.ellipse([left + 138, mid_y - 5, left + 150, mid_y + 5],
                    fill=RED)
    elif motif == "factory":
        pen.rectangle([left, top, right, bottom], fill=(90, 90, 96))
        pen.rectangle([left + 40, mid_y - 4, left + 150, bottom - 3],
                      fill=(60, 60, 66))
        pen.rectangle([left + 52, mid_y - 12, left + 60, mid_y - 4],
                      fill=(60, 60, 66))
        pen.rectangle([left + 120, mid_y - 12, left + 128, mid_y - 4],
                      fill=(60, 60, 66))
        for wx in (72, 96, 120):
            pen.rectangle([wx, mid_y + 2, wx + 12, mid_y + 10],
                          fill=(255, 213, 0))
    elif motif == "bottle":
        pen.rectangle([left, top, right, bottom], fill=(60, 30, 30))
        pen.rectangle([left + 88, top + 2, left + 104, bottom - 2],
                      fill=(220, 220, 220))
        pen.rectangle([left + 92, top + 2, left + 100, top + 7],
                      fill=(120, 60, 40))
        pen.line([(left + 76, top + 4), (left + 116, bottom - 4)],
                 fill=RED, width=4)
        pen.line([(left + 116, top + 4), (left + 76, bottom - 4)],
                 fill=RED, width=4)
    elif motif == "chip":
        pen.rectangle([left, top, right, bottom], fill=(16, 22, 44))
        pen.rectangle([left + 76, mid_y - 9, left + 116, mid_y + 9],
                      fill=(0, 150, 130), outline=(255, 255, 255), width=1)
        for px in (84, 96, 108):
            pen.line([(px, mid_y - 9), (px, mid_y - 14)],
                     fill=(255, 213, 0), width=2)
            pen.line([(px, mid_y + 9), (px, mid_y + 14)],
                     fill=(255, 213, 0), width=2)
        pen.text((left + 86, mid_y - 6), "AI", font=font(SANS_B, 10),
                 fill=(255, 255, 255))
    elif motif == "megaphone":
        pen.rectangle([left, top, right, bottom], fill=(140, 44, 62))
        pen.polygon([(left + 60, mid_y - 8), (left + 130, mid_y - 14),
                     (left + 130, mid_y + 14), (left + 60, mid_y + 8)],
                    fill=(255, 255, 255))
        pen.rectangle([left + 52, mid_y - 4, left + 62, mid_y + 10],
                      fill=(255, 213, 0))
    elif motif == "missile":
        pen.rectangle([left, top, right, bottom], fill=(30, 20, 20))
        pen.polygon([(left + 60, mid_y), (left + 130, mid_y - 6),
                     (left + 130, mid_y + 6)], fill=(200, 200, 200))
        pen.rectangle([left + 40, mid_y - 3, left + 60, mid_y + 3],
                      fill=(255, 140, 0))
        pen.polygon([(left + 40, mid_y - 6), (left + 24, mid_y),
                     (left + 40, mid_y + 6)], fill=(255, 213, 0))
    elif motif == "robot":
        pen.rectangle([left, top, right, bottom], fill=(24, 48, 96))
        pen.rectangle([left + 76, mid_y - 8, left + 116, mid_y + 10],
                      fill=(180, 180, 190), outline=INK, width=1)
        pen.ellipse([left + 84, mid_y - 3, left + 90, mid_y + 3],
                    fill=RED)
        pen.ellipse([left + 102, mid_y - 3, left + 108, mid_y + 3],
                    fill=RED)
        pen.line([(left + 96, mid_y - 8), (left + 96, mid_y - 14)],
                 fill=(255, 213, 0), width=2)
    elif motif == "ball":
        pen.rectangle([left, top, right, bottom], fill=(34, 110, 54))
        pen.ellipse([left + 70, mid_y - 9, left + 122, mid_y + 9],
                    fill=(150, 90, 40), outline=(255, 255, 255), width=1)
        pen.line([(left + 84, mid_y), (left + 108, mid_y)],
                 fill=(255, 255, 255), width=2)
        for lx in (88, 96, 104):
            pen.line([(lx, mid_y - 4), (lx, mid_y + 4)],
                     fill=(255, 255, 255), width=1)
    elif motif == "trophy":
        pen.rectangle([left, top, right, bottom], fill=(24, 48, 96))
        pen.polygon([(left + 82, top + 3), (left + 110, top + 3),
                     (left + 106, mid_y + 2), (left + 86, mid_y + 2)],
                    fill=(255, 213, 0), outline=(255, 255, 255), width=1)
        pen.ellipse([left + 76, top + 5, left + 84, mid_y - 2],
                    outline=(255, 213, 0), width=2)
        pen.ellipse([left + 108, top + 5, left + 116, mid_y - 2],
                    outline=(255, 213, 0), width=2)
        pen.rectangle([left + 92, mid_y + 2, left + 100, bottom - 3],
                      fill=(255, 213, 0))
    elif motif == "deal":
        pen.rectangle([left, top, right, bottom], fill=(13, 110, 102))
        pen.ellipse([left + 60, mid_y - 8, left + 84, mid_y + 8],
                    outline=(255, 255, 255), width=3)
        pen.ellipse([left + 108, mid_y - 8, left + 132, mid_y + 8],
                    outline=(255, 255, 255), width=3)
        pen.line([(left + 84, mid_y), (left + 108, mid_y)],
                 fill=(255, 213, 0), width=3)
    elif motif == "phone":
        pen.rectangle([left, top, right, bottom], fill=(10, 10, 26))
        pen.rectangle([left + 82, top + 2, left + 110, bottom - 2],
                      fill=(30, 30, 44), outline=(255, 255, 255), width=1)
        pen.polygon([(left + 90, mid_y - 6), (left + 90, mid_y + 6),
                     (left + 104, mid_y)], fill=(255, 213, 0))


def paint_grid(pen):
    y0 = 448
    gap = 8
    col_w = (CW - gap * 3) / 4
    row_h = 118
    for idx, card in enumerate(GRID):
        n, tag, region, head, body, motif = card
        col = idx % 4
        row = idx // 4
        x = MARGIN + col * (col_w + gap)
        y = y0 + row * (row_h + 6)
        colr = REGION_COLOUR[region]
        pen.rectangle([x, y, x + col_w, y + row_h], fill=CARD,
                      outline=FAINT, width=1)
        draw_motif(pen, motif, x + 1, y + 1, x + col_w - 1, y + 25)
        pen.rectangle([x + 5, y + 29, x + 27, y + 47], fill=RED)
        nf = font(SANS_B, 12)
        s = str(n)
        tw = pen.textlength(s, font=nf)
        pen.text((x + 16 - tw / 2, y + 31), s, font=nf,
                 fill=(255, 255, 255))
        pen.text((x + 31, y + 32), tag, font=font(SANS_B, 9), fill=colr)
        para(pen, head, font(SERIF_B, 11), x + 5, y + 50, col_w - 10,
             13, max_lines=2)
        para(pen, body, font(SANS, 9), x + 5, y + 78, col_w - 10, 11,
             fill=BODY, max_lines=3)


def paint_map(pen):
    y0 = 696
    title = font(SANS_B, 10)
    pen.text((MARGIN, y0), "WHERE IT HAPPENED - STORIES 1-11",
             font=title, fill=INK)
    mx0, mx1 = MARGIN, MARGIN + CW
    my0, my1 = y0 + 14, y0 + 84
    pen.rectangle([mx0, my0, mx1, my1], outline=FAINT, width=1)
    x_scale = (mx1 - mx0) / 360.0
    y_scale = (my1 - my0) / 140.0
    lat_top = 80.0

    def to_xy(lon, lat):
        return (mx0 + (lon + 180) * x_scale,
                my0 + (lat_top - lat) * y_scale)

    lon = -179.0
    while lon < 180:
        lat = -58.0
        while lat < 80:
            if on_land(lon, lat):
                px, py = to_xy(lon, lat)
                pen.ellipse([px - 1.2, py - 1.2, px + 1.2, py + 1.2],
                            fill=(120, 118, 108))
            lat += 7.5
        lon += 2.2
    for n in sorted(PINS):
        lon, lat = PINS[n]
        px, py = to_xy(lon, lat)
        if n == 5:
            px -= 8
            py += 7
        if n == 6:
            px += 8
            py -= 7
        if n == 9:
            px += 16
            py += 9
        if n == 10:
            px += 14
            py -= 8
        pen.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                    outline=(255, 255, 255), width=1)
        nf = font(SANS_B, 8)
        s = str(n)
        tw = pen.textlength(s, font=nf)
        pen.text((px - tw / 2, py - 5), s, font=nf, fill=(255, 255, 255))


def paint_more(pen):
    y0 = 790
    title = font(SANS_B, 10)
    pen.text((MARGIN, y0), "ALSO ON MONDAY - 12-44",
             font=title, fill=INK)
    rule(pen, MARGIN, MARGIN + CW, y0 + 14, 1, fill=FAINT)
    fnt = font(SANS, 8)
    bold = font(SANS_B, 8)
    col_w = (CW - 32) / 3
    for idx, (n, text, region) in enumerate(MORE):
        col = idx // 11
        row = idx % 11
        x = MARGIN + col * (col_w + 16)
        y = y0 + 19 + row * 12
        pen.text((x, y), "%d." % n, font=bold, fill=RED)
        pen.text((x + 17, y), text, font=fnt, fill=INK)


def paint_datecheck(pen):
    y0 = 940
    pen.rectangle([MARGIN, y0, MARGIN + CW, y0 + 52], outline=RED, width=1)
    pen.text((MARGIN + 6, y0 + 4), "DATE CHECK - NOT TODAY'S NEWS",
             font=font(SANS_B, 9), fill=RED)
    para(pen, EXCLUDED_INTRO + " " + EXCLUDED, font(SANS, 8),
         MARGIN + 6, y0 + 17, CW - 12, 10, fill=BODY, max_lines=3)


def paint_footer(pen):
    para(pen, FOOTER, font(SANS, 8), MARGIN, 996, CW, 9, fill=GREY,
         max_lines=2)


def render():
    page = Image.new("RGB", (W, H), PAPER)
    pen = ImageDraw.Draw(page)
    tally = region_counts()
    paint_masthead(pen)
    paint_tabs(pen, tally)
    paint_stats(pen)
    paint_timeline(pen)
    paint_leads(pen)
    paint_grid(pen)
    paint_map(pen)
    paint_more(pen)
    paint_datecheck(pen)
    paint_footer(pen)
    page.save(OUT_PATH, "PNG", optimize=True)
    return OUT_PATH


if __name__ == "__main__":
    path = render()
    import os
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))
