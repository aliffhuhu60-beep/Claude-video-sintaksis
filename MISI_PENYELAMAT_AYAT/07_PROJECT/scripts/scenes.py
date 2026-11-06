"""Arahan adegan bagi setiap babak A–K: motion graphics, B-roll gameplay, muzik & kesan bunyi.
Semua masa grafik ditambat pada frasa yang benar-benar diucapkan (A(...))."""
import gfx
from gfx import *
import compositor as C

GY = 70  # had atas grafik
LEFT_AREA_W = 1130


def center_pos(img, y=None, x=None):
    w, h = img.size
    return ((1920 - w) // 2 if x is None else x, (1080 - h) // 2 if y is None else y)


def left_pos(img, y):
    w, h = img.size
    return (max(20, (LEFT_AREA_W - w) // 2 + 30), y)


def build(P, T, A, G, gaps_by, R):
    L, S = P.L, P.S

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
        gg = g(tag)
        for s in P.v1:
            if s.get("tag") == tag:
                s["bg"] = bgk
        L(title_card(kicker, title, sub, accent), gg["t0"], gg["t1"] + 0.25, (0, 0), "wipe", "fade", 0.6, 0.35, z=30, name=f"sting {tag}")
        S(gg["t0"], "sfx_whoosh", 0.35)

    def chipsec(sec, letter, text, until=None):
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
    op = g("opener"); wt = g("worldtitle"); mt = g("maintitle")
    for s in P.v1:
        if s.get("tag") == "opener":
            s["bg"] = "dark"
    L(None, op["t0"], op["t1"], (0, 0), "fade", "fade", 0.01, 0.01, z=15, dyn=scramble_intro, name="scramble")
    S(op["t0"] + 0.15, "sfx_impact", 0.9)
    S(op["t1"] - 3.2, "sfx_riser", 0.6)
    L(None, op["t1"] - 0.05, op["t1"] + 0.6, (0, 0), "fade", "fade", 0.01, 0.01, z=40, dyn=flash, name="flash")
    S(op["t1"], "sfx_impact", 0.7)
    # dunia Minecraft (rakaman sebenar) + tajuk projek
    P.override(wt["t0"], wt["t1"], [
        {"type": "game", "src_in": 1056.0, "src_end": 1056.0 + 5.5 * 0.8, "speed": 0.8, "dur": 5.5, "cam": {"zoom": (1.0, 1.12), "fullscreen": True}},
        {"type": "game", "src_in": 16.0, "src_end": 16.0 + 5.5 * 0.8, "speed": 0.8, "dur": 5.5, "cam": {"zoom": (1.12, 1.0), "fullscreen": True}},
    ], pip=False)
    L(None, wt["t0"], mt["t0"] + 0.4, (0, 0), "fade", "fade", 0.01, 0.01, z=14, dyn=letterbox, name="letterbox")
    tp = big_word("MISI PENYELAMAT AYAT", WHITE, 120, "mk", stroke=6, stroke_fill=GREEN_DEEP)
    L(tp, wt["t0"] + 2.0, mt["t0"] + 0.3, center_pos(tp, 380), "scale", "fade", 0.9, 0.4, z=20, name="judul projek")
    sub = text_img("Cadangan Penambahbaikan melalui Minecraft Education", F("ps", 44), GOLD)
    L(shadowed(sub, 10, (0, 4), 0.8, 20)[0], wt["t0"] + 3.4, mt["t0"] + 0.3, center_pos(sub, 540), "up", "fade", 0.7, 0.4, z=20, name="subjudul")
    S(wt["t0"] + 2.0, "sfx_impact", 0.45)
    L(None, wt["t0"] + 1.5, mt["t0"], (0, 0), "fade", "fade", 0.5, 0.5, z=18, dyn=lambda lt, d: sparkles(lt, d, 50, 4, (300, 250, 1620, 700)), name="sparkle")
    # kad tajuk utama – kekal semasa salam pembukaan (suara latar)
    t_hormat = A("Yang kami hormati", "A1")
    tc = title_card("BMMB3233  •  SINTAKSIS BAHASA MELAYU", "ISU KERANCUAN BAHASA DALAM ASPEK [G:SINTAKSIS]",
                    "Misi Penyelamat Ayat – Cadangan Penambahbaikan melalui Minecraft Education", GOLD)
    t_end_title = (t_hormat or (mt["t1"] + 5)) - 0.1
    P.override(mt["t0"], t_end_title - 0.2, [{"type": "bg", "bg": "navy", "dur": t_end_title - 0.2 - mt["t0"]}], pip=False)
    L(tc, mt["t0"], t_end_title, (0, -120), "wipe", "fade", 0.9, 0.5, z=25, name="kad tajuk utama")
    inst = text_img("IPG Kampus Tun Hussein Onn, Batu Pahat", F("mb", 36), WHITE)
    L(inst, mt["t0"] + 1.2, t_end_title, (140, 735), "up", "fade", 0.6, 0.5, z=26, name="institusi")
    pen = text_img("Pensyarah: Dr. Siti Dahlia binti Abdullah", F("pm", 32), (200, 215, 230))
    L(pen, mt["t0"] + 1.8, t_end_title, (140, 790), "up", "fade", 0.6, 0.5, z=26, name="pensyarah")
    S(mt["t0"], "sfx_whoosh", 0.4)
    # pembentang P1
    chipsec("A1", "A", "PEMBUKAAN & PENGHARGAAN", until=sec_end("A2"))
    lower("A1", *ALIFF_, t=t_end_title + 0.6)
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
        ta = P.A_src(159.0); ti = P.A_src(163.2)
        L(lower_third(*AMIN_), ta, ta + 4.0, (1180, 600), "right", "fade", 0.6, 0.4, z=20, name="LT amin")
        L(lower_third(*IMAN_), ti, ti + 4.0, (60, 520), "left", "fade", 0.6, 0.4, z=20, name="LT iman")
    t = A("terbahagi kepada", "A2")
    if t:
        tend = sec_end("A2")
        P.set_mode(t - 0.2, tend + 0.1, "win")
        hd = heading("ALIRAN PEMBENTANGAN", "Enam Bahagian", 900)
        card(hd, t, tend, (70, 120), "left", snd=None, name="aliran")
        items = ["Pengenalan isu & sebab dipilih", "Tiga jenis kesalahan ayat", "Cadangan: Minecraft Education",
                 "Demonstrasi cara bermain", "Cadangan penambahbaikan lain", "Harapan & penutup"]
        keys = ["pertama", "kedua", "Seterusnya, cadangan", "demonstrasi cara bermain", "cadangan penambahan baikan lain", "harapan serta penutup"]
        prev = t + 0.6
        for i, (it, k) in enumerate(zip(items, keys)):
            tk = A(k, "A2", after=prev - 0.5) or prev + 2.5
            tk = max(tk, prev)
            img = list_item(i + 1, it, [GOLD, RED, PURPLE, PURPLE, LGREEN, BLUE][i], w=880)
            L(img, tk, tend, (70, 270 + i * 92), "left", "fade", 0.45, 0.4, z=12, name=f"aliran {i + 1}")
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
        d1 = keypoint_card("RANCU =", "[Y:KACAU] • [Y:TIDAK TERATUR] • [Y:CAMPUR ADUK]", None, accent=GOLD, w=1000)
        card(d1, A("kacau", "B") or t + 3, t_def, left_pos(d1, 470), "up", name="rancu def")
        d2 = keypoint_card("DEFINISI", "KERANCUAN BAHASA", "= penggunaan bahasa yang [Y:kacau dan tidak teratur] sehingga [R:menyalahi peraturan tatabahasa] bahasa Melayu.", accent=GOLD, w=1000)
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
        k = keypoint_card("SINTAKSIS", "Cara perkataan disusun → [B:FRASA] → [B:KLAUSA] → [B:AYAT]", "(Nik Safiah Karim et al., 2024)", accent=BLUE, w=1000)
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
            img = list_item(i + 1, txt, RED, w=1040)
            L(img, tk, t_tegas, (70, 290 + i * 100), "left", "fade", 0.45, 0.4, z=12, name=f"ganggu {i}")
            S(tk, "sfx_tick", 0.25)
            prev = tk
    if t_tegas:
        t_tutur = A("Dalam pertuturan", "B")
        P.set_mode(t_tegas - 0.2, sec_end("B") + 0.1, "split")
        k1 = keypoint_card("✗  BUKAN FOKUS", "Kesalahan KATA secara terpencil", "cth. salah ejaan: “sye”, “x”, “dlm”", accent=RED, w=1000)
        k2 = keypoint_card("✓  FOKUS KAJIAN", "KESALAHAN [Y:AYAT] (SINTAKSIS)", "Kesalahan yang menjejaskan [Y:binaan ayat secara keseluruhan].", accent=LGREEN, w=1000)
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
        q3 = sentence_box("salah", "Harini [r:team] kami nak [r:share] cara buat kek.", w=1060, label="Contoh ayat (YouTube)", size=36)
        q4 = sentence_box("salah", "[r:Overall best gila], wajib [r:try guys]!", w=1060, label="Contoh ayat (Threads)", size=36)
        card(q3, t3, t_ditulis, left_pos(q3, 170), "left", name="contoh share")
        card(q4, A("Overall", "C") or t3 + 4, t_ditulis, left_pos(q4, 420), "left", name="contoh overall")
        if t_ditulis:
            k = keypoint_card("SIAPA MENULIS? SIAPA MEMBACA?", "Peniaga & pencipta kandungan → [Y:jutaan pengguna]", "…termasuklah [R:kanak-kanak].", accent=GOLD, w=1000)
            card(k, t_ditulis, t_empat, left_pos(k, 300), "scale", name="ditulis")
    if t_empat:
        t_tiga = A("Daripada bukti yang kami kumpulkan", "C")
        P.set_mode(t_empat - 0.2, sec_end("C") + 0.1, "split")
        hd = heading("SEBAB ISU DIPILIH", "Empat Sebab Utama", 1000)
        card(hd, t_empat, t_tiga, (70, 90), "left", snd=None, name="4 sebab hd")
        reasons = [("Paling hampir dengan murid", "Murid membesar dengan TikTok & YouTube.", "Sebab yang pertama"),
                   ("Sudah dinormalkan", "Pengguna tidak sedar ayat itu salah.", "Sebab yang kedua"),
                   ("Berkait terus dengan sintaksis", "Subjek, predikat, klausa bebas & terikat.", "Sebab yang ketiga"),
                   ("Tanggungjawab bakal guru", "Bukan sekadar mengkritik – beri penyelesaian.", "Sebab yang keempat")]
        for i, (ti, bd, k) in enumerate(reasons):
            tk = A(k, "C") or t_empat + 3 + i * 15
            nc = numbered_card(i + 1, ti, bd, [GOLD, RED, BLUE, LGREEN][i], w=520, h=300)
            L(nc, tk, t_tiga, (50 + (i % 2) * 560, 240 + (i // 2) * 320), "scale", "fade", 0.5, 0.4, z=12, name=f"sebab {i + 1}")
            S(tk, "sfx_pop", 0.2)
        tc = A("Kajian juga mendapati", "C")
        if tc:
            cit = pill("Chew Fong Peng & Vanithmalar Jayabalan (2026)", F("ps", 24), fg=WHITE, bg=(30, 50, 90))
            L(cit, tc, tc + 9, (60, 872), "fade", "fade", 0.4, 0.4, z=13, name="sitasi chew")
        if t_tiga:
            hd2 = heading("TIGA JENIS KESALAHAN", "Paling Kerap Ditemui", 1000)
            card(hd2, t_tiga, sec_end("C"), (70, 110), "left", snd=None, name="3 jenis hd")
            for i, (lbl, k, c) in enumerate([("JENIS 1 • Ayat Tanpa Subjek", "ayat tanpa subjek", RED), ("JENIS 2 • Ayat Tidak Lengkap", "ayat tidak lengkap", GOLD),
                                             ("JENIS 3 • Bahasa Rojak", "bahasa rojak", PURPLE)]):
                tk = A(k, "C", after=t_tiga) or t_tiga + 2 + i
                img = list_item(i + 1, lbl, c, w=1000)
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
        k2 = keypoint_card("KEADAAN 2", "Subjek [R:digugurkan] terus", "Kata ganti nama seperti [Y:saya], [Y:anda], [Y:kami] dibuang kerana penulis menganggap pembaca sudah faham.", accent=RED, w=1000)
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
    for (ts, tr, te, i) in blocks:
        if ts is None:
            continue
        _, wrong, right, lbl, ana = ex[i]
        P.set_mode(ts - 0.6, te, "split")
        b1 = sentence_box("salah", wrong, w=1080, label=lbl, size=40)
        card(b1, ts - 0.2, te, left_pos(b1, 90), "left", name=f"D salah {i + 1}", snd="sfx_fail", sg=0.12)
        an = analysis_box(ana, w=1080, size=28)
        card(an, ts + 3.0, te, left_pos(an, 330), "up", name=f"D analisis {i + 1}", snd=None)
        if tr:
            b2 = sentence_box("betul", right, w=1080, size=40)
            card(b2, tr, te, left_pos(b2, 560), "left", name=f"D betul {i + 1}", snd="sfx_success", sg=0.12)
        if i == 0:
            tcara = A("Kata sendi nama kepada digugurkan", "D") or (tr + 4 if tr else None)
            if tcara:
                cr = keypoint_card("CARA PEMBETULAN", "1. Gugurkan kata sendi nama  2. Tambah subjek", None, accent=LGREEN, w=1080)
                card(cr, tcara, te, left_pos(cr, 790), "up", name="cara betul", snd="sfx_pop")
    if t_ex3:
        te = t_kesan or t_ex3 + 20
        P.set_mode(t_ex34_hdr - 0.4, te, "split")
        tr = A("Ayat yang betul", "D", after=t_ex3)
        for j, i in enumerate((2, 3)):
            _, wrong, right, lbl, ana = ex[i]
            b1 = sentence_box("salah", wrong, w=1080, label=lbl, size=36)
            card(b1, (t_ex3 if j == 0 else (t_ex4 or t_ex3 + 2)), te, left_pos(b1, 90 + j * 200), "left", name=f"D salah {i + 1}", snd="sfx_fail", sg=0.1)
            if tr:
                b2 = sentence_box("betul", right, w=1080, size=36)
                tb = tr if j == 0 else (A("pelanggan yang berminat", "D", after=tr) or tr + 3)
                card(b2, tb, te, left_pos(b2, 500 + j * 200), "left", name=f"D betul {i + 1}", snd="sfx_success", sg=0.1)
    if t_kesan:
        P.set_mode(t_kesan - 0.2, sec_end("D") + 0.1, "split")
        hd = heading("KESAN JENIS 1", "Mengapa ini [R:serius]?", 1000)
        card(hd, t_kesan, sec_end("D"), (70, 100), "left", snd=None, name="kesan D hd")
        ks = [("Maksud kabur", "Pembaca tidak tahu siapa pelaku.", "Kesan yang pertama"),
              ("Sukar disedari", "“Bagi saya berpendapat…” dibawa ke karangan.", "Kedua, kesalahan ini sukar"),
              ("Hilang markah", "Dikira kesalahan tatabahasa dalam peperiksaan.", "Akhir sekali")]
        for i, (ti, bd, kk) in enumerate(ks):
            tk = A(kk, "D", after=t_kesan) or t_kesan + 3 + 12 * i
            nc = numbered_card(i + 1, ti, bd, RED, w=350, h=330)
            L(nc, tk, sec_end("D"), (50 + i * 370, 280), "up", "fade", 0.5, 0.4, z=12, name=f"kesanD {i}")
            S(tk, "sfx_pop", 0.2)

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
        for i, (lt, ti, bd, tk) in enumerate(panels):
            if tk is None:
                continue
            kc = keypoint_card(f"BENTUK {lt}", ti, bd, accent=GOLD, w=1060)
            L(kc, tk, t_ex1, (50, 90 + i * 245), "left", "fade", 0.5, 0.4, z=12, name=f"bentuk {lt}")
            S(tk, "sfx_pop", 0.2)
        tay = A("Ayah membeli di kedai", "E")
        if tay:
            a1 = formula_row([block("AYAH", "SUBJEK", BLUE, w=230, h=130, tsize=42), block("MEMBELI", "KK TRANSITIF", (46, 160, 70), w=290, h=130, tsize=42),
                              block("???", "OBJEK HILANG", RED, w=230, h=130, tsize=42), block("DI KEDAI", "", NAVY, w=260, h=130, tsize=42)], gap=10)
            a2 = formula_row([block("AYAH", "SUBJEK", BLUE, w=200, h=130, tsize=40), block("MEMBELI", "KK TRANSITIF", (46, 160, 70), w=250, h=130, tsize=40),
                              block("SEBUAH BASIKAL", "OBJEK", (46, 160, 70), w=380, h=130, tsize=40), block("DI KEDAI", "", NAVY, w=220, h=130, tsize=40)], gap=10)
            ta2 = A("apakah yang dibeli", "E") or tay + 2.5
            L(a1, tay, ta2 + 0.5, left_pos(a1, 650), "up", "fade", 0.4, 0.3, z=15, name="ayah ???")
            L(a2, ta2 + 0.5, t_ex1, left_pos(a2, 650), "scale", "fade", 0.4, 0.4, z=15, name="ayah basikal")
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
    for i in range(3):
        ts = tE[i]
        if ts is None:
            continue
        _, wrong, right, lbl, ana = exE[i]
        te = ends[i] or ts + 20
        P.set_mode(ts - 0.4, te, "split")
        b1 = sentence_box("salah", wrong, w=1080, label=lbl, size=40)
        card(b1, ts, te, left_pos(b1, 90), "left", name=f"E salah {i + 1}", snd="sfx_fail", sg=0.12)
        an = analysis_box(ana, w=1080, size=28)
        card(an, ts + 3.5, te, left_pos(an, 320), "up", name=f"E analisis {i + 1}", snd=None)
        tr = A("Ayat yang betul", "E", after=ts)
        if tr and tr < te:
            b2 = sentence_box("betul", right, w=1080, size=40)
            card(b2, tr, te, left_pos(b2, 520), "left", name=f"E betul {i + 1}", snd="sfx_success", sg=0.12)
        if i == 0:
            tk = A("Kini, kedai ini menjadi subjek", "E") or A("Kini", "E")
            if tk:
                sp = formula_row([block("KEDAI INI", "SUBJEK", BLUE, w=330, h=130, tsize=44), "+",
                                  block("IALAH KEDAI MALATANG PALING SEDAP DI KL", "PREDIKAT", (46, 160, 70), w=690, h=130, tsize=30)], op_size=50)
                card(sp, tk, te, left_pos(sp, 770), "scale", name="E subjek predikat")
    if t_kesanE:
        tser = A("saya serahkan", "E") or A("serahkan", "E")
        P.set_mode(t_kesanE - 0.2, sec_end("E") + 0.1, "split")
        hd = heading("KESAN JENIS 2", "Mesej [R:tidak sampai]", 1000)
        card(hd, t_kesanE, sec_end("E"), (70, 100), "left", snd=None, name="kesan E hd")
        ks = [("Mesej tidak lengkap", "Tawaran & tindakan tidak jelas.", "Pertama"), ("Ayat tergantung", "“Apabila loceng berbunyi.” lalu noktah.", "Kedua"),
              ("Ayat majmuk lemah", "Klausa terikat perlukan klausa utama.", "Ketiga")]
        for i, (ti, bd, kk) in enumerate(ks):
            tk = A(kk, "E", after=t_kesanE) or t_kesanE + 3 + 10 * i
            nc = numbered_card(i + 1, ti, bd, GOLD, w=350, h=330)
            L(nc, tk, sec_end("E"), (50 + i * 370, 280), "up", "fade", 0.5, 0.4, z=12, name=f"kesanE {i}")
            S(tk, "sfx_pop", 0.2)

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
                img = list_item(i + 1, f"{a}:  {b}", PURPLE, w=1000)
                L(img, t_jaw + 1.5 + i * 1.6, t_c1, (70, 290 + i * 98), "left", "fade", 0.45, 0.4, z=12, name=f"fungsi {i}")
            if t_akib:
                st = keypoint_card("AKIBATNYA", "Ayat rasmi WAJIB guna bahasa Melayu [Y:BAKU]", None, accent=PURPLE, w=1000)
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
    for i in range(4):
        ts = tF[i]
        if ts is None:
            continue
        _, wrong, right, lbl, ana = exF[i]
        te = endsF[i] or ts + 15
        if i == 2:
            yb = 330
        else:
            yb = 90
        if i != 2:
            P.set_mode(ts - 0.4, te, "split")
        b1 = sentence_box("salah", wrong, w=1080, label=lbl, size=36 if i == 2 else 40)
        card(b1, ts, te, left_pos(b1, yb if i != 1 else 90), "left", name=f"F salah {i + 1}", snd="sfx_fail", sg=0.12)
        if i in (0, 3):
            an = analysis_box(ana, w=1080, size=28)
            card(an, ts + 3.0, te, left_pos(an, 300), "up", name=f"F analisis {i + 1}", snd=None)
        tr = A("Ayat yang betul", "F", after=ts) or A("Ayat betul", "F", after=ts)
        if tr and tr < te:
            b2 = sentence_box("betul", right, w=1080, size=36 if i in (1, 2) else 40)
            yy = 520 if i in (0, 3) else (300 if i == 1 else 640)
            if i == 1:
                continue
            card(b2, tr, te, left_pos(b2, yy), "left", name=f"F betul {i + 1}", snd="sfx_success", sg=0.12)
    if tF[1] and tF[3]:
        tr = A("Ayat betul ialah secara keseluruhan", "F") or A("secara keseluruhan", "F", after=tF[1])
        if tr:
            b2 = sentence_box("betul", exF[1][2], w=1080, size=34)
            card(b2, tr, tF[3], left_pos(b2, 560), "left", name="F betul 2", snd=None)
            b3 = sentence_box("betul", exF[2][2], w=1080, size=34)
            card(b3, tr + 0.4, tF[3], left_pos(b3, 740), "left", name="F betul 3", snd="sfx_success", sg=0.12)
    if t_kesanF:
        t_rum = A("Secara keseluruhan", "F", after=t_kesanF)
        P.set_mode(t_kesanF - 0.2, sec_end("F") + 0.1, "split")
        hd = heading("KESAN JENIS 3", "Bahasa rojak [R:merugikan]", 1000)
        card(hd, t_kesanF, t_rum, (70, 90), "left", snd=None, name="kesan F hd")
        ks = [("Martabat bahasa terjejas", "Perkara 152 Perlembagaan Persekutuan.", "Yang pertama"), ("Kosa kata hilang", "submit/share/busy ≠ menghantar/berkongsi/sibuk", "Yang kedua"),
              ("Terbawa ke situasi rasmi", "Karangan, surat rasmi, peperiksaan.", "Yang ketiga"), ("Dianggap betul", "Generasi akan datang menormalkannya.", "yang keempat")]
        for i, (ti, bd, kk) in enumerate(ks):
            tk = A(kk, "F", after=t_kesanF) or t_kesanF + 3 + 9 * i
            nc = numbered_card(i + 1, ti, bd, PURPLE, w=520, h=290)
            L(nc, tk, t_rum, (50 + (i % 2) * 560, 240 + (i // 2) * 310), "scale", "fade", 0.5, 0.4, z=12, name=f"kesanF {i}")
            S(tk, "sfx_pop", 0.2)
        if t_rum:
            fr = formula_row([block("3 JENIS KESALAHAN", "SATU PERSAMAAN", RED, w=470, h=150, tsize=40), "→",
                              block("SUBJEK ✗ PREDIKAT", "HUBUNGAN DIROSAKKAN", NAVY, w=520, h=150, tsize=40)], op_size=56)
            card(fr, t_rum, sec_end("F"), left_pos(fr, 200), "scale", name="rumusan")
            tsr = A("sekolah rendah", "F", after=t_rum, nth=1)
            k = keypoint_card("KESIMPULAN ISU", "Usaha membasmi kerancuan mesti bermula di [Y:SEKOLAH RENDAH]", None, accent=GOLD, w=1000)
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
        P.gshots(t_bina - 0.3, t_pilih, [(1057.0, 1085.0, "t")], "G-lobi", cam={"zoom": (1.0, 1.08)})
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
            c = icon_card(i + 1, ti, bd, ic, LGREEN, w=1000, h=190)
            L(c, tk, t_dunia, (50, 250 + i * 215), "left", "fade", 0.5, 0.4, z=12, name=f"mc sebab {i}")
            S(tk, "sfx_pop", 0.2)
    if t_dunia:
        P.gshots(t_dunia - 0.3, t_sek, [(135.0, 172.0, "t")], "G-gerbang", cam={"zoom": (1.0, 1.06)})
        P.pips.append({"t0": t_dunia - 0.3, "t1": t_sek, "label": None})
        fl = formula_row([block("BUKTI MEDIA SOSIAL", "", NAVY, w=420, h=120, tsize=34), "→", block("3 JENIS KESALAHAN", "", RED, w=420, h=120, tsize=34), "→",
                          block("3 MISI PERMAINAN", "", PURPLE, w=420, h=120, tsize=34)], op_size=48)
        card(fl, t_dunia, A("Contohnya", "G", after=t_dunia) or t_dunia + 9, center_pos(fl, 120), "scale", name="aliran bukti")
        for i, (nm, c) in enumerate([("MISI 1: AYAT TANPA SUBJEK", RED), ("MISI 2: AYAT TIDAK LENGKAP", GOLD), ("MISI 3: BAHASA ROJAK", PURPLE)]):
            tk = (A("dijadikan sebagai tiga misi", "G") or t_dunia + 5) + i * 0.6
            ch = chip(nm, c, 32, fg=INK if c == GOLD else WHITE)
            L(ch, tk, (A("Contohnya", "G", after=t_dunia) or tk + 6) + 1.5, (130 + i * 570 - (60 if i == 2 else 0), 290), "pop", "fade", 0.4, 0.4, z=13, name=f"misi chip {i}")
            S(tk, "sfx_tick", 0.2)
        tf = A("Setiap jawapan murid", "G")
        feats = ["Galeri isu", "3 misi", "Maklum balas segera", "Markah & pingat", "MAIN INDIVIDU", "MAIN BERKUMPULAN", "Laporan guru"]
        if tf:
            for i, f_ in enumerate(feats):
                c = [NAVY, PURPLE, (46, 160, 70), GOLD, (46, 160, 70), PURPLE, RED][i]
                ch = chip(f_, c, 28, fg=INK if c == GOLD else WHITE)
                L(ch, tf + i * 0.35, t_sek, (100 + (i % 4) * 430, 170 + (i // 4) * 100), "pop", "fade", 0.35, 0.4, z=13, name=f"ciri {f_}")
    if t_sek:
        tb = big_word("MULA DEMONSTRASI", GOLD, 84, "mk", stroke=5, stroke_fill=INK)
        card(tb, t_sek, sec_end("G") + 0.2, center_pos(tb, 380), "scale", name="mula demo", snd="sfx_riser", sg=0.35)

    # =================================================================
    # H – DEMONSTRASI MINECRAFT
    # =================================================================
    sh = g("sting-H")
    for s in P.v1:
        if s.get("tag") == "sting-H":
            s["bg"] = "game"
    L(title_card("BAHAGIAN H  •  DEMONSTRASI", "Cara Bermain [P:Misi Penyelamat Ayat]", "Rakaman sebenar Minecraft Education", PURPLE), sh["t0"], sh["t1"] + 0.2, (0, 0), "wipe", "fade", 0.6, 0.3, z=30, name="sting H")
    S(sh["t0"], "sfx_whoosh", 0.35)
    h0, h1 = sec_start("H1"), sec_end("H6")
    P.sub_margin.append((h0 - 0.5, h1 + 0.5, 260, 560))
    labels = {"H1": "H1 • LOBI UTAMA & GALERI ISU", "H2": "H2 • MOD PERMAINAN & MARKAH", "H3": "H3 • MISI 1: AYAT TANPA SUBJEK",
              "H4": "H4 • MISI 2: AYAT TIDAK LENGKAP", "H5": "H5 • MISI 3: BAHASA ROJAK", "H6": "H6 • KEPUTUSAN & SUDUT GURU"}
    for k_, lb in labels.items():
        im = pill(lb, F("mb", 24), fg=WHITE, bg=(60, 30, 110))
        L(im, sec_start(k_) - 0.1, sec_end(k_) + 0.2, (125, 900), "left", "fade", 0.5, 0.3, z=6, name=f"chip {k_}")
    # PiP pembentang sepanjang H (naratif)
    P.pips.append({"t0": h0 - 0.2, "t1": h1 + 0.3, "label": None, "size": (512, 288), "pos": (1920 - 512 - 22, 1080 - 288 - 14)})
    spk = {"H1": ALIFF_, "H2": AMIN_, "H3": IMAN_, "H4": AMIN_, "H5": AMIN_, "H6": AMIN_}
    for k_, (nm, rl) in spk.items():
        f = F("mb", 20)
        nm_s = nm.split(" bin ")[0]
        pl = pill(nm_s, f, fg=WHITE, bg=(20, 20, 30))
        L(pl, sec_start(k_) + 0.2, sec_end(k_), (1920 - 512 - 22 + 10, 1080 - 288 - 14 + 10), "fade", "fade", 0.4, 0.3, z=22, name=f"pip nama {k_}")

    def beats(sec, plan):
        """plan: senarai (frasa_penambat, shots, cam, extra) ; segmen berakhir pada penambat seterusnya."""
        times = []
        for anc, shots, cam in plan:
            if isinstance(anc, (int, float)):
                times.append(anc)
            else:
                times.append(A(anc, sec) if anc else sec_start(sec))
        times = [t if t is not None else None for t in times]
        for i, (anc, shots, cam) in enumerate(plan):
            t0 = times[i]
            t1 = times[i + 1] if i + 1 < len(plan) else sec_end(sec) + (0.0 if i + 1 < len(plan) else 0.0)
            if t0 is None or t1 is None:
                print("  !! beat tiada penambat", sec, anc); continue
            P.gshots(t0, t1, shots, f"{sec}#{i}", cam=cam)
        return times

    # gap sebelum/selepas: isi gameplay juga
    def gapfill(tag, shots, i=0, cam=None, label=""):
        gg = gaps_by[tag][i]
        P.gshots(gg["t0"], gg["t1"], shots, label or tag, cam=cam, pip=False)

    # H1 – Lobi & galeri
    tb = beats("H1", [
        (None, [(14.0, 22.0, "k"), (33.0, 41.0, "k")], {"zoom": (1.0, 1.06)}),
        ("Apabila murid mendekati watak", [(41.0, 67.0, "t")], {}),
        ("Poster di dinding sebelah utara", [(88.0, 100.0, "k")], {"zoom": (1.0, 1.12)}),
        ("Dan Jenis yang kedua", [(100.5, 108.0, "k")], {"zoom": (1.0, 1.12)}),
        ("Dan akhir sekali Jenis ketiga", [(108.0, 117.0, "k")], {"zoom": (1.0, 1.12)}),
        ("kiri dan kanan pula", [(67.0, 76.0, "t")], {}),
        ("Contohnya, kapsyen kepada yang berminat", [(76.0, 86.0, "k")], {"zoom": (1.15, 1.4), "center": (960, 520)}),
        ("Galeri ini penting", [(121.0, 133.0, "t")], {}),
    ])
    k = keypoint_card("GALERI ISU", "Telefon: [R:MEDIA SOSIAL] → [Y:>> ISU <<] → [G:AYAT BETUL]", "Kapsyen sebenar daripada bukti media sosial.", accent=PURPLE, w=700)
    tgal = A("kiri dan kanan pula", "H1")
    card(k, (tgal or 0) + 1.5, A("Galeri ini penting", "H1"), (140, 60), "left", name="galeri kad")
    # H2 – mod & markah
    gapfill("h-mid", [(130.0, 135.0, "t")], 0)
    beats("H2", [
        (None, [(134.0, 158.0, "t")], {}),
        ("Untuk bermain secara berkumpulan", [(158.0, 170.0, "k")], {"zoom": (1.0, 1.1)}),
        ("Sebelum bermula", [(170.0, 176.0, "t")], {}),
        ("Sistem markahnya mudah", [(116.5, 125.0, "k")], {"zoom": (1.25, 1.3), "center": (700, 520)}),
    ])
    tm = A("Murid boleh memilih", "H2")
    if tm:
        c1 = chip("GERBANG HIJAU • MAIN INDIVIDU • blok zamrud", (46, 160, 70), 28)
        c2 = chip("GERBANG UNGU • MAIN BERKUMPULAN • bulu warna", PURPLE, 28)
        card(c1, A("Untuk bermain secara individu", "H2") or tm + 2, A("Sebelum bermula", "H2"), (140, 70), "left", name="mod individu")
        card(c2, A("Untuk bermain secara berkumpulan", "H2") or tm + 5, A("Sebelum bermula", "H2"), (140, 170), "left", name="mod kumpulan")
        tsk = A("Sistem markahnya mudah", "H2")
        if tsk:
            s1 = score_pop("+100", "BETUL!")
            s2 = score_pop("−50", "SALAH!", RED)
            card(s1, A("diberi tambahan", "H2") or tsk + 1.5, sec_end("H2"), (260, 220), "pop", name="+100 sistem", snd="sfx_success", sg=0.2)
            card(s2, A("ditolak 50 markah", "H2") or tsk + 4, sec_end("H2"), (1060, 220), "pop", name="-50 sistem", snd="sfx_fail", sg=0.2)
            k = keypoint_card("PERATURAN", "[Y:5 betul] → naik ke jenis seterusnya", "Setiap jenis mempunyai [Y:10 soalan].", accent=GOLD, w=900)
            card(k, A("Murid perlu menjawab 5 soalan", "H2") or tsk + 7, sec_end("H2"), center_pos(k, 540), "up", name="peraturan")
    # H3 – Misi 1
    gapfill("h-mid", [(172.0, 176.0, "k")], 1)
    beats("H3", [
        (None, [(176.0, 192.0, "k")], {}),
        ("Papan ini mengingatkan", [(192.0, 203.0, "t")], {"zoom": (1.15, 1.15), "center": (960, 480)}),
        ("Masa membaca ini sengaja", [(203.0, 206.0, "t")], {}),
        ("Soalan pertama", [(206.0, 224.0, "k")], {"zoom": (1.0, 1.1), "center": (960, 450)}),
        ("Murid menjawab dengan memijak", [(224.0, 236.6, "t")], {}),
        ("Jawapan betul", [(239.0, 246.0, "k")], {"punch": [(0.3, 4.0, 1.35, (960, 420))]}),
        ("Sekarang, saya tunjukkan", [(246.0, 260.0, "k")], {}),
        ("Saya sengaja memilih murid", [(626.5, 634.0, "k")], {"punch": [(0.4, 4.5, 1.3, (960, 420))]}),
        ("Melalui cara ini", [(272.0, 312.0, "t")], {}),
    ])
    tj = A("Jawapan betul", "H3")
    if tj:
        sp = score_pop("+100", "BETUL!")
        L(sp, tj + 0.3, tj + 3.2, (1370, 70), "pop", "fade", 0.5, 0.4, z=20, name="H3 +100")
        L(None, tj + 0.2, tj + 3.0, (0, 0), "fade", "fade", 0.2, 0.5, z=19, dyn=lambda lt, d: confetti(lt, d, 90, 7, True), name="H3 confetti")
        S(tj + 0.3, "sfx_success", 0.5)
    ts_ = A("Saya sengaja memilih murid", "H3")
    if ts_:
        lb = pill("Contoh paparan jawapan SALAH – rakaman sebenar (Misi 2)", F("mb", 24), fg=WHITE, bg=(150, 30, 30))
        L(lb, ts_ + 0.1, ts_ + 7.2, (140, 60), "left", "fade", 0.4, 0.3, z=20, name="label salah")
        sp = score_pop("−50", "SALAH!", RED)
        L(sp, ts_ + 2.0, ts_ + 5.5, (1370, 70), "pop", "fade", 0.5, 0.4, z=20, name="H3 -50")
        S(ts_ + 2.0, "sfx_fail", 0.45)
        k = keypoint_card("MAKLUM BALAS SEGERA", "Murid tahu [R:mengapa] jawapannya salah", "Jawapan betul (“[G:Bagi]”) & sebabnya dipaparkan.", accent=RED, w=760)
        card(k, A("Dan permainan terus", "H3") or ts_ + 5, A("Melalui cara ini", "H3"), (140, 60), "left", name="maklum balas")
    # peralihan Misi 1 → 2
    gg = g("m1-done")
    P.gshots(gg["t0"], gg["t1"], [(372.0, 384.0, "t")], "M1 selesai", cam={"zoom": (1.0, 1.15)}, pip=False)
    mb = mission_banner("MISI 1 SELESAI ✓", "AYAT TIDAK LENGKAP", GOLD, done=True)
    L(mb, gg["t0"] + 0.2, gg["t1"] + 0.6, center_pos(mb, 330), "scale", "fade", 0.5, 0.4, z=25, name="banner M2")
    nx = pill("MISI SETERUSNYA ↓", F("mb", 28), fg=INK, bg=GOLD)
    L(nx, gg["t0"] + 0.6, gg["t1"] + 0.6, center_pos(nx, 270), "down", "fade", 0.4, 0.4, z=26, name="seterusnya")
    S(gg["t0"], "sfx_whoosh", 0.4); S(gg["t0"] + 0.3, "sfx_success", 0.3)
    # H4 – Misi 2
    beats("H4", [
        (None, [(385.0, 409.0, "t")], {}),
        ("Soalan pertama", [(409.0, 424.0, "k")], {"zoom": (1.0, 1.1), "center": (960, 450)}),
        ("Murid perlu membuka peti satu", [(424.0, 444.0, "t")], {}),
        ("Saya ambil", [(444.0, 455.0, "k"), (455.0, 470.0, "t")], {"punch": [(0.5, 6.0, 1.3, (960, 520))]}),
        ("Jawapan terus disemak", [(476.0, 484.0, "k")], {"punch": [(0.8, 4.0, 1.3, (960, 420))]}),
        ("Perhatikan bahawa peti juga", [(553.0, 562.0, "k"), (593.0, 606.0, "k")], {"punch": [(0.5, 8.0, 1.35, (960, 520))]}),
        ("Jika murid tersalah susun", [(633.0, 652.0, "t")], {}),
    ])
    tj = A("Jawapan terus disemak", "H4")
    if tj:
        sp = score_pop("+100", "BETUL!")
        L(sp, tj + 1.2, tj + 4.0, (1370, 70), "pop", "fade", 0.5, 0.4, z=20, name="H4 +100")
        S(tj + 1.2, "sfx_success", 0.5)
        fr = formula_row([block("Rumah Ali yang besar itu", "SUBJEK", BLUE, w=620, h=130, tsize=38), "+",
                          block("terletak di hujung kampung.", "PREDIKAT", (46, 160, 70), w=640, h=130, tsize=38)], op_size=50)
        card(fr, tj + 4.0, A("Perhatikan bahawa peti juga", "H4") or tj + 9, center_pos(fr, 90), "scale", name="Rumah Ali S+P")
    tq = A("Soalan pertama", "H4")
    if tq:
        b = sentence_box("salah", "Rumah Ali yang besar di hujung kampung itu. [R:(tiada predikat)]", w=1100, label="Soalan 1 • Misi 2", size=34)
        card(b, tq + 4.0, A("Murid perlu membuka peti satu", "H4"), center_pos(b, 70), "down", name="soalan rumah ali")
    tp_ = A("Perhatikan bahawa peti juga", "H4")
    if tp_:
        c1 = chip("PENGECOH: “Kerana rumah Ali”", RED, 30)
        c2 = chip("PENGECOH: “yang di hujung kampung”", RED, 30)
        card(c1, tp_ + 1.5, A("Jika murid tersalah susun", "H4"), (140, 70), "left", name="pengecoh1")
        card(c2, tp_ + 2.3, A("Jika murid tersalah susun", "H4"), (140, 170), "left", name="pengecoh2")
        tss = A("Jika murid tersalah susun", "H4")
        cs = chip("BLOK SET SEMULA (obsidian menangis)", PURPLE, 30)
        card(cs, tss, sec_end("H4"), (140, 70), "left", name="set semula")
    # peralihan Misi 2 → 3
    gg = g("m2-done")
    P.gshots(gg["t0"], gg["t1"], [(735.0, 745.0, "t")], "M2 selesai", cam={"zoom": (1.15, 1.0)}, pip=False)
    mb = mission_banner("MISI 2 SELESAI ✓", "MISI 3: BAHASA ROJAK", PURPLE, done=True)
    L(mb, gg["t0"] + 0.2, gg["t1"] + 0.6, center_pos(mb, 330), "scale", "fade", 0.5, 0.4, z=25, name="banner M3")
    S(gg["t0"], "sfx_whoosh", 0.4); S(gg["t0"] + 0.3, "sfx_success", 0.3)
    # H5 – Misi 3
    beats("H5", [
        (None, [(745.0, 774.0, "t")], {}),
        ("Soalan pertama ialah", [(774.0, 788.0, "k")], {"zoom": (1.0, 1.1), "center": (960, 450)}),
        ("Saya melompat ke platform A", [(812.4, 817.0, "k")], {}),
        ("Jawapan betul", [(817.0, 823.0, "k")], {"punch": [(0.2, 3.0, 1.3, (960, 420))]}),
        ("Jika murid jatuh ke dalam air", [(818.2, 821.0, "k"), (821.0, 905.0, "t")], {}),
    ])
    t1q = A("Soalan pertama ialah", "H5")
    if t1q:
        b = sentence_box("salah", "Saya sangat [r:happy] kerana dapat hadiah.", w=1000, label="Soalan 1 • Misi 3", size=36)
        card(b, t1q + 0.3, A("Saya melompat ke platform A", "H5"), center_pos(b, 70), "down", name="soalan happy")
    tj = A("Jawapan betul", "H5")
    if tj:
        sp = score_pop("+100", "BETUL!")
        L(sp, tj, tj + 3.0, (1370, 70), "pop", "fade", 0.5, 0.4, z=20, name="H5 +100")
        S(tj, "sfx_success", 0.5)
    tw_ = A("Jika murid jatuh ke dalam air", "H5")
    if tw_:
        for i, (en, bm) in enumerate([("HAPPY", "GEMBIRA"), ("STUDY", "BELAJAR"), ("BUSY", "SIBUK")]):
            row = formula_row([chip(en, RED, 40), "→", chip(bm, (46, 160, 70), 40)], op_size=50)
            t0_ = tw_ + 1.0 + i * 4.5
            L(row, t0_, t0_ + 4.3, (140, 70), "left", "fade", 0.4, 0.3, z=20, name=f"swap {en}")
            S(t0_, "sfx_pop", 0.25)
        b2 = sentence_box("betul", "Mari kita [g:belajar] bersama di perpustakaan.", w=1000, label="Jawapan Soalan 2", size=34)
        card(b2, tw_ + 5.5, tw_ + 9.8, center_pos(b2, 680), "up", name="belajar betul")
    # H6 – keputusan
    gapfill("h-mid", [(985.0, 991.5, "t")], 2)
    beats("H6", [
        (None, [(991.5, 1000.0, "k")], {"zoom": (1.0, 1.08)}),
        ("Keputusan murid dipaparkan", [(1000.0, 1016.0, "k")], {"punch": [(0.5, 8.0, 1.6, (520, 300))]}),
        ("Murid yang membuat kesalahan", [(1016.0, 1040.0, "t")], {}),
        ("Papan kedudukan memaparkan", [(1040.0, 1052.0, "k")], {}),
        ("Dunia ini juga mesra guru", [(1193.0, 1212.0, "k")], {}),
        ("Di sudut guru", [(1062.0, 1100.0, "t")], {}),
    ])
    tt = sec_start("H6")
    L(None, tt + 0.6, tt + 6.5, (0, 0), "fade", "fade", 0.2, 0.8, z=19, dyn=lambda lt, d: confetti(lt, d, 200, 21), name="H6 confetti")
    L(None, tt + 0.6, tt + 8.0, (0, 0), "fade", "fade", 0.3, 0.8, z=19, dyn=lambda lt, d: sparkles(lt, d, 70, 9), name="H6 sparkle")
    S(tt + 0.6, "sfx_achievement", 0.7)
    gl = big_word("PENYELAMAT AYAT!", GOLD, 96, "mk", stroke=6, stroke_fill=INK)
    L(gl, tt + 1.0, tt + 6.0, center_pos(gl, 150), "pop", "fade", 0.6, 0.5, z=21, name="gelaran")
    tm = A("Murid yang membuat kesalahan", "H6")
    if tm:
        meds = medal_row()
        for i, m in enumerate(meds):
            tk = [tm, A("Murid yang membuat kesalahan", "H6", nth=2) or tm + 6, A("selebihnya", "H6") or tm + 12][i]
            L(m, tk, A("Papan kedudukan memaparkan", "H6") or tm + 18, (260 + i * 470, 220), "pop", "fade", 0.5, 0.4, z=20, name=f"pingat {i}")
            S(tk, "sfx_success", 0.25)
    tp_ = A("Papan kedudukan memaparkan", "H6")
    if tp_:
        c = chip("PAPAN KEDUDUKAN • 15 pemain teratas", GOLD, 30, fg=INK)
        card(c, tp_, tp_ + 5, (140, 70), "left", name="papan kedudukan")
        c2 = chip("LODESTONE → majlis penyampaian juara", PURPLE, 30)
        card(c2, A("apabila guru memijak", "H6") or tp_ + 3, A("Dunia ini juga mesra guru", "H6"), (140, 170), "left", name="lodestone")
    tg = A("Dunia ini juga mesra guru", "H6")
    if tg:
        c1 = chip("BLOK BESI → keluar, progres disimpan", (120, 130, 145), 30)
        c2 = chip("GLOWSTONE → sambung misi", GOLD, 30, fg=INK)
        card(c1, A("blok besi", "H6") or tg + 2, A("Di sudut guru", "H6"), (140, 70), "left", name="besi")
        card(c2, A("Pada sesi seterusnya", "H6") or tg + 5, A("Di sudut guru", "H6"), (140, 170), "left", name="glowstone")
    tsg = A("Di sudut guru", "H6")
    if tsg:
        tp2 = teacher_panel()
        card(tp2, tsg, sec_end("H6") + 0.3, (150, 70), "scale", name="sudut guru", snd="sfx_whoosh", sg=0.25)
        nt = pill("Paparan fungsi – tiada data murid dipaparkan", F("is", 20), fg=(220, 220, 230), bg=(30, 30, 50))
        L(nt, tsg + 1, sec_end("H6"), (160, 630), "fade", "fade", 0.4, 0.3, z=21, name="nota sudut guru")

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
            ic_ = icon_card(i + 1, tt_, bd, ic, c, w=1060, h=250)
            L(ic_, ti[i], sec_end("I"), (50, 80 + i * 270), "left", "fade", 0.55, 0.4, z=12, name=f"cadangan {i + 1}")
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
    for i, (nm, bd, c, ic) in enumerate(nodes):
        t0_ = tj[i] or sec_start("J") + 2 + 9 * i
        hn = harapan_node(nm, bd, c, w=340)
        L(hn, t0_, sec_end("J") + 0.2, (40 + i * 375, 300), "up", "fade", 0.6, 0.4, z=12, name=f"harapan {nm}")
        L(icon(ic, 110, c), t0_ + 0.2, sec_end("J") + 0.2, (40 + i * 375 + 115, 160), "pop", "fade", 0.5, 0.4, z=12, name=f"ikon {nm}")
        S(t0_, "sfx_pop", 0.22)
    tbd = A("kerana bahasa yang betul", "J")
    if tbd:
        bn = keypoint_card("BERSAMA", "[Y:Bahasa betul] tetap menarik & dekat dengan khalayak", None, accent=GOLD, w=1080)
        L(bn, tbd, sec_end("J") + 0.2, (40, 690), "up", "fade", 0.5, 0.3, z=13, name="gabung harapan")

    # =================================================================
    # K – PENUTUP & OUTRO
    # =================================================================
    chipsec("K", "K", "PENUTUP")
    tk = A("Kesimpulannya", "K")
    if tk:
        P.set_mode(tk - 0.2, A("Sekali lagi", "K") or tk + 10, "split")
        k = keypoint_card("KESIMPULAN", "Kerancuan sintaksis [R:bukan isu kecil]", "Ia merosakkan asas ayat – hubungan [B:subjek] dengan [G:predikat].", accent=GOLD, w=1060)
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
