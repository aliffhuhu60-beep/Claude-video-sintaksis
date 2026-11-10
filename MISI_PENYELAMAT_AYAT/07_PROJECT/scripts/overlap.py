"""Pemeriksa tindihan grafik: laporkan pasangan lapisan yang bertindih (kotak nyata) pada masa yang sama."""
import sys, build, gfx
SKIP = ("latar bukti", "kad tajuk utama", "sting", "scramble", "flash", "letterbox", "confetti", "sparkle", "kad akhir", "H6 ", "gelaran", "slogan", "pip nama")
words = build.load_words(); T = build.build_timeline(words); P, mw = build.make_plan(T, words)
ls = [L for L in P.layers if L.dynamic is None and L.img is not None and not any(L.name.startswith(k) or k in L.name for k in SKIP)]
box = {}
for L in ls:
    b = gfx.vis_box(L.img)
    box[id(L)] = (L.pos[0] + b[0], L.pos[1] + b[1], L.pos[0] + b[2], L.pos[1] + b[3])
MIN_GAP = 14
bad = []
for i, a in enumerate(ls):
    for b in ls[i + 1:]:
        t0, t1 = max(a.t0, b.t0), min(a.t1, b.t1)
        if t1 - t0 < 0.3:
            continue
        A, B = box[id(a)], box[id(b)]
        ox = min(A[2], B[2]) - max(A[0], B[0]); oy = min(A[3], B[3]) - max(A[1], B[1])
        if ox > -MIN_GAP and oy > -MIN_GAP and (ox > 0 or oy > 0) and min(ox, oy) > -MIN_GAP:
            bad.append((round(t0, 1), a.name, b.name, ox, oy))
# kawasan tetingkap pembentang (split) – grafik tidak boleh masuk x>=985 semasa mod split
import compositor as C
wx = C.SPLIT_DST[0] - 5
for (m0, m1, mode, back) in P.modes:
    if mode != "split":
        continue
    for L in ls:
        a_, b_ = max(L.t0, m0), min(L.t1, m1)
        pres = any(sg["type"] == "pres" and min(sg["t1"], b_) - max(sg["t0"], a_) > 0.3 for sg in P.v1)
        if b_ - a_ > 0.3 and pres and box[id(L)][2] > wx and box[id(L)][0] < wx + 900:
            bad.append((round(max(L.t0, m0), 1), L.name, "TETINGKAP PEMBENTANG", box[id(L)][2] - wx, 0))
# grafik kawasan kiri yang dipapar semasa pembentang skrin penuh (bukan split/win)
FULL_OK = ("lower ", "LT ", "chip ", "PB1")
for L in ls:
    if any(L.name.startswith(k) for k in FULL_OK) or box[id(L)][0] > 985:
        continue
    for sg in P.v1:
        if sg["type"] != "pres":
            continue
        a_, b_ = max(L.t0 + 0.6, sg["t0"]), min(L.t1 - 0.5, sg["t1"])
        if b_ - a_ <= 0.3:
            continue
        cov = 0.0
        for (m0, m1, mode, back) in P.modes:
            cov += max(0.0, min(b_, m1) - max(a_, m0))
        if (b_ - a_) - cov > 0.4:
            bad.append((round(a_, 1), L.name, "PEMBENTANG PENUH", round((b_ - a_) - cov, 1), 0))
for r in sorted(set(bad)):
    print(r)
print("JUMLAH TINDIHAN:", len(bad))
