"""MISI PENYELAMAT AYAT – skrip binaan utama (EDL → video asas → compositor → audio → eksport).
Guna:  python3 build.py plan | base | render [t0 t1] | audio | mux | all
"""
import os, sys, json, math, subprocess, wave, re, difflib, bisect, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import gfx, subs
import compositor as C

FPS = 30
TOTAL = 1800.0
PEN = f"{ROOT}/01_RAW_VIDEO/video_penerangan.mp4"
GAME = f"{ROOT}/03_MINECRAFT_GAMEPLAY/gameplay_minecraft.mp4"
SGURU = f"{ROOT}/03_MINECRAFT_GAMEPLAY/sudut_guru.mp4"
CACHE = f"{ROOT}/07_PROJECT/cache"
os.makedirs(CACHE, exist_ok=True)


def q(t):  # kuantum ke bingkai
    return round(t * FPS) / FPS


# =====================================================================
# 1. KEPINGAN UCAPAN (masa sumber, saat) – dipilih daripada transkrip
# =====================================================================
ALIFF = ("Mohamad Aliff bin Ahmad Shahabuddin", "Pembentang")
IMAN = ("Muhammad Iman Irfan bin Mohd Ramzi", "Pembentang")
AMIN = ("Amin Najmi bin Mohyidin", "Pembentang")

PIECES = {
    "A1": [(1.52, 66.42)],
    "A2": [(153.91, 165.55, "hard"), (85.69, 124.09)],
    "B": [(214.00, 359.88)],
    "C": [(367.62, 539.21), (547.88, 555.54)],
    "D": [(562.54, 652.78), (707.44, 730.92), (732.40, 734.56), (738.72, 758.56), (655.40, 701.52)],
    "E": [(767.89, 862.09), (914.96, 940.20), (946.80, 965.48), (865.32, 904.52)],
    "F": [(972.39, 1016.57), (1028.04, 1055.08), (1155.72, 1186.06), (1187.98, 1202.14), (1057.85, 1134.07), (1138.66, 1147.68)],
    "G": [(1208.72, 1316.56)],
    "H1": [(1322.57, 1427.29)],
    "H2": [(1441.54, 1493.94)],
    "H3": [(1497.23, 1509.45), (1513.80, 1524.66), (1548.63, 1585.75), (1589.20, 1627.06)],
    "H4": [(1633.80, 1678.35), (1686.32, 1711.80)],
    "H5": [(1727.82, 1777.04)],
    "H6": [(1779.82, 1850.80)],
    "I": [(1854.42, 1912.02), (1921.53, 1923.73), (1937.97, 1977.29)],
    "J": [(1991.77, 2029.03)],
    "K": [(2029.43, 2052.53)],
}
SPEAKER = {"A1": ALIFF, "A2": ALIFF, "B": AMIN, "C": IMAN, "D": ALIFF, "E": AMIN, "F": IMAN, "G": ALIFF,
           "H1": ALIFF, "H2": AMIN, "H3": IMAN, "H4": AMIN, "H5": AMIN, "H6": AMIN, "I": ALIFF, "J": ALIFF, "K": ALIFF}

# kawasan potongan potret (x,y,w,h dalam 1920x1080) mengikut syot
SPLIT = {"A1": (500, 0, 920, 1080), "B": (640, 160, 640, 751), "C": (560, 0, 920, 1080), "D": (1000, 0, 920, 1080),
         "E": (500, 0, 920, 1080), "F": (500, 0, 920, 1080), "G": (420, 0, 920, 1080), "I": (500, 0, 920, 1080),
         "J": (500, 0, 920, 1080), "K": (500, 0, 920, 1080), "H1": (500, 0, 920, 1080)}
BASEZOOM = {"B": (1.42, 1.48), "C": (1.0, 1.05), "D": (1.0, 1.05), "E": (1.0, 1.04), "F": (1.0, 1.05)}
CENTER = {"B": (960, 520), "D": (1500, 520)}

PAD_IN, PAD_OUT, MAXGAP = 0.16, 0.28, 0.75
# selang tambahan (tanpa ucapan) disisip dalam bahagian: (masa sumber, tempoh, tag)
PAUSES = {"C": [(443.5, 4.5, "bukti-C")], "D": [(618.30, 4.6, "bukti-D")], "E": [(832.85, 4.6, "bukti-E")]}
MAXGAP_SEC = {"A2": 6.0}

# =====================================================================
# 2. ENERGI AUDIO – untuk melaraskan titik potong ke kawasan senyap
# =====================================================================
_env = None


def energy():
    global _env
    if _env is None:
        wf = wave.open(f"{ROOT}/02_AUDIO/penerangan_16k.wav")
        a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
        hop = 160  # 10 ms
        n = len(a) // hop
        _env = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    return _env


def snap_quiet(t, lo, hi):
    """Cari titik paling senyap dalam [lo,hi] (saat)."""
    e = energy()
    i0, i1 = max(0, int(lo * 100)), min(len(e) - 1, int(hi * 100))
    if i1 <= i0:
        return t
    seg = np.convolve(e[i0:i1 + 1], np.ones(5) / 5, mode="same")
    return (i0 + int(np.argmin(seg))) / 100.0


# =====================================================================
# 3. PERKATAAN (ASR dijajarkan dengan skrip)
# =====================================================================
def load_words():
    asr = subs.load_asr(f"{ROOT}/06_SUBTITLES/asr_penerangan.json")
    ref = subs.script_words(f"{ROOT}/07_PROJECT/skrip_ucapan.tsv")
    al = subs.align(asr, ref)
    fix_words(al)
    return al


