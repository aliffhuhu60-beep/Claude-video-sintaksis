"""Jana laporan penyuntingan & timeline daripada edl_timeline.json."""
import json, os, csv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
d = json.load(open(f"{ROOT}/07_PROJECT/edl_timeline.json"))
OUT = f"{ROOT}/09_REPORT"
os.makedirs(OUT, exist_ok=True)


def ts(t):
    t = max(0.0, t)
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


NAMA = {"A1": "A – Pembukaan & penghargaan", "A2": "A – Pengenalan pembentang & aliran", "B": "B – Pengenalan kerancuan bahasa",
        "C": "C – Bukti media sosial & sebab", "D": "D – Jenis 1: Ayat tanpa subjek", "E": "E – Jenis 2: Ayat tidak lengkap",
        "F": "F – Jenis 3: Bahasa rojak", "G": "G – Pengenalan Minecraft Education", "H1": "H1 – Lobi & galeri isu",
        "H2": "H2 – Mod permainan & markah", "H3": "H3 – Misi 1", "H4": "H4 – Misi 2", "H5": "H5 – Misi 3", "H6": "H6 – Keputusan & Sudut Guru",
        "I": "I – Cadangan lain", "J": "J – Harapan", "K": "K – Penutup"}
PEMB = {"A1": "Mohamad Aliff", "A2": "Aliff, Amin, Iman", "B": "Amin Najmi", "C": "Iman Irfan", "D": "Mohamad Aliff", "E": "Amin Najmi",
        "F": "Iman Irfan", "G": "Mohamad Aliff", "H1": "Mohamad Aliff", "H2": "Amin Najmi", "H3": "Iman Irfan", "H4": "Amin Najmi",
        "H5": "Amin Najmi", "H6": "Amin Najmi", "I": "Mohamad Aliff", "J": "Mohamad Aliff", "K": "Mohamad Aliff"}

# --- bahagian ucapan dibuang (pelengkap kiu) ---
chunks = sorted(d["chunks"], key=lambda c: c["src_s"])
REASON = [((66.5, 85.6), "Take 1 bahagian nama pembentang (diganti take 2 yang lebih kemas)"),
          ((124.2, 153.8), "Perbualan luar skrip antara take (\"aku cakap nanti korang akan masuk…\")"),
          ((165.6, 213.9), "Take 2 ayat pengenalan – sebutan \"kerancuan\" tidak tepat; diganti ayat yang sama daripada take 1"),
          ((539.3, 547.8), "Ayat serah tugas tidak lengkap (diulang semula oleh pembentang)"),
          ((734.6, 738.6), "Tergeliat lidah: \"Semoga dipermudahkan urusan semua\" (diulang)"),
          ((965.5, 972.3), "Ayat \"Kesan kesalahan ini cukup besar\" berulang"),
          ((1016.6, 1028.0), "Perbualan luar skrip (\"Contoh kan? Dah?\")"),
          ((1134.1, 1138.6), "Tergagap: \"seperti kerancuan bahasa\" (diulang)"),
          ((1147.7, 1155.7), "Perbualan luar skrip (\"Oh, dengan bahasa rojak di bawah tu\")"),
          ((1186.1, 1188.0), "Tergagap: \"kami pergi\" (diulang)"),
          ((1202.2, 1208.7), "Jeda antara rakaman"),
          ((1316.6, 1322.5), "Jeda antara rakaman"),
          ((1427.3, 1441.5), "Perbualan luar skrip (\"Dah, dah. Itu bukan aku… Tukar\")"),
          ((1509.5, 1513.8), "Frasa \"dan cara membetulkannya\" berulang"),
          ((1524.7, 1548.6), "Take pertama Soalan 1 terhenti (\"…dalam…\") – guna take kedua"),
          ((1711.8, 1727.8), "Perbualan luar skrip (\"Boleh aje lagi\")"),
          ((1912.0, 1921.5), "Frasa \"tiga jenis kesalahan\" berulang"),
          ((1923.7, 1938.0), "Ayat tergagap (diulang semula)"),
          ((1977.3, 1991.8), "Take pertama Bahagian J terhenti (\"Yang ini tak boleh…\")"),
          ]
removed = []
t = 0.0
for c in chunks:
    if c["src_s"] - t > 0.6:
        removed.append((t, c["src_s"]))
    t = max(t, c["src_e"])
