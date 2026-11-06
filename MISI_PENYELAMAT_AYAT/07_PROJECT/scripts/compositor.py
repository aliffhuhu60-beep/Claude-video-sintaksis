"""Compositor bingkai demi bingkai: kamera/susun atur + lapisan grafik beranimasi.
Membaca V1 (1920x1080) dan V2 (PiP 640x360) sebagai rawvideo daripada ffmpeg, menulis ke pengekod akhir."""
import subprocess, math, bisect
import numpy as np, cv2
from PIL import Image
import gfx

W, H, FPS = 1920, 1080, 30
PW, PH = 640, 360


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class Layer:
    """Elemen grafik. img: PIL RGBA atau fungsi f(t_local)->PIL. pos: (x,y) kiri-atas.
    anim_in: fade|left|right|up|down|scale|pop|wipe ; anim_out: fade|left|right|down|scale"""

    def __init__(self, img, t0, t1, pos=(0, 0), anim_in="fade", anim_out="fade", din=0.5, dout=0.4, z=10,
                 dynamic=None, name=""):
        self.img = img
        self.t0, self.t1 = t0, t1
        self.pos = pos
        self.ain, self.aout = anim_in, anim_out
        self.din, self.dout = din, dout
        self.z = z
        self.dynamic = dynamic
        self.name = name
        self._arr = None
        self._scaled = {}

    def arr(self):
        if self._arr is None:
            a = np.asarray(self.img.convert("RGBA"), dtype=np.float32)
            rgb = a[..., :3]
            al = a[..., 3:4] / 255.0
            self._arr = (rgb * al, al)
        return self._arr

    def scaled(self, s):
        k = round(s, 2)
        if k not in self._scaled:
            pm, al = self.arr()
            h, w = al.shape[:2]
            nw, nh = max(1, int(w * k)), max(1, int(h * k))
            self._scaled[k] = (cv2.resize(pm, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR),
                               cv2.resize(al, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)[..., None])
            if len(self._scaled) > 40:
                self._scaled.pop(next(iter(self._scaled)))
        return self._scaled[k]


