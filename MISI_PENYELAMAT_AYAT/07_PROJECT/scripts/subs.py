"""Sarikata: penjajaran ASR ↔ skrip, penandaan kata kunci, penjanaan ASS (dinamik) & SRT."""
import json, re, difflib


def norm(w):
    w = w.lower()
    w = re.sub(r"[^\w\-]", "", w)
    return w.replace("-", "")


def load_asr(path):
    segs = json.load(open(path))
    words = []
    for s in segs:
        for w in s["words"]:
            t = w["w"].strip()
            if t:
                words.append({"s": w["s"], "e": w["e"], "w": t})
    return words


def script_words(path):
    toks = []
    for line in open(path):
        who, txt = line.rstrip("\n").split("\t", 1)
        txt = txt.replace("rakan- rakan", "rakan-rakan").replace("tertunggu- tunggu", "tertunggu-tunggu").replace("murid- murid", "murid-murid")
        for w in txt.split():
            toks.append(w)
    return toks


def align(asr, ref_words, sim_min=0.55):
    """Pulangkan senarai perkataan dgn masa audio; ejaan diambil daripada skrip bila sepadan."""
    a = [norm(w["w"]) for w in asr]
    b = [norm(w) for w in ref_words]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                w = asr[i1 + k]
                out.append({"s": w["s"], "e": w["e"], "w": ref_words[j1 + k], "src": "skrip"})
        elif op == "replace":
            sa = " ".join(a[i1:i2]); sb = " ".join(b[j1:j2])
            ratio = difflib.SequenceMatcher(None, sa, sb).ratio()
            la, lb = i2 - i1, j2 - j1
            if ratio >= sim_min and 0.5 <= lb / la <= 2.0 and la <= 12:
                t0, t1 = asr[i1]["s"], asr[i2 - 1]["e"]
                # agih masa ikut panjang aksara
                lens = [max(len(x), 2) for x in ref_words[j1:j2]]
                tot = sum(lens); acc = 0
                for k, x in enumerate(ref_words[j1:j2]):
                    s = t0 + (t1 - t0) * acc / tot; acc += lens[k]
                    e = t0 + (t1 - t0) * acc / tot
                    out.append({"s": s, "e": e, "w": x, "src": "skrip~"})
            else:
                for k in range(i1, i2):
                    w = asr[k]
                    out.append({"s": w["s"], "e": w["e"], "w": w["w"], "src": "asr"})
        elif op == "insert":
            pass  # perkataan skrip yang tidak diucapkan – tidak dipaparkan
        elif op == "delete":
            for k in range(i1, i2):
                w = asr[k]
                out.append({"s": w["s"], "e": w["e"], "w": w["w"], "src": "asr"})
    return out