NAME_FIX = [
    (r"^pencarah$", "pensyarah"), (r"^seterakan-rakan$", "serta rakan-rakan"), (r"^Iman$", "Iman"),
    (r"^Rifai\.$", "Irfan."), (r"^Halif$", "Aliff"), (r"^Alif,?$", "Aliff,"), (r"^Alif$", "Aliff"),
    (r"^Dewat\.?$", "dewan."), (r"^delimit\.$", "DELIMa."), (r"^halia\.$", "khalayak."), (r"^Dahliah$", "Dahlia"),
    (r"^gilirik$", "galeri"), (r"^geliri$", "galeri"), (r"^kaksian$", "kapsyen"), (r"^caption$", "kapsyen"),
    (r"^zamrut,?$", "zamrud,"), (r"^lobby$", "lobi"), (r"^pengacuh$", "pengecoh"), (r"^klausak$", "klausa"),
    (r"^klasak\.?$", "klausa."), (r"^klausah$", "klausa"), (r"^perasaan$", "frasa"), (r"^perasa$", "frasa"),
    (r"^Tread$", "Threads"), (r"^bakuk\.$", "baku."), (r"^keracuan$", "kerancuan"), (r"^membazmi$", "membasmi"),
    (r"^Bahasa Had\.$", "basahan."), (r"^Had\.$", "basahan."), (r"^membentulkannya\.?$", "membetulkannya."),
    (r"^menghomongi\??$", "menghubungi"), (r"^Pakis$", "Pakej"), (r"^gamsa\.$", "gangsa."), (r"^Papam$", "Papan"),
    (r"^permain$", "pemain"), (r"^mengulap\.$", "ulang."), (r"^kompset$", "konsep"), (r"^pakor$", "parkour"),
    (r"^bergila$", "bergilir"), (r"^-gila$", "-gilir"), (r"^membetukkan$", "membetulkan"), (r"^penetia$", "panitia"),
    (r"^dikelingi$", "dikelilingi"), (r"^percipta$", "pencipta"), (r"^merakankan$", "merakamkan"),
    (r"^doktor$", "Dr."), (r"^situasi$", "sintaksis"), (r"^mengusungkan$", "mengosongkan"), (r"^Activity$", "Aktiviti"),
    (r"^membentukannya\.$", "membetulkannya."), (r"^bakar$", "bakal"), (r"^cake\.$", "kek."), (r"^tim$", "team"),
]


SEQ_FIX = [
    # (urutan perkataan dipaparkan [dinormalkan], teks pengganti)
    ("hari ni tim kami nak share cara buat kek", 'Harini team kami nak share cara buat kek.'),
    ("dan overall best gila wajib cuba guys", 'Dan "Overall best gila, wajib try guys!"'),
    ("pakej rendah rm30 saja tekan link di bio", '"Pakej serendah RM30 only! Tekan link di bio."'),
    ("dan overall best gila wajib cuba", 'Dan "Overall best gila, wajib try guys!"'),
    ("keterangan peranikat dan objek", "keterangan, predikat dan objek"),
    ("kami pergi membeli-belah di pasar raya jadi kami sangat penat", '"Kami pergi shopping di pasar raya, so kami penat sangat."'),
    ("kata hubung bahasa inggeris jadi digunakan untuk menghubungkan dua kawasan", 'Kata hubung bahasa Inggeris "so" digunakan untuk menghubungkan dua klausa.'),
    ("karangan mereka surat rasmi", "karangan mereka, surat rasmi"),
    ("saya sangat bahagia kerana dapat hadiah", '"Saya sangat happy kerana dapat hadiah."'),
    ("gembira bahagia dan marah", '"gembira", "happy" dan "marah".'),
    ("ialah saya benar-benar semua urusan sis dipermudah", 'ialah "Saya berdoa semoga urusan sis dipermudah"'),
    ("semoga dipermudahkan urusan sis dan berminat boleh masuk ke kedai kami", '"Semoga dipermudahkan urusan sis" dan "Berminat boleh walkin ke kedai kami."'),
    ("dimudakan", "dimulakan"),
    ("6 bahagian bahagian pertama", "6 bahagian. Bahagian pertama,"),
    ("bagi klausa utama", "bagi klausa utama."),
]


def apply_seq_fix(words):
    for old, new in SEQ_FIX:
        o = [subs.norm(x) for x in old.split()]
        o = [x for x in o if x]
        i = 0
        while i <= len(words) - len(o):
            seg = [subs.norm(w["w"]) for w in words[i:i + len(o)]]
            # gabung token berpisah sempang (cth. "membeli" "-belah")
            if seg == o:
                t0, t1 = words[i]["s"], words[i + len(o) - 1]["e"]
                nw = new.split()
                lens = [max(len(x), 2) for x in nw]
                tot = sum(lens); acc = 0
                rep = []
                for k, x in enumerate(nw):
                    a = t0 + (t1 - t0) * acc / tot; acc += lens[k]
                    rep.append({"s": a, "e": t0 + (t1 - t0) * acc / tot, "w": x, "src": "betul"})
                words[i:i + len(o)] = rep
                i += len(rep)
            else:
                i += 1


def merge_hyphen(words):
    out = []
    for w in words:
        if out and w["w"].startswith("-") and len(w["w"]) > 1:
            out[-1]["w"] += w["w"]; out[-1]["e"] = w["e"]
        else:
            out.append(w)
    words[:] = out


def fix_words(words):
    merge_hyphen(words)
    _name_fix(words)
    apply_seq_fix(words)


def _name_fix(words):
    for w in words:
        if w["src"] == "skrip":
            continue
        for pat, rep in NAME_FIX:
            if re.match(pat, w["w"]):
                w["w"] = re.sub(pat, rep, w["w"])
                break
    # nama penuh
    for i in range(len(words) - 4):
        seg = " ".join(x["w"] for x in words[i:i + 5]).lower()
        if seg.startswith("muhammad ali bin ahmad"):
            words[i]["w"] = "Mohamad"; words[i + 1]["w"] = "Aliff"; words[i + 4]["w"] = "Shahabuddin"
        if seg.startswith("dr. siti dahlia binti abdullah") or seg.startswith("dr. siti dahlia binti"):
            pass


