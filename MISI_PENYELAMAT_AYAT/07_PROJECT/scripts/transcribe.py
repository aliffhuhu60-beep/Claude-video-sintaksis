import sys, json
from faster_whisper import WhisperModel
src, out, model = sys.argv[1], sys.argv[2], sys.argv[3]
import wave, numpy as np
wf=wave.open(src); audio=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=4)
segs, info = m.transcribe(audio, language="ms", word_timestamps=True, vad_filter=True,
    initial_prompt="Kerancuan bahasa, sintaksis, subjek, predikat, Minecraft Education, Misi Penyelamat Ayat, Dr. Siti Dahlia binti Abdullah.")
res = []
for s in segs:
    res.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"s": w.start, "e": w.end, "w": w.word} for w in (s.words or [])]})
    print(f"[{s.start:8.2f}-{s.end:8.2f}] {s.text.strip()}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