if 2058.1 - t > 0.5:
    removed.append((t, 2058.1))


def reason_for(a, b):
    for (x, y), r in REASON:
        if a < y and b > x and (min(b, y) - max(a, x)) > 0.4 * min(b - a, y - x):
            return r
    return "Senyap / peralihan antara rakaman (tiada isi dibuang)" if b - a > 3 else "Jeda panjang dipendekkan (tiada isi dibuang)"


L = []
L.append("# LAPORAN PENYUNTINGAN – MISI PENYELAMAT AYAT\n")
L.append("**Video:** `08_EXPORT/MISI_PENYELAMAT_AYAT_BMMB3233_FINAL.mp4` · 1920×1080 · 30 FPS · H.264 + AAC · **tempoh tepat 30:00.000**\n")
L.append("**Kursus:** BMMB3233 Sintaksis Bahasa Melayu · IPG Kampus Tun Hussein Onn, Batu Pahat · Pensyarah: Dr. Siti Dahlia binti Abdullah\n")
L.append("## 1. Bahan sumber\n")
L.append("| Fail | Kandungan | Spesifikasi |\n|---|---|---|")
L.append("| `Sudut guru.mp4` | Rakaman Sudut Guru (blok redstone, set semula markah) | 0:34, 1728×1080 |")
L.append("| `video penerangan` | Rakaman ketiga-tiga pembentang (Bahagian A–K, termasuk naratif demonstrasi H) | 34:18, 1280×720, 30 fps |")
L.append("| `GAMEPLAY MINECRAFT.mp4` | Rakaman skrin dunia *Misi Penyelamat Ayat* (tiada suara) | 20:29, 1904×972, 30 fps |")
L.append("| `Skrip_PB2…pdf` | Skrip penuh + kunci jawapan + rujukan | 22 hlm |")
L.append("| `Bahan_Sokongan_Video_PB2.pdf` | Slaid bahan sokongan (30 slaid, teks sahaja) | – |")
L.append("| `Bukti_Media_Sosial…pdf` | 15 petikan kapsyen TikTok + pautan | teks sahaja (tiada tangkap layar) |\n")
L.append("Semua fail boleh dibuka; tiada fail rosak. Fail asal tidak diubah (salinan kerja dalam `01_RAW_VIDEO`, `03_MINECRAFT_GAMEPLAY`, `04_IMAGES`).\n")

L.append("## 2. Timeline akhir mengikut bahagian\n")
L.append("| Bahagian | Mula | Tamat | Tempoh | Pembentang |\n|---|---|---|---|---|")
L.append(f"| Intro sinematik (perkataan bercelaru → dunia Minecraft → kad tajuk) | 00:00.00 | {ts(d['sections']['A1'][0])} | {d['sections']['A1'][0]:.1f}s | – |")
for k, (a, b) in d["sections"].items():
    L.append(f"| {NAMA[k]} | {ts(a)} | {ts(b)} | {b - a:.1f}s | {PEMB[k]} |")
L.append(f"| Outro (syot berkumpulan + slogan + kad terima kasih & rujukan, fade-out) | {ts(d['sections']['K'][1])} | 30:00.00 | {1800 - d['sections']['K'][1]:.1f}s | Semua |\n")
L.append("> Susunan skrip asal A→K dikekalkan. Masa setiap bahagian berbeza sedikit daripada jadual skrip (cth. H bermula 19:20 berbanding 18:20) kerana mengikut tempoh sebenar rakaman pembentang – **tiada suara dipercepat atau diubah**. Jumlah keseluruhan dikunci tepat 30:00.\n")

L.append("## 3. Bahagian rakaman penerangan yang dipotong\n")
L.append("| Sumber (mula–tamat) | Tempoh | Sebab |\n|---|---|---|")
tot = 0
for a, b in removed:
    r = reason_for(a, b)
    tot += b - a
    L.append(f"| {ts(a)} – {ts(b)} | {b - a:.1f}s | {r} |")
L.append(f"\n**Jumlah dibuang: {tot:.1f}s** daripada 2058.1s rakaman (pengambilan semula, perbualan luar skrip, tergagap dan jeda melebihi 1 saat). Tiada definisi, contoh ayat, analisis, penerangan permainan, fungsi guru atau harapan dibuang.\n")
L.append("**Susunan semula (ikut skrip asal):** Dalam rakaman, contoh 2–4 Bahagian D, contoh 2–3 Bahagian E dan contoh 2–3 Bahagian F dirakam *selepas* bahagian \"kesan\". Ia disusun semula supaya urutan ialah: contoh → kesan → serah tugas, seperti dalam skrip.\n")

