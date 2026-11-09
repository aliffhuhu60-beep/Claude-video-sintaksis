"""Pustaka motion graphics – Misi Penyelamat Ayat.
Setiap pembina mengembalikan imej RGBA (PIL). Animasi dikendalikan oleh compositor (render.py)."""
import os, math, functools, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(HERE, "..", "..", "05_GRAPHICS", "fonts")

# ---------- Identiti warna ----------
GREEN_DARK = (10, 58, 42)
GREEN_DEEP = (6, 34, 26)
NAVY = (18, 40, 84)
NAVY_DEEP = (10, 22, 48)
WHITE = (255, 255, 255)
GOLD = (247, 196, 58)
RED = (235, 64, 52)
LGREEN = (88, 214, 110)
PURPLE = (150, 92, 240)
BLUE = (52, 152, 245)
YELLOW = (255, 214, 10)
GREY = (190, 200, 210)
INK = (14, 20, 30)


@functools.lru_cache(None)
def F(name, size):
    m = {
        "mx": "Montserrat-800.ttf", "mb": "Montserrat-700.ttf", "ms": "Montserrat-600.ttf", "mk": "Montserrat-900.ttf",
        "mm": "Montserrat-500.ttf", "pr": "Poppins-400.ttf", "pm": "Poppins-500.ttf", "ps": "Poppins-600.ttf",
        "pb": "Poppins-700.ttf",
    }
    if name in m:
        return ImageFont.truetype(os.path.join(FONTDIR, m[name]), size)
    inter = {"ir": "Inter-Regular.otf", "is": "Inter-SemiBold.otf", "ib": "Inter-Bold.otf"}
    return ImageFont.truetype(os.path.join("/usr/share/fonts/opentype/inter", inter[name]), size)


SYMS = set("→←↓↑✓✗×•+=▶")


@functools.lru_cache(None)
def SYMF(size):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def canvas(w, h):
    return Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))


def tw(font, s):
    b = font.getbbox(s)
    return b[2] - b[0]


def shadowed(img, radius=18, offset=(0, 10), opacity=0.55, pad=40):
    """Tambah bayang lembut di sekeliling elemen."""
    w, h = img.size
    out = canvas(w + 2 * pad, h + 2 * pad)
    a = img.split()[3]
    sh = Image.new("L", out.size, 0)
    sh.paste(a, (pad + offset[0], pad + offset[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * opacity))
    black = Image.new("RGBA", out.size, (0, 0, 0, 255))
    black.putalpha(sh)
    out = Image.alpha_composite(out, black)
    out.alpha_composite(img, (pad, pad))
    return out, pad


def panel(w, h, fill=(12, 26, 52, 225), r=22, border=None, bw=3, accent=None, accent_w=10):
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], r, fill=fill, outline=border, width=bw if border else 0)
    if accent:
        m = canvas(w, h)
        md = ImageDraw.Draw(m)
        md.rounded_rectangle([0, 0, w - 1, h - 1], r, fill=(255, 255, 255, 255))
        bar = canvas(w, h)
        ImageDraw.Draw(bar).rectangle([0, 0, accent_w, h], fill=accent + (255,))
        bar.putalpha(Image.fromarray(np.minimum(np.array(bar.split()[3]), np.array(m.split()[3]))))
        im.alpha_composite(bar)
    return im


def pill(text, font, fg=WHITE, bg=GREEN_DARK, padx=18, pady=8, r=None):
    sym = ""
    if text[:1] in "✓✗→★":
        sym, text = text[:2], text[2:]
    sf = SYMF(font.size)
    sw = tw(sf, sym) if sym else 0
    w = tw(font, text) + 2 * padx + sw
    asc, desc = font.getmetrics()
    h = asc + desc + 2 * pady
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], r if r is not None else h // 2, fill=bg + (255,) if len(bg) == 3 else bg)
    if sym:
        d.text((padx, pady + 2), sym, font=sf, fill=fg)
    d.text((padx + sw, pady), text, font=font, fill=fg)
    return im


# ---------- Teks kaya (rich text) ----------
def layout_rich(tokens, maxw, base_font, line_gap=1.25):
    """tokens: senarai (teks, gaya) ; gaya = dict(font, color, hl(bg), ul(warna garis bawah), strike)
    Pulangkan senarai baris: setiap baris = senarai (x, perkataan, gaya)."""
    words = []
    tokens = [(t, (dict(st, font=SYMF(st.get("font", base_font).size)) if t.strip() and all(c in SYMS or c == " " for c in t) else st)) for t, st in tokens]
    for txt, st in tokens:
        parts = txt.split(" ")
        for i, p in enumerate(parts):
            if p == "":
                continue
            words.append((p, st, i < len(parts) - 1 or txt.endswith(" ")))
    lines, cur, x = [], [], 0
    for wd, st, _ in words:
        f = st.get("font", base_font)
        ww = tw(f, wd)
        sp = tw(f, " ")
        if cur and x + ww > maxw:
            lines.append(cur); cur, x = [], 0
        cur.append((x, wd, st))
        x += ww + sp
    if cur:
        lines.append(cur)
    return lines