# =====================================================================
# 4. GARIS MASA
# =====================================================================
class TL:
    def __init__(self):
        self.t = 0.0
        self.chunks = []      # dict(sec, src_s, src_e, out_s, out_e)
        self.gaps = []        # dict(t0,t1,tag)
        self.sec_range = {}

    def gap(self, dur, tag=""):
        t0 = self.t
        self.t = q(self.t + dur)
        self.gaps.append({"t0": t0, "t1": self.t, "tag": tag})
        return t0

    def speech(self, sec, words, between=0.0, pause_before_piece=None):
        t_start = self.t
        pauses = sorted(PAUSES.get(sec, []))
        for pi, piece in enumerate(PIECES[sec]):
            a, b = piece[0], piece[1]
            if pause_before_piece and pi in pause_before_piece:
                d_, tag_ = pause_before_piece[pi]
                self.gap(d_, tag_)
            if len(piece) > 2 and piece[2] == "hard":
                s0 = math.floor((a - PAD_IN) * FPS) / FPS
                n = round((b - s0) * FPS)
                ws = [w for w in words if w["s"] >= s0 and w["e"] <= b + 0.05]
                ch = {"sec": sec, "src_s": s0, "src_e": s0 + n / FPS, "out_s": self.t, "out_e": q(self.t + n / FPS), "words": ws}
                self.chunks.append(ch); self.t = ch["out_e"]
                if pi < len(PIECES[sec]) - 1 and between:
                    self.t = q(self.t + between)
                continue
            ws = [w for w in words if w["s"] >= a - 0.05 and w["e"] <= b + 0.08]
            runs, cur = [], [ws[0]]
            e = energy()
            floor = np.percentile(e[int(a * 100):int(b * 100)], 20) + 1e-5
            for w in ws[1:]:
                g0, g1 = cur[-1]["e"] + 0.1, w["s"] - 0.1
                speechy = int((e[int(g0 * 100):int(g1 * 100)] > floor * 6).sum()) if g1 > g0 else 0
                forced = any(cur[-1]["e"] <= pt <= w["s"] + 0.05 for pt, _, _ in pauses)
                if forced or (w["s"] - cur[-1]["e"] > MAXGAP_SEC.get(sec, MAXGAP) and speechy < 35):
                    runs.append(cur); cur = [w]
                else:
                    cur.append(w)
            runs.append(cur)
            for ri, r in enumerate(runs):
                for pt, pd, ptag in pauses:
                    if abs(r[0]["s"] - pt) < 0.6 and ri > 0:
                        self.gap(pd, ptag)
                s0 = r[0]["s"] - PAD_IN
                s1 = r[-1]["e"] + PAD_OUT
                s0 = snap_quiet(s0, s0 - 0.12, r[0]["s"] - 0.04)
                s1 = snap_quiet(s1, r[-1]["e"] + 0.06, s1 + 0.15)
                s0 = math.floor(s0 * FPS) / FPS
                n = max(1, round((s1 - s0) * FPS))
                ch = {"sec": sec, "src_s": s0, "src_e": s0 + n / FPS, "out_s": self.t, "out_e": q(self.t + n / FPS), "words": r}
                self.chunks.append(ch)
                self.t = ch["out_e"]
            if pi < len(PIECES[sec]) - 1 and between:
                self.t = q(self.t + between)
        self.sec_range[sec] = (t_start, self.t)
        return t_start


def build_timeline(words):
    T = TL()
    T.gap(11.0, "opener")          # 0:00 skrin gelap + perkataan bercelaru
    T.gap(3.4, "maintitle")        # kad tajuk utama (tanpa klip Minecraft)
    T.speech("A1", words)
    T.gap(0.5, "a-mid")
    T.speech("A2", words, between=0.35)
    T.gap(1.8, "sting-B")
    T.speech("B", words)
    T.gap(1.8, "sting-C")
    T.speech("C", words, between=0.3)
    T.gap(1.8, "sting-D")
    T.speech("D", words, between=0.45)
    T.gap(1.8, "sting-E")
    T.speech("E", words, between=0.45)
    T.gap(1.8, "sting-F")
    T.speech("F", words, between=0.45, pause_before_piece={1: (4.8, "bukti-F")})
    T.gap(1.8, "sting-G")
    T.speech("G", words)
    T.gap(2.6, "sting-H")
    T.speech("H1", words)
    T.gap(0.6, "h-mid")
    T.speech("H2", words)
    T.gap(0.6, "h-mid")
    T.speech("H3", words, between=0.35)
    T.gap(3.2, "ulang")
    T.gap(3.0, "m1-done")
    T.speech("H4", words, between=0.4)
    T.gap(3.0, "m2-done")
    T.speech("H5", words)
    T.gap(0.8, "h-mid")
    T.speech("H6", words)
    T.gap(1.8, "sting-I")
    T.speech("I", words, between=0.3)
    T.gap(1.4, "sting-J")
    T.speech("J", words)
    T.gap(0.4, "j-k")
    T.speech("K", words)
    rest = TOTAL - T.t
    T.gap(rest, "outro")
    return T


def map_words(T):
    out = []
    for ch in T.chunks:
        for w in ch["words"]:
            d = dict(w)
            d["os"] = ch["out_s"] + (w["s"] - ch["src_s"])
            d["oe"] = ch["out_s"] + (w["e"] - ch["src_s"])
            d["sec"] = ch["sec"]
            out.append(d)
    out.sort(key=lambda w: w["os"])
    return out