def blend(frame, pm, al, x, y, opacity=1.0):
    h, w = al.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0 or opacity <= 0.003:
        return
    sx, sy = x0 - x, y0 - y
    p = pm[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
    a = al[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
    if opacity < 1:
        p = p * opacity; a = a * opacity
    reg = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = (p + reg * (1 - a)).astype(np.uint8)


def draw_layer(frame, L, t):
    lt = t - L.t0
    if L.dynamic is not None:
        img = L.dynamic(lt, L.t1 - L.t0)
        if img is None:
            return
        if isinstance(img, np.ndarray):
            # dynamic boleh pulangkan (pm, al, x, y, opacity)
            return
        a = np.asarray(img, dtype=np.float32)
        al = a[..., 3:4] / 255.0
        pm = a[..., :3] * al
    else:
        pm = al = None
    pin = ease(lt / L.din) if L.din > 0 else 1.0
    pout = ease((L.t1 - t) / L.dout) if L.dout > 0 else 1.0
    op = 1.0
    dx = dy = 0
    s = 1.0
    x, y = L.pos
    if pin < 1:
        if L.ain in ("fade", "wipe"):
            op *= pin
        elif L.ain == "left":
            dx -= int((1 - pin) * 120); op *= pin
        elif L.ain == "right":
            dx += int((1 - pin) * 120); op *= pin
        elif L.ain == "up":
            dy += int((1 - pin) * 80); op *= pin
        elif L.ain == "down":
            dy -= int((1 - pin) * 80); op *= pin
        elif L.ain == "scale":
            s = 0.82 + 0.18 * pin; op *= pin
        elif L.ain == "pop":
            q = min(1.0, lt / L.din)
            s = 0.4 + 0.6 * (1 - (1 - q) ** 3) + 0.12 * math.sin(q * math.pi)
            op *= min(1.0, q * 2.5)
    if pout < 1:
        if L.aout == "fade":
            op *= pout
        elif L.aout == "left":
            dx -= int((1 - pout) * 120); op *= pout
        elif L.aout == "right":
            dx += int((1 - pout) * 120); op *= pout
        elif L.aout == "down":
            dy += int((1 - pout) * 80); op *= pout
        elif L.aout == "scale":
            s *= 0.9 + 0.1 * pout; op *= pout
    if pm is None:
        if abs(s - 1) > 0.005:
            pm, al = L.scaled(s)
        else:
            pm, al = L.arr()
    if abs(s - 1) > 0.005 and L.dynamic is not None:
        pm = cv2.resize(pm, None, fx=s, fy=s); al = cv2.resize(al, None, fx=s, fy=s)[..., None]
    h, w = al.shape[:2]
    if abs(s - 1) > 0.005:
        ow, oh = int(w / s), int(h / s)
        x += (ow - w) // 2; y += (oh - h) // 2
    if L.ain == "wipe" and pin < 1:
        cut = int(w * pin)
        pm = pm[:, :cut]; al = al[:, :cut]
    blend(frame, pm, al, x + dx, y + dy, op)


# ---------- Kamera / susun atur ----------
def lerp(a, b, k):
    return a + (b - a) * k


def lerp_rect(r1, r2, k):
    return tuple(lerp(a, b, k) for a, b in zip(r1, r2))


FULL_SRC = (0, 0, W, H)
FULL_DST = (0, 0, W, H)
SPLIT_SRC = (500, 0, 920, H * 1.0)          # potongan potret sekitar pembentang
SPLIT_DST = (1190, 70, 700, 822)           # tetingkap di kanan
SPLIT_SRC_L = (500, 0, 920, H * 1.0)
SPLIT_DST_L = (30, 70, 700, 822)           # tetingkap di kiri


def layout_state(cam, t):
    """cam: dict(mode keyframes). Pulang (src, dst, mix_bg, zoom)."""
    kfs = cam.get("kf", [])
    # kf: senarai (t, mode) ; mod: 'full', 'split', 'splitL', 'bg' (latar grafik penuh)
    mode_prev, mode_next, k = "full", "full", 1.0
    if kfs:
        idx = bisect.bisect_right([kf[0] for kf in kfs], t) - 1
        if idx < 0:
            mode_prev = mode_next = kfs[0][1]
        else:
            mode_next = kfs[idx][1]
            mode_prev = kfs[idx - 1][1] if idx > 0 else kfs[idx][1]
            k = ease_io((t - kfs[idx][0]) / 0.7)
    return mode_prev, mode_next, k


WIN_DST = (990, 120, 900, 506)


def face_at(cam, t):
    tr = (cam or {}).get("face")
    if not tr:
        return None
    if t <= tr[0][0]:
        return tr[0][1], tr[0][2]
    for a, b in zip(tr, tr[1:]):
        if a[0] <= t <= b[0]:
            k = (t - a[0]) / max(b[0] - a[0], 1e-3)
            return lerp(a[1], b[1], k), lerp(a[2], b[2], k)
    return tr[-1][1], tr[-1][2]


def mode_rects(mode, zoom, center, cam=None, t=0.0):
    ss = (cam or {}).get("split_src", SPLIT_SRC)
    fc = face_at(cam, t)
    if fc is not None and mode in ("split", "splitL", "bg"):
        sw, sh_ = ss[2], ss[3]
        x0 = min(max(fc[0] - sw / 2, 0), W - sw)
        y0 = min(max(fc[1] - sh_ * 0.30, 0), H - sh_)  # wajah di ~30% dari atas
        ss = (x0, y0, sw, sh_)
    if mode == "win":
        return FULL_SRC, WIN_DST, 1.0
    if mode == "winL":
        return FULL_SRC, (60, 150, 850, 478), 1.0
    if mode == "split":
        return ss, SPLIT_DST, 1.0
    if mode == "splitL":
        return ss, SPLIT_DST_L, 1.0
    if mode == "bg":
        return ss, (W + 50, 120, 620, 728), 1.0
    # full dengan zoom
    cw, ch = W / zoom, H / zoom
    cx, cy = center
    x0 = min(max(cx - cw / 2, 0), W - cw)
    y0 = min(max(cy - ch / 2, 0), H - ch)
    return (x0, y0, cw, ch), FULL_DST, 0.0


def make_bg(frame, kind):
    if kind == "blur":
        small = cv2.resize(frame, (W // 12, H // 12), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 3)
        bg = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32)
        tint = np.array(gfx.GREEN_DEEP, np.float32)
        return (bg * 0.35 + tint * 0.65).astype(np.uint8)
    return gfx.bg_gradient(kind).copy()


_mask_cache = {}


def round_mask(w, h, r=26):
    key = (w, h, r)
    if key not in _mask_cache:
        m = np.zeros((h, w), np.uint8)
        cv2.rectangle(m, (r, 0), (w - r, h), 255, -1)
        cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
        for cx, cy in ((r, r), (w - r - 1, r), (r, h - r - 1), (w - r - 1, h - r - 1)):
            cv2.circle(m, (cx, cy), r, 255, -1, lineType=cv2.LINE_AA)
        _mask_cache[key] = (m.astype(np.float32) / 255.0)[..., None]
        if len(_mask_cache) > 60:
            _mask_cache.pop(next(iter(_mask_cache)))
    return _mask_cache[key]


def render_camera(src, seg, t_local):
    """src: bingkai V1 1920x1080 RGB. seg: dict segmen dgn 'cam'."""
    cam = seg.get("cam", {})
    z0, z1 = cam.get("zoom", (1.0, 1.0))
    dur = max(seg["t1"] - seg["t0"], 1e-3)
    zoom = lerp(z0, z1, ease_io(t_local / dur))
    # zum tambahan sementara (punch) : senarai (ta, tb, z, (cx,cy))
    center = cam.get("center", (W / 2, H / 2))
    if "zsrc" in cam:  # keyframe zum berasaskan masa sumber
        st = seg.get("src_in", 0) + t_local
        ks = cam["zsrc"]
        if st <= ks[0][0]:
            zoom, center = ks[0][1], ks[0][2]
        elif st >= ks[-1][0]:
            zoom, center = ks[-1][1], ks[-1][2]
        else:
            for a, b in zip(ks, ks[1:]):
                if a[0] <= st <= b[0]:
                    kk = ease_io((st - a[0]) / (b[0] - a[0]))
                    zoom = lerp(a[1], b[1], kk)
                    center = (lerp(a[2][0], b[2][0], kk), lerp(a[2][1], b[2][1], kk))
                    break
    for (ta, tb, zz, cc) in cam.get("punch", []):
        if ta - 0.5 <= t_local <= tb + 0.5:
            kin = ease_io((t_local - (ta - 0.5)) / 0.5)
            kout = ease_io(((tb + 0.5) - t_local) / 0.5)
            kk = min(kin, kout)
            zoom = lerp(zoom, zz, kk)
            center = (lerp(center[0], cc[0], kk), lerp(center[1], cc[1], kk))
    mp, mn, k = layout_state(cam, t_local)
    s1, d1, b1 = mode_rects(mp, zoom, center, cam, t_local)
    s2, d2, b2 = mode_rects(mn, zoom, center, cam, t_local)
    s = lerp_rect(s1, s2, k)
    d = lerp_rect(d1, d2, k)
    bmix = lerp(b1, b2, k)
    if bmix < 0.01 and d == FULL_DST:
        x, y, w, h = s
        if abs(w - W) < 1 and abs(h - H) < 1:
            return src.copy()
        M = np.array([[W / w, 0, -x * W / w], [0, H / h, -y * H / h]], np.float32)
        return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR)
    bgk = cam.get("bg", "blur")
    out = make_bg(src, bgk)
    if bmix < 1:
        full = cv2.warpAffine(src, np.array([[1, 0, 0], [0, 1, 0]], np.float32), (W, H))
        out = (full.astype(np.float32) * (1 - bmix) + out.astype(np.float32) * bmix).astype(np.uint8)
    x, y, w, h = [int(round(v)) for v in s]
    dx, dy, dw, dh = [int(round(v)) for v in d]
    if dw < 4 or dh < 4 or dx >= W:
        return out
    crop = src[max(0, y):y + h, max(0, x):x + w]
    win = cv2.resize(crop, (dw, dh), interpolation=cv2.INTER_AREA if dw < w else cv2.INTER_LINEAR)
    r = int(lerp(0, 26, bmix))
    m = round_mask(dw, dh, max(r, 1)) if r > 1 else np.ones((dh, dw, 1), np.float32)
    # bingkai/bayang
    if bmix > 0.05:
        bx0, by0 = max(0, dx - 6), max(0, dy - 6)
        bx1, by1 = min(W, dx + dw + 6), min(H, dy + dh + 6)
        ov = out.copy()
        cv2.rectangle(ov, (bx0, by0), (bx1, by1), gfx.GOLD[::1], -1)
        out = (out * (1 - 0.9 * bmix) + ov * (0.9 * bmix)).astype(np.uint8) if False else out
    x0, y0 = max(0, dx), max(0, dy)
    x1, y1 = min(W, dx + dw), min(H, dy + dh)
    if x1 > x0 and y1 > y0:
        sub = win[y0 - dy:y1 - dy, x0 - dx:x1 - dx].astype(np.float32)
        mm = m[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = (sub * mm + reg * (1 - mm)).astype(np.uint8)
        if bmix > 0.3:
            cv2.rectangle(out, (x0 - 1, y0 - 1), (x1, y1), (247, 196, 58), 3, lineType=cv2.LINE_AA)
    return out


GAME_SRC = (0, 50, 1920, 980)
GAME_DST = (115, 26, 1690, 862)


def render_game(src, seg, t_local):
    cam = seg.get("cam", {})
    z0, z1 = cam.get("zoom", (1.0, 1.0))
    dur = max(seg["t1"] - seg["t0"], 1e-3)
    zoom = lerp(z0, z1, ease_io(t_local / dur))
    center = cam.get("center", (960, 540))
    for (ta, tb, zz, cc) in cam.get("punch", []):
        if ta - 0.4 <= t_local <= tb + 0.4:
            kk = min(ease_io((t_local - (ta - 0.4)) / 0.4), ease_io(((tb + 0.4) - t_local) / 0.4))
            zoom = lerp(zoom, zz, kk)
            center = (lerp(center[0], cc[0], kk), lerp(center[1], cc[1], kk))
    gx, gy, gw, gh = GAME_SRC
    cw, ch = gw / zoom, gh / zoom
    x0 = min(max(center[0] - cw / 2, gx), gx + gw - cw)
    y0 = min(max(center[1] - ch / 2, gy), gy + gh - ch)
    full = cam.get("fullscreen", False)
    if full:
        dx, dy, dw, dh = 0, 50, W, 980
        out = np.zeros((H, W, 3), np.uint8)
    else:
        dx, dy, dw, dh = GAME_DST
        out = gfx.bg_gradient("game").copy()
    M = np.array([[dw / cw, 0, dx - x0 * dw / cw], [0, dh / ch, dy - y0 * dh / ch]], np.float32)
    warped = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR)
    if full:
        out[dy:dy + dh] = warped[dy:dy + dh]
        return out
    m = round_mask(dw, dh, 20)
    reg = out[dy:dy + dh, dx:dx + dw].astype(np.float32)
    out[dy:dy + dh, dx:dx + dw] = (warped[dy:dy + dh, dx:dx + dw].astype(np.float32) * m + reg * (1 - m)).astype(np.uint8)
    cv2.rectangle(out, (dx - 2, dy - 2), (dx + dw + 1, dy + dh + 1), (150, 92, 240), 3, lineType=cv2.LINE_AA)
    return out


def draw_pip(frame, pip, spec, t):
    """spec: dict(t0,t1,pos,name,color). Tetingkap PiP pembentang beranimasi."""
    lt = t - spec["t0"]
    k = min(ease(lt / 0.45), ease((spec["t1"] - t) / 0.45))
    if k <= 0.01:
        return
    w, h = spec.get("size", (448, 252))
    x, y = spec.get("pos", (W - w - 36, 36))
    img = cv2.resize(pip, (w, h), interpolation=cv2.INTER_AREA)
    m = round_mask(w, h, 22) * k
    sh = frame[y + 6:y + h + 14, x - 4:x + w + 4].astype(np.float32)
    frame[y + 6:y + h + 14, x - 4:x + w + 4] = (sh * (1 - 0.45 * k)).astype(np.uint8)
    reg = frame[y:y + h, x:x + w].astype(np.float32)
    frame[y:y + h, x:x + w] = (img.astype(np.float32) * m + reg * (1 - m)).astype(np.uint8)
    cv2.rectangle(frame, (x - 1, y - 1), (x + w, y + h), (247, 196, 58), 3, lineType=cv2.LINE_AA)
    if spec.get("label") is not None:
        L = spec["label"]
        pm, al = L
        blend(frame, pm, al, x + 12, y + h - al.shape[0] - 10, k)


class Reader:
    def __init__(self, path, w, h, start_frame=0):
        self.w, self.h = w, h
        ss = start_frame / FPS
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{ss:.4f}", "-i", path, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE, bufsize=w * h * 3 * 4)
        self.n = w * h * 3

    def read(self):
        b = self.p.stdout.read(self.n)
        if len(b) < self.n:
            return None
        return np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3)


def run(base_v1, base_v2, segments, layers, pips, nframes, out_writer_cmd, start_frame=0, progress=True):
    """segments: senarai dict(t0,t1,type,cam). layers: senarai Layer. pips: senarai spec."""
    r1 = Reader(base_v1, W, H, start_frame)
    r2 = Reader(base_v2, PW, PH, start_frame) if base_v2 else None
    wp = subprocess.Popen(out_writer_cmd, stdin=subprocess.PIPE, bufsize=W * H * 3 * 4)
    seg_t0 = [s["t0"] for s in segments]
    layers = sorted(layers, key=lambda L: (L.z, L.t0))
    # indeks lapisan mengikut masa (baldi 1 s)
    buckets = {}
    for L in layers:
        for sec in range(int(L.t0), int(L.t1) + 1):
            buckets.setdefault(sec, []).append(L)
    pbuck = {}
    for P in pips:
        for sec in range(int(P["t0"]), int(P["t1"]) + 1):
            pbuck.setdefault(sec, []).append(P)
    import time
    tstart = time.time()
    for fi in range(start_frame, nframes):
        t = fi / FPS
        f1 = r1.read()
        f2 = r2.read() if r2 else None
        if f1 is None:
            f1 = np.zeros((H, W, 3), np.uint8)
        si = bisect.bisect_right(seg_t0, t) - 1
        seg = segments[max(si, 0)]
        if seg.get("type") == "bg":
            frame = gfx.bg_gradient(seg.get("bg", "green")).copy()
        elif seg.get("type") == "game":
            frame = render_game(f1, seg, t - seg["t0"])
        else:
            frame = render_camera(f1, seg, t - seg["t0"])
        if f2 is not None:
            for P in pbuck.get(int(t), []):
                if P["t0"] <= t < P["t1"]:
                    draw_pip(frame, f2, P, t)
        for L in buckets.get(int(t), []):
            if L.t0 <= t < L.t1:
                draw_layer(frame, L, t)
        wp.stdin.write(frame.tobytes())
        if progress and fi % 300 == 0:
            el = time.time() - tstart
            fps = (fi - start_frame + 1) / max(el, 1e-6)
            print(f"  frame {fi}/{nframes}  {fps:.1f} fps  ETA {(nframes - fi) / max(fps, 1e-6) / 60:.1f} min", flush=True)
    wp.stdin.close()
    wp.wait()