def draw_rich(im, xy, tokens, maxw, base_font, color=WHITE, align="left", line_h=None):
    d = ImageDraw.Draw(im)
    lines = layout_rich(tokens, maxw, base_font)
    asc, desc = base_font.getmetrics()
    lh = line_h or int((asc + desc) * 1.22)
    x0, y = xy
    for ln in lines:
        lw = ln[-1][0] + tw(ln[-1][2].get("font", base_font), ln[-1][1])
        off = (maxw - lw) // 2 if align == "center" else 0
        # latar highlight dahulu (gabung perkataan berturutan)
        for i, (x, wd, st) in enumerate(ln):
            f = st.get("font", base_font)
            if st.get("hl"):
                nxt_hl = i + 1 < len(ln) and ln[i + 1][2].get("hl") == st.get("hl")
                ex = tw(f, " ") if nxt_hl else 0
                d.rounded_rectangle([x0 + off + x - 6, y - 2, x0 + off + x + tw(f, wd) + 6 + ex, y + asc + desc + 2], 8, fill=st["hl"])
        for x, wd, st in ln:
            f = st.get("font", base_font)
            c = st.get("color", color)
            d.text((x0 + off + x, y), wd, font=f, fill=c)
            if st.get("strike"):
                yy = y + (asc + desc) // 2 + 2
                d.line([x0 + off + x - 4, yy, x0 + off + x + tw(f, wd) + 4, yy], fill=st["strike"], width=5)
            if st.get("ul"):
                yy = y + asc + desc + 4
                d.line([x0 + off + x, yy, x0 + off + x + tw(f, wd), yy], fill=st["ul"], width=5)
        y += lh
    return y


def rich_height(tokens, maxw, base_font):
    lines = layout_rich(tokens, maxw, base_font)
    asc, desc = base_font.getmetrics()
    return len(lines) * int((asc + desc) * 1.22)


def _split_syms(tokens):
    out = []
    for t, st in tokens:
        buf = ""
        for ch in t:
            if ch in "→←↓↑✓✗":
                if buf: out.append((buf, st)); buf = ""
                out.append((ch, st))
            else:
                buf += ch
        if buf: out.append((buf, st))
    return out


def parse_marked(s, base=None, marks=None):
    return _split_syms(_parse_marked(s, base, marks))


def _parse_marked(s, base=None, marks=None):
    """Sintaks ringkas: [r:teks] merah-highlight, [g:teks] hijau, [b:teks] biru, [y:teks] kuning,
    [s:teks] coret merah, [B:teks] tebal putih."""
    import re
    marks = marks or {}
    out = []
    pos = 0
    for m in re.finditer(r"\[(\w):([^\]]+)\]", s):
        if m.start() > pos:
            out.append((s[pos:m.start()], dict(base or {})))
        k, t = m.group(1), m.group(2)
        st = dict(base or {})
        st.update(marks.get(k, {}))
        out.append((t, st))
        pos = m.end()
    if pos < len(s):
        out.append((s[pos:], dict(base or {})))
    return out


def MARKS(size):
    b = F("pb", size)
    return {
        "r": {"font": b, "color": WHITE, "hl": (200, 40, 40, 255)},
        "g": {"font": b, "color": INK, "hl": LGREEN + (255,)},
        "b": {"font": b, "color": WHITE, "hl": BLUE + (255,)},
        "y": {"font": b, "color": INK, "hl": YELLOW + (255,)},
        "p": {"font": b, "color": WHITE, "hl": PURPLE + (255,)},
        "s": {"font": b, "color": (255, 150, 140), "strike": RED + (255,)},
        "B": {"font": b, "color": WHITE},
        "Y": {"font": b, "color": YELLOW},
        "G": {"font": b, "color": LGREEN},
        "R": {"font": b, "color": (255, 110, 100)},
        "C": {"font": b, "color": (120, 190, 255)},
    }


# ---------- Pembina elemen ----------
def keypoint_card(tag, title, sub=None, accent=GOLD, w=560, tag_bg=None):
    """Kad isi penting di sisi kiri/kanan."""
    ft = F("mx", 44 if len(title) < 26 else 38)
    fs = F("pm", 27)
    fg = F("mb", 22)
    title_tok = parse_marked(title, {"font": ft, "color": WHITE}, MARKS(44))
    th = rich_height(title_tok, w - 70, ft)
    sh = 0
    sub_tok = None
    if sub:
        sub_tok = parse_marked(sub, {"font": fs, "color": (220, 228, 240)}, MARKS(27))
        sh = rich_height(sub_tok, w - 70, fs) + 14
    h = 40 + 46 + 16 + th + sh + 30
    im = panel(w, h, fill=(10, 24, 50, 232), accent=accent, accent_w=10)
    p = pill(tag, fg, fg=INK if accent in (GOLD, YELLOW, LGREEN) else WHITE, bg=tag_bg or accent)
    im.alpha_composite(p, (36, 34))
    y = draw_rich(im, (36, 34 + p.size[1] + 16), title_tok, w - 70, ft)
    if sub_tok:
        draw_rich(im, (36, y + 10), sub_tok, w - 70, fs)
    return shadowed(im)[0]