class Anchors:
    def __init__(self, mw):
        self.mw = mw
        self.nw = [subs.norm(w["w"]) for w in mw]
        self.missing = []

    def __call__(self, phrase, sec=None, nth=1, after=None, end=False, default=None):
        p = [subs.norm(x) for x in phrase.split()]
        p = [x for x in p if x]
        n = len(p)
        cands = []
        for i in range(len(self.mw) - n + 1):
            if sec and not self.mw[i]["sec"].startswith(sec):
                continue
            if after is not None and self.mw[i]["os"] < after:
                continue
            seg = self.nw[i:i + n]
            if seg == p:
                sc = 1.0
            else:
                sc = difflib.SequenceMatcher(None, " ".join(seg), " ".join(p)).ratio()
            if sc >= 0.8:
                cands.append((i, sc))
        exact = [c[0] for c in cands if c[1] == 1.0]
        fuzzy = [c[0] for c in cands]
        if len(exact) >= nth:
            i = exact[nth - 1]
        elif len(fuzzy) >= nth:
            # buang padanan bertindih (indeks berturutan) – ambil kumpulan terbaik
            groups = []
            for c in cands:
                if groups and c[0] - groups[-1][-1][0] < n:
                    groups[-1].append(c)
                else:
                    groups.append([c])
            best = [max(gp, key=lambda c: c[1])[0] for gp in groups]
            if len(best) < nth:
                self.missing.append((phrase, sec)); return default
            i = best[nth - 1]
        else:
            self.missing.append((phrase, sec))
            return default
        return self.mw[i + n - 1]["oe"] if end else self.mw[i]["os"]


# =====================================================================
# 5. GAMEPLAY – padanan kelajuan
# =====================================================================
def fit_shots(shots, T, label=""):
    """shots: (a, b, 'k'|'t'). Pulang senarai (a,b,speed)."""
    K = sum(b - a for a, b, k in shots if k == "k")
    R = sum(b - a for a, b, k in shots if k == "t")
    res = [list(s) for s in shots]
    if R > 0 and T - K > 0.5:
        sp = R / (T - K)
    else:
        sp = 1.0
    sp = min(max(sp, 1.0), 4.0)
    out = []
    for a, b, k in res:
        out.append([a, b, 1.0 if k == "k" else sp])
    dur = sum((b - a) / s for a, b, s in out)
    diff = T - dur
    if diff > 0.02:  # kurang – panjangkan syot terakhir
        out[-1][1] += diff * out[-1][2]
    elif diff < -0.02:  # lebih – potong hujung syot (yang terpanjang dahulu)
        need = -diff
        for s in sorted(out, key=lambda s: -(s[1] - s[0]) / s[2]):
            avail = (s[1] - s[0]) / s[2] - 0.2
            cut = min(avail, need)
            if cut > 0:
                s[1] -= cut * s[2]; need -= cut
            if need <= 0.01:
                break
    print(f"   fit {label:<10} T={T:6.2f}s keys={K:5.1f} travel={R:5.1f} speed={sp:.2f}")
    return out


# =====================================================================
# 6. PENJANA EDL VISUAL + GRAFIK
# =====================================================================
class Plan:
    def __init__(self, T, A):
        self.T, self.A = T, A
        self.v1 = []      # dict(t0,t1,type,src_in,speed,src_end,cam,bg)
        self.v2 = []      # dict(t0,t1,src_in)
        self.layers = []
        self.pips = []
        self.sfx = []
        self.music = []
        self.game_audio = []
        self.notes = []
        self.sub_margin = []  # (t0,t1,ml,mr)
        self.chips = []

    # --- lapisan ---
    def L(self, img, t0, t1, pos, ain="fade", aout="fade", din=0.5, dout=0.4, z=10, dyn=None, name=""):
        if t0 is None or t1 is None:
            print("  !! lapisan tanpa masa:", name)
            return
        self.layers.append(C.Layer(img, t0, t1, pos, ain, aout, din, dout, z, dynamic=dyn, name=name))

    def S(self, t, f, g=0.5):
        if t is not None:
            self.sfx.append((t, f, g))


