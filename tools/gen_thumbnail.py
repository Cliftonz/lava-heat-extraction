import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "thumbnail.png")
N = 256
S = 4
W = N * S


def s(v):
    return int(round(v * S))


BG_TOP = (46, 46, 48)
BG_BOT = (24, 24, 26)
BORDER = (12, 12, 13)
BORDER_HI = (78, 78, 82)

LAVA_CRUST = (118, 22, 8)
LAVA_DARK = (150, 30, 8)
LAVA_MID = (222, 74, 10)
LAVA_HOT = (255, 146, 24)
LAVA_CORE = (255, 216, 110)
LAVA_WHITE = (255, 250, 226)

SLAG = (54, 30, 26)

STEEL_DARK = (26, 26, 30)
STEEL = (66, 66, 72)
STEEL_HI = (128, 128, 136)

STONE_LIT = (178, 178, 182)
STONE_MID = (122, 122, 128)
STONE_DARK = (62, 62, 68)
STONE_EDGE = (28, 28, 32)


def background():
    img = Image.new("RGB", (W, W), BG_BOT)
    d = ImageDraw.Draw(img)
    for y in range(W):
        t = y / (W - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return img


def screen_glow(img, blobs, color, blur, strength):
    mask = Image.new("L", (W, W), 0)
    md = ImageDraw.Draw(mask)
    for (cx, cy, rx, ry, a) in blobs:
        md.ellipse([s(cx - rx), s(cy - ry), s(cx + rx), s(cy + ry)], fill=a)
    mask = mask.filter(ImageFilter.GaussianBlur(s(blur)))
    m = mask.point(lambda v: int(v * strength))
    glow = Image.new("RGB", (W, W), color)
    out = Image.new("RGB", (W, W))
    bp, gp, mp, op = img.load(), glow.load(), m.load(), out.load()
    for y in range(W):
        for x in range(W):
            a = mp[x, y] / 255.0
            if a <= 0.002:
                op[x, y] = bp[x, y]
                continue
            br, bg, bb = bp[x, y]
            gr, gg, gb = gp[x, y]
            op[x, y] = (min(255, int(br + gr * a)), min(255, int(bg + gg * a)), min(255, int(bb + gb * a)))
    return out


def stream_poly(y0, y1, edges, inset=0.0, steps=64):
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        y = y0 + (y1 - y0) * t
        l, r = edges(t)
        cx = (l + r) / 2.0
        half = max(0.8, (r - l) / 2.0 - inset)
        left.append((s(cx - half), s(y)))
        right.append((s(cx + half), s(y)))
    return left + right[::-1]


def rock(d, cx, cy, size, seed, squash=1.0, pal=None):
    lit, mid, dark = pal if pal else (STONE_LIT, STONE_MID, STONE_DARK)
    rnd = random.Random(seed)
    n = 7
    pts = []
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-0.16, 0.16)) / n - math.pi / 2
        rr = size * 0.5 * rnd.uniform(0.66, 1.0)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * squash))
    sp = [(s(x), s(y)) for x, y in pts]
    d.polygon(sp, fill=mid)
    ctr = (s(cx + size * 0.06), s(cy + size * 0.05))
    litface = [sp[-1], sp[0], sp[1], ctr]
    d.polygon(litface, fill=lit)
    darkface = [sp[2], sp[3], sp[4], sp[5], ctr]
    d.polygon(darkface, fill=dark)
    d.line(sp + [sp[0]], fill=STONE_EDGE, width=s(2), joint="curve")
    d.line([sp[1], ctr], fill=STONE_EDGE, width=s(1))
    d.line([sp[-1], ctr], fill=STONE_EDGE, width=s(1))


img = background()
img = screen_glow(img, [(128, 78, 82, 66, 255)], (132, 34, 4), 30, 0.45)
img = screen_glow(img, [(128, 200, 92, 44, 255)], (176, 58, 6), 24, 0.62)

# ---------------------------------------------------------------- raw lava in
raw = Image.new("RGBA", (W, W), (0, 0, 0, 0))
dr = ImageDraw.Draw(raw)

DECK_TOP = 112.0


def pour_edges(t):
    e = t ** 1.2
    l = 46 + (86 - 46) * e + math.sin(t * 3.1) * 5
    r = 210 - (210 - 170) * e - math.sin(t * 2.3 + 0.9) * 5
    return l, r


dr.polygon(stream_poly(-10, DECK_TOP + 6, pour_edges, 0), fill=LAVA_CRUST)
dr.polygon(stream_poly(-10, DECK_TOP + 6, pour_edges, 6), fill=LAVA_DARK)
dr.polygon(stream_poly(-10, DECK_TOP + 6, pour_edges, 20), fill=LAVA_MID)
dr.polygon(stream_poly(-10, DECK_TOP + 6, pour_edges, 34), fill=LAVA_HOT)
dr.polygon(stream_poly(-10, DECK_TOP + 6, pour_edges, 48), fill=LAVA_CORE)

# unrefined stone riding in the raw stream
RAW_STONE = ((146, 120, 114), (94, 70, 66), (46, 30, 30))
for (cx, cy, sz, sd) in [(72, 38, 25, 31), (177, 72, 22, 47)]:
    rock(dr, cx, cy, sz, sd, pal=RAW_STONE)

img = Image.alpha_composite(img.convert("RGBA"), raw).convert("RGB")