def lower_third(name, role, accent=GOLD):
    fn = F("mx", 46)
    fr = F("pm", 28)
    w = max(tw(fn, name), tw(fr, role)) + 90
    h = 132
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=(8, 30, 24, 235))
    d.rectangle([0, 0, 12, h], fill=accent)
    d.text((40, 16), name, font=fn, fill=WHITE)
    d.text((40, 78), role, font=fr, fill=accent)
    # jalur piksel (motif Minecraft)
    for i in range(0, w - 12, 24):
        c = [(84, 160, 60), (120, 80, 40), (60, 130, 50)][(i // 24) % 3]
        d.rectangle([12 + i, h - 8, 12 + i + 23, h], fill=c)
    return shadowed(im)[0]


def sentence_box(kind, text, w=1180, label=None, size=40):
    """kind: 'salah' / 'betul'. text boleh mengandungi penanda [r:...] dsb."""
    col = RED if kind == "salah" else LGREEN
    head = "AYAT SALAH" if kind == "salah" else "AYAT BETUL"
    fb = F("pm", size)
    tok = parse_marked("“" + text + "”", {"font": fb, "color": WHITE}, MARKS(size))
    th = rich_height(tok, w - 80, fb)
    fl = F("is", 22)
    h = 30 + 50 + 18 + th + (40 if label else 0) + 28
    fill = (60, 12, 14, 236) if kind == "salah" else (10, 52, 28, 236)
    im = panel(w, h, fill=fill, border=col + (255,), bw=4)
    hp = pill(("✗ " if kind == "salah" else "✓ ") + head, F("mx", 26), fg=WHITE if kind == "salah" else INK, bg=col)
    im.alpha_composite(hp, (36, 28))
    if label:
        d = ImageDraw.Draw(im)
        d.text((w - 36 - tw(fl, label), 40), label, font=fl, fill=(230, 230, 230))
    draw_rich(im, (40, 28 + hp.size[1] + 18), tok, w - 80, fb)
    return shadowed(im)[0]


def analysis_box(text, w=1180, size=30):
    fb = F("pr", size)
    tok = parse_marked(text, {"font": fb, "color": (230, 236, 245)}, MARKS(size))
    th = rich_height(tok, w - 80, fb)
    h = th + 40 + 46
    im = panel(w, h, fill=(14, 30, 64, 236), accent=BLUE)
    d = ImageDraw.Draw(im)
    d.text((40, 16), "ANALISIS", font=F("mx", 22), fill=(130, 190, 255))
    draw_rich(im, (40, 52), tok, w - 80, fb)
    return shadowed(im)[0]


def block(text, sub, color, w=None, h=150, tsize=50):
    ft = F("mx", tsize)
    fs = F("ms", 22)
    w = w or max(tw(ft, text), tw(fs, sub)) + 80
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 20, fill=color + (255,))
    d.rounded_rectangle([0, h - 12, w - 1, h - 1], 6, fill=tuple(int(c * 0.7) for c in color) + (255,))
    d.text(((w - tw(fs, sub)) // 2, 18), sub, font=fs, fill=(255, 255, 255, 220))
    if any(c in "✗✓→" for c in text):
        parts = text.split(" ")
        fs_ = SYMF(tsize)
        widths = [tw(fs_ if any(c in "✗✓→" for c in p_) else ft, p_) for p_ in parts]
        sp = tw(ft, " ")
        x = (w - sum(widths) - sp * (len(parts) - 1)) // 2
        for p_, wd in zip(parts, widths):
            d.text((x, 52 + (6 if p_ in "✗✓→" else 0)), p_, font=fs_ if any(c in "✗✓→" for c in p_) else ft, fill=WHITE if p_ not in "✗" else (255, 120, 110))
            x += wd + sp
        return im
    d.text(((w - tw(ft, text)) // 2, 52), text, font=ft, fill=WHITE)
    return im


def formula_row(items, gap=26, op_size=70):
    """items: senarai blok PIL atau rentetan operator ('+', '=', '→')."""
    fo_m = F("mx", op_size)
    fo_s = SYMF(op_size)
    fof = lambda it: fo_s if any(c in SYMS for c in it) and it not in ("+", "=") else fo_m
    ws = [it.size[0] if isinstance(it, Image.Image) else tw(fof(it), it) for it in items]
    hh = max(it.size[1] for it in items if isinstance(it, Image.Image))
    w = sum(ws) + gap * (len(items) - 1)
    im = canvas(w, hh)
    d = ImageDraw.Draw(im)
    x = 0
    for it, iw in zip(items, ws):
        if isinstance(it, Image.Image):
            im.alpha_composite(it, (x, (hh - it.size[1]) // 2))
        else:
            fo = fof(it)
            asc, desc = fo.getmetrics()
            d.text((x, (hh - asc - desc) // 2 - 6), it, font=fo, fill=WHITE)
        x += iw + gap
    return shadowed(im, 14)[0]


def big_word(text, color=WHITE, size=170, font="mk", stroke=0, stroke_fill=INK):
    f = F(font, size)
    b = f.getbbox(text, stroke_width=stroke)
    im = canvas(b[2] - b[0] + 20, b[3] - b[1] + 30)
    ImageDraw.Draw(im).text((10 - b[0], 10 - b[1]), text, font=f, fill=color, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def text_img(text, font, color=WHITE, maxw=None, align="left", spacing=10):
    if maxw:
        tok = [(text, {"font": font, "color": color})]
        h = rich_height(tok, maxw, font) + 10
        im = canvas(maxw, h)
        draw_rich(im, (0, 0), tok, maxw, font, align=align)
        return im
    b = font.getbbox(text)
    im = canvas(b[2] + 10, b[3] + 14)
    ImageDraw.Draw(im).text((0, 0), text, font=font, fill=color)
    return im


def numbered_card(num, title, body, accent=GOLD, w=400, h=330, icon=None):
    im = panel(w, h, fill=(10, 24, 50, 238))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, 14], 6, fill=accent)
    d.text((32, 34), str(num), font=F("mk", 72), fill=accent)
    if icon:
        d.text((w - 32 - tw(F("mx", 60), icon), 44), icon, font=F("mx", 60), fill=(255, 255, 255, 60))
    y = draw_rich(im, (32, 130), [(title, {"font": F("mx", 32), "color": WHITE})], w - 64, F("mx", 32))
    if body:
        draw_rich(im, (32, y + 8), parse_marked(body, {"font": F("pr", 23), "color": (210, 220, 235)}, MARKS(23)), w - 64, F("pr", 23))
    return shadowed(im)[0]


def score_pop(text="+100", sub="BETUL!", color=GOLD):
    f1 = F("mk", 150)
    f2 = F("mx", 56)
    w = max(tw(f1, text), tw(f2, sub)) + 80
    im = canvas(w, 270)
    d = ImageDraw.Draw(im)
    d.text(((w - tw(f2, sub)) // 2, 0), sub, font=f2, fill=LGREEN if color == GOLD else RED, stroke_width=4, stroke_fill=INK)
    d.text(((w - tw(f1, text)) // 2, 60), text, font=f1, fill=color, stroke_width=7, stroke_fill=INK)
    return shadowed(im, 16, (0, 8), 0.6)[0]


def mission_banner(top, title, color=PURPLE, done=False):
    f1 = F("mx", 34)
    f2 = F("mk", 76)
    w = max(tw(f1, top), tw(f2, title)) + 140
    h = 210
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=(16, 10, 40, 240), outline=color + (255,), width=5)
    d.text(((w - tw(f1, top)) // 2, 26), top, font=f1, fill=GOLD if done else color)
    d.text(((w - tw(f2, title)) // 2, 82), title, font=f2, fill=WHITE)
    for i in range(0, w - 40, 30):
        c = [color, GOLD, LGREEN][(i // 30) % 3]
        d.rectangle([20 + i, h - 16, 20 + i + 26, h - 8], fill=c)
    return shadowed(im)[0]


def section_chip(letter, text):
    f = F("mb", 22)
    s = f"BAHAGIAN {letter}  •  {text}"
    w = tw(f, s) + 54
    im = canvas(w, 46)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, 45], 23, fill=(8, 30, 24, 200))
    d.ellipse([16, 16, 30, 30], fill=GOLD)
    d.text((40, 9), s, font=f, fill=WHITE)
    return im


def phone_quote(platform, ctx, quote_marked, flag, w=470, h=760):
    """Bingkai telefon yang memaparkan PETIKAN kapsyen awam (bukan tangkap layar rekaan)."""
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 60, fill=(20, 20, 24, 255), outline=(90, 90, 100, 255), width=6)
    d.rounded_rectangle([18, 18, w - 19, h - 19], 46, fill=(246, 247, 250, 255))
    d.rounded_rectangle([w // 2 - 70, 30, w // 2 + 70, 58], 14, fill=(20, 20, 24, 255))
    d.text((44, 84), platform, font=F("mx", 34), fill=INK)
    d.text((44, 128), ctx, font=F("ps", 22), fill=(90, 100, 115))
    # akaun dikaburkan
    d.ellipse([44, 176, 104, 236], fill=(170, 175, 185))
    av = im.crop((44, 176, 104, 236)).filter(ImageFilter.GaussianBlur(6))
    im.paste(av, (44, 176))
    d.rounded_rectangle([118, 190, 330, 222], 10, fill=(190, 195, 205))
    d.text((120, 236), "nama akaun dikaburkan", font=F("ir", 18), fill=(120, 125, 135))
    tok = parse_marked(quote_marked, {"font": F("ps", 33), "color": INK}, {
        "r": {"font": F("pb", 33), "color": WHITE, "hl": (215, 45, 45, 255)}})
    y = draw_rich(im, (44, 290), tok, w - 88, F("ps", 33))
    fp = pill(flag, F("mx", 22), fg=WHITE, bg=RED)
    im.alpha_composite(fp, (44, y + 26))
    d.text((44, h - 110), "Petikan hantaran awam", font=F("is", 19), fill=(110, 115, 125))
    d.text((44, h - 84), "Dikumpul: 5 November 2026", font=F("ir", 19), fill=(110, 115, 125))
    return shadowed(im, 24, (0, 16), 0.6)[0]


# ---------- Latar belakang ----------
@functools.lru_cache(None)
def bg_gradient(kind="green"):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    if kind == "green":
        c1, c2 = np.array(GREEN_DEEP, np.float32), np.array(NAVY_DEEP, np.float32)
    elif kind == "purple":
        c1, c2 = np.array((26, 10, 48), np.float32), np.array(NAVY_DEEP, np.float32)
    elif kind == "game":
        c1, c2 = np.array((20, 10, 40), np.float32), np.array((6, 30, 24), np.float32)
    elif kind == "dark":
        c1, c2 = np.array((4, 8, 10), np.float32), np.array((8, 18, 22), np.float32)
    else:
        c1, c2 = np.array(NAVY_DEEP, np.float32), np.array(GREEN_DEEP, np.float32)
    k = (x / W * 0.6 + y / H * 0.4)[..., None]
    img = c1 * (1 - k) + c2 * k
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)[..., None]
    img *= (1.15 - 0.7 * r)
    # grid halus
    grid = ((x.astype(int) % 80 == 0) | (y.astype(int) % 80 == 0))[..., None]
    img = img + grid * 6
    return np.clip(img, 0, 255).astype(np.uint8)


def pixel_strip(w, h=14, seed=0):
    r = random.Random(seed)
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    cols = [(84, 160, 60), (120, 80, 40), (60, 130, 50), (100, 180, 70)]
    for i in range(0, w, h * 2):
        d.rectangle([i, 0, i + h * 2 - 1, h], fill=cols[r.randrange(4)])
    return im


def title_card(kicker, title, sub=None, accent=GOLD):
    """Kad tajuk bahagian (lapisan lutsinar – latar dilukis berasingan)."""
    im = canvas(W, H)
    d = ImageDraw.Draw(im)
    fk = F("mb", 34)
    ft = F("mk", 96 if len(title) < 22 else 78)
    d.text((140, 380), kicker, font=fk, fill=accent)
    d.rectangle([140, 430, 260, 438], fill=accent)
    y = draw_rich(im, (140, 470), parse_marked(title, {"font": ft, "color": WHITE}, {
        "G": {"font": ft, "color": LGREEN}, "Y": {"font": ft, "color": GOLD}, "R": {"font": ft, "color": RED},
        "P": {"font": ft, "color": PURPLE}}), 1640, ft)
    if sub:
        draw_rich(im, (140, y + 14), parse_marked(sub, {"font": F("pm", 38), "color": (215, 225, 235)}, MARKS(38)), 1600, F("pm", 38))
    im.alpha_composite(pixel_strip(W, 18, 3), (0, H - 18))
    return im


def harapan_node(title, body, color, w=500):
    ft = F("mk", 54)
    fb = F("pm", 27)
    tok = [(body, {"font": fb, "color": (220, 230, 240)})]
    bh = rich_height(tok, w - 60, fb)
    h = 120 + bh + 40
    im = panel(w, h, fill=(10, 24, 50, 238), border=color + (255,), bw=4)
    d = ImageDraw.Draw(im)
    d.text(((w - tw(ft, title)) // 2, 34), title, font=ft, fill=color)
    draw_rich(im, (30, 118), tok, w - 60, fb, align="center")
    return shadowed(im)[0]


# ---------- Elemen dinamik (fungsi masa) ----------
def _ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


_word_cache = {}


def _word_img(text, size, color, font="mk"):
    k = (text, size, color, font)
    if k not in _word_cache:
        _word_cache[k] = big_word(text, color, size, font)
    return _word_cache[k]


def scramble_intro(lt, dur):
    """Perkataan bercelaru terapung, kemudian runtuh ke tengah (0:00–0:16)."""
    im = canvas(W, H)
    rnd = random.Random(11)
    words = [("RANCU", 150, RED), ("KACAU", 120, WHITE), ("TIDAK GRAMATIS", 96, WHITE), ("CAMPUR ADUK", 90, (200, 200, 210)),
             ("kepada yang berminat...", 54, (255, 140, 130)), ("best gila", 60, (255, 140, 130)), ("nak share", 58, (255, 140, 130)),
             ("korang kalau suka...", 52, (255, 140, 130)), ("TIDAK TERATUR", 80, WHITE), ("ayat tergantung", 56, GOLD),
             ("tiada subjek", 64, GOLD), ("so, because", 54, (255, 140, 130))]
    collapse = max(0.0, (lt - (dur - 2.6)) / 1.6)
    for i, (t, s, c) in enumerate(words):
        appear = 0.6 + i * 0.75
        if lt < appear:
            continue
        a = _ease((lt - appear) / 0.5)
        bx = rnd.uniform(120, W - 700); by = rnd.uniform(100, H - 220)
        vx = rnd.uniform(-18, 18); vy = rnd.uniform(-10, 10)
        ang0 = rnd.uniform(-14, 14)
        jitter = math.sin(lt * 9 + i) * 2.5 if i % 3 == 0 else 0
        x = bx + vx * lt + jitter; y = by + vy * lt
        k = _ease(collapse)
        img = _word_img(t, s, c)
        ang = ang0 * (1 - k) + math.sin(lt * 1.3 + i) * 3 * (1 - k)
        if abs(ang) > 0.5:
            img = img.rotate(ang, resample=Image.BICUBIC, expand=True)
        cx, cy = W / 2 - img.size[0] / 2, H / 2 - img.size[1] / 2
        x = x * (1 - k) + cx * k; y = y * (1 - k) + cy * k
        alpha = a * (1 - k) * (0.55 if i % 2 else 1.0)
        if alpha <= 0.01:
            continue
        if alpha < 0.99:
            img = img.copy(); img.putalpha(img.split()[3].point(lambda v, al=alpha: int(v * al)))
        im.alpha_composite(img, (int(x), int(y)))
    return im


def rancu_assemble(lt, dur):
    """Huruf R-A-N-C-U bercelaru lalu tersusun kemas."""
    im = canvas(1100, 300)
    letters = "RANCU"
    f = F("mk", 210)
    rnd = random.Random(5)
    widths = [tw(f, ch) for ch in letters]
    total = sum(widths) + 14 * 4
    x = (1100 - total) // 2
    k = _ease((lt - 0.4) / 1.4)
    for i, ch in enumerate(letters):
        sx, sy = rnd.uniform(0, 950), rnd.uniform(-20, 120)
        ang = rnd.uniform(-40, 40)
        gx, gy = x, 20
        px, py = sx * (1 - k) + gx * k, sy * (1 - k) + gy * k
        col = tuple(int(a * (1 - k) + b * k) for a, b in zip(RED, WHITE))
        li = _word_img(ch, 210, col)
        a2 = ang * (1 - k)
        if abs(a2) > 0.5:
            li = li.rotate(a2, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(li, (int(px), int(py)))
        x += widths[i] + 14
    if k > 0.98:
        d = ImageDraw.Draw(im)
        d.rectangle([(1100 - total) // 2, 270, (1100 + total) // 2, 282], fill=GOLD)
    return im


def confetti(lt, dur, n=170, seed=3, gold_only=False):
    im = canvas(W, H)
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    cols = [GOLD, (255, 230, 120)] if gold_only else [GOLD, LGREEN, PURPLE, RED, BLUE, (255, 230, 120)]
    fade = min(1.0, (dur - lt) / 0.8)
    for i in range(n):
        x0 = rnd.uniform(0, W); delay = rnd.uniform(0, 1.2); sp = rnd.uniform(220, 520)
        sw = rnd.uniform(-60, 60); size = rnd.uniform(8, 18); rot = rnd.uniform(0, 6.28); vr = rnd.uniform(-6, 6)
        c = cols[i % len(cols)]
        t = lt - delay
        if t < 0:
            continue
        y = -30 + sp * t
        if y > H + 30:
            continue
        x = x0 + sw * math.sin(t * 2 + i)
        r = rot + vr * t
        w2, h2 = size, size * 0.5 * abs(math.cos(r * 1.7)) + 2
        pts = [(x + math.cos(r) * dx - math.sin(r) * dy, y + math.sin(r) * dx + math.cos(r) * dy)
               for dx, dy in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))]
        d.polygon(pts, fill=c + (int(255 * fade),))
    return im


def sparkles(lt, dur, n=60, seed=8, box=(0, 0, W, H)):
    im = canvas(W, H)
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(box[0], box[2]); y = rnd.uniform(box[1], box[3])
        ph = rnd.uniform(0, 6.28); sp = rnd.uniform(1.5, 4)
        a = max(0.0, math.sin(lt * sp + ph)) ** 3
        if a < 0.05:
            continue
        r = 3 + 5 * a
        y -= 30 * lt
        c = GOLD + (int(255 * a),)
        d.line([x - r * 2, y, x + r * 2, y], fill=c, width=2)
        d.line([x, y - r * 2, x, y + r * 2], fill=c, width=2)
        d.ellipse([x - r / 2, y - r / 2, x + r / 2, y + r / 2], fill=(255, 250, 220, int(255 * a)))
    return im


def flash(lt, dur):
    a = max(0.0, 1 - lt / dur) ** 2
    im = Image.new("RGBA", (W, H), (255, 255, 255, int(200 * a)))
    return im


def letterbox(lt, dur, h=110):
    k = min(_ease(lt / 0.8), _ease((dur - lt) / 0.8))
    im = canvas(W, H)
    d = ImageDraw.Draw(im)
    hh = int(h * k)
    if hh > 0:
        d.rectangle([0, 0, W, hh], fill=(0, 0, 0, 255))
        d.rectangle([0, H - hh, W, H], fill=(0, 0, 0, 255))
    return im


# ---------- Ikon vektor ringkas ----------
def icon(kind, s=110, col=WHITE):
    im = canvas(s, s)
    d = ImageDraw.Draw(im)
    w = max(4, s // 14)
    if kind == "search":
        d.ellipse([s * .12, s * .12, s * .62, s * .62], outline=col, width=w)
        d.line([s * .56, s * .56, s * .88, s * .88], fill=col, width=w + 4)
    elif kind == "cards":
        d.rounded_rectangle([s * .30, s * .10, s * .80, s * .78], 10, outline=col, width=w)
        d.rounded_rectangle([s * .16, s * .22, s * .66, s * .90], 10, fill=(10, 24, 50, 255), outline=col, width=w)
        d.text((s * .28, s * .36), "A", font=F("mk", int(s * .36)), fill=col)
    elif kind == "hash":
        d.text((s * .18, s * .02), "#", font=F("mk", int(s * .9)), fill=col)
    elif kind == "student":
        d.ellipse([s * .32, s * .08, s * .68, s * .44], fill=col)
        d.pieslice([s * .14, s * .48, s * .86, s * 1.2], 180, 360, fill=col)
    elif kind == "teacher":
        d.rectangle([s * .05, s * .12, s * .62, s * .55], outline=col, width=w)
        d.ellipse([s * .62, s * .18, s * .90, s * .46], fill=col)
        d.pieslice([s * .52, s * .5, s * 1.0, s * 1.1], 180, 360, fill=col)
    elif kind == "people":
        for cx in (.25, .5, .75):
            d.ellipse([s * (cx - .12), s * .18, s * (cx + .12), s * .42], fill=col)
            d.pieslice([s * (cx - .2), s * .48, s * (cx + .2), s * .98], 180, 360, fill=col)
    elif kind == "game":
        d.rounded_rectangle([s * .06, s * .28, s * .94, s * .76], 26, outline=col, width=w)
        d.line([s * .24, s * .52, s * .40, s * .52], fill=col, width=w)
        d.line([s * .32, s * .44, s * .32, s * .60], fill=col, width=w)
        d.ellipse([s * .64, s * .42, s * .72, s * .50], fill=col); d.ellipse([s * .74, s * .52, s * .82, s * .60], fill=col)
    elif kind == "medal":
        d.polygon([(s * .3, 0), (s * .45, s * .4), (s * .55, s * .4), (s * .7, 0)], fill=col)
        d.ellipse([s * .22, s * .36, s * .78, s * .92], fill=col)
    elif kind == "phone":
        d.rounded_rectangle([s * .28, s * .04, s * .72, s * .96], 14, outline=col, width=w)
    elif kind == "block":
        d.rectangle([s * .15, s * .15, s * .85, s * .85], fill=col)
        d.rectangle([s * .15, s * .15, s * .85, s * .35], fill=tuple(min(255, c + 40) for c in col[:3]))
    return im


def icon_card(num, title, body, ic, accent=GOLD, w=520, h=None):
    ft = F("mx", 34)
    fb = F("pr", 24)
    btok = parse_marked(body, {"font": fb, "color": (215, 225, 238)}, MARKS(24))
    bh = rich_height(btok, w - 64, fb)
    th = rich_height([(title, {"font": ft})], w - 190, ft)
    h = h or max(170, 40 + max(th, 110) + 20 + bh + 34)
    im = panel(w, h, fill=(10, 24, 50, 238), accent=accent)
    d = ImageDraw.Draw(im)
    im.alpha_composite(icon(ic, 96, accent), (32, 30))
    d.text((w - 80, 22), str(num), font=F("mk", 56), fill=accent + (90,))
    draw_rich(im, (146, 40), [(title, {"font": ft, "color": WHITE})], w - 220, ft)
    draw_rich(im, (32, 40 + max(th, 110) + 14), btok, w - 64, fb)
    return shadowed(im)[0]


def chip(text, color=BLUE, size=34, fg=WHITE, font="mx"):
    return shadowed(pill(text, F(font, size), fg=fg, bg=color, padx=24, pady=12), 10, (0, 6), 0.5, 24)[0]


def list_item(num, text, accent=GOLD, w=980, active=True):
    f = F("ps", 34)
    h = 74
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=(10, 24, 50, 230) if active else (10, 24, 50, 150))
    d.rounded_rectangle([0, 0, 74, h - 1], 16, fill=accent)
    nf = F("mk", 38)
    d.text(((74 - tw(nf, str(num))) // 2, 12), str(num), font=nf, fill=INK)
    draw_rich(im, (98, 14), parse_marked(text, {"font": f, "color": WHITE}, MARKS(34)), w - 120, f)
    return im


def heading(kicker, title, w=1080, accent=GOLD):
    fk = F("mb", 26); ft = F("mk", 60)
    tok = parse_marked(title, {"font": ft, "color": WHITE}, {"Y": {"font": ft, "color": GOLD}, "G": {"font": ft, "color": LGREEN},
                                                              "R": {"font": ft, "color": RED}, "B": {"font": ft, "color": BLUE},
                                                              "P": {"font": ft, "color": PURPLE}})
    th = rich_height(tok, w, ft)
    im = canvas(w, 50 + th + 10)
    d = ImageDraw.Draw(im)
    d.text((0, 0), kicker, font=fk, fill=accent)
    d.rectangle([0, 38, 90, 44], fill=accent)
    draw_rich(im, (0, 54), tok, w, ft)
    return shadowed(im, 12, (0, 4), 0.7, 20)[0]


def flow_vertical(items, w=700):
    """items: senarai (teks, warna, subteks) dengan anak panah ke bawah."""
    blocks = []
    for t, c, sub in items:
        blocks.append(block(t, sub, c, w=w, h=130, tsize=46))
    ah = 64
    H2 = sum(b.size[1] for b in blocks) + ah * (len(blocks) - 1)
    im = canvas(w, H2)
    d = ImageDraw.Draw(im)
    y = 0
    for i, b in enumerate(blocks):
        im.alpha_composite(b, (0, y)); y += b.size[1]
        if i < len(blocks) - 1:
            d.polygon([(w / 2 - 22, y + 12), (w / 2 + 22, y + 12), (w / 2, y + ah - 8)], fill=GOLD)
            y += ah
    return shadowed(im, 14)[0]


def medal_row():
    data = [("EMAS", (247, 196, 58), "Salah 0–3", "Bonus +300"), ("PERAK", (200, 205, 215), "Salah 4–7", "Bonus +150"),
            ("GANGSA", (205, 127, 50), "Salah 8 ke atas", "Bonus +0")]
    out = []
    for name, col, a, b in data:
        w, h = 330, 330
        im = panel(w, h, fill=(14, 12, 36, 240), border=col + (255,), bw=4)
        d = ImageDraw.Draw(im)
        im.alpha_composite(icon("medal", 120, col), ((w - 120) // 2, 26))
        f = F("mk", 44)
        d.text(((w - tw(f, name)) // 2, 160), name, font=f, fill=col)
        f2 = F("ps", 28)
        d.text(((w - tw(f2, a)) // 2, 222), a, font=f2, fill=WHITE)
        d.text(((w - tw(f2, b)) // 2, 262), b, font=F("pb", 28), fill=LGREEN)
        out.append(shadowed(im)[0])
    return out


def teacher_panel():
    w, h = 760, 520
    im = panel(w, h, fill=(12, 16, 40, 245), border=(235, 64, 52, 255), bw=4)
    d = ImageDraw.Draw(im)
    im.alpha_composite(icon("block", 70, (200, 30, 30)), (34, 30))
    d.text((124, 30), "SUDUT GURU", font=F("mk", 50), fill=WHITE)
    d.text((126, 92), "Blok redstone • fungsi untuk guru", font=F("ps", 24), fill=(255, 170, 160))
    items = ["Menetapkan semula markah", "Melihat laporan kemajuan murid", "Mengenal pasti kesalahan yang kerap",
             "Merancang pengajaran susulan"]
    y = 160
    for i, t in enumerate(items):
        d.rounded_rectangle([34, y, w - 34, y + 70], 14, fill=(26, 34, 70, 255))
        d.text((54, y + 12), "✓", font=SYMF(36), fill=LGREEN)
        d.text((104, y + 14), t, font=F("ps", 30), fill=WHITE)
        y += 86
    return shadowed(im)[0]


# ---------- Bukti media sosial ----------
PLATFORM_COL = {"TikTok": (20, 20, 24), "YouTube": (205, 32, 31), "Threads": (40, 40, 48)}

EVIDENCE = {
    1: [("J1.1", "TikTok", "iklan jawatan", "[r:kepada yang berminat] boleh maklumkan di ruangan comment."),
        ("J1.2", "TikTok", "iklan jawatan", "[r:Kepada yang berminat] boleh emailkan resume ke […] atau WhatsApp ke […]"),
        ("J1.3", "TikTok", "promosi homestay", "[r:Kalau berminat boleh wasap] ya..click link di bio"),
        ("J1.4", "TikTok", "balasan penonton", "[r:Semoga dipermudahkan] urusan sis"),
        ("J1.5", "TikTok", "promosi servis", "[r:Yang mana berminat] nak buat pemasangan aircond boleh wasap saya okeh")],
    2: [("J2.1", "TikTok", "ulasan makanan", "Kedai malatang [r:yang paling sedap kat KL.]"),
        ("J2.2", "TikTok", "ulasan restoran", "[r:Restoran mewah] tapi [r:harga murah]"),
        ("J2.3", "TikTok", "resipi", "Korang [r:kalau suka snek sayur goreng rangup macam ni.]"),
        ("J2.4", "TikTok", "ulasan makanan", "[r:Nasi Lemak Paling Sedap Di KL]"),
        ("J2.5", "TikTok", "ulasan makanan", "Nasi lemak sedap di Bukit Bintang KL [r:yang wajib korang singgah.]")],
    3: [("J3.1", "TikTok", "promosi fotografi", "Pakej serendah RM 30 [r:only] !! Cepat tekan [r:link] di bio utk [r:booking slot]"),
        ("J3.2", "TikTok", "ulasan kafe", "[r:Best gila] lepak [r:chill] kat Notte by MÜES guys, wajib [r:try] pizza dia!"),
        ("J3.3", "TikTok", "ulasan makanan", "Strudel dia [r:best gila]!!! […] Wajib [r:try] kalau korang suka strudel !!"),
        ("J3.4", "TikTok", "tips perniagaan", "Jangan risau, saya nak [r:share] sikit tips ni! […] [r:So], kalau beg kuning korang hilang, [r:check] dulu semua ni."),
        ("J3.5", "TikTok", "promosi produk", "Sabun aleppo [r:viral] ni memang lain macam lembut & [r:best gila] kat kulit!")],
}
EXTRA_EVIDENCE = [("Skrip", "YouTube", "tajuk video", "Harini [r:team] kami nak [r:share] cara buat kek."),
                  ("Skrip", "Threads", "ulasan", "[r:Overall best gila], wajib [r:try guys]!")]


def evidence_card(ref, platform, ctx, quote, accent, w=580, size=22):
    fq = F("ps", size)
    tok = parse_marked(quote, {"font": fq, "color": INK}, {"r": {"font": F("pb", size), "color": WHITE, "hl": (205, 40, 40, 255)}})
    th = rich_height(tok, w - 44, fq)
    hh = 44
    h = 18 + hh + 12 + th + 18
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=(246, 247, 250, 255))
    d.rounded_rectangle([0, 0, 8, h - 1], 4, fill=accent + (255,))
    pp = pill(platform, F("mx", 18), fg=WHITE, bg=PLATFORM_COL.get(platform, INK), padx=12, pady=5)
    im.alpha_composite(pp, (22, 18))
    x = 22 + pp.size[0] + 10
    d.text((x, 22), f"{'Bukti ' + ref if ref != 'Skrip' else 'Contoh skrip'} • {ctx}", font=F("is", 17), fill=(95, 102, 115))
    # akaun dikaburkan
    d.rounded_rectangle([w - 120, 24, w - 22, 40], 8, fill=(200, 204, 212))
    draw_rich(im, (22, 18 + hh + 6), tok, w - 44, fq)
    return shadowed(im, 12, (0, 6), 0.45, 22)[0]


def vis_box(img):
    """Kotak nyata (tanpa bayang) bagi imej lapisan: (x0,y0,x1,y1)."""
    a = img.getchannel("A").point(lambda v: 255 if v > 180 else 0)
    return a.getbbox() or (0, 0, img.size[0], img.size[1])


def medal_small(name, col, a, b, w=560):
    h = 120
    im = panel(w, h, fill=(14, 12, 36, 240), border=col + (255,), bw=3)
    d = ImageDraw.Draw(im)
    im.alpha_composite(icon("medal", 84, col), (24, 18))
    d.text((128, 20), name, font=F("mk", 40), fill=col)
    d.text((128, 72), a, font=F("ps", 24), fill=WHITE)
    fb = F("pb", 26)
    d.text((w - 30 - tw(fb, b), 40), b, font=fb, fill=LGREEN)
    return shadowed(im, 12, (0, 6), 0.5, 22)[0]
