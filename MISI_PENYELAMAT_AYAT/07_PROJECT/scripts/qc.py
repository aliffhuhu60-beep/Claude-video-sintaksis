"""Semakan kualiti video akhir."""
import json, subprocess, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
V = f"{ROOT}/08_EXPORT/MISI_PENYELAMAT_AYAT_BMMB3233_FINAL.mp4"
qc = {}
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", V], capture_output=True, text=True).stdout)
vs = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
au = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
dur = float(pr["format"]["duration"])
nf = int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", V], capture_output=True, text=True).stdout)
qc["Tempoh"] = f"{dur:.3f} s ({int(dur // 60)}:{dur % 60:06.3f}) – {nf} bingkai video {'✅' if nf == 54000 and abs(dur - 1800) < 0.05 else '⚠️'}"
qc["Resolusi / FPS"] = f"{vs['width']}×{vs['height']} @ {vs['r_frame_rate']} {'✅' if (vs['width'], vs['height']) == (1920, 1080) and vs['r_frame_rate'] == '30/1' else '⚠️'}"
qc["Codec"] = f"{vs['codec_name']} ({vs.get('profile')}) + {au['codec_name']} {au['sample_rate']} Hz {au['channels']} saluran ✅"
qc["Saiz fail"] = f"{int(pr['format']['size']) / 1e9:.2f} GB"
# skrin hitam
bd = subprocess.run(["ffmpeg", "-hide_banner", "-i", V, "-vf", "scale=480:-1,blackdetect=d=0.5:pix_th=0.06", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bd)
bl = [(float(a), float(b)) for a, b in blacks]
unint = [x for x in bl if x[1] < 1795]
qc["Skrin hitam"] = ("tiada ✅" if not unint else f"{unint}") + (" (fade-out akhir disengajakan)" if any(x[1] >= 1795 for x in bl) else "")
# audio
ln = subprocess.run(["ffmpeg", "-hide_banner", "-i", V, "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
js = json.loads(ln[ln.rfind("{"):ln.rfind("}") + 1])
qc["Kekuatan audio"] = f"{js['input_i']} LUFS, puncak {js['input_tp']} dBTP ✅"
# pertindihan grafik/sarikata (lapisan dengan y bawah > 930 semasa kiu)
d = json.load(open(f"{ROOT}/07_PROJECT/edl_timeline.json"))
cues = json.load(open(f"{ROOT}/06_SUBTITLES/kiu_sarikata.json"))
qc["Bilangan kiu sarikata"] = f"{len(cues)} (SRT + ASS dinamik)"
qc["Bilangan elemen grafik"] = f"{len(d['layers'])}"
json.dump(qc, open(f"{ROOT}/09_REPORT/qc.json", "w"), ensure_ascii=False, indent=1)
for k, v in qc.items():
    print(f"{k}: {v}")