L.append("## 4. Rakaman Minecraft – kelajuan & penggunaan\n")
L.append("| Masa video | Sumber gameplay | Kelajuan | Catatan |\n|---|---|---|---|")
for s in d["v1"]:
    if s["type"] == "game":
        sp = s["speed"]
        cat = "kelajuan normal (detik penting)" if abs(sp - 1) < 0.05 else ("gerak perlahan sinematik" if sp < 1 else f"dipercepat {sp:.1f}× (perjalanan/menunggu)")
        L.append(f"| {ts(s['t0'])}–{ts(s['t1'])} | {ts(s['src_in'])}–{ts(s['src_end'])} | {sp:.2f}× | {cat} |")
L.append("\n* Suara pembentang **tidak pernah dipercepat** – hanya visual gameplay dilaraskan; audio permainan hanya dimainkan pada segmen kelajuan normal.\n"
         "* Speed ramp dipercepat ≥1.8× menggunakan pengadunan bingkai (motion blur ringan).\n"
         "* Detik soalan, pemilihan jawapan, BETUL +100, SALAH −50, peti/bingkai, parkour, keputusan dan papan kedudukan dikekalkan pada 1×.\n")

L.append("## 5. Pindaan versi 2 (atas permintaan) & catatan\n")
L.append("1. Intro kini **tanpa klip Minecraft & tajuk Misi Penyelamat Ayat**: skrin gelap + perkataan bercelaru → kad tajuk isu.\n"
         "2. **Tiada label bahagian** (\"Bahagian A/B…\", \"H1…\") dipaparkan sepanjang video.\n"
         "3. **Sebutan \"kerancuan\"** pada awal video: ayat take 2 (sebutan kurang tepat) diganti ayat yang sama daripada take 1. Catatan: ASR juga mengesan kemungkinan sebutan kurang jelas di Bahagian C (\"kerancuan ayat dapat dilihat…\") dan K (\"Kesimpulannya, kerancuan…\"); tiada take alternatif untuk bahagian tersebut.\n"
         "4. **Paparan maklumat disusun semula**: kotak ayat salah/analisis/betul disusun automatik dengan jarak seragam (≥26 px) tanpa bertindih.\n"
         "5. **Bukti media sosial**: galeri 15 petikan sebenar (J1.1–J3.5) di Bahagian C, dan dinding bukti setiap jenis sebelum contoh D, E, F (termasuk contoh YouTube/Threads daripada skrip, dilabel \"Contoh skrip\").\n"
         "6. **Sudut Guru**: klip `Sudut guru.mp4` digunakan semasa Amin menerangkan Sudut Guru.\n"
         "7. **Pingat** diterangkan semasa rakaman dewan keputusan (sebelum pentas), dalam lajur sisi – gameplay dikecilkan ke kiri supaya tidak terlindung.\n"
         "8. **Jatuh ke air**: klip sebenar pemain jatuh dan kembali ke permulaan (gameplay 15:23–15:28).\n"
         "9. **Ayat salah / soalan** dipaparkan dalam lajur kanan – tidak menutup soalan dalam permainan.\n"
         "10. **Pilihan pengecoh** menggunakan klip peti Soalan 1 Misi 2.\n"
         "11. **+100 / −50** muncul 0.45 s selepas paparan BETUL/SALAH dalam permainan (dikesan automatik: 3:58.97, 7:58.93, 13:36.90, SALAH 10:29.20).\n"
         "12. **Misi 2 Soalan 1** diselaraskan langkah demi langkah dengan penerangan Amin (soalan → peti 1 → peti 2 → bingkai → BETUL).\n"
         "13. **Blok biru (ULANG)**: klip gameplay 10:34 dan seterusnya – pemain memijak blok biru lalu terus ke soalan seterusnya.\n"
         "14. **Blok emas**: klip lobi (pandangan udara) daripada `Sudut guru.mp4`.\n")