def side_pos(img, side="L", y=None):
    w, h = img.size
    x = 40 if side == "L" else 1920 - w - 40
    if y is None:
        y = max(70, (880 - h) // 2)
    return (x, y)


def center_pos(img, y=None, x=None):
    w, h = img.size
    return ((1920 - w) // 2 if x is None else x, (1080 - h) // 2 if y is None else y)


LEFT_AREA_W = 1150  # kawasan grafik semasa susun atur split (kanan = pembentang)


def left_pos(img, y):
    w, h = img.size
    return (max(20, (LEFT_AREA_W - w) // 2 + 30), y)


def make_plan(T, words):
    mw = map_words(T)
    A = Anchors(mw)
    P = Plan(T, A)
    G = {g["tag"]: g for g in T.gaps}
    gaps_by = {}
    for g in T.gaps:
        gaps_by.setdefault(g["tag"], []).append(g)
    R = T.sec_range

    # ---------- V1 lalai: pembentang untuk setiap kiu ucapan ----------
    for ch in T.chunks:
        sec = ch["sec"]
        cam = {"zoom": BASEZOOM.get(sec, (1.0, 1.03)), "split_src": SPLIT.get(sec, C.SPLIT_SRC), "kf": []}
        if sec in CENTER:
            cam["center"] = CENTER[sec]
        if sec == "B":
            cam["zsrc"] = [(219.5, 1.0, (960, 540)), (223.0, 1.5, (860, 470)), (360.0, 1.58, (860, 470))]
        P.v1.append({"t0": ch["out_s"], "t1": ch["out_e"], "type": "pres", "src_in": ch["src_s"], "cam": cam, "sec": sec})
    # selang: latar grafik
    for g in T.gaps:
        P.v1.append({"t0": g["t0"], "t1": g["t1"], "type": "bg", "bg": "navy", "tag": g["tag"]})
    P.v1.sort(key=lambda s: s["t0"])
    for a, b in zip(P.v1, P.v1[1:]):
        if b["t0"] - a["t1"] > 0.001:
            a["t1"] = b["t0"]  # isi jarak antara kepingan dengan sambungan rakaman

    def set_mode(t0, t1, mode, back="full"):
        """Tetapkan mod susun atur pembentang (split/win/bg) bagi [t0,t1] – kerangka utama berpandukan masa global."""
        if t0 is None or t1 is None:
            return
        P.modes.append((t0, t1, mode, back))

    P.modes = []

    def override(t0, t1, segs, pip=True, pip_pos=None):
        """Ganti V1 dalam [t0,t1] dengan segmen gameplay/latar; pembentang dipindah ke PiP."""
        if t0 is None or t1 is None:
            return
        t0, t1 = q(t0), q(t1)
        new = []
        for s in P.v1:
            if s["t1"] <= t0 or s["t0"] >= t1:
                new.append(s); continue
            if s["t0"] < t0:
                a = dict(s); a["t1"] = t0; new.append(a)
            if s["t1"] > t1:
                b = dict(s); b["t0"] = t1
                if s["type"] == "pres":
                    b["src_in"] = s["src_in"] + (t1 - s["t0"])
                new.append(b)
            if s["type"] == "pres" and pip:
                a0, a1 = max(s["t0"], t0), min(s["t1"], t1)
                P.v2.append({"t0": a0, "t1": a1, "src_in": s["src_in"] + (a0 - s["t0"]), "sec": s["sec"]})
        tt = t0
        for sg in segs:
            sg = dict(sg); sg["t0"] = q(tt); dur = sg.pop("dur"); sg["t1"] = q(tt + dur); tt = sg["t1"]
            new.append(sg)
        if abs(tt - t1) > 0.05:
            print(f"  !! override panjang tidak padan {t0:.2f}-{t1:.2f} vs {tt:.2f}")
        new[-1]["t1"] = new[-1]["t1"]
        P.v1 = sorted(new, key=lambda s: s["t0"])

    def game_segs(shots, cam=None, file=None):
        segs = []
        for a, b, sp in shots:
            segs.append({"type": "game", "src_in": a, "src_end": b, "speed": sp, "dur": (b - a) / sp, "cam": dict(cam or {}), "file": file})
        return segs

    def gshots(t0, t1, shots, label="", cam=None, pip=True, file=None):
        if t0 is None or t1 is None:
            print("  !! gshots tanpa masa", label); return []
        fitted = fit_shots(shots, q(t1) - q(t0), label)
        segs = game_segs(fitted, cam, file)
        override(t0, t1, segs, pip=pip)
        for s in segs:
            pass
        return fitted

    def A_src(t):
        for ch in T.chunks:
            if ch["src_s"] <= t < ch["src_e"]:
                return ch["out_s"] + (t - ch["src_s"])
        return None

    def gsrc2out(t, file=None):
        for s in P.v1:
            if s["type"] == "game" and s.get("file") == file and s["src_in"] <= t <= s["src_end"]:
                return s["t0"] + (t - s["src_in"]) / s["speed"]
        return None

    P.gside = []
    P.override, P.gshots, P.set_mode, P.A_src, P.gsrc2out = override, gshots, set_mode, A_src, gsrc2out
    import scenes
    scenes.build(P, T, A, G, gaps_by, R)

    # susun atur sisi untuk gameplay (grafik di lajur kanan, tidak menutup permainan)
    gs = []
    for m in sorted(P.gside):
        if gs and m[0] <= gs[-1][1] + 1.2:
            gs[-1] = (gs[-1][0], max(gs[-1][1], m[1]))
        else:
            gs.append(m)
    for s in P.v1:
        if s["type"] != "game":
            continue
        kf = [(-20.0, "full")]
        for (m0, m1) in gs:
            if m1 <= s["t0"] or m0 >= s["t1"]:
                continue
            kf.append((-10.0 + 0.001 * len(kf), "side") if m0 < s["t0"] - 0.01 else (m0 - s["t0"], "side"))
            if m1 < s["t1"]:
                kf.append((m1 - s["t0"], "full"))
        s["cam"] = dict(s.get("cam", {})); s["cam"]["gkf"] = sorted(kf)
    # gabung selang mod yang bertindih / berdekatan
    merged = []
    for m in sorted(P.modes):
        if merged and m[2] == merged[-1][2] and m[0] <= merged[-1][1] + 1.5:
            merged[-1] = (merged[-1][0], max(merged[-1][1], m[1]), m[2], m[3])
        else:
            merged.append(m)
    P.modes = merged
    # penjejakan wajah untuk tetingkap split
    for s in P.v1:
        if s["type"] != "pres" or s.get("sec") == "OUT":
            continue
        pts = face_track(s["src_in"], s["t1"] - s["t0"])
        if pts:
            xs = np.array([p[1] for p in pts]); ys = np.array([p[2] for p in pts])
            # lancarkan
            if len(xs) >= 3:
                xs = np.convolve(np.pad(xs, 1, mode="edge"), np.ones(3) / 3, mode="valid")
            track = [(p[0], float(x), float(y)) for p, x in zip(pts, xs) for y in [p[2]]]
            s["cam"] = dict(s["cam"]); s["cam"]["face"] = track
    # gabungkan mod ke cam setiap segmen pembentang
    for s in P.v1:
        if s["type"] != "pres":
            continue
        kf = [(-20.0, "full")]
        for (m0, m1, mode, back) in sorted(P.modes):
            if m1 <= s["t0"] or m0 >= s["t1"]:
                continue
            a = max(m0, s["t0"]) - s["t0"]
            b = m1 - s["t0"]
            # jika mod bermula sebelum segmen ini, terus dalam mod (tanpa animasi)
            if m0 < s["t0"] - 0.01:
                kf.append((-10.0 + 0.001 * len(kf), mode))
            else:
                kf.append((a, mode))
            if b < s["t1"] - s["t0"]:
                kf.append((b, back))
        kf.sort()
        s["cam"] = dict(s["cam"]); s["cam"]["kf"] = kf
    if A.missing:
        print("  !! penambat tidak dijumpai:", A.missing)
    return P, mw


# =====================================================================
# 6b. PENJEJAKAN WAJAH (memastikan wajah pembentang sentiasa kelihatan)
# =====================================================================
_FACE = None


def face_track(src_in, dur, step=1.0):
    global _FACE
    import cv2
    cf = f"{CACHE}/face_cache.json"
    if _FACE is None:
        _FACE = json.load(open(cf)) if os.path.exists(cf) else {}
    key = f"{src_in:.3f}_{dur:.3f}"
    if key in _FACE:
        return _FACE[key]
    n = max(1, int(dur / step) + 1)
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{src_in:.3f}", "-t", f"{dur:.3f}", "-i", PEN, "-vf", f"fps=1/{step},scale=640:360",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    fr = np.frombuffer(p.stdout, np.uint8)
    k = len(fr) // (640 * 360)
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    pts = []
    for i in range(k):
        im = fr[i * 640 * 360:(i + 1) * 640 * 360].reshape(360, 640)
        faces = det.detectMultiScale(im, 1.1, 5, minSize=(14, 14))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            pts.append((i * step, (x + w / 2) * 3.0, (y + h / 2) * 3.0))
    _FACE[key] = pts
    json.dump(_FACE, open(cf, "w"))
    return pts


# =====================================================================
# 7. VIDEO ASAS (ffmpeg per segmen)
# =====================================================================
GRADE = "eq=contrast=1.05:saturation=1.07:gamma=0.98,unsharp=5:5:0.45"


def seg_cmd(s, out, w=1920, h=1080, pip=False):
    n = round((s["t1"] - s["t0"]) * FPS)
    base = ["ffmpeg", "-v", "error", "-y"]
    enc = ["-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "12" if not pip else "16", "-pix_fmt", "yuv420p", "-r", str(FPS), out]
    if s["type"] in ("pres", "pip"):
        vf = f"scale={w}:{h}:flags=lanczos,{GRADE},fps={FPS},tpad=stop=-1:stop_mode=clone"
        return base + ["-ss", f"{s['src_in']:.3f}", "-i", PEN, "-vf", vf] + enc
    if s["type"] == "game":
        sp = s["speed"]
        a, b = s["src_in"], s["src_end"]
        blur = f"tmix=frames={min(4, max(2, int(round(sp))))}," if sp >= 1.8 else ""
        vf = (f"{blur}setpts=(PTS-STARTPTS)/{sp:.5f},fps={FPS},scale=1920:980:flags=lanczos,pad=1920:1080:0:50:color=0x06221a,"
              f"tpad=stop=-1:stop_mode=clone")
        if pip:
            vf += f",scale={w}:{h}"
        src = SGURU if s.get("file") == "sg" else GAME
        if s.get("file") == "sg":
            vf = vf.replace("scale=1920:980:flags=lanczos,pad=1920:1080:0:50:color=0x06221a", "scale=-2:980:flags=lanczos,pad=1920:1080:(ow-iw)/2:50:color=0x06221a")
        return base + ["-ss", f"{a:.3f}", "-t", f"{(b - a) + 0.5:.3f}", "-i", src, "-vf", vf] + enc
    # latar (hitam) – compositor melukis latar
    return base + ["-f", "lavfi", "-i", f"color=c=black:s={w}x{h}:r={FPS}"] + enc


def run_parallel(cmds, nproc=3):
    procs = []
    for i, c in enumerate(cmds):
        while len(procs) >= nproc:
            for p in procs[:]:
                if p.poll() is not None:
                    if p.returncode != 0:
                        print("  !! gagal:", " ".join(p.args)[:300])
                    procs.remove(p)
            if len(procs) >= nproc:
                import time; time.sleep(0.05)
        procs.append(subprocess.Popen(c))
        if i % 40 == 0:
            print(f"   segmen {i}/{len(cmds)}", flush=True)
    for p in procs:
        p.wait()


def build_base(P, which="v1"):
    if which == "v1":
        segs = P.v1; w, h = 1920, 1080; pip = False
    else:
        # V2: hanya segmen PiP; selebihnya hitam
        segs = []
        t = 0.0
        v2 = sorted(P.v2, key=lambda s: s["t0"])
        for a, b in zip(v2, v2[1:]):
            if 0.01 < b["t0"] - a["t1"] < 6.0:
                a["t1"] = b["t0"]  # sambung rakaman pembentang (senyap) merentas selang pendek
        for s in v2:
            if s["t0"] > t + 0.01:
                segs.append({"t0": t, "t1": s["t0"], "type": "bg"})
            segs.append({"t0": s["t0"], "t1": s["t1"], "type": "pip", "src_in": s["src_in"]})
            t = s["t1"]
        if t < TOTAL:
            segs.append({"t0": t, "t1": TOTAL, "type": "bg"})
        w, h = C.PW, C.PH; pip = True
    d = f"{CACHE}/{which}"
    os.makedirs(d, exist_ok=True)
    cmds, files = [], []
    for i, s in enumerate(segs):
        f = f"{d}/s{i:04d}.mp4"
        files.append(f)
        key = json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items() if k in ("t0", "t1", "type", "src_in", "src_end", "speed", "file")}, sort_keys=True)
        kf = f + ".key"
        if os.path.exists(f) and os.path.exists(kf) and open(kf).read() == key:
            continue
        cmds.append(seg_cmd(s, f, w, h, pip))
        open(kf, "w").write(key)
    print(f"  {which}: {len(segs)} segmen, {len(cmds)} perlu dijana")
    run_parallel(cmds)
    lst = f"{d}/list.txt"
    open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    out = f"{CACHE}/{which}_base.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip())
    print(f"  {which}_base: {n} bingkai (sasaran {round(TOTAL * FPS)})")
    return out


# =====================================================================
# 8. SARIKATA
# =====================================================================
def build_subs(P, mw):
    ws = []
    for w in mw:
        ws.append({"s": w["os"], "e": w["oe"], "w": w["w"], "tag": None})
    # pemisah kiu pada sempadan bahagian
    prev = None
    for w, m in zip(ws, mw):
        if prev is not None and m["sec"] != prev:
            w["cut"] = True
        prev = m["sec"]
    subs.tag_words(ws)
    cues = subs.build_cues(ws)
    for c in cues:
        c["margin"] = None
        for (a, b, ml, mr) in P.sub_margin:
            if a - 0.2 <= c["s"] < b:
                c["margin"] = (ml, mr)
    write_ass_m(cues, f"{ROOT}/06_SUBTITLES/MISI_PENYELAMAT_AYAT_dinamik.ass")
    subs.write_srt(cues, f"{ROOT}/06_SUBTITLES/MISI_PENYELAMAT_AYAT.srt")
    json.dump([{"s": round(c["s"], 3), "e": round(c["e"], 3), "text": " ".join(w["w"] for w in c["words"]),
                "tags": [w.get("tag") for w in c["words"]]} for c in cues],
              open(f"{ROOT}/06_SUBTITLES/kiu_sarikata.json", "w"), ensure_ascii=False, indent=0)
    return cues


def write_ass_m(cues, path):
    subs.write_ass(cues, path)
    # tambah margin per kiu (gameplay + PiP)
    lines = open(path).read().split("\n")
    out = []
    ci = 0
    valid = [c for c in cues if any(subs.clean_display(w["w"]) for w in c["words"])]
    for ln in lines:
        if ln.startswith("Dialogue:") and ci < len(valid):
            c = valid[ci]; ci += 1
            if c.get("margin"):
                parts = ln.split(",", 9)
                parts[5], parts[6] = str(c["margin"][0]), str(c["margin"][1])
                ln = ",".join(parts)
        out.append(ln)
    open(path, "w").write("\n".join(out))


# =====================================================================
# 9. AUDIO
# =====================================================================
SR = 48000


def read_wav(path):
    wf = wave.open(path)
    ch = wf.getnchannels()
    a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    if ch == 2:
        a = a.reshape(-1, 2)
    else:
        a = np.stack([a, a], 1)
    return a


def write_wav(path, a):
    a = np.clip(a, -1, 1)
    wf = wave.open(path, "wb"); wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((a * 32767).astype(np.int16).tobytes()); wf.close()


def build_audio(P, T):
    N = int(TOTAL * SR)
    voice_src = read_wav(f"{ROOT}/02_AUDIO/voice_clean.wav")[:, 0]
    voice = np.zeros(N, np.float32)
    active = np.zeros(N, np.float32)
    # padanan kekuatan per bahagian
    sec_gain = {}
    for sec in PIECES:
        segs = [voice_src[int(ch["src_s"] * SR):int(ch["src_e"] * SR)] for ch in T.chunks if ch["sec"] == sec]
        x = np.concatenate(segs)
        fr = x[:len(x) // 480 * 480].reshape(-1, 480)
        r = np.sqrt((fr ** 2).mean(1))
        act = r[r > np.percentile(r, 40)]
        rms = np.sqrt((act ** 2).mean()) if len(act) else 0.05
        sec_gain[sec] = min(3.0, 0.12 / max(rms, 1e-4))
    fade = int(0.012 * SR)
    for ch in T.chunks:
        a, b = int(ch["src_s"] * SR), int(ch["src_e"] * SR)
        x = voice_src[a:b].copy() * sec_gain[ch["sec"]]
        x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
        o = int(round(ch["out_s"] * FPS)) * SR // FPS
        voice[o:o + len(x)] += x[:N - o]
        active[o:o + len(x)] = 1
    # sampul ducking
    k = int(0.35 * SR)
    sm = np.convolve(active[::480], np.ones(int(k / 480)) / int(k / 480), mode="same")
    sm = np.repeat(sm, 480)[:N]
    if len(sm) < N:
        sm = np.pad(sm, (0, N - len(sm)))
    duck = 1.0 - 0.80 * np.clip(sm * 1.3, 0, 1)   # di bawah ucapan muzik ~ -14 dB daripada aras penuh
    # muzik
    mus = np.zeros((N, 2), np.float32)
    for (t0, t1, name, gain, fi, fo) in P.music:
        m = read_wav(f"{ROOT}/02_AUDIO/music/{name}.wav")
        n = int((t1 - t0) * SR)
        if len(m) < n:
            reps = int(np.ceil(n / len(m)))
            m = np.concatenate([m] * reps)
        m = m[:n].copy()
        e = np.ones(n, np.float32)
        nfi, nfo = int(fi * SR), int(fo * SR)
        if nfi: e[:nfi] = np.linspace(0, 1, nfi)
        if nfo: e[-nfo:] = np.minimum(e[-nfo:], np.linspace(1, 0, nfo))
        o = int(t0 * SR)
        mus[o:o + n] += m * (e * gain)[:, None]
    mus *= duck[:, None]
    # kesan bunyi
    sfx = np.zeros((N, 2), np.float32)
    cache = {}
    for (t, f, g) in P.sfx:
        if f not in cache:
            cache[f] = read_wav(f"{ROOT}/02_AUDIO/music/{f}.wav")
        x = cache[f]
        o = int(t * SR)
        if o >= N: continue
        x = x[:N - o]
        sfx[o:o + len(x)] += x * g
    # audio permainan (hanya segmen kelajuan normal)
    gam = np.zeros((N, 2), np.float32)
    gsrc = None
    for s in P.v1:
        if s["type"] == "game" and abs(s["speed"] - 1) < 0.05 and s.get("file") != "sg":
            if gsrc is None:
                p = f"{CACHE}/game48.wav"
                if not os.path.exists(p):
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", GAME, "-vn", "-ac", "2", "-ar", str(SR), "-af", "volume=14dB", p], check=True)
                gsrc = read_wav(p)
            a = int(s["src_in"] * SR); n = int((s["t1"] - s["t0"]) * SR)
            x = gsrc[a:a + n].copy()
            f2 = min(int(0.2 * SR), len(x) // 2)
            if f2 > 0:
                x[:f2] *= np.linspace(0, 1, f2)[:, None]; x[-f2:] *= np.linspace(1, 0, f2)[:, None]
            o = int(s["t0"] * SR)
            gam[o:o + len(x)] += x
    gam *= (0.12 + 0.25 * (1 - np.clip(sm * 1.3, 0, 1)))[:, None]
    mix = np.stack([voice, voice], 1) + mus + sfx + gam
    # fade akhir
    nf = int(2.5 * SR)
    mix[-nf:] *= np.linspace(1, 0, nf)[:, None] ** 1.5
    write_wav(f"{CACHE}/mix_pre.wav", mix * 0.7)
    write_wav(f"{ROOT}/02_AUDIO/stem_suara.wav", np.stack([voice, voice], 1) * 0.7)
    write_wav(f"{ROOT}/02_AUDIO/stem_muzik_sfx.wav", (mus + sfx) * 0.7)
    # normalisasi kekuatan (EBU R128, 2 laluan)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{CACHE}/mix_pre.wav", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    lf = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
          f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{CACHE}/mix_pre.wav", "-af", lf + ",aresample=48000", "-ar", "48000", f"{ROOT}/02_AUDIO/mix_akhir.wav"], check=True)
    print("  audio siap:", js["input_i"], "LUFS →  -16 LUFS")


# =====================================================================
# 10. RENDER & MUX
# =====================================================================
def render(P, t0=0.0, t1=TOTAL, out=None, burn=True):
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    out = out or f"{CACHE}/video_akhir.mp4"
    ass = f"{ROOT}/06_SUBTITLES/MISI_PENYELAMAT_AYAT_dinamik.ass"
    vf = []
    if burn:
        sh = f"setpts=PTS+{f0}/{FPS}/TB," if f0 else ""
        vf = ["-vf", f"{sh}ass='{ass}':fontsdir='{ROOT}/05_GRAPHICS/fonts',setpts=PTS-STARTPTS"]
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS), "-i", "-"] + vf + \
          ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-g", "60", "-movflags", "+faststart", out]
    C.run(f"{CACHE}/v1_base.mp4", f"{CACHE}/v2_base.mp4", P.v1, P.layers, P.pips, f1, cmd, start_frame=f0)
    return out


def mux(video, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", f"{ROOT}/02_AUDIO/mix_akhir.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", out], check=True)


def save_plan(T, P):
    js = {"jumlah_saat": TOTAL, "chunks": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in ch.items() if k != "words"} for ch in T.chunks],
          "gaps": T.gaps, "v1": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if k != "cam"} for s in P.v1],
          "v2": P.v2, "sections": {k: [round(a, 3), round(b, 3)] for k, (a, b) in T.sec_range.items()},
          "layers": [{"name": L.name, "t0": round(L.t0, 2), "t1": round(L.t1, 2)} for L in P.layers], "notes": P.notes}
    json.dump(js, open(f"{ROOT}/07_PROJECT/edl_timeline.json", "w"), ensure_ascii=False, indent=1)


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "plan"
    words = load_words()
    T = build_timeline(words)
    P, mw = make_plan(T, words)
    print(f"Jumlah ucapan: {sum(c['out_e'] - c['out_s'] for c in T.chunks):.1f}s ; garis masa {T.t:.2f}s ; outro {T.gaps[-1]['t1'] - T.gaps[-1]['t0']:.2f}s")
    for k, (a, b) in T.sec_range.items():
        print(f"   {k:<3} {int(a // 60):2d}:{a % 60:05.2f} – {int(b // 60):2d}:{b % 60:05.2f}  ({b - a:6.1f}s)")
    save_plan(T, P)
    build_subs(P, mw)
    if stage in ("base", "all"):
        build_base(P, "v1"); build_base(P, "v2")
    if stage in ("audio", "all"):
        build_audio(P, T)
    if stage == "render":
        t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
        t1 = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
        out = sys.argv[4] if len(sys.argv) > 4 else f"{CACHE}/preview_{int(t0)}_{int(t1)}.mp4"
        render(P, t0, t1, out)
    if stage == "stills":
        times = [float(x) for x in sys.argv[2].split(",")]
        os.makedirs(f"{CACHE}/stills", exist_ok=True)
        ass = f"{ROOT}/06_SUBTITLES/MISI_PENYELAMAT_AYAT_dinamik.ass"
        for t in times:
            f0 = round(t * FPS)
            out = f"{CACHE}/stills/t{int(t):04d}.png"
            cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", str(FPS), "-i", "-",
                   "-vf", f"setpts=PTS+{f0}/{FPS}/TB,ass='{ass}':fontsdir='{ROOT}/05_GRAPHICS/fonts'", "-frames:v", "1", out]
            C.run(f"{CACHE}/v1_base.mp4", f"{CACHE}/v2_base.mp4", P.v1, P.layers, P.pips, f0 + 1, cmd, start_frame=f0, progress=False)
    if stage == "all":
        v = render(P)
        mux(v, f"{ROOT}/08_EXPORT/MISI_PENYELAMAT_AYAT_BMMB3233_FINAL.mp4")


if __name__ == "__main__":
    main()
