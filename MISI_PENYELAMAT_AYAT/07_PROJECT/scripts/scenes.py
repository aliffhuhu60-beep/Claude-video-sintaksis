"""Arahan adegan bagi setiap babak A–K: motion graphics, B-roll gameplay, muzik & kesan bunyi.
Semua masa grafik ditambat pada frasa yang benar-benar diucapkan (A(...))."""
import gfx
from gfx import *
import compositor as C

GY = 70  # had atas grafik
LEFT_AREA_W = 940


def center_pos(img, y=None, x=None):
    w, h = img.size
    return ((1920 - w) // 2 if x is None else x, (1080 - h) // 2 if y is None else y)


def left_pos(img, y):
    w, h = img.size
    return (max(20, (LEFT_AREA_W - w) // 2 + 30), y)


RC_X, RC_W = 1236, 616   # lajur kanan semasa susun atur sisi gameplay


def build(P, T, A, G, gaps_by, R):
    L, S = P.L, P.S

    def stack(items, top=80, gap=30, bottom=880, area=(0, LEFT_AREA_W + 30), z=12):
        """items: dict(img,t0,t1,ain,name,snd,sg). Susun menegak dengan jarak seragam; skala jika perlu."""
        items = [it for it in items if it.get("img") is not None and it.get("t0") is not None]
        if not items:
            return
        boxes = [vis_box(it["img"]) for it in items]
        hs = [b[3] - b[1] for b in boxes]
        avail = bottom - top - gap * (len(items) - 1)
        sc = min(1.0, avail / max(1, sum(hs)))
        y = top
        for it, b in zip(items, boxes):
            img = it["img"]
            if sc < 0.999:
                img = img.resize((int(img.size[0] * sc), int(img.size[1] * sc)), Image.LANCZOS)
                b = vis_box(img)
            vw = b[2] - b[0]
            x = area[0] + (area[1] - area[0] - vw) // 2 - b[0]
            L(img, it["t0"], it["t1"], (x, y - b[1]), it.get("ain", "left"), "fade", 0.5, 0.4, z=z, name=it.get("name", ""))
            if it.get("snd"):
                S(it["t0"], it["snd"], it.get("sg", 0.15))
            y += (b[3] - b[1]) + gap

    def rc_stack(items, top=200, gap=28, bottom=880):
        stack(items, top, gap, bottom, area=(RC_X, RC_X + RC_W), z=20)

    def evidence_wall(tag, jenis, accent, title, extra=None):
        gg = g(tag)
        for s_ in P.v1:
            if s_.get("tag") == tag:
                s_["bg"] = "navy"
        t0, t1 = gg["t0"], gg["t1"] + 0.3
        bgimg = Image.fromarray(bg_gradient("navy")).convert("RGBA")
        L(bgimg, t0 - 0.05, t1, (0, 0), "fade", "fade", 0.35, 0.35, z=29, name=f"latar bukti {jenis}")
        hd = heading(f"BUKTI MEDIA SOSIAL  •  JENIS {jenis}", title, 1700, accent)
        L(hd, t0, t1, (60, 40), "left", "fade", 0.5, 0.35, z=30, name=f"bukti hd {jenis}")
        items = list(EVIDENCE[jenis]) + list(extra or [])
        cards = [evidence_card(r, pl, cx, qt, accent, w=860, size=25) for r, pl, cx, qt in items]
        half = (len(cards) + 1) // 2
        for col, sub in enumerate((cards[:half], cards[half:])):
            x0 = 40 + col * 930
            stack([{"img": c, "t0": t0 + 0.35 + 0.22 * (k + col * half), "t1": t1, "ain": "up", "name": f"bukti {jenis}.{k}"}
                   for k, c in enumerate(sub)], top=190, gap=26, bottom=930, area=(x0, x0 + 900), z=31)
        nt = pill("Petikan hantaran awam (dikumpul 5 Nov 2026) • nama akaun dikaburkan", F("is", 20), fg=(220, 225, 235), bg=(25, 35, 70))
        L(nt, t0 + 0.6, t1, (1920 - nt.size[0] - 40, 60), "fade", "fade", 0.4, 0.3, z=31, name=f"nota bukti {jenis}")
        S(t0, "sfx_whoosh", 0.3)
        for k in range(len(cards)):
            S(t0 + 0.35 + 0.22 * k, "sfx_tick", 0.12)

    def side(t0, t1):
        if t0 is not None and t1 is not None:
            P.gside.append((t0 - 0.5, t1))

    def g(tag, i=0):
        return gaps_by[tag][i]

    def sec_end(s):
        return R[s][1]

    def sec_start(s):
        return R[s][0]

    def lower(sec, name, role, t=None, dur=5.5):
        t = t if t is not None else sec_start(sec) + 1.2
        img = lower_third(name, role)
        L(img, t, t + dur, (60, 690), "left", "fade", 0.6, 0.5, z=20, name=f"lower {name}")
        S(t, "sfx_whoosh", 0.18)

    def sting(tag, kicker, title, sub=None, accent=GOLD, bgk="navy"):
        import re as _re
        kicker = _re.sub(r"BAHAGIAN [A-K]\s*•\s*", "", kicker).strip()
        gg = g(tag)
        for s in P.v1:
            if s.get("tag") == tag:
                s["bg"] = bgk
        L(title_card(kicker, title, sub, accent), gg["t0"], gg["t1"] + 0.25, (0, 0), "wipe", "fade", 0.6, 0.35, z=30, name=f"sting {tag}")
        S(gg["t0"], "sfx_whoosh", 0.35)

    def chipsec(sec, letter, text, until=None):
        return  # label bahagian tidak dipaparkan (permintaan pengguna)
        t0 = sec_start(sec) + 0.4
        L(section_chip(letter, text), t0, until or sec_end(sec), (36, 14), "fade", "fade", 0.6, 0.6, z=5, name=f"chip {sec}")

    def card(img, t0, t1, pos, ain="left", aout="fade", z=12, name="", snd="sfx_pop", sg=0.15):
        if t0 is None:
            print("  !! tiada masa untuk", name); return
        if t1 is None:
            t1 = t0 + 4
        L(img, t0, t1, pos, ain, aout, 0.5, 0.4, z=z, name=name)
        if snd:
            S(t0, snd, sg)

    # =================================================================
    # MUZIK (garis besar)
    # =================================================================
    P.music += [
        (0.0, g("maintitle")["t1"] + 8, "mus_intro_suspense", 0.95, 0.5, 6.0),
        (g("maintitle")["t1"] + 2, sec_end("A2") + 2, "mus_documentary", 0.55, 4.0, 3.0),
        (g("sting-B")["t0"], sec_end("C") + 1.5, "mus_ambient", 0.55, 2.0, 3.0),
        (g("sting-D")["t0"], sec_end("F") + 1.5, "mus_ambient", 0.5, 2.0, 3.0),
        (g("sting-G")["t0"], sec_end("G") + 3.0, "mus_documentary", 0.5, 2.0, 3.0),
        (g("sting-H")["t0"], sec_end("H6") + 2.0, "mus_adventure", 0.42, 1.5, 3.0),
        (g("sting-I")["t0"], sec_end("I") + 1.0, "mus_documentary", 0.45, 2.0, 2.5),
        (g("sting-J")["t0"], 1800.0, "mus_outro", 0.75, 2.0, 3.0),
    ]

    # =================================================================
    # A – PEMBUKAAN
    # =================================================================
    op = g("opener"); mt = g("maintitle")
    for s_ in P.v1:
        if s_.get("tag") == "opener":
            s_["bg"] = "dark"
    L(None, op["t0"], op["t1"], (0, 0), "fade", "fade", 0.01, 0.01, z=15, dyn=scramble_intro, name="scramble")
    S(op["t0"] + 0.15, "sfx_impact", 0.9)
    S(op["t1"] - 3.2, "sfx_riser", 0.6)
    L(None, op["t1"] - 0.05, op["t1"] + 0.6, (0, 0), "fade", "fade", 0.01, 0.01, z=40, dyn=flash, name="flash")
    S(op["t1"], "sfx_impact", 0.7)
    # kad tajuk utama
    t_hormat = A("Yang kami hormati", "A1")
    tc = title_card("BMMB3233  •  SINTAKSIS BAHASA MELAYU", "ISU KERANCUAN BAHASA DALAM ASPEK [G:SINTAKSIS]",
                    "Ayat Tanpa Subjek  •  Ayat Tidak Lengkap  •  Bahasa Rojak", GOLD)
    t_end_title = mt["t1"] + 0.25
    L(tc, mt["t0"], t_end_title, (0, -120), "wipe", "fade", 0.9, 0.35, z=25, name="kad tajuk utama")
    inst = text_img("IPG Kampus Tun Hussein Onn, Batu Pahat", F("mb", 36), WHITE)
    L(inst, mt["t0"] + 1.2, t_end_title, (140, 735), "up", "fade", 0.6, 0.5, z=26, name="institusi")
    pen = text_img("Pensyarah: Dr. Siti Dahlia binti Abdullah", F("pm", 32), (200, 215, 230))
    L(pen, mt["t0"] + 1.8, t_end_title, (140, 790), "up", "fade", 0.6, 0.5, z=26, name="pensyarah")
    S(mt["t0"], "sfx_whoosh", 0.4)
    # pembentang P1
    chipsec("A1", "A", "PEMBUKAAN & PENGHARGAAN", until=sec_end("A2"))
    lower("A1", *ALIFF_, t=sec_start("A1") + 0.4, dur=6.5)
    t = A("Melalui tugasan PB1", "A1")
    if t:
        P.set_mode(t - 0.3, A("dunia permainan ini", "A1", end=True) or t + 20, "split")
        pb = formula_row([block("PB1", "Frasa • Klausa • Transformasi", NAVY, w=420, h=150, tsize=60), "→",
                          block("PB2", "Kenal pasti & betulkan ayat", GREEN_DARK, w=420, h=150, tsize=60)])
        card(pb, t + 0.2, A("Tanpa pemahaman", "A1") or t + 10, left_pos(pb, 180), "scale", name="PB1→PB2")
        t2 = A("Tanpa pemahaman", "A1")
        k1 = keypoint_card("ASAS PB1", "Setiap ayat = [Y:SUBJEK + PREDIKAT]", "Klausa terikat [R:tidak dapat berdiri sendiri].", accent=GOLD, w=900)
        card(k1, t2, A("Kami juga", "A1"), left_pos(k1, 420), "up", name="asas PB1")
    # nama pembentang – syot berkumpulan
    t_saya = A("Saya", "A2")
    if t_saya:
        L(lower_third(*ALIFF_), t_saya + 0.3, t_saya + 5.0, (60, 690), "left", "fade", 0.6, 0.4, z=20, name="LT aliff")
        ta = P.A_src(159.0); ti = P.A_src(83.1)
        L(lower_third(*AMIN_), ta, ta + 3.6, (60, 690), "left", "fade", 0.5, 0.4, z=20, name="LT amin")
        L(lower_third(*IMAN_), ti, ti + 4.2, (60, 690), "left", "fade", 0.5, 0.4, z=20, name="LT iman")
    t = A("terbahagi kepada", "A2")
    t_take1 = P.A_src(85.8)
    if t_take1:
        P.set_mode(t_take1 - 0.9, sec_end("A2") + 0.1, "win")
        S(t_take1 - 0.9, "sfx_whoosh", 0.25)
        kt = keypoint_card("TOPIK PEMBENTANGAN", "ISU KERANCUAN BAHASA DALAM ASPEK [Y:SINTAKSIS]", "Kesalahan pada peringkat [Y:AYAT].", accent=GOLD, w=560)
        card(kt, t_take1 - 0.3, t or t_take1 + 7, (10, 200), "left", name="topik")
    if t:
        tend = sec_end("A2")
        hd = heading("ALIRAN PEMBENTANGAN", "Enam Bahagian", 560)
        card(hd, t, tend, (24, 70), "left", snd=None, name="aliran")
        items = ["Pengenalan isu & sebab dipilih", "Tiga jenis kesalahan ayat", "Cadangan: Minecraft Education",
                 "Demonstrasi cara bermain", "Cadangan penambahbaikan lain", "Harapan & penutup"]
        keys = ["pertama", "Seterusnya, 3 jenis", "Seterusnya, cadangan", "demonstrasi cara bermain", "cadangan penambahan baikan lain", "harapan serta penutup"]
        prev = t + 0.6
        for i, (it, k) in enumerate(zip(items, keys)):
            tk = A(k, "A2", after=prev - 0.5) or prev + 2.5
            tk = max(tk, prev)
            img = list_item(i + 1, it, [GOLD, RED, PURPLE, PURPLE, LGREEN, BLUE][i], w=570)
            L(img, tk, tend, (30, 220 + i * 100), "left", "fade", 0.45, 0.4, z=12, name=f"aliran {i + 1}")
            S(tk, "sfx_tick", 0.25)
            prev = tk + 0.3

    # =================================================================
    # B – PENGENALAN KERANCUAN BAHASA
    # =================================================================
    sting("sting-B", "BAHAGIAN B  •  PENGENALAN", "Apakah [Y:Kerancuan Bahasa]?", "Kamus Dewan • Sintaksis • Subjek & Predikat")
    chipsec("B", "B", "PENGENALAN KERANCUAN BAHASA")
    lower("B", *AMIN_)
    t = A("perkataan rancu", "B") or A("rancu", "B")
    t_def = A("Oleh itu, kerancuan bahasa ialah", "B")
    t_aspek = A("Kerancuan bahasa boleh berlaku", "B")
    t_tumpuan = A("Dalam pembentangan ini", "B")
    if t:
        P.set_mode(t - 0.3, t_tumpuan or t + 25, "split")
        L(None, t, t_def, (60, 150), "fade", "fade", 0.3, 0.4, z=12, dyn=rancu_assemble, name="RANCU")
        S(t, "sfx_whoosh", 0.3)
        kd = text_img("Kamus Dewan", F("mb", 30), GOLD)
        card(kd, t + 0.8, t_def, (110, 120), "fade", snd=None, name="kamus dewan")
        d1 = keypoint_card("RANCU =", "[Y:KACAU] • [Y:TIDAK TERATUR] • [Y:CAMPUR ADUK]", None, accent=GOLD, w=900)
        card(d1, A("kacau", "B") or t + 3, t_def, left_pos(d1, 470), "up", name="rancu def")
        d2 = keypoint_card("DEFINISI", "KERANCUAN BAHASA", "= penggunaan bahasa yang [Y:kacau dan tidak teratur] sehingga [R:menyalahi peraturan tatabahasa] bahasa Melayu.", accent=GOLD, w=900)
        card(d2, t_def, t_aspek, left_pos(d2, 200), "left", name="kerancuan def")
        if t_aspek:
            hd = heading("BERLAKU DALAM PELBAGAI ASPEK", "Di manakah kerancuan berlaku?", 1000)
            card(hd, t_aspek, t_tumpuan + 3, (70, 130), "left", snd=None, name="aspek hd")
            for i, (lbl, k, c) in enumerate([("Ejaan", "ejaan", NAVY), ("Sebutan", "sebutan", NAVY), ("Pembentukan kata", "pembentukan kata", NAVY), ("Susunan ayat (SINTAKSIS)", "susunan ayat", GREEN_DARK)]):
                tk = A(k, "B", after=t_aspek) or t_aspek + 1 + i
                ch = chip(lbl, c if i < 3 else (46, 160, 70), 34)
                L(ch, tk, t_tumpuan + 3, (80 + (i % 2) * 470, 330 + (i // 2) * 120), "pop", "fade", 0.45, 0.4, z=12, name=f"aspek {lbl}")
                S(tk, "sfx_pop", 0.18)
            fk = chip("← FOKUS KAMI", RED, 30)
            card(fk, t_tumpuan, t_tumpuan + 3, (620, 590), "left", name="fokus kami")
    t_sin = A("sintaksis ialah bidang", "B")
    t_dua = A("Ayat yang gramatis", "B") or A("dua unsur utama", "B")
    t_murid = A("Contohnya, dalam ayat", "B")
    t_ganggu = A("Kerancuan sintaksis berlaku", "B")
    if t_sin:
        P.set_mode(t_sin - 0.3, t_ganggu + 1.0 if t_ganggu else t_sin + 30, "split")
        k = keypoint_card("SINTAKSIS", "Cara perkataan disusun → [B:FRASA] → [B:KLAUSA] → [B:AYAT]", "(Nik Safiah Karim et al., 2024)", accent=BLUE, w=900)
        card(k, t_sin, t_dua, left_pos(k, 260), "left", name="sintaksis")
    if t_dua:
        fv = flow_vertical([("AYAT", NAVY, "UNIT TATABAHASA"), ("SUBJEK + PREDIKAT", (46, 120, 200), "DUA UNSUR UTAMA"), ("AYAT GRAMATIS", (46, 160, 70), "HASIL")], w=760)
        card(fv, t_dua, t_murid, left_pos(fv, 110), "scale", name="aliran ayat")
    if t_murid:
        fr = formula_row([block("MURID", "SUBJEK • diterangkan", BLUE, w=380, h=170, tsize=64), "+",
                          block("MEMBACA BUKU", "PREDIKAT • menerangkan", (46, 160, 70), w=560, h=170, tsize=58)])
        card(fr, t_murid, t_ganggu, left_pos(fr, 330), "scale", name="murid membaca buku")
    t_tegas = A("Kami ingin menegaskan", "B")
    if t_ganggu:
        P.set_mode(t_ganggu - 0.2, t_tegas or t_ganggu + 30, "split")
        hd = heading("APABILA HUBUNGAN TERGANGGU", "Subjek [R:✗] Predikat", 1000)
        card(hd, t_ganggu, t_tegas, (70, 110), "left", snd=None, name="ganggu hd")
        rows = [("Subjek [R:hilang] – ditenggelami kata sendi nama", "subjek hilang"),
                ("Predikat [R:tidak wujud] – hanya frasa nama panjang", "predikat tidak wujud"),
                ("Klausa terikat [R:berdiri sendiri]", "klausa terikat dibiarkan"),
                ("Unsur [R:bahasa asing] ambil alih fungsi", "bahasa asing")]
        prev = t_ganggu
        for i, (txt, k) in enumerate(rows):
            tk = A(k, "B", after=prev) or prev + 4
            img = list_item(i + 1, txt, RED, w=900)
            L(img, tk, t_tegas, (70, 290 + i * 100), "left", "fade", 0.45, 0.4, z=12, name=f"ganggu {i}")
            S(tk, "sfx_tick", 0.25)
            prev = tk
    if t_tegas:
        t_tutur = A("Dalam pertuturan", "B")
        P.set_mode(t_tegas - 0.2, sec_end("B") + 0.1, "split")
        k1 = keypoint_card("✗  BUKAN FOKUS", "Kesalahan KATA secara terpencil", "cth. salah ejaan: “sye”, “x”, “dlm”", accent=RED, w=900)
        k2 = keypoint_card("✓  FOKUS KAJIAN", "KESALAHAN [Y:AYAT] (SINTAKSIS)", "Kesalahan yang menjejaskan [Y:binaan ayat secara keseluruhan].", accent=LGREEN, w=900)
        card(k1, t_tegas + 0.3, t_tutur, left_pos(k1, 120), "left", name="bukan fokus")
        card(k2, A("Fokus kami ialah", "B") or t_tegas + 4, t_tutur, left_pos(k2, 440), "left", name="fokus")
        if t_tutur:
            k3 = formula_row([block("PERTUTURAN", "konteks + nada + gerak badan", (46, 120, 200), w=500, h=160, tsize=46), "vs",
                              block("PENULISAN", "hanya susunan ayat", RED, w=460, h=160, tsize=46)], op_size=50)
            card(k3, t_tutur, sec_end("B"), left_pos(k3, 330), "scale", name="tutur vs tulis")

    # =================================================================
    # C – BUKTI MEDIA SOSIAL & SEBAB
    # =================================================================
    sting("sting-C", "BAHAGIAN C  •  BUKTI", "Di Manakah Isu Ini [Y:Berlaku]?", "Media sosial • Empat sebab isu dipilih")
    chipsec("C", "C", "BUKTI MEDIA SOSIAL & SEBAB ISU DIPILIH")
    lower("C", *IMAN_)
    t_plat = A("Kami telah meneliti", "C")
    t_contoh = A("Contohnya, dalam kapsyen jualan", "C") or A("Contohnya", "C", after=t_plat)
    t_ditulis = A("Ayat-ayat ini ditulis", "C")
    t_empat = A("Kami memilih isu ini", "C")
    if t_plat:
        P.set_mode(t_plat - 0.3, t_empat or t_plat + 60, "split")
        for i, (nm, d) in enumerate([("TikTok", "Kapsyen jualan & ulasan"), ("Threads", "Hantaran & komen"), ("YouTube", "Tajuk video")]):
            tk = A(["TikTok", "Threads", "YouTube"][i], "C", after=t_plat) or t_plat + 1 + i
            k = keypoint_card(f"PLATFORM {i + 1}", nm, d, accent=[RED, PURPLE, (255, 60, 60)][i], w=330)
            L(k, tk, t_contoh, (40 + i * 370, 200), "up", "fade", 0.45, 0.4, z=12, name=f"platform {nm}")
            S(tk, "sfx_pop", 0.18)
        tk = A("kapsyen jualan, tajuk video", "C") or t_plat + 6
        for i, lbl in enumerate(["Kapsyen jualan", "Tajuk video", "Hantaran", "Ruangan komen"]):
            ch = chip(lbl, NAVY, 30)
            L(ch, tk + i * 0.5, t_contoh, (60 + (i % 2) * 520, 560 + (i // 2) * 110), "pop", "fade", 0.4, 0.4, z=12, name=f"chip {lbl}")
    if t_contoh:
        t2 = A("Dalam tajuk video makanan", "C")
        t3 = A("Di YouTube dan Threads", "C")
        ph1 = phone_quote("TikTok", "Kapsyen jualan  •  Bukti J1.1", "[r:kepada yang berminat] boleh maklumkan di ruangan comment.", "JENIS 1 • TIADA SUBJEK")
        ph2 = phone_quote("TikTok", "Tajuk video makanan  •  Bukti J2.1", "Kedai malatang [r:yang paling sedap] kat KL.", "JENIS 2 • TIADA PREDIKAT")
        card(ph1, t_contoh, t3, (110, 90), "up", name="telefon J1.1", snd="sfx_whoosh", sg=0.2)
        card(ph2, t2, t3, (620, 90), "up", name="telefon J2.1", snd="sfx_whoosh", sg=0.2)
        q3 = sentence_box("salah", "Harini [r:team] kami nak [r:share] cara buat kek.", w=900, label="Contoh ayat (YouTube)", size=36)
        q4 = sentence_box("salah", "[r:Overall best gila], wajib [r:try guys]!", w=900, label="Contoh ayat (Threads)", size=36)
        card(q3, t3, t_ditulis, left_pos(q3, 170), "left", name="contoh share")
        card(q4, A("Overall", "C") or t3 + 4, t_ditulis, left_pos(q4, 420), "left", name="contoh overall")
    gC = g("bukti-C")
    if t_ditulis:
        tg0, tg1 = t_ditulis, gC["t1"] + 0.2
        P.override(tg0, gC["t1"], [{"type": "bg", "bg": "navy", "dur": gC["t1"] - tg0}], pip=True)
        P.pips.append({"t0": tg0, "t1": gC["t0"] + 0.4, "size": (400, 225), "pos": (1490, 360)})
        hd = heading("BUKTI SEBENAR DARIPADA MEDIA SOSIAL", "15 hantaran awam dianalisis", 1400, GOLD)
        L(hd, tg0, tg1, (40, 30), "left", "fade", 0.5, 0.4, z=30, name="galeri hd")
        cols = [(1, RED, "JENIS 1 • TANPA SUBJEK"), (2, GOLD, "JENIS 2 • TIDAK LENGKAP"), (3, PURPLE, "JENIS 3 • BAHASA ROJAK")]
        for ci, (jn, ac, lab) in enumerate(cols):
            x0 = 30 + ci * 485
            lp = pill(lab, F("mx", 20), fg=INK if ac == GOLD else WHITE, bg=ac)
            L(lp, tg0 + 0.3 + ci * 0.3, tg1, (x0 + 10, 190), "down", "fade", 0.4, 0.4, z=31, name=f"galeri lab {jn}")
            cards = [evidence_card(r, pl, cx, qt, ac, w=470, size=17) for r, pl, cx, qt in EVIDENCE[jn]]
            stack([{"img": c, "t0": tg0 + 0.6 + 0.35 * (k * 3 + ci), "t1": tg1, "ain": "up", "name": f"galeri {jn}.{k}"}
                   for k, c in enumerate(cards)], top=250, gap=16, bottom=905, area=(x0, x0 + 475), z=31)
        sx = pill("TikTok • YouTube • Threads", F("mx", 24), fg=WHITE, bg=(30, 40, 80))
        L(sx, tg0 + 1.0, tg1, (1490, 260), "fade", "fade", 0.4, 0.4, z=31, name="platform pill")
        nt = text_img("Sumber: dokumen Bukti Media Sosial (J1.1–J3.5), dikumpul 5 November 2026. Nama akaun & gambar profil dikaburkan.", F("pm", 22), (210, 220, 232), maxw=400)
        L(nt, tg0 + 1.2, tg1, (1490, 620), "fade", "fade", 0.4, 0.4, z=31, name="galeri sumber")
        S(tg0, "sfx_whoosh", 0.3)
    if t_empat:
        t_tiga = A("Daripada bukti yang kami kumpulkan", "C")
        P.set_mode(t_empat - 0.2, sec_end("C") + 0.1, "split")
        hd = heading("SEBAB ISU DIPILIH", "Empat Sebab Utama", 1000)
        card(hd, t_empat, t_tiga, (70, 90), "left", snd=None, name="4 sebab hd")
        reasons = [("Paling hampir dengan murid", "Murid membesar dengan TikTok & YouTube.", "Sebab yang pertama"),
                   ("Sudah dinormalkan", "Pengguna tidak sedar ayat itu salah.", "Sebab yang kedua"),
                   ("Berkait terus dengan sintaksis", "Subjek, predikat, klausa bebas & terikat.", "Sebab yang ketiga"),
                   ("Tanggungjawab bakal guru", "Bukan sekadar mengkritik – beri penyelesaian.", "Sebab yang keempat")]
        stack([{"img": keypoint_card(f"SEBAB {i + 1}", ti, bd, accent=[GOLD, RED, BLUE, LGREEN][i], w=900), "t0": A(k, "C") or t_empat + 3 + i * 15,
                 "t1": t_tiga, "name": f"sebab {i + 1}", "snd": "sfx_pop", "sg": 0.2} for i, (ti, bd, k) in enumerate(reasons)], top=200, gap=24, bottom=860)
        tc = A("Kajian juga mendapati", "C")
        if tc:
            cit = pill("Chew Fong Peng & Vanithmalar Jayabalan (2026)", F("ps", 24), fg=WHITE, bg=(30, 50, 90))
            L(cit, tc, tc + 9, (70, 880), "fade", "fade", 0.4, 0.4, z=13, name="sitasi chew")
        if t_tiga:
            hd2 = heading("TIGA JENIS KESALAHAN", "Paling Kerap Ditemui", 1000)
            card(hd2, t_tiga, sec_end("C"), (70, 110), "left", snd=None, name="3 jenis hd")
            for i, (lbl, k, c) in enumerate([("JENIS 1 • Ayat Tanpa Subjek", "ayat tanpa subjek", RED), ("JENIS 2 • Ayat Tidak Lengkap", "ayat tidak lengkap", GOLD),
                                             ("JENIS 3 • Bahasa Rojak", "bahasa rojak", PURPLE)]):
                tk = A(k, "C", after=t_tiga) or t_tiga + 2 + i
                img = list_item(i + 1, lbl, c, w=900)
                L(img, tk, sec_end("C"), (70, 300 + i * 110), "left", "fade", 0.45, 0.4, z=12, name=f"3jenis {i}")
                S(tk, "sfx_tick", 0.25)

    # =================================================================
    # D – JENIS 1: AYAT TANPA SUBJEK
    # =================================================================
    sting("sting-D", "BAHAGIAN D  •  JENIS 1", "AYAT [R:TANPA SUBJEK]", "Kata sendi nama + frasa nama = [Y:frasa sendi nama], bukan subjek", RED)
    chipsec("D", "D", "JENIS 1: AYAT TANPA SUBJEK")
    lower("D", *ALIFF_)
    k = keypoint_card("JENIS 1", "AYAT TANPA SUBJEK", None, accent=RED, w=520)
    t_kead1 = A("Keadaan yang pertama", "D") or A("dua keadaan", "D")
    card(k, sec_start("D") + 1.0, t_kead1, (40, 120), "left", name="jenis1 kad")
    t_ksn = A("kata sendi nama seperti", "D")
    t_apabila = A("Apabila kata sendi nama diletakkan", "D")
    t_kead2 = A("Keadaan kedua", "D")
    t_mari = A("mari kita lihat contoh", "D") or A("Baiklah", "D")
    if t_ksn:
        P.set_mode(t_kead1 - 0.2, t_mari, "split")
        hd = heading("PENANDA", "Ayat bermula dengan [R:kata sendi nama]", 1050)
        card(hd, t_kead1 + 0.2, t_apabila, (60, 100), "left", snd=None, name="penanda hd")
        words = ["KEPADA", "BAGI", "UNTUK", "DALAM", "DI", "DARIPADA", "MENURUT", "DENGAN ADANYA"]
        x, y = 70, 300
        for i, wd in enumerate(words):
            tk = A(wd.lower(), "D", after=t_ksn - 0.3) or t_ksn + 0.4 * i
            ch = chip(wd, RED, 38)
            if x + ch.size[0] > 1150:
                x, y = 70, y + 120
            L(ch, tk, t_apabila, (x, y), "pop", "fade", 0.4, 0.4, z=12, name=f"ksn {wd}")
            S(tk, "sfx_tick", 0.2)
            x += ch.size[0] - 20
    if t_apabila:
        fv = flow_vertical([("KATA SENDI NAMA + FRASA NAMA", RED, "cth. KEPADA + yang berminat"), ("FRASA SENDI NAMA", NAVY, "berfungsi sebagai KETERANGAN")], w=900)
        card(fv, t_apabila, t_kead2, left_pos(fv, 120), "scale", name="formula FSN")
        st = big_word("BUKAN SUBJEK AYAT", RED, 74, "mk", stroke=5, stroke_fill=WHITE)
        tb = A("bukan lagi sebagai subjek", "D") or t_apabila + 5
        L(st.rotate(-6, expand=True, resample=Image.BICUBIC), tb, t_kead2, left_pos(st, 640), "pop", "fade", 0.5, 0.4, z=14, name="stamp bukan subjek")
        S(tb, "sfx_impact", 0.25)
    if t_kead2:
        k2 = keypoint_card("KEADAAN 2", "Subjek [R:digugurkan] terus", "Kata ganti nama seperti [Y:saya], [Y:anda], [Y:kami] dibuang kerana penulis menganggap pembaca sudah faham.", accent=RED, w=900)
        card(k2, t_kead2, t_mari, left_pos(k2, 260), "left", name="keadaan 2")
    # contoh 1–4
    ex = [("Kepada yang berminat boleh maklumkan", "[r:Kepada] yang berminat boleh maklumkan di ruangan komen.", "[g:Mereka] yang berminat boleh [g:memaklumkan] di ruangan komen.", "TikTok • kapsyen jualan",
           "[B:“Kepada yang berminat”] = frasa sendi nama. Predikat [B:“boleh maklumkan”] [R:tiada subjek]. Gugurkan “Kepada”, tambah “Mereka”."),
          ("Kalau berminat boleh wasap", "[r:Kalau berminat] boleh [r:wasap] ya.", "Jika [g:anda] berminat, [g:anda] boleh menghubungi kami.", "TikTok • kapsyen jualan",
           "Klausa “kalau berminat” dan “boleh wasap” [R:kedua-duanya tiada subjek]. Tambah subjek [G:“anda”]."),
          ("Semoga dipermudahkan urusan sis", "[r:Semoga dipermudahkan] urusan sis.", "[g:Saya berdoa] semoga urusan sis dipermudah.", "Threads • ruangan komen",
           "Hanya klausa harapan “semoga…” – [R:tiada klausa utama bersubjek]."),
          ("Berminat boleh walkin", "[r:Berminat] boleh [r:walkin] ke kedai kami.", "[g:Pelanggan yang berminat] boleh [g:datang] ke kedai kami.", "TikTok • video kedai",
           "Ayat bermula dengan predikat – [R:tiada subjek]. Tambah [G:“Pelanggan yang berminat”].")]
    t_kesan = A("apakah kesan kesalahan ini", "D")
    exD = []
    for i, (anc, wrong, right, lbl, ana) in enumerate(ex):
        tw_ = A(anc, "D")
        exD.append(tw_)
    # urutan: contoh1 (+analisis), contoh2, contoh3&4, kesan
    t_ex1, t_ex2, t_ex3, t_ex4 = exD
    t_ex2_hdr = A("Contoh yang kedua", "D") or t_ex2
    t_ex34_hdr = A("Contoh yang ketiga dan keempat", "D") or t_ex3
    blocks = [(t_ex1, A("Ayat yang betul ialah", "D", after=t_ex1), t_ex2_hdr, 0),
              (t_ex2, A("Ayat yang betul", "D", after=t_ex2), t_ex34_hdr, 1)]
    evidence_wall("bukti-D", 1, RED, "Ayat tanpa subjek dalam kapsyen sebenar")
    for (ts, tr, te, i) in blocks:
        if ts is None:
            continue
        _, wrong, right, lbl, ana = ex[i]
        P.set_mode(ts - 0.6, te, "split")
        items = [{"img": sentence_box("salah", wrong, w=900, label=lbl, size=38), "t0": ts - 0.2, "t1": te, "name": f"D salah {i + 1}", "snd": "sfx_fail", "sg": 0.12},
                 {"img": analysis_box(ana, w=900, size=30), "t0": ts + 3.0, "t1": te, "ain": "up", "name": f"D analisis {i + 1}"}]
        if tr:
            items.append({"img": sentence_box("betul", right, w=900, size=38), "t0": tr, "t1": te, "name": f"D betul {i + 1}", "snd": "sfx_success", "sg": 0.12})
        if i == 0:
            tcara = A("Kata sendi nama kepada digugurkan", "D") or (tr + 4 if tr else None)
            items.append({"img": keypoint_card("CARA PEMBETULAN", "1. Gugurkan kata sendi nama   2. Tambah subjek", None, accent=LGREEN, w=900),
                          "t0": tcara, "t1": te, "ain": "up", "name": "cara betul", "snd": "sfx_pop"})
        stack(items, top=70, gap=30)
    if t_ex3:
        te = t_kesan or t_ex3 + 20
        P.set_mode(t_ex34_hdr - 0.4, te, "split")
        tr = A("Ayat yang betul", "D", after=t_ex3)
        tb2 = A("pelanggan yang berminat", "D", after=tr) if tr else None
        items = []
        for j_, i_ in enumerate((2, 3)):
            items.append({"img": sentence_box("salah", ex[i_][1], w=900, label=ex[i_][3], size=34), "t0": t_ex3 if j_ == 0 else (t_ex4 or t_ex3 + 2), "t1": te,
                          "name": f"D salah {i_ + 1}", "snd": "sfx_fail", "sg": 0.1})
        for j_, i_ in enumerate((2, 3)):
            if tr:
                items.append({"img": sentence_box("betul", ex[i_][2], w=900, size=34), "t0": tr if j_ == 0 else (tb2 or tr + 3), "t1": te,
                              "name": f"D betul {i_ + 1}", "snd": "sfx_success", "sg": 0.1})
        stack(items, top=70, gap=28)
    if t_kesan:
        P.set_mode(t_kesan - 0.2, sec_end("D") + 0.1, "split")
        hd = heading("KESAN JENIS 1", "Mengapa ini [R:serius]?", 1000)
        card(hd, t_kesan, sec_end("D"), (70, 100), "left", snd=None, name="kesan D hd")
        ks = [("Maksud kabur", "Pembaca tidak tahu siapa pelaku.", "Kesan yang pertama"),
              ("Sukar disedari", "“Bagi saya berpendapat…” dibawa ke karangan.", "Kedua, kesalahan ini sukar"),
              ("Hilang markah", "Dikira kesalahan tatabahasa dalam peperiksaan.", "Akhir sekali")]
        stack([{"img": keypoint_card(f"KESAN {i + 1}", ti, bd, accent=RED, w=900), "t0": A(kk, "D", after=t_kesan) or t_kesan + 3 + 12 * i,
                 "t1": sec_end("D"), "name": f"kesanD {i}", "snd": "sfx_pop", "sg": 0.2} for i, (ti, bd, kk) in enumerate(ks)], top=230, gap=30, bottom=880)

    # =================================================================
    # E – JENIS 2: AYAT TIDAK LENGKAP
    # =================================================================
    sting("sting-E", "BAHAGIAN E  •  JENIS 2", "AYAT [Y:TIDAK LENGKAP]", "Ayat lengkap = [B:SUBJEK] + [G:PREDIKAT]", GOLD)
    chipsec("E", "E", "JENIS 2: AYAT TIDAK LENGKAP")
    lower("E", *AMIN_)
    t_def = A("Ayat tidak lengkap ialah", "E")
    t_b1 = A("Bentuk pertama", "E")
    t_b2 = A("Bentuk kedua", "E")
    t_b3 = A("Bentuk ketiga", "E")
    t_ex1 = A("Contoh pertama ialah tajuk video", "E")
    if t_def:
        P.set_mode(t_def - 0.2, t_ex1, "split")
        fr = formula_row([block("AYAT LENGKAP", "", NAVY, w=400, h=140, tsize=44), "=", block("SUBJEK", "", BLUE, w=270, h=140, tsize=44), "+",
                          block("PREDIKAT", "", (46, 160, 70), w=300, h=140, tsize=44)], op_size=56)
        card(fr, t_def, t_b1, left_pos(fr, 300), "scale", name="ayat lengkap formula")
        panels = [("A", "TIADA PREDIKAT", "FN + [Y:“yang …”] sahaja", t_b1), ("B", "KLAUSA TERGANTUNG", "[Y:APABILA / KERANA / KALAU / SELEPAS] tanpa klausa utama", t_b2),
                  ("C", "KK TRANSITIF TANPA OBJEK", "cth. “Ayah membeli [R:___] di kedai.”", t_b3)]
        tay_ = A("Ayah membeli di kedai", "E")
        stack([{"img": keypoint_card(f"BENTUK {lt}", ti, bd, accent=GOLD, w=900), "t0": tk, "t1": (tay_ if lt != "C" else t_ex1) or t_ex1,
                "name": f"bentuk {lt}", "snd": "sfx_pop", "sg": 0.2} for lt, ti, bd, tk in panels], top=80, gap=30, bottom=860)
        tay = A("Ayah membeli di kedai", "E")
        if tay:
            a1 = formula_row([block("AYAH", "SUBJEK", BLUE, w=230, h=130, tsize=42), block("MEMBELI", "KK TRANSITIF", (46, 160, 70), w=290, h=130, tsize=42),
                              block("???", "OBJEK HILANG", RED, w=230, h=130, tsize=42), block("DI KEDAI", "", NAVY, w=260, h=130, tsize=42)], gap=10)
            a2 = formula_row([block("AYAH", "SUBJEK", BLUE, w=200, h=130, tsize=40), block("MEMBELI", "KK TRANSITIF", (46, 160, 70), w=250, h=130, tsize=40),
                              block("SEBUAH BASIKAL", "OBJEK", (46, 160, 70), w=380, h=130, tsize=40), block("DI KEDAI", "", NAVY, w=220, h=130, tsize=40)], gap=10)
            ta2 = A("apakah yang dibeli", "E") or tay + 2.5
            L(a1, tay, ta2 + 0.5, left_pos(a1, 640), "up", "fade", 0.4, 0.3, z=15, name="ayah ???")
            L(a2, ta2 + 0.5, t_ex1, left_pos(a2, 640), "scale", "fade", 0.4, 0.4, z=15, name="ayah basikal")
            S(ta2 + 0.5, "sfx_success", 0.14)
    exE = [("Kedai malatang yang paling sedap kat KL", "Kedai malatang [r:yang paling sedap] [r:kat] KL.", "[b:Kedai ini] [g:ialah kedai malatang paling sedap di KL].", "TikTok / YouTube • tajuk video",
            "Hanya FN + klausa relatif “yang …” – [R:tiada predikat]."),
           ("Restoran mewah tapi harga murah", "Restoran mewah [r:tapi] harga murah.", "[b:Restoran ini] [g:mewah] tetapi [b:harganya] [g:murah].", "YouTube • tajuk video",
            "Tanpa penentu “ini”, “restoran mewah” dibaca sebagai [R:satu frasa nama] (inti + penerang)."),
           ("korang kalau suka snek", "[r:Korang kalau suka] snek macam ni.", "Kalau kalian suka snek ini, [g:kalian wajib mencubanya].", "TikTok • kapsyen video",
            "Klausa syarat “kalau …” [R:tergantung] – tiada klausa utama.")]
    t_kesanE = A("Kesan kesalahan ini cukup besar", "E")
    tE = [A("Kedai malatang yang paling sedap", "E"), A("Contoh kedua", "E"), A("Contoh ketiga", "E")]
    ends = [tE[1], tE[2], t_kesanE]
    evidence_wall("bukti-E", 2, GOLD, "Ayat tidak lengkap dalam kapsyen sebenar")
    for i in range(3):
        ts = tE[i]
        if ts is None:
            continue
        _, wrong, right, lbl, ana = exE[i]
        te = ends[i] or ts + 20
        P.set_mode(ts - 0.4, te, "split")
        items = [{"img": sentence_box("salah", wrong, w=900, label=lbl, size=38), "t0": ts, "t1": te, "name": f"E salah {i + 1}", "snd": "sfx_fail", "sg": 0.12},
                 {"img": analysis_box(ana, w=900, size=30), "t0": ts + 3.5, "t1": te, "ain": "up", "name": f"E analisis {i + 1}"}]
        tr = A("Ayat yang betul", "E", after=ts)
        if tr and tr < te:
            items.append({"img": sentence_box("betul", right, w=900, size=38), "t0": tr, "t1": te, "name": f"E betul {i + 1}", "snd": "sfx_success", "sg": 0.12})
        if i == 0:
            tk = A("Kini, kedai ini menjadi subjek", "E") or A("Kini", "E")
            if tk:
                items.append({"img": formula_row([block("KEDAI INI", "SUBJEK", BLUE, w=260, h=124, tsize=38), "+",
                                                  block("ialah kedai malatang paling sedap di KL", "PREDIKAT", (46, 160, 70), w=760, h=124, tsize=27)], op_size=44),
                              "t0": tk, "t1": te, "ain": "scale", "name": "E subjek predikat"})
        stack(items, top=70, gap=30)
    if t_kesanE:
        tser = A("saya serahkan", "E") or A("serahkan", "E")
        P.set_mode(t_kesanE - 0.2, sec_end("E") + 0.1, "split")
        hd = heading("KESAN JENIS 2", "Mesej [R:tidak sampai]", 1000)
        card(hd, t_kesanE, sec_end("E"), (70, 100), "left", snd=None, name="kesan E hd")
        ks = [("Mesej tidak lengkap", "Tawaran & tindakan tidak jelas.", "Pertama"), ("Ayat tergantung", "“Apabila loceng berbunyi.” lalu noktah.", "Kedua"),
              ("Ayat majmuk lemah", "Klausa terikat perlukan klausa utama.", "Ketiga")]
        stack([{"img": keypoint_card(f"KESAN {i + 1}", ti, bd, accent=GOLD, w=900), "t0": A(kk, "E", after=t_kesanE) or t_kesanE + 3 + 10 * i,
                 "t1": sec_end("E"), "name": f"kesanE {i}", "snd": "sfx_pop", "sg": 0.2} for i, (ti, bd, kk) in enumerate(ks)], top=230, gap=30, bottom=880)

    # =================================================================
    # F – JENIS 3: BAHASA ROJAK
    # =================================================================
    sting("sting-F", "BAHAGIAN F  •  JENIS 3", "[P:BAHASA ROJAK] dalam Binaan Ayat", "Unsur asing mengambil alih [Y:fungsi dalam ayat]", PURPLE, "purple")
    chipsec("F", "F", "JENIS 3: BAHASA ROJAK")
    lower("F", *IMAN_)
    t_def = A("Bahasa rojak ialah", "F")
    t_jaw = A("Jawapannya", "F")
    t_akib = A("Akibatnya", "F")
    t_c1 = A("contoh yang pertama", "F")
    if t_def:
        P.set_mode(t_def - 0.2, t_c1, "split")
        pairs = [("HAPPY", "GEMBIRA"), ("STUDY", "BELAJAR"), ("BUSY", "SIBUK"), ("DRIVE", "MEMANDU"), ("BEST", "SEDAP"),
                 ("GAME", "PERMAINAN VIDEO"), ("SUBMIT", "MENGHANTAR"), ("SHARE", "BERKONGSI"), ("SHOPPING", "MEMBELI-BELAH"), ("BECAUSE", "KERANA")]
        hd = heading("PERCAMPURAN BAHASA", "Inggeris [P:→] Melayu baku", 1000, PURPLE)
        card(hd, t_def, t_jaw or t_def + 12, (70, 90), "left", snd=None, name="rojak hd")
        for i, (en, bm) in enumerate(pairs):
            col, row = i % 2, i // 2
            x = 70 + col * 540; y = 250 + row * 104
            ce = chip(en, RED, 30)
            cb = chip(bm, (46, 160, 70), 30)
            t0 = t_def + 0.8 + i * 0.45
            tsw = t_def + 6.5 + i * 0.35
            L(ce, t0, tsw, (x, y), "pop", "fade", 0.35, 0.25, z=12, name=f"en {en}")
            L(cb, tsw, (t_jaw or t_def + 14) + 0.3, (x, y), "pop", "fade", 0.35, 0.3, z=12, name=f"bm {bm}")
            S(t0, "sfx_tick", 0.12)
        if t_jaw:
            hd2 = heading("BILA JADI ISU SINTAKSIS?", "Unsur asing ambil [Y:fungsi dalam ayat]", 1000, PURPLE)
            card(hd2, t_jaw, t_c1, (70, 90), "left", snd=None, name="fungsi hd")
            fn = [("Inti frasa kerja", "nak [r:SHARE]"), ("Kata hubung", "[r:SO], [r:BECAUSE]"), ("Penerang", "[r:BEST GILA], [r:ONLY]"), ("Kata ganti nama", "[r:KORANG]")]
            for i, (a, b) in enumerate(fn):
                img = list_item(i + 1, f"{a}:  {b}", PURPLE, w=900)
                L(img, t_jaw + 1.5 + i * 1.6, t_c1, (70, 290 + i * 98), "left", "fade", 0.45, 0.4, z=12, name=f"fungsi {i}")
            if t_akib:
                st = keypoint_card("AKIBATNYA", "Ayat rasmi WAJIB guna bahasa Melayu [Y:BAKU]", None, accent=PURPLE, w=900)
                card(st, t_akib, t_c1, left_pos(st, 700), "up", name="baku")
    exF = [("hari ini team kami nak share", "Harini [r:team] kami [r:nak share] cara [r:buat] kek.", "Hari ini [g:pasukan] kami [g:ingin berkongsi] cara [g:membuat] kek.", "YouTube • tajuk video",
            "Inti subjek [R:“team”] & inti predikat [R:“share”] ialah bahasa Inggeris; “nak”, “buat” = bentuk basahan."),
           ("Pakej serendah RM30", "Pakej serendah RM30 [r:only]! Tekan [r:link] di bio.", "Pakej serendah RM30 [g:sahaja]! Tekan [g:pautan] di bio.", "TikTok • kapsyen jualan",
            "[R:“only”] menggantikan kata penegas “sahaja”; [R:“link”] menggantikan FN “pautan”."),
           ("Overall best gila", "[r:Overall best gila], wajib [r:try guys]!", "[g:Secara keseluruhan], makanan ini [g:sangat bagus]. Anda wajib [g:mencubanya]!", "Threads • ulasan",
            "Keterangan, predikat & objek dalam bahasa Inggeris/basahan; [R:subjek juga tiada]."),
           ("Bahasa rojak juga merosakkan binaan ayat majmuk", "Kami pergi [r:shopping] di pasar raya, [r:so] kami penat sangat.", "Kami pergi [g:membeli-belah] di pasar raya, [g:oleh itu] kami sangat penat.", "Ayat majmuk",
            "Kata hubung Inggeris [R:“so”] menghubungkan dua klausa.")]
    tF = [t_c1, A("Contoh kedua dan ketiga", "F"), A("Overall best gila", "F", after=A("Contoh kedua dan ketiga", "F")), A("Bahasa rojak juga merosakkan", "F")]
    t_kesanF = A("Apakah kesannya", "F")
    endsF = [tF[1], tF[3], tF[3], t_kesanF]
    evidence_wall("bukti-F", 3, PURPLE, "Bahasa rojak dalam kapsyen sebenar", extra=EXTRA_EVIDENCE)
    for i in (0, 3):
        ts = tF[i]
        if ts is None:
            continue
        _, wrong, right, lbl, ana = exF[i]
        te = endsF[i] or ts + 15
        P.set_mode(ts - 0.4, te, "split")
        items = [{"img": sentence_box("salah", wrong, w=900, label=lbl, size=38), "t0": ts, "t1": te, "name": f"F salah {i + 1}", "snd": "sfx_fail", "sg": 0.12},
                 {"img": analysis_box(ana, w=900, size=30), "t0": ts + 3.0, "t1": te, "ain": "up", "name": f"F analisis {i + 1}"}]
        tr = A("Ayat yang betul", "F", after=ts) or A("Ayat betul", "F", after=ts)
        if tr and tr < te:
            items.append({"img": sentence_box("betul", right, w=900, size=38), "t0": tr, "t1": te, "name": f"F betul {i + 1}", "snd": "sfx_success", "sg": 0.12})
        stack(items, top=70, gap=30)
    if tF[1] and tF[3]:
        te = tF[3]
        P.set_mode(tF[1] - 0.4, te, "split")
        tr = A("Ayat betul ialah secara keseluruhan", "F") or A("secara keseluruhan", "F", after=tF[1])
        stack([{"img": sentence_box("salah", exF[1][1], w=900, label=exF[1][3], size=32), "t0": tF[1], "t1": te, "name": "F salah 2", "snd": "sfx_fail", "sg": 0.12},
               {"img": sentence_box("salah", exF[2][1], w=900, label=exF[2][3], size=32), "t0": tF[2] or tF[1] + 3, "t1": te, "name": "F salah 3", "snd": "sfx_fail", "sg": 0.1},
               {"img": sentence_box("betul", exF[1][2], w=900, size=32), "t0": tr, "t1": te, "name": "F betul 2"},
               {"img": sentence_box("betul", exF[2][2], w=900, size=32), "t0": (tr + 0.4) if tr else None, "t1": te, "name": "F betul 3", "snd": "sfx_success", "sg": 0.12}],
              top=70, gap=26)
    if t_kesanF:
        t_rum = A("Secara keseluruhan", "F", after=t_kesanF)
        P.set_mode(t_kesanF - 0.2, sec_end("F") + 0.1, "split")
        hd = heading("KESAN JENIS 3", "Bahasa rojak [R:merugikan]", 1000)
        card(hd, t_kesanF, t_rum, (70, 90), "left", snd=None, name="kesan F hd")
        ks = [("Martabat bahasa terjejas", "Perkara 152 Perlembagaan Persekutuan.", "Yang pertama"), ("Kosa kata hilang", "submit/share/busy ≠ menghantar/berkongsi/sibuk", "Yang kedua"),
              ("Terbawa ke situasi rasmi", "Karangan, surat rasmi, peperiksaan.", "Yang ketiga"), ("Dianggap betul", "Generasi akan datang menormalkannya.", "yang keempat")]
        stack([{"img": keypoint_card(f"KESAN {i + 1}", ti, bd, accent=PURPLE, w=900), "t0": A(kk, "F", after=t_kesanF) or t_kesanF + 3 + 9 * i,
                 "t1": t_rum, "name": f"kesanF {i}", "snd": "sfx_pop", "sg": 0.2} for i, (ti, bd, kk) in enumerate(ks)], top=210, gap=24, bottom=880)
        if t_rum:
            fr = formula_row([block("3 JENIS KESALAHAN", "SATU PERSAMAAN", RED, w=470, h=150, tsize=40), "→",
                              block("SUBJEK ✗ PREDIKAT", "HUBUNGAN DIROSAKKAN", NAVY, w=520, h=150, tsize=40)], op_size=56)
            card(fr, t_rum, sec_end("F"), left_pos(fr, 200), "scale", name="rumusan")
            tsr = A("sekolah rendah", "F", after=t_rum, nth=1)
            k = keypoint_card("KESIMPULAN ISU", "Usaha membasmi kerancuan mesti bermula di [Y:SEKOLAH RENDAH]", None, accent=GOLD, w=900)
            card(k, A("Oleh itu, kami percaya", "F") or t_rum + 10, sec_end("F"), left_pos(k, 460), "up", name="sekolah rendah")

    # =================================================================
    # G – PENGENALAN MINECRAFT EDUCATION
    # =================================================================
    sting("sting-G", "BAHAGIAN G  •  CADANGAN PENAMBAHBAIKAN", "Dunia Minecraft Education [G:“Misi Penyelamat Ayat”]", "Daripada bukti media sosial → misi permainan", LGREEN, "green")
    chipsec("G", "G", "CADANGAN: MINECRAFT EDUCATION")
    lower("G", *ALIFF_)
    t_bina = A("Oleh itu, kami membina sebuah dunia", "G")
    t_pilih = A("Kami memilih Minecraft Education", "G")
    t_dunia = A("Dunia ini dibina berdasarkan bukti", "G")
    t_sek = A("Sekarang, kami akan", "G") or A("Sekarang", "G", after=t_dunia)
    if t_bina:
        P.gshots(t_bina - 0.3, t_pilih, [(1057.0, 1085.0, "t")], "G-lobi", cam={})
        tp = big_word("MISI PENYELAMAT AYAT", WHITE, 92, "mk", stroke=5, stroke_fill=GREEN_DEEP)
        card(tp, A("Misi Penyelamat Ayat", "G", after=t_bina) or t_bina + 3, t_pilih, center_pos(tp, 700), "scale", name="G judul", snd="sfx_impact", sg=0.25)
        P.pips.append({"t0": t_bina - 0.3, "t1": t_pilih, "label": None})
    if t_pilih:
        P.set_mode(t_pilih - 0.2, t_dunia, "split")
        hd = heading("MENGAPA MINECRAFT EDUCATION?", "Tiga Sebab", 1000, LGREEN)
        card(hd, t_pilih, t_dunia, (70, 90), "left", snd=None, name="3 sebab mc hd")
        rs = [("Diminati murid", "Murid terlibat secara aktif.", "game", "Sebab yang pertama"), ("Akaun DELIMa", "Akses guru & murid tanpa kos tambahan.", "student", "Sebab yang kedua"),
              ("Belajar melalui permainan", "Misi, markah, pingat & papan kedudukan.", "medal", "akhir sekali")]
        for i, (ti, bd, ic, kk) in enumerate(rs):
            tk = A(kk, "G", after=t_pilih) or t_pilih + 3 + 8 * i
            c = icon_card(i + 1, ti, bd, ic, LGREEN, w=900, h=190)
            L(c, tk, t_dunia, (50, 250 + i * 215), "left", "fade", 0.5, 0.4, z=12, name=f"mc sebab {i}")
            S(tk, "sfx_pop", 0.2)
    if t_dunia:
        P.gshots(t_dunia - 0.3, t_sek, [(135.0, 172.0, "t")], "G-gerbang", cam={})
        P.pips.append({"t0": t_dunia - 0.3, "t1": t_sek, "label": None})
        t_cth = A("Contohnya", "G", after=t_dunia) or t_dunia + 9
        P.pips[-1]["pos"] = (1920 - 448 - 36, 1080 - 252 - 190)
        fl = formula_row([block("BUKTI MEDIA SOSIAL", "", NAVY, w=470, h=120, tsize=34), "→", block("3 JENIS KESALAHAN", "", RED, w=470, h=120, tsize=34), "→",
                          block("3 MISI PERMAINAN", "", PURPLE, w=470, h=120, tsize=34)], op_size=48)
        card(fl, t_dunia, t_cth + 1.5, center_pos(fl, 60), "scale", name="aliran bukti")
        t_m = A("dijadikan sebagai tiga misi", "G") or t_dunia + 5
        stack([{"img": chip(nm, c, 34, fg=INK if c == GOLD else WHITE), "t0": t_m + i * 0.6, "t1": t_cth + 1.5, "ain": "pop", "name": f"misi chip {i}", "snd": "sfx_tick", "sg": 0.2}
               for i, (nm, c) in enumerate([("MISI 1: AYAT TANPA SUBJEK", RED), ("MISI 2: AYAT TIDAK LENGKAP", GOLD), ("MISI 3: BAHASA ROJAK", PURPLE)])],
              top=260, gap=22, bottom=600, area=(40, 760), z=13)
        tf = A("Setiap jawapan murid", "G")
        feats = ["Galeri isu", "3 misi", "Maklum balas segera", "Markah & pingat", "Main individu", "Main berkumpulan", "Laporan guru"]
        if tf:
            cols_ = [NAVY, PURPLE, (46, 160, 70), GOLD, (46, 160, 70), PURPLE, RED]
            for col in range(2):
                idx = [i for i in range(len(feats)) if i % 2 == col]
                stack([{"img": chip(feats[i], cols_[i], 32, fg=INK if cols_[i] == GOLD else WHITE), "t0": tf + i * 0.35, "t1": t_sek, "ain": "pop", "name": f"ciri {feats[i]}"}
                       for i in idx], top=90, gap=20, bottom=620, area=(40 + col * 480, 40 + col * 480 + 460), z=13)
    if t_sek:
        tb = big_word("MULA DEMONSTRASI", GOLD, 84, "mk", stroke=5, stroke_fill=INK)
        card(tb, t_sek, sec_end("G") + 0.2, center_pos(tb, 380), "scale", name="mula demo", snd="sfx_riser", sg=0.35)

    # =================================================================
    # H – DEMONSTRASI MINECRAFT
    # =================================================================
    sh = g("sting-H")
    for s_ in P.v1:
        if s_.get("tag") == "sting-H":
            s_["bg"] = "game"
    L(title_card("DEMONSTRASI", "Cara Bermain [P:Misi Penyelamat Ayat]", "Rakaman sebenar Minecraft Education", PURPLE), sh["t0"], sh["t1"] + 0.2, (0, 0), "wipe", "fade", 0.6, 0.3, z=30, name="sting H")
    S(sh["t0"], "sfx_whoosh", 0.35)
    h0, h1 = sec_start("H1"), sec_end("H6")
    P.sub_margin.append((sh["t0"], h1 + 8.0, 380, 380))
    P.pips.append({"t0": h0 - 0.2, "t1": h1 + 0.3, "label": None, "size": (320, 180), "pos": (1920 - 320 - 12, 900)})
    spk = {"H1": ALIFF_, "H2": AMIN_, "H3": IMAN_, "H4": AMIN_, "H5": AMIN_, "H6": AMIN_}
    for k_, (nm, rl) in spk.items():
        pl = pill(nm.split(" bin ")[0], F("mb", 20), fg=WHITE, bg=(20, 20, 30))
        L(pl, sec_start(k_) + 0.2, sec_end(k_), (1920 - 320 - 12 + 8, 908), "fade", "fade", 0.4, 0.3, z=22, name=f"pip nama {k_}")

    def beats(sec, plan):
        """plan: (frasa_penambat, shots, cam[, file]) ; tamat pada penambat seterusnya."""
        times = []
        for item in plan:
            anc = item[0]
            times.append(anc if isinstance(anc, (int, float)) else (A(anc, sec) if anc else sec_start(sec)))
        for i, item in enumerate(plan):
            anc, shots, cam = item[0], item[1], item[2]
            fl = item[3] if len(item) > 3 else None
            t0 = times[i]
            t1 = times[i + 1] if i + 1 < len(plan) else sec_end(sec)
            if t0 is None or t1 is None:
                print("  !! beat tiada penambat", sec, anc); continue
            P.gshots(t0, t1, shots, f"{sec}#{i}", cam=cam, file=fl)
        return times

    def gapfill(tag, shots, i=0, cam=None, label="", file=None):
        gg = gaps_by[tag][i]
        P.gshots(gg["t0"], gg["t1"], shots, label or tag, cam=cam, pip=False, file=file)

    def plus100(src_t, file=None, txt="+100", sub="BETUL!", col=GOLD):
        t = P.gsrc2out(src_t, file)
        if t is None:
            print("  !! +100 tiada pemetaan", src_t); return None
        sp = score_pop(txt, sub, col)
        sp = sp.resize((int(sp.size[0] * 0.72), int(sp.size[1] * 0.72)), Image.LANCZOS)
        L(sp, t + 0.45, t + 2.6, (C.GAME_DST[0] + C.GAME_DST[2] - sp.size[0] + 10, C.GAME_DST[1] - 8), "pop", "fade", 0.45, 0.4, z=21, name=f"pop {txt}@{src_t}")
        S(t + 0.45, "sfx_success" if col == GOLD else "sfx_fail", 0.45)
        return t

    # ---- H1 – Lobi & galeri ----
    beats("H1", [
        (None, [(14.0, 22.0, "k"), (33.0, 41.0, "k")], {}),
        ("Apabila murid mendekati watak", [(41.0, 67.0, "t")], {}),
        ("Poster di dinding sebelah utara", [(88.0, 100.0, "k")], {}),
        ("Dan Jenis yang kedua", [(100.5, 108.0, "k")], {}),
        ("Dan akhir sekali Jenis ketiga", [(108.0, 117.0, "k")], {}),
        ("kiri dan kanan pula", [(67.0, 76.0, "t")], {}),
        ("Contohnya, kapsyen kepada yang berminat", [(76.0, 86.0, "k")], {"zoom": (1.15, 1.4), "center": (960, 520)}),
        ("Galeri ini penting", [(121.0, 133.0, "t")], {}),
    ])
    tgal = A("kiri dan kanan pula", "H1"); tgp = A("Galeri ini penting", "H1")
    side(tgal, tgp)
    rc_stack([{"img": keypoint_card("GALERI ISU", "Paparan telefon: [R:MEDIA SOSIAL] → [Y:ISU] → [G:AYAT BETUL]", "Kapsyen sebenar daripada bukti media sosial.", accent=PURPLE, w=600),
               "t0": (tgal or 0) + 0.6, "t1": tgp, "name": "galeri kad", "ain": "right"}])
    # ---- H2 – mod & markah ----
    gapfill("h-mid", [(130.0, 135.0, "t")], 0)
    beats("H2", [
        (None, [(134.0, 158.0, "t")], {}),
        ("Untuk bermain secara berkumpulan", [(158.0, 170.0, "k")], {}),
        ("Sebelum bermula", [(0.0, 7.5, "k")], {}, "sg"),
        ("Sistem markahnya mudah", [(116.5, 125.0, "k")], {}),
    ])
    tm = A("Murid boleh memilih", "H2"); tsb = A("Sebelum bermula", "H2"); tsk = A("Sistem markahnya mudah", "H2")
    side(tm, sec_end("H2"))
    rc_stack([{"img": keypoint_card("MAIN INDIVIDU", "Gerbang [G:HIJAU] • blok zamrud", None, accent=LGREEN, w=600), "t0": A("Untuk bermain secara individu", "H2") or tm, "t1": tsb, "name": "mod individu", "ain": "right"},
              {"img": keypoint_card("MAIN BERKUMPULAN", "Gerbang [P:UNGU] • bulu warna", "Merah / biru / hijau / kuning • markah dikongsi.", accent=PURPLE, w=600),
               "t0": A("Untuk bermain secara berkumpulan", "H2") or tm + 4, "t1": tsb, "name": "mod kumpulan", "ain": "right"}])
    rc_stack([{"img": keypoint_card("PETAK LATIHAN", "Pijak [Y:BLOK EMAS] untuk membiasakan diri", None, accent=GOLD, w=600), "t0": tsb, "t1": tsk, "name": "blok emas", "ain": "right"}])
    if tsk:
        rc_stack([{"img": keypoint_card("BETUL", "[G:+100] markah", None, accent=LGREEN, w=600), "t0": A("diberi tambahan", "H2") or tsk + 1.5, "t1": sec_end("H2") + 0.3, "name": "+100 sistem", "snd": "sfx_success", "sg": 0.2, "ain": "right"},
                  {"img": keypoint_card("SALAH", "[R:−50] markah", None, accent=RED, w=600), "t0": A("ditolak 50 markah", "H2") or tsk + 4, "t1": sec_end("H2") + 0.3, "name": "-50 sistem", "snd": "sfx_fail", "sg": 0.2, "ain": "right"},
                  {"img": keypoint_card("PERATURAN", "[Y:5 betul] → jenis seterusnya", "Setiap jenis ada [Y:10 soalan].", accent=GOLD, w=600),
                   "t0": A("Murid perlu menjawab 5 soalan", "H2") or tsk + 7, "t1": sec_end("H2") + 0.3, "name": "peraturan", "ain": "right"}])
    # ---- H3 – Misi 1 ----
    gapfill("h-mid", [(172.0, 176.0, "k")], 1)
    beats("H3", [
        (None, [(176.0, 192.0, "k")], {}),
        ("Papan ini mengingatkan", [(192.0, 203.0, "t")], {}),
        ("Masa membaca ini sengaja", [(203.0, 206.0, "t")], {}),
        ("Soalan pertama", [(206.0, 224.0, "k")], {}),
        ("Murid menjawab dengan memijak", [(224.0, 238.6, "t")], {}),
        ("Jawapan betul", [(238.6, 246.0, "k")], {}),
        ("Sekarang, saya tunjukkan", [(246.0, 260.0, "k")], {}),
        ("Saya sengaja memilih murid", [(624.0, 628.9, "t")], {}),
        ("Jawapan salah", [(628.9, 634.5, "k")], {}),
        ("Melalui cara ini", [(634.5, 648.0, "t")], {}),
        ("Jika murid mahu mencuba soalan lain", [(648.0, 651.6, "k")], {}),
    ])
    plus100(238.97)
    plus100(629.2, txt="−50", sub="SALAH!", col=RED)
    ts_ = A("Saya sengaja memilih murid", "H3")
    tmc = A("Melalui cara ini", "H3")
    if ts_:
        lb = pill("Contoh jawapan SALAH – rakaman sebenar (soalan Misi 2)", F("mb", 22), fg=WHITE, bg=(150, 30, 30))
        L(lb, ts_ + 0.1, (tmc or ts_ + 8) + 0.5, (C.GAME_DST[0] + 14, C.GAME_DST[1] + C.GAME_DST[3] - 60), "left", "fade", 0.4, 0.3, z=20, name="label salah")
    # ULANG: blok biru → soalan seterusnya (rakaman 10:34–10:58)
    gu = g("ulang")
    P.gshots(gu["t0"], gu["t1"], [(651.6, 656.0, "k")], "ulang", pip=False)
    tj = A("Jika murid mahu mencuba soalan lain", "H3")
    side(tj, gu["t1"])
    rc_stack([{"img": keypoint_card("JAWAPAN SALAH?", "Pijak [B:BLOK BIRU] (ULANG)", "Murid terus ke [Y:soalan seterusnya] – tidak tersekat.", accent=BLUE, w=600),
               "t0": tj, "t1": gu["t1"] + 0.2, "name": "blok biru", "snd": "sfx_pop", "sg": 0.2, "ain": "right"}])
    # peralihan Misi 1 → 2
    gg = g("m1-done")
    P.gshots(gg["t0"], gg["t1"], [(372.0, 384.0, "t")], "M1 selesai", cam={"zoom": (1.0, 1.15)}, pip=False)
    mb = mission_banner("MISI 1 SELESAI ✓", "AYAT TIDAK LENGKAP", GOLD, done=True)
    L(mb, gg["t0"] + 0.2, gg["t1"] + 0.6, center_pos(mb, 330), "scale", "fade", 0.5, 0.4, z=25, name="banner M2")
    S(gg["t0"], "sfx_whoosh", 0.4); S(gg["t0"] + 0.3, "sfx_success", 0.3)
    # ---- H4 – Misi 2 (selari dengan penerangan Amin) ----
    beats("H4", [
        (None, [(385.0, 410.0, "t")], {}),
        ("Soalan pertama", [(410.0, 426.5, "k")], {}),
        ("Murid perlu membuka Peti satu", [(426.5, 445.0, "t")], {}),
        ("Saya ambil", [(445.0, 456.0, "k")], {}),
        ("terletak di hujung kampung daripada Peti dua", [(456.0, 463.0, "t"), (463.0, 473.0, "k")], {}),
        ("Kemudian, saya letakkan", [(473.0, 478.7, "k")], {}),
        ("Jawapan terus disemak", [(478.7, 486.0, "k")], {}),
        ("Perhatikan bahawa peti juga", [(446.3, 453.5, "k"), (463.3, 470.5, "k")], {"zoom": (1.15, 1.15), "center": (960, 520)}),
        ("Jika murid tersalah susun", [(640.0, 652.0, "t")], {"zoom": (1.3, 1.35), "center": (620, 640)}),
    ])
    plus100(478.93)
    tq = A("Soalan pertama", "H4"); tpb = A("Murid perlu membuka Peti satu", "H4"); tjd = A("Jawapan terus disemak", "H4")
    tpe = A("Perhatikan bahawa peti juga", "H4"); tss = A("Jika murid tersalah susun", "H4")
    side(tq, tpb)
    rc_stack([{"img": sentence_box("salah", "Rumah Ali yang besar di hujung kampung itu.", w=616, label="Soalan 1", size=32), "t0": tq + 0.3 if tq else None, "t1": tpb, "name": "soalan rumah ali", "snd": None, "ain": "right"},
              {"img": keypoint_card("MENGAPA SALAH?", "[R:Tiada predikat]", None, accent=RED, w=600), "t0": A("Ayat ini tidak lengkap", "H4"), "t1": tpb, "name": "tiada predikat", "ain": "right"}])
    side(tjd, tss)
    rc_stack([{"img": formula_row([block("Rumah Ali yang besar itu", "SUBJEK", BLUE, w=520, h=110, tsize=30)], op_size=40), "t0": (tjd or 0) + 3.4, "t1": tpe, "name": "S", "ain": "right"},
              {"img": formula_row([block("terletak di hujung kampung.", "PREDIKAT", (46, 160, 70), w=520, h=110, tsize=30)], op_size=40), "t0": (tjd or 0) + 4.0, "t1": tpe, "name": "P", "ain": "right"}])
    rc_stack([{"img": keypoint_card("PILIHAN PENGECOH", "“Kerana rumah Ali”", "Klausa [R:tergantung].", accent=RED, w=600), "t0": (tpe or 0) + 1.5, "t1": tss, "name": "pengecoh1", "ain": "right"},
              {"img": keypoint_card("PILIHAN PENGECOH", "“yang di hujung kampung”", "Masih [R:tiada predikat].", accent=RED, w=600), "t0": (tpe or 0) + 2.5, "t1": tss, "name": "pengecoh2", "ain": "right"}])
    side(tss, sec_end("H4"))
    rc_stack([{"img": keypoint_card("TERSALAH SUSUN?", "Pijak blok [P:SET SEMULA]", "Peti diisi semula, bingkai dikosongkan.", accent=PURPLE, w=600), "t0": tss, "t1": sec_end("H4") + 0.2, "name": "set semula", "ain": "right"}])
    # peralihan Misi 2 → 3
    gg = g("m2-done")
    P.gshots(gg["t0"], gg["t1"], [(735.0, 745.0, "t")], "M2 selesai", cam={"zoom": (1.15, 1.0)}, pip=False)
    mb = mission_banner("MISI 2 SELESAI ✓", "MISI 3: BAHASA ROJAK", PURPLE, done=True)
    L(mb, gg["t0"] + 0.2, gg["t1"] + 0.6, center_pos(mb, 330), "scale", "fade", 0.5, 0.4, z=25, name="banner M3")
    S(gg["t0"], "sfx_whoosh", 0.4); S(gg["t0"] + 0.3, "sfx_success", 0.3)
    # ---- H5 – Misi 3 ----
    beats("H5", [
        (None, [(745.0, 774.0, "t")], {}),
        ("Soalan pertama ialah", [(774.0, 788.0, "k")], {}),
        ("Saya melompat ke platform A", [(812.7, 816.7, "k")], {}),
        ("Jawapan betul", [(816.7, 822.0, "k")], {}),
        ("Jika murid jatuh ke dalam air", [(923.2, 928.6, "k")], {}),
        ("Setiap bilik mempunyai laluan", [(822.0, 905.0, "t")], {}),
    ])
    plus100(816.9)
    t1q = A("Soalan pertama ialah", "H5"); tml = A("Saya melompat ke platform A", "H5")
    side(t1q, tml)
    rc_stack([{"img": sentence_box("salah", "Saya sangat [r:happy] kerana dapat hadiah.", w=616, label="Soalan 1", size=32), "t0": (t1q or 0) + 0.3, "t1": tml, "name": "soalan happy", "ain": "right"},
              {"img": keypoint_card("PILIHAN", "gembira  •  happy  •  marah", None, accent=PURPLE, w=600), "t0": A("Pilihannya ialah", "H5"), "t1": tml, "name": "pilihan", "ain": "right"}])
    tw_ = A("Jika murid jatuh ke dalam air", "H5")
    if tw_:
        lb = pill("Jatuh ke air: kembali ke permulaan", F("mb", 22), fg=WHITE, bg=(30, 90, 170))
        L(lb, tw_ + 0.3, A("Setiap bilik mempunyai laluan", "H5") or tw_ + 5, (C.GAME_DST[0] + 14, C.GAME_DST[1] + C.GAME_DST[3] - 60), "left", "fade", 0.4, 0.3, z=20, name="label jatuh")
    tlb = A("Setiap bilik mempunyai laluan", "H5")
    if tlb:
        side(tlb, sec_end("H5"))
        rc_stack([{"img": formula_row([chip(en, RED, 32), "→", chip(bm, (46, 160, 70), 32)], op_size=40), "t0": tlb + 0.6 + i * 2.2, "t1": sec_end("H5") + 0.4,
                   "name": f"swap {en}", "snd": "sfx_pop", "sg": 0.2, "ain": "right"} for i, (en, bm) in enumerate([("HAPPY", "GEMBIRA"), ("STUDY", "BELAJAR"), ("BUSY", "SIBUK")])],
                 top=120, gap=40)
    # ---- H6 – keputusan, pingat, pentas, Sudut Guru ----
    gapfill("h-mid", [(986.0, 989.5, "t")], 2)
    beats("H6", [
        (None, [(989.5, 996.5, "k")], {}),
        ("Keputusan murid dipaparkan", [(996.5, 1003.0, "k")], {"punch": [(0.5, 5.0, 1.5, (560, 320))]}),
        ("Murid yang membuat kesalahan", [(1003.0, 1012.8, "k")], {}),
        ("Papan kedudukan memaparkan", [(1021.0, 1030.0, "t"), (1044.0, 1048.0, "k")], {}),
        ("Dunia ini juga mesra guru", [(1193.0, 1212.0, "k")], {}),
        ("Di Sudut Guru", [(8.0, 16.0, "t"), (16.0, 33.5, "k")], {}, "sg"),
    ])
    tt = sec_start("H6")
    L(None, tt + 0.6, tt + 6.5, (0, 0), "fade", "fade", 0.2, 0.8, z=19, dyn=lambda lt, d: confetti(lt, d, 200, 21), name="H6 confetti")
    L(None, tt + 0.6, tt + 8.0, (0, 0), "fade", "fade", 0.3, 0.8, z=19, dyn=lambda lt, d: sparkles(lt, d, 70, 9), name="H6 sparkle")
    S(tt + 0.6, "sfx_achievement", 0.7)
    gl = big_word("PENYELAMAT AYAT!", GOLD, 84, "mk", stroke=6, stroke_fill=INK)
    L(gl, tt + 1.0, tt + 6.0, center_pos(gl, 120), "pop", "fade", 0.6, 0.5, z=21, name="gelaran")
    tm = A("Murid yang membuat kesalahan", "H6"); tp_ = A("Papan kedudukan memaparkan", "H6")
    if tm:
        side(tm, tp_)
        med = [("EMAS", (247, 196, 58), "Salah 0–3 kali", "+300", tm), ("PERAK", (200, 205, 215), "Salah 4–7 kali", "+150", A("Murid yang membuat kesalahan", "H6", nth=2) or tm + 6),
               ("GANGSA", (205, 127, 50), "Salah 8 kali ke atas", "+0", A("selebihnya", "H6") or tm + 12)]
        rc_stack([{"img": medal_small(n, c, a_, b_, w=616), "t0": t_, "t1": tp_, "name": f"pingat {n}", "snd": "sfx_success", "sg": 0.22, "ain": "right"} for n, c, a_, b_, t_ in med],
                 top=110, gap=34)
    tg = A("Dunia ini juga mesra guru", "H6"); tsg = A("Di Sudut Guru", "H6")
    if tg:
        side(tg, tsg)
        rc_stack([{"img": keypoint_card("KELUAR", "Pijak [B:BLOK BESI]", "Kemajuan murid disimpan.", accent=(150, 160, 175), w=600), "t0": A("blok besi", "H6") or tg + 2, "t1": tsg, "name": "besi", "ain": "right"},
                  {"img": keypoint_card("SAMBUNG MISI", "Pijak [Y:GLOWSTONE]", None, accent=GOLD, w=600), "t0": A("Pada sesi seterusnya", "H6") or tg + 5, "t1": tsg, "name": "glowstone", "ain": "right"}])
    if tsg:
        tlap = A("Melalui laporan ini", "H6")
        side(tsg + 3.0, sec_end("H6") + 0.3)
        rc_stack([{"img": keypoint_card("SUDUT GURU", "Blok [R:REDSTONE]", "Set semula semua markah.", accent=RED, w=600), "t0": tsg + 3.0, "t1": sec_end("H6") + 0.3, "name": "sg redstone", "ain": "right"},
                  {"img": keypoint_card("LAPORAN KEMAJUAN", "Markah, betul, salah & misi setiap murid", None, accent=BLUE, w=600), "t0": A("memaparkan laporan", "H6") or tsg + 5, "t1": sec_end("H6") + 0.3, "name": "sg laporan", "ain": "right"},
                  {"img": keypoint_card("PENGAJARAN SUSULAN", "Kenal pasti kesalahan paling kerap", None, accent=LGREEN, w=600), "t0": tlap or tsg + 8, "t1": sec_end("H6") + 0.3, "name": "sg susulan", "ain": "right"}])

    # =================================================================
    # I – CADANGAN LAIN
    # =================================================================
    sting("sting-I", "BAHAGIAN I  •  CADANGAN LAIN", "Tanpa Peranti pun [G:Boleh]", "Tiga cadangan penambahbaikan tambahan", LGREEN, "green")
    chipsec("I", "I", "CADANGAN PENAMBAHBAIKAN LAIN")
    lower("I", *ALIFF_)
    ti = [A("Cadangan yang pertama", "I"), A("Cadangan yang kedua", "I"), A("Cadangan yang terakhir", "I")]
    if ti[0]:
        P.set_mode(ti[0] - 0.3, sec_end("I") + 0.1, "split")
        cards = [("Detektif Ayat Media Sosial", "Garis [b:subjek] & [g:predikat], kenal pasti jenis kesalahan, tulis semula → [Y:Dinding Ayat Betul].", "search", BLUE),
                 ("Kad Permainan “Selamatkan Ayat”", "Kad ayat salah 3 jenis • murah • tanpa internet • pengayaan & pemulihan.", "cards", GOLD),
                 ("Kempen #AyatBetulSekolahku", "Pengumuman & media sosial sekolah disemak panitia BM; ibu bapa jadi contoh.", "hash", LGREEN)]
        for i, (tt_, bd, ic, c) in enumerate(cards):
            if ti[i] is None:
                continue
            ic_ = icon_card(i + 1, tt_, bd, ic, c, w=900)
            stack([{"img": ic_, "t0": ti[i], "t1": sec_end("I"), "name": f"cadangan {i + 1}"}], top=[60, 340, 620][i], gap=20, bottom=[320, 600, 900][i])
            S(ti[i], "sfx_whoosh", 0.2)

    # =================================================================
    # J – HARAPAN
    # =================================================================
    sting("sting-J", "BAHAGIAN J  •  HARAPAN", "Harapan [Y:Masa Hadapan]", None, GOLD, "navy")
    chipsec("J", "J", "HARAPAN MASA HADAPAN")
    tj = [A("dapat digunakan oleh guru", "J"), A("berharap agar murid", "J"), A("berharap agar masyarakat", "J")]
    P.set_mode(sec_start("J") + 0.3, sec_end("J") + 0.1, "split")
    nodes = [("GURU", "Menggunakan pendekatan pembelajaran berasaskan permainan.", LGREEN, "teacher"),
             ("MURID", "Pengguna media sosial yang celik bahasa.", BLUE, "student"),
             ("MASYARAKAT", "Bangga menggunakan bahasa Melayu yang betul.", GOLD, "people")]
    hdj = heading("HARAPAN KAMI", "Masa hadapan [Y:bahasa]", 900, GOLD)
    card(hdj, sec_start("J") + 0.4, sec_end("J") + 0.2, (40, 50), "left", snd=None, name="harapan hd")
    stack([{"img": icon_card(i + 1, nm, bd, ic, c, w=900, h=190), "t0": tj[i] or sec_start("J") + 2 + 9 * i, "t1": sec_end("J") + 0.2,
            "name": f"harapan {nm}", "snd": "sfx_pop", "sg": 0.22} for i, (nm, bd, c, ic) in enumerate(nodes)], top=200, gap=26, bottom=860)
    tbd = A("kerana bahasa yang betul", "J")
    if tbd:
        bn = keypoint_card("BERSAMA", "[Y:Bahasa betul] tetap menarik & dekat dengan khalayak", None, accent=GOLD, w=900)
        L(bn, tbd, sec_end("J") + 0.2, (40, 200), "scale", "fade", 0.5, 0.3, z=14, name="gabung harapan")

    # =================================================================
    # K – PENUTUP & OUTRO
    # =================================================================
    chipsec("K", "K", "PENUTUP")
    tk = A("Kesimpulannya", "K")
    if tk:
        P.set_mode(tk - 0.2, A("Sekali lagi", "K") or tk + 10, "split")
        k = keypoint_card("KESIMPULAN", "Kerancuan sintaksis [R:bukan isu kecil]", "Ia merosakkan asas ayat – hubungan [B:subjek] dengan [G:predikat].", accent=GOLD, w=900)
        card(k, tk + 0.3, A("Sekali lagi", "K"), left_pos(k, 300), "left", name="kesimpulan K")
    tdr = A("Sekali lagi", "K")
    if tdr:
        L(lower_third("Dr. Siti Dahlia binti Abdullah", "Pensyarah BMMB3233 • Terima kasih atas bimbingan"), tdr + 1.0, tdr + 7.5, (60, 690), "left", "fade", 0.6, 0.5, z=20, name="LT dr")
    tbs = A("Betulkan ayat", "K")
    og = g("outro")
    # outro: syot berkumpulan (rakaman sebenar ketiga-tiga pembentang, A2)
    P.override(og["t0"], og["t1"], [{"type": "pres", "src_in": 186.0, "dur": og["t1"] - og["t0"], "sec": "OUT",
                                     "cam": {"zoom": (1.05, 1.15), "kf": [(0.0, "full")]}}], pip=False)
    big = big_word("BETULKAN AYAT, SELAMATKAN BAHASA.", WHITE, 84, "mk", stroke=6, stroke_fill=GREEN_DEEP)
    tb0 = tbs or og["t0"]
    L(big, tb0, og["t0"] + 6.0, center_pos(big, 360), "scale", "fade", 0.8, 0.6, z=25, name="slogan")
    S(tb0, "sfx_impact", 0.35)
    L(None, tb0, og["t0"] + 6.0, (0, 0), "fade", "fade", 0.3, 0.6, z=24, dyn=lambda lt, d: sparkles(lt, d, 60, 5), name="sparkle akhir")
    # kad penghargaan akhir + rujukan
    o2 = og["t0"] + 5.6
    endc = gfx.canvas(1920, 1080)
    from PIL import ImageDraw
    d = ImageDraw.Draw(endc)
    d.rectangle([0, 0, 1920, 1080], fill=(6, 22, 18, 236))
    endc.alpha_composite(big_word("TERIMA KASIH", GOLD, 110, "mk"), (110, 90))
    lines = [("MISI PENYELAMAT AYAT", F("mx", 40), WHITE), ("Isu Kerancuan Bahasa dalam Aspek Sintaksis", F("ps", 32), (210, 225, 235)),
             ("BMMB3233 Sintaksis Bahasa Melayu  •  IPG Kampus Tun Hussein Onn, Batu Pahat", F("pm", 28), (210, 225, 235)),
             ("Pensyarah: Dr. Siti Dahlia binti Abdullah", F("pm", 28), (210, 225, 235)),
             ("Mohamad Aliff bin Ahmad Shahabuddin  •  Muhammad Iman Irfan bin Mohd Ramzi  •  Amin Najmi bin Mohyidin", F("pm", 26), GOLD)]
    y = 250
    for t_, f_, c_ in lines:
        d.text((115, y), t_, font=f_, fill=c_); y += f_.size + 22
    y += 18
    d.text((115, y), "RUJUKAN", font=F("mx", 30), fill=LGREEN); y += 50
    refs = ["Ab. Razak Ab. Rahim & Nurul Ain Alizuddin. (2021).", "Chew Fong Peng & Vanithmalar Jayabalan. (2026).",
            "Kamus Dewan (Edisi Keempat). (2005). Dewan Bahasa dan Pustaka.", "Kho Thong Eng. (2023).  •  Mat Isa et al. (2025).",
            "Nik Safiah Karim, Farid M. Onn, Hashim Haji Musa & Abdul Hamid Mahmood. (2024). Tatabahasa Dewan. DBP.",
            "Perlembagaan Persekutuan, Perkara 152.  •  Bukti media sosial: 15 hantaran awam TikTok (diakses 5 November 2026)."]
    for r_ in refs:
        d.text((115, y), r_, font=F("pr", 24), fill=(200, 210, 222)); y += 38
    d.text((115, 1000), "Muzik & kesan bunyi: dijana secara sintesis (bebas royalti)  •  Rakaman: Minecraft Education (dunia Misi Penyelamat Ayat)", font=F("ir", 18), fill=(140, 150, 160))
    endc.alpha_composite(pixel_strip(1920, 14, 9), (0, 1066))
    L(endc, o2, og["t1"], (0, 0), "fade", "fade", 1.0, 2.2, z=30, name="kad akhir")
    S(o2, "sfx_whoosh", 0.25)


ALIFF_ = ("Mohamad Aliff bin Ahmad Shahabuddin", "Pembentang")
IMAN_ = ("Muhammad Iman Irfan bin Mohd Ramzi", "Pembentang")
AMIN_ = ("Amin Najmi bin Mohyidin", "Pembentang")