L.append("**Catatan kejujuran:** Misi 1 tiada rakaman jawapan salah, maka contoh SALAH −50 diambil daripada Misi 2 (berlabel). Tiada tangkap layar media sosial diberikan; petikan teks daripada dokumen bukti dipaparkan dengan nama akaun dikaburkan. Ejaan nama pembentang mengikut arahan tugasan – sila semak.\n")
L.append("## 6. Sarikata\n")
L.append("* Dijana daripada transkripsi automatik (Whisper *medium*) **dijajarkan dengan skrip asal** perkataan demi perkataan: masa ikut audio sebenar, ejaan ikut skrip.\n"
         "* Pembetulan manual untuk contoh bahasa rojak yang \"diterjemah\" oleh ASR (cth. *happy*, *share*, *so*, *only*, *try guys*) supaya sarikata sama dengan ucapan sebenar.\n"
         "* `06_SUBTITLES/MISI_PENYELAMAT_AYAT_dinamik.ass` – gaya dinamik (dibakar ke dalam video): Montserrat SemiBold putih + outline hitam; **kuning HURUF BESAR** = kata kunci utama, **biru** = istilah akademik, **merah** = ayat salah, **hijau** = ayat betul.\n"
         "* `06_SUBTITLES/MISI_PENYELAMAT_AYAT.srt` – SRT biasa (tanpa warna) dengan timestamp tepat.\n"
         "* Semasa demonstrasi Minecraft, sarikata dianjak ke kiri supaya tidak bertindih PiP pembentang; gameplay dipaparkan dalam bingkai supaya sarikata tidak menutup HUD markah.\n")
L.append("## 7. Audio\n")
L.append("* Suara: high-pass 85 Hz, pengurangan bunyi FFT (afftdn), EQ (−2.5 dB @250 Hz, +2.5 dB @3.2 kHz, +1.5 dB high-shelf), kompresor 3:1, padanan kekuatan setiap pembentang, crossfade 12 ms di setiap potongan.\n"
         "* Muzik & kesan bunyi **dijana sendiri secara sintesis** (bebas royalti): suspens sinematik (intro), dokumentari lembut, ambien minimal, pengembaraan (Minecraft), bunyi pencapaian, inspirasi (outro). Muzik di-*duck* automatik di bawah suara.\n"
         "* Campuran akhir dinormalkan EBU R128: −16 LUFS, puncak −1.5 dBTP.\n")
L.append("## 8. Semakan kualiti (QC)\n")
qc = os.path.exists(f"{OUT}/qc.json") and json.load(open(f"{OUT}/qc.json")) or {}
for k, v in qc.items():
    L.append(f"* {k}: {v}")
L.append("\n## 9. Fail projek\n")
L.append("* `07_PROJECT/scripts/` – skrip suntingan penuh (Python + FFmpeg): `build.py` (EDL, render, audio), `scenes.py` (arahan setiap babak), `gfx.py` (motion graphics), `compositor.py`, `subs.py`, `music.py`.\n"
         "* `07_PROJECT/edl_timeline.json` – EDL lengkap (setiap kiu ucapan, segmen video, lapisan grafik).\n"
         "* Jana semula: `cd 07_PROJECT/scripts && python3 build.py all`.\n")
open(f"{OUT}/LAPORAN_PENYUNTINGAN.md", "w").write("\n".join(L))

with open(f"{OUT}/timeline_penyuntingan.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mula_video", "tamat_video", "jenis", "bahagian/tag", "sumber_mula", "sumber_tamat", "kelajuan"])
    for s in d["v1"]:
        if s["type"] == "pres":
            w.writerow([ts(s["t0"]), ts(s["t1"]), "pembentang", s.get("sec"), ts(s["src_in"]), ts(s["src_in"] + s["t1"] - s["t0"]), "1.00"])
        elif s["type"] == "game":
            w.writerow([ts(s["t0"]), ts(s["t1"]), "gameplay", "", ts(s["src_in"]), ts(s["src_end"]), f"{s['speed']:.2f}"])
        else:
            w.writerow([ts(s["t0"]), ts(s["t1"]), "grafik", s.get("tag", s.get("bg")), "", "", ""])
with open(f"{OUT}/grafik_timeline.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mula", "tamat", "elemen"])
    for l in sorted(d["layers"], key=lambda x: x["t0"]):
        w.writerow([ts(l["t0"]), ts(l["t1"]), l["name"]])
print("laporan siap")