# ---------------------------------------------------------------- sluice deck
deck = Image.new("RGBA", (W, W), (0, 0, 0, 0))
dd = ImageDraw.Draw(deck)
DL, DR, DB = 20.0, 236.0, 156.0
IL, IR = 34.0, 222.0
dd.polygon([(s(DL), s(DECK_TOP)), (s(DR), s(DECK_TOP)), (s(IR), s(DB)), (s(IL), s(DB))], fill=STEEL)
dd.polygon([(s(DL), s(DECK_TOP)), (s(DR), s(DECK_TOP)), (s(DR - 1), s(DECK_TOP + 9)), (s(DL + 1), s(DECK_TOP + 9))], fill=STEEL_HI)
dd.polygon([(s(IL + 1.4), s(DB - 9)), (s(IR - 1.4), s(DB - 9)), (s(IR), s(DB)), (s(IL), s(DB))], fill=STEEL_DARK)
# end caps to read as a machine, not a plank
dd.polygon([(s(DL), s(DECK_TOP)), (s(DL + 16), s(DECK_TOP)), (s(IL + 14), s(DB)), (s(IL), s(DB))], fill=(52, 52, 58))
dd.polygon([(s(DR - 16), s(DECK_TOP)), (s(DR), s(DECK_TOP)), (s(IR), s(DB)), (s(IR - 14), s(DB))], fill=(52, 52, 58))
img = Image.alpha_composite(img.convert("RGBA"), deck).convert("RGB")

# ---------------------------------------------------------------- slots
slots = Image.new("RGBA", (W, W), (0, 0, 0, 0))
dsl = ImageDraw.Draw(slots)
for i in range(4):
    xt = 76 + i * 28
    xb = xt + (IL - DL) * ((DB - DECK_TOP) / (DB - DECK_TOP)) * 0.0 + 6
    dsl.polygon(
        [(s(xt), s(DECK_TOP + 11)), (s(xt + 16), s(DECK_TOP + 11)), (s(xb + 12), s(DB - 11)), (s(xb - 2), s(DB - 11))],
        fill=LAVA_WHITE,
    )
img = Image.alpha_composite(img.convert("RGBA"), slots).convert("RGB")
img = screen_glow(img, [(128, 134, 58, 22, 255)], (190, 88, 12), 7, 0.75)

# ---------------------------------------------------------------- filtered out
out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
do = ImageDraw.Draw(out)


def clean_edges(t):
    e = t ** 2.1
    l = 96 - 30 * e
    r = 160 + 30 * e
    return l, r


do.polygon(stream_poly(DB - 2, 212, clean_edges, 0), fill=LAVA_MID)
do.polygon(stream_poly(DB - 2, 212, clean_edges, 6), fill=LAVA_HOT)
do.polygon(stream_poly(DB - 2, 212, clean_edges, 13), fill=LAVA_CORE)
do.polygon(stream_poly(DB - 2, 212, clean_edges, 21), fill=LAVA_WHITE)

# molten basin, a bed of melt filling the base of the frame
do.polygon([(s(24), s(204)), (s(232), s(204)), (s(226), s(246)), (s(30), s(246))], fill=LAVA_DARK)
do.polygon([(s(34), s(208)), (s(222), s(208)), (s(217), s(246)), (s(39), s(246))], fill=LAVA_MID)
do.polygon([(s(50), s(212)), (s(206), s(212)), (s(202), s(246)), (s(54), s(246))], fill=LAVA_HOT)
do.polygon([(s(74), s(215)), (s(182), s(215)), (s(178), s(246)), (s(78), s(246))], fill=LAVA_CORE)
do.polygon([(s(100), s(218)), (s(156), s(218)), (s(153), s(246)), (s(103), s(246))], fill=LAVA_WHITE)

sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
ImageDraw.Draw(sh).polygon(
    [(s(IL), s(DB - 1)), (s(IR), s(DB - 1)), (s(IR - 4), s(DB + 5)), (s(IL + 4), s(DB + 5))],
    fill=(10, 6, 6, 150),
)
out = Image.alpha_composite(out, sh)
img = Image.alpha_composite(img.convert("RGBA"), out).convert("RGB")

# ---------------------------------------------------------------- stone out
st = Image.new("RGBA", (W, W), (0, 0, 0, 0))
dst = ImageDraw.Draw(st)
rock(dst, 44, 174, 58, 3)
rock(dst, 76, 198, 44, 9)
rock(dst, 34, 202, 40, 21)
rock(dst, 214, 174, 54, 5)
rock(dst, 188, 198, 42, 14)
img = Image.alpha_composite(img.convert("RGBA"), st).convert("RGB")

# ---------------------------------------------------------------- heat bloom
img = screen_glow(img, [(128, 40, 52, 42, 200), (128, 182, 30, 30, 210), (128, 234, 92, 24, 255)], (200, 74, 8), 13, 0.5)

vig = Image.new("L", (W, W), 0)
ImageDraw.Draw(vig).rectangle([s(14), s(14), W - 1 - s(14), W - 1 - s(14)], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(s(16)))
img = Image.composite(img, Image.eval(img, lambda v: int(v * 0.62)), vig)

d = ImageDraw.Draw(img)
d.rectangle([0, 0, W - 1, W - 1], outline=BORDER, width=s(3))
d.rectangle([s(4), s(4), W - 1 - s(4), W - 1 - s(4)], outline=BORDER_HI, width=s(1))

final = img.resize((N, N), Image.LANCZOS)
final.save(OUT, optimize=True)
final.resize((144, 144), Image.LANCZOS).save(OUT.replace(".png", "-144.png"), optimize=True)
final.resize((64, 64), Image.LANCZOS).save(OUT.replace(".png", "-64.png"), optimize=True)
print("ok")
