"""Fast hook-first product video: python3 render3.py config.json out.mp4 music.wav
Style (from research): hook text in first second, cut every 3 beats (~1.6s),
punch-in zoom on each cut, big text in upper part of the frame, total ~8.5s."""
import subprocess, math, json, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
F_BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
cfg = json.load(open(sys.argv[1]))
BPM = cfg.get("bpm", 112)
BEAT = 60 / BPM
ACCENT = tuple(cfg.get("accent", [255, 102, 26]))
DIR = cfg["dir"]

def font(s): return ImageFont.truetype(F_BOLD, s)

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def load(n): return Image.open(DIR + n).convert("RGB")

def grid(names):
    cols = 2; rows = math.ceil(len(names) / 2); cell = 540
    g = Image.new("RGB", (cell * cols, cell * rows), (255, 255, 255))
    for i, n in enumerate(names):
        im = load(n); s = min(im.size)
        im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2))
        g.paste(im.resize((cell - 6, cell - 6), Image.LANCZOS), ((i % 2) * cell + 3, (i // 2) * cell + 3))
    return g

def base_frame(spec):
    prod = grid(spec) if isinstance(spec, list) else load(spec)
    # blurred full-bleed background
    sc = max(W / prod.width, H / prod.height)
    bg = prod.resize((int(prod.width * sc) + 2, int(prod.height * sc) + 2), Image.BILINEAR)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.35)
    fs = min((W - 40) / prod.width, 1150 / prod.height)
    fg = prod.resize((int(prod.width * fs), int(prod.height * fs)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, 640 + (1150 - fg.height) // 2))
    return bg

def caption_layer(text, size, boxcol, txtcol):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer); f = font(size)
    lines = wrap(d, text, f, W - 160)
    lh = int(size * 1.45); th = lh * len(lines)
    y0 = 420 - th // 2
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f); x = (W - tw) / 2; y = y0 + i * lh
        bx0, by0, bx1, by1 = d.textbbox((x, y), ln, font=f)
        d.rounded_rectangle([bx0 - 30, by0 - 18, bx1 + 30, by1 + 20], radius=22, fill=boxcol)
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f); x = (W - tw) / 2; y = y0 + i * lh
        d.text((x, y), ln, font=f, fill=txtcol)
    return layer

shots = cfg["shots"]
lens = [s.get("beats", 3) * BEAT for s in shots]
total_frames = int(sum(lens) * FPS)
proc = subprocess.Popen([
    "ffmpeg", "-y", "-loglevel", "error",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", sys.argv[3], "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", sys.argv[2]], stdin=subprocess.PIPE)

fidx = 0
for si, s in enumerate(shots):
    base = base_frame(s["img"])
    hook = si == 0; cta = s.get("cta", False)
    if hook: cap = caption_layer(s["text"], 104, (255, 230, 0, 255), (20, 20, 20))
    elif cta: cap = caption_layer(s["text"], 96, ACCENT + (255,), (255, 255, 255))
    else: cap = caption_layer(s["text"], 84, (255, 255, 255, 245), (20, 20, 20))
    n = int(lens[si] * FPS)
    for i in range(n):
        t = i / FPS
        # punch-in on the cut, then slow push
        z = 1.0 + 0.10 * max(0, 1 - t / 0.22) + 0.04 * (i / n)
        bw, bh = int(W * z), int(H * z)
        f = base.resize((bw, bh), Image.BILINEAR).crop(((bw - W) // 2, (bh - H) // 2, (bw - W) // 2 + W, (bh - H) // 2 + H))
        # caption pops in (scale) over first 0.15s
        k = min(1, t / 0.15)
        if k < 1:
            cw, ch = int(W * (0.85 + 0.15 * k)), int(H * (0.85 + 0.15 * k))
            c = cap.resize((cw, ch), Image.BILINEAR)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer.paste(c, ((W - cw) // 2, int(420 * (1 - (0.85 + 0.15 * k)))))
        else:
            layer = cap
        if hook and int(t / (BEAT / 2)) % 2 == 1 and t < BEAT * 2:
            layer = layer.transform(layer.size, Image.AFFINE, (1, 0, -6, 0, 1, 0))  # small shake
        f = Image.alpha_composite(f.convert("RGBA"), layer)
        d = ImageDraw.Draw(f)
        if cta:
            p = 1 + 0.05 * math.sin(t * 2 * math.pi / BEAT)
            bw2, bh2 = int(720 * p), int(118 * p); bx, by = (W - bw2) // 2, H - 250
            d.rounded_rectangle([bx, by, bx + bw2, by + bh2], radius=bh2 // 2, fill=(255, 255, 255, 255))
            fb = font(50); lab = "KLIK LINK DI PROFIL"; tw = d.textlength(lab, font=fb)
            d.text(((W - tw) / 2, by + (bh2 - 68) / 2), lab, font=fb, fill=(20, 20, 20))
        fd = font(28); disc = "Link affiliate"; tw = d.textlength(disc, font=fd)
        d.text(((W - tw) / 2, H - 95), disc, font=fd, fill=(230, 230, 230))
        d.rectangle([0, 0, int(W * (fidx + 1) / total_frames), 12], fill=ACCENT)
        if i < 2 and si > 0:  # white flash on cut
            f = Image.blend(f, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.35 if i == 0 else 0.15)
        proc.stdin.write(f.convert("RGB").tobytes()); fidx += 1
proc.stdin.close(); proc.wait()