# ---------- Penandaan kata kunci ----------
# kelas: Y (kuning, kata kunci utama, HURUF BESAR), B (biru, istilah akademik), R (merah, kesalahan), G (hijau, pembetulan)
KEYWORDS = [
    ("Y", "kacau dan tidak teratur"), ("Y", "kacau, tidak teratur atau campur aduk"), ("Y", "menyalahi peraturan tatabahasa"),
    ("Y", "kerancuan bahasa"), ("Y", "subjek dan predikat"), ("Y", "dua unsur utama"), ("Y", "ayat tanpa subjek"),
    ("Y", "ayat tidak lengkap"), ("Y", "bahasa rojak"), ("Y", "Misi Penyelamat Ayat"), ("Y", "empat sebab"),
    ("Y", "media sosial"), ("Y", "paling hampir dengan murid"), ("Y", "dianggap normal"), ("Y", "bakal guru"),
    ("Y", "bukan kesalahan kata secara terpencil"), ("Y", "binaan ayat secara keseluruhan"), ("Y", "tiada predikat"),
    ("Y", "klausa tergantung"), ("Y", "tanpa klausa utama"), ("Y", "Minecraft Education"), ("Y", "seratus markah"),
    ("Y", "lima puluh"), ("Y", "Penyelamat Ayat"), ("Y", "Sudut Guru"), ("Y", "celik bahasa"), ("Y", "pingat emas"),
    ("Y", "Betulkan ayat, selamatkan bahasa"), ("Y", "maksud ayat menjadi kabur"), ("Y", "mesej tidak sampai"),
    ("Y", "martabat bahasa Melayu"), ("Y", "Perkara 152"), ("Y", "sekolah rendah"), ("Y", "laporan kemajuan"),
    ("Y", "Detektif Ayat Media Sosial"), ("Y", "Selamatkan Ayat"), ("Y", "#AyatBetulSekolahku"),
    ("B", "sintaksis"), ("B", "subjek"), ("B", "predikat"), ("B", "frasa sendi nama"), ("B", "kata sendi nama"),
    ("B", "frasa nama"), ("B", "klausa relatif"), ("B", "klausa terikat"), ("B", "klausa bebas"), ("B", "klausa utama"),
    ("B", "klausa"), ("B", "kata kerja transitif"), ("B", "objek"), ("B", "ayat majmuk"), ("B", "kata hubung"),
    ("B", "frasa kerja"), ("B", "frasa adjektif"), ("B", "inti"), ("B", "penerang"), ("B", "keterangan"),
    ("B", "Kamus Dewan"), ("B", "gramatis"), ("B", "tatabahasa"), ("B", "kata ganti nama"), ("B", "penentu"),
    ("B", "kata penegas"),
]
WRONG = [
    "Kepada yang berminat boleh maklumkan di ruangan komen", "Kalau berminat boleh wasap ya", "Semoga dipermudahkan urusan sis",
    "Berminat boleh walkin ke kedai kami", "Kedai malatang yang paling sedap kat KL", "Restoran mewah tapi harga murah",
    "Korang kalau suka snek macam ni", "Harini team kami nak share cara buat kek", "Overall best gila, wajib try guys",
    "Pakej serendah RM30 only", "Tekan link di bio", "Kami pergi shopping di pasar raya, so kami penat sangat",
    "Bagi saya berpendapat bahawa", "Dalam cerita itu mengisahkan", "Apabila loceng berbunyi",
    "Ayah membeli di kedai", "Kepada semua murid dikehendaki berkumpul di dewan", "Bagi murid yang datang lewat akan didenda",
    "Rumah Ali yang besar di hujung kampung itu", "Saya sangat happy kerana dapat hadiah", "Kerana rumah Ali", "yang di hujung kampung",
]
RIGHT = [
    "Mereka yang berminat boleh memaklumkan di ruangan komen", "Jika anda berminat, anda boleh menghubungi kami",
    "Saya berdoa semoga urusan sis dipermudah", "Pelanggan yang berminat boleh datang ke kedai kami",
    "Kedai ini ialah kedai malatang paling sedap di KL", "Restoran ini mewah tetapi harganya murah",
    "Kalau kalian suka snek ini, kalian wajib mencubanya", "Hari ini pasukan kami ingin berkongsi cara membuat kek",
    "Pakej serendah RM30 sahaja", "Tekan pautan di bio", "Secara keseluruhan, makanan ini sangat bagus",
    "Anda wajib mencubanya", "Kami pergi membeli-belah di pasar raya, oleh itu kami sangat penat",
    "Rumah Ali yang besar itu terletak di hujung kampung", "Rumah Ali yang besar itu", "terletak di hujung kampung",
    "Murid membaca buku", "gembira",
]


def tag_words(words):
    nw = [norm(w["w"]) for w in words]
    for w in words:
        w.setdefault("tag", None)

    def mark(phrase, tag, fuzzy=False):
        p = [norm(x) for x in phrase.split()]
        n = len(p)
        if n == 0:
            return
        i = 0
        while i <= len(nw) - n:
            seg = nw[i:i + n]
            ok = seg == p
            if not ok and fuzzy and n >= 4:
                ok = difflib.SequenceMatcher(None, " ".join(seg), " ".join(p)).ratio() > 0.8
            if ok and all(words[i + k]["tag"] in (None, "B") or tag in ("R", "G") for k in range(n)):
                if all(words[i + k]["tag"] is None or tag in ("R", "G") for k in range(n)):
                    for k in range(n):
                        words[i + k]["tag"] = tag
                    i += n
                    continue
            i += 1

    for s in WRONG:
        mark(s, "R", fuzzy=True)
    for s in RIGHT:
        mark(s, "G", fuzzy=True)
    for tag, s in KEYWORDS:
        mark(s, tag)
    return words


# ---------- Pembinaan kiu ----------
def build_cues(words, max_chars=78, max_dur=6.5, gap_break=0.6):
    cues, cur = [], []

    def flush():
        if cur:
            cues.append(list(cur)); cur.clear()

    for i, w in enumerate(words):
        if cur:
            txt = " ".join(x["w"] for x in cur)
            if (len(txt) + 1 + len(w["w"]) > max_chars or w["s"] - cur[-1]["e"] > gap_break
                    or w["e"] - cur[0]["s"] > max_dur or w.get("cut")):
                flush()
        cur.append(w)
        if re.search(r"[.?!]['\"”’)]?$", w["w"]) and len(" ".join(x["w"] for x in cur)) > 18:
            flush()
        elif re.search(r"[,;:]$", w["w"]) and len(" ".join(x["w"] for x in cur)) > 52:
            flush()
    flush()
    out = []
    for c in cues:
        s = c[0]["s"] - 0.04
        e = c[-1]["e"] + 0.25
        out.append({"s": s, "e": e, "words": c})
    for a, b in zip(out, out[1:]):
        if a["e"] > b["s"] - 0.04:
            a["e"] = max(a["s"] + 0.3, b["s"] - 0.04)
    for c in out:
        if c["e"] - c["s"] < 0.9:
            c["e"] = c["s"] + 0.9
    for a, b in zip(out, out[1:]):
        if a["e"] > b["s"] - 0.04:
            a["e"] = max(a["s"] + 0.3, b["s"] - 0.04)
    return out


def split_two_lines(txt_words, max_line=42):
    s = " ".join(txt_words)
    if len(s) <= max_line:
        return [txt_words]
    best, bi = 1e9, 1
    acc = 0
    for i in range(1, len(txt_words)):
        l1 = len(" ".join(txt_words[:i])); l2 = len(" ".join(txt_words[i:]))
        sc = abs(l1 - l2) + (0 if txt_words[i - 1][-1:] in ",.;:" else 6)
        if sc < best:
            best, bi = sc, i
    return [txt_words[:bi], txt_words[bi:]]


ASS_COL = {"Y": "&H0AD6FF&", "B": "&HF5A63F&", "R": "&H4E4CFF&", "G": "&H6ED658&"}  # BGR


def fmt_ass_time(t):
    t = max(0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def fmt_srt_time(t):
    t = max(0, t)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clean_display(w):
    return w.replace('"', "").replace("“", "").replace("”", "")


def write_ass(cues, path, margin_v=46):
    head = f"""[Script Info]
Title: Misi Penyelamat Ayat – Sarikata Dinamik
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat SemiBold,50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0.5,0,1,3.2,2.2,2,160,160,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in cues:
        ws = c["words"]
        disp = []
        for w in ws:
            t = clean_display(w["w"])
            if not t:
                continue
            tag = w.get("tag")
            if tag == "Y":
                t = t.upper()
            disp.append((t, tag))
        if not disp:
            continue
        rows = split_two_lines([d[0] for d in disp])
        k = 0
        parts = []
        for ri, row in enumerate(rows):
            seg = []
            for _ in row:
                t, tag = disp[k]; k += 1
                if tag:
                    seg.append("{\\fnMontserrat ExtraBold\\c" + ASS_COL[tag] + "}" + t + "{\\r}")
                else:
                    seg.append(t)
            parts.append(" ".join(seg))
        text = "\\N".join(parts)
        # animasi masuk halus: fade + naik sedikit
        lines.append(f"Dialogue: 0,{fmt_ass_time(c['s'])},{fmt_ass_time(c['e'])},Sub,,0,0,0,,{{\\fad(90,70)}}{text}")
    open(path, "w").write(head + "\n".join(lines) + "\n")


def write_srt(cues, path):
    out = []
    n = 0
    for c in cues:
        words = [clean_display(w["w"]) for w in c["words"]]
        words = [w for w in words if w]
        if not words:
            continue
        n += 1
        rows = split_two_lines(words)
        out.append(f"{n}\n{fmt_srt_time(c['s'])} --> {fmt_srt_time(c['e'])}\n" + "\n".join(" ".join(r) for r in rows) + "\n")
    open(path, "w").write("\n".join(out))
