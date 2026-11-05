import sys, os, json, math, subprocess
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
FBI = '/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf'
YEL = (255, 214, 0); RED = (235, 50, 50); GRN = (40, 200, 90)
CREAM = (241, 230, 210); INK = (25, 22, 20)
_c = {}
def F(p, s):
    k = (p, s)
    if k not in _c: _c[k] = ImageFont.truetype(p, s)
    return _c[k]
_i = {}
def photo(n):
    if n not in _i: _i[n] = Image.open(f'src/1000148{n}.jpg').convert('RGB')
    return _i[n]
def cut(n):
    k = 'c%d' % n
    if k not in _i:
        im = Image.open(f'cut_{n}.png').convert('RGBA'); _i[k] = im.crop(im.getbbox())
    return _i[k]

def cl(x): return max(0.0, min(1.0, x))
def ease(t): t = cl(t); return 1 - (1 - t) ** 3
def back(t):
    t = cl(t); c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

TL = json.load(open('vo_tl.json'))
PH = ["Cowok yang masih pake celana ketat...", "ganti ini deh!",
      "Jeans baggy loose straight, lagi rame banget.", "Bahannya adem, nggak kaku.",
      "Sakunya dalem, HP aman.", "Potongannya lurus,", "kaki keliatan lebih jenjang.",
      "Warnanya banyak,", "ukurannya S sampai 4XL.", "Kamu pilih yang mana?", "Linknya di bio!"]
KEY = {'ketat...', 'ganti', 'baggy', 'rame', 'adem,', 'dalem,', 'lurus,', 'jenjang.', 'banyak,', '4XL.', 'mana?', 'bio!'}
WORDS = []  # (start,end,word,phrase_idx)
for k, ((a, b), p) in enumerate(zip(TL, PH)):
    ws = p.split(); tot = sum(len(w) + 2 for w in ws); t = a
    for w in ws:
        d = (b - a) * (len(w) + 2) / tot; WORDS.append((t, t + d, w, k)); t += d

def caption(fr, T):
    cur = None
    for j, (a, b, w, k) in enumerate(WORDS):
        if a <= T < b + 0.12: cur = j
    if cur is None: return fr
    k = WORDS[cur][3]
    idx = [j for j, x in enumerate(WORDS) if x[3] == k]
    d = ImageDraw.Draw(fr); f = F(FB, 78)
    groups = []; g = []; wsum = 0
    for j in idx:
        wl = d.textlength(WORDS[j][2].upper(), font=f) + 22
        if g and (wsum + wl > 900 or len(g) == 3): groups.append(g); g = []; wsum = 0
        g.append(j); wsum += wl
    groups.append(g)
    grp = [g for g in groups if cur in g][0]
    widths = [d.textlength(WORDS[j][2].upper(), font=f) for j in grp]; sp = 22
    x = W / 2 - (sum(widths) + sp * (len(grp) - 1)) / 2; y = 1320
    for j, wd in zip(grp, widths):
        w = WORDS[j][2].upper(); act = j == cur
        if act:
            pop = 1 + 0.12 * (1 - ease((T - WORDS[j][0]) / 0.12))
            fa = F(FB, int(78 * pop))
            col = YEL if WORDS[j][2] in KEY or True else (255, 255, 255)
            d.text((x + wd / 2, y), w, font=fa, fill=YEL, anchor='mm', stroke_width=9, stroke_fill=(0, 0, 0))
        elif j < cur:
            d.text((x + wd / 2, y), w, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=9, stroke_fill=(0, 0, 0))
        else:
            d.text((x + wd / 2, y), w, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=9, stroke_fill=(0, 0, 0))
        x += wd + sp
    return fr

def pill(fr, cx, cy, s, size, bg=YEL, fg=INK, sc=1.0, rot=0):
    if sc <= 0.03: return fr
    f = F(FB, size); tmp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    bb = tmp.textbbox((0, 0), s, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    bw, bh = tw + 70, th + 46
    L = Image.new('RGBA', (bw + 40, bh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([20, 26, 20 + bw, 26 + bh], 24, fill=(0, 0, 0, 120))
    d.rounded_rectangle([20, 20, 20 + bw, 20 + bh], 24, fill=bg + (255,))
    d.text((20 + bw / 2, 20 + bh / 2), s, font=f, fill=fg, anchor='mm')
    if rot: L = L.rotate(rot, resample=Image.BICUBIC, expand=True)
    if sc != 1: L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.BICUBIC)
    fr.paste(L, (int(cx - L.width / 2), int(cy - L.height / 2)), L); return fr

def title(fr, s, y, size=96, t=1.0, col=(255, 255, 255)):
    d = ImageDraw.Draw(fr); a = ease(t / 0.18)
    d.text((W / 2, y + 40 * (1 - a)), s, font=F(FB, size), fill=col, anchor='mm', stroke_width=9, stroke_fill=(0, 0, 0))
    return fr

def flash(fr, t, dur=0.1, a0=0.85):
    if t < dur: fr = Image.blend(fr, Image.new('RGB', (W, H), (255, 255, 255)), a0 * (1 - t / dur))
    return fr

def shake(fr, t, amp=18, dur=0.18):
    if t < dur:
        k = amp * (1 - t / dur); dx = int(k * math.sin(t * 90)); dy = int(k * math.cos(t * 70))
        fr = fr.transform(fr.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR)
    return fr

def kb(n, p, z0=1.0, z1=1.12, cx=0.5, cy=0.5):
    im = photo(n); s = im.width; z = z0 + (z1 - z0) * p
    ch = s / z; cw = ch * 9 / 16
    x = min(max(cx * s - cw / 2, 0), s - cw); y = min(max(cy * s - ch / 2, 0), s - ch)
    return im.resize((W, H), Image.LANCZOS, box=(x, y, x + cw, y + ch))

def cream_bg(p=0.0):
    bg = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(bg)
    for y in range(0, H, 4):  # subtle vertical gradient
        v = int(12 * y / H); d.line([(0, y), (W, y)], fill=(CREAM[0] - v, CREAM[1] - v, CREAM[2] - v))
    return bg

def paste_cut(fr, n, cx, bottom, h, sx=1.0, sc=1.0, shadow=True):
    c = cut(n); hh = int(h * sc); ww = int(c.width * hh / c.height * sx)
    if ww < 2 or hh < 2: return fr
    c2 = c.resize((ww, hh), Image.LANCZOS)
    if shadow:
        sh = Image.new('RGBA', (ww + 160, 90), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([40, 20, ww + 120, 70], fill=(0, 0, 0, 70))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        fr.paste(sh, (int(cx - sh.width / 2), int(bottom - 50)), sh)
    fr.paste(c2, (int(cx - ww / 2), int(bottom - hh)), c2); return fr

def card(fr, crop, cx, cy, w, sc=1.0, r=40, border=10):
    sc = max(sc, 0.03); cw = int(w * sc); chh = int(cw * crop.height / crop.width)
    c = crop.resize((cw, chh), Image.LANCZOS)
    m = Image.new('L', c.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, chh - 1], r, fill=255)
    pad = border
    B = Image.new('RGBA', (cw + pad * 2 + 80, chh + pad * 2 + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(B)
    d.rounded_rectangle([40, 52, 40 + cw + pad * 2, 52 + chh + pad * 2], r + pad, fill=(0, 0, 0, 110))
    B = B.filter(ImageFilter.GaussianBlur(18)); d = ImageDraw.Draw(B)
    d.rounded_rectangle([40, 40, 40 + cw + pad * 2, 40 + chh + pad * 2], r + pad, fill=(255, 255, 255, 255))
    fr.paste(B, (int(cx - B.width / 2), int(cy - B.height / 2)), B)
    fr.paste(c, (int(cx - cw / 2), int(cy - chh / 2)), m); return fr

def blurbg(n, p):
    b = kb(n, p, 1.3, 1.36).filter(ImageFilter.GaussianBlur(28))
    return Image.blend(b, Image.new('RGB', (W, H), (12, 12, 16)), 0.55)

def topgrad(fr, h=620, a=150):
    g = Image.new('L', (1, h)); [g.putpixel((0, y), int(a * (1 - y / h) ** 2)) for y in range(h)]
    g = g.resize((W, h)); fr.paste(Image.new('RGB', (W, h), (0, 0, 0)), (0, 0), g)
    g2 = Image.new('L', (1, 700)); [g2.putpixel((0, y), int(170 * (y / 700) ** 2)) for y in range(700)]
    g2 = g2.resize((W, 700)); fr.paste(Image.new('RGB', (W, 700), (0, 0, 0)), (0, H - 700), g2)
    return fr

# ---------------- scenes: fn(t, dur) ----------------
def s1(t, D):  # skinny "ketat" squeeze, POV hook
    fr = cream_bg()
    sx = 0.52 + 0.03 * math.sin(t * 9)
    fr = paste_cut(fr, 214, W / 2, 1640, 1380, sx=sx)
    fr = pill(fr, W / 2, 330, 'POV: MASIH PAKE', 64, bg=INK, fg=(255, 255, 255), sc=back(t / 0.25))
    if t > 0.25:
        fr = title(fr, 'CELANA KETAT? 😬'.replace(' 😬', ''), 470, 116, t - 0.25, col=RED)
    if t > 0.9:
        d = ImageDraw.Draw(fr); s = ease((t - 0.9) / 0.15)
        r = 70 * s; cx, cy = 860, 900
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        d.line([(cx - r * .45, cy - r * .45), (cx + r * .45, cy + r * .45)], fill='white', width=16)
        d.line([(cx - r * .45, cy + r * .45), (cx + r * .45, cy - r * .45)], fill='white', width=16)
    return fr

def s2(t, D):  # snap to baggy
    fr = cream_bg()
    sx = 0.52 + 0.48 * back(t / 0.22)
    fr = paste_cut(fr, 214, W / 2, 1640, 1380, sx=sx, sc=1 + 0.04 * ease(t / D))
    fr = flash(fr, t, 0.12); fr = shake(fr, t, 22, 0.22)
    fr = pill(fr, W / 2, 400, 'GANTI INI!', 120, bg=GRN, fg=(255, 255, 255), sc=back((t - 0.05) / 0.25), rot=-3)
    return fr

LINE = [214, 215, 217, 216, 218, 219]
def s3(t, D):  # lineup of 6 colours sliding in
    fr = cream_bg()
    xs = [W / 2 + (k - 2.5) * 172 for k in range(6)]
    order = [2, 3, 1, 4, 0, 5]
    for rank, k in enumerate(order):
        st = 0.08 * rank; a = back((t - st) / 0.35)
        if t < st: continue
        bottom = 1560 + 300 * (1 - a)
        z = 1 + 0.05 * ease(t / D)
        fr = paste_cut(fr, LINE[k], W / 2 + (xs[k] - W / 2) * z, bottom + 60, 880 * z, shadow=False)
    fr = pill(fr, W / 2, 300, 'LAGI RAME 🔥'.replace(' 🔥', ''), 70, bg=RED, fg=(255, 255, 255), sc=back(t / 0.25), rot=-2)
    fr = title(fr, 'BAGGY LOOSE', 440, 112, t, col=INK)
    d = ImageDraw.Draw(fr); a = ease((t - 0.15) / 0.2)
    d.text((W / 2, 560 + 30 * (1 - a)), 'STRAIGHT JEANS', font=F(FBI, 78), fill=(70, 110, 170), anchor='mm')
    return fr

def detail(n, box, label, sub, bgn):
    def f(t, D):
        fr = blurbg(bgn, t / D)
        crop = photo(n).crop(box)
        sc = 0.8 + 0.2 * back(t / 0.3) if t < 0.5 else 1 + 0.05 * (t - 0.5) / D
        fr = card(fr, crop, W / 2, 950, 740, sc=sc)
        fr = flash(fr, t, 0.08, 0.7)
        fr = pill(fr, W / 2, 300, label, 92, sc=back(t / 0.22), rot=-2)
        d = ImageDraw.Draw(fr)
        if t > 0.2:
            d.text((W / 2, 430), sub, font=F(FB, 56), fill=(255, 255, 255), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0))
        return fr
    return f
s4 = detail(211, (532, 424, 766, 690), 'KATUN + DENIM', 'adem • lembut • nggak kaku', 211)
s5 = detail(208, (556, 460, 773, 649), 'SAKU DALAM', 'HP masuk, aman 📱'.replace(' 📱', ''), 214)

def s6(t, D):  # tilt shoes -> waist, "jenjang"
    p = t / D; im = photo(216); s = im.width; z = 1.3
    ch = s / z; cw = ch * 9 / 16; y = (s - ch) * (1 - ease(p * 1.15)); x = s / 2 - cw / 2
    fr = im.resize((W, H), Image.LANCZOS, box=(x, y, x + cw, y + ch))
    fr = topgrad(fr); fr = flash(fr, t, 0.1, 0.7)
    fr = pill(fr, W / 2, 300, 'POTONGAN LURUS', 84, sc=back(t / 0.22))
    if t > 1.05:
        fr = title(fr, 'KAKI KELIATAN', 440, 96, t - 1.05)
        fr = title(fr, 'JENJANG ↕'.replace(' ↕', ''), 555, 110, t - 1.15, col=YEL)
    return fr

FLIP = [214, 219, 217, 218, 215, 216]
def s7(t, D):  # beat flips
    k = min(len(FLIP) - 1, int(t / (D / len(FLIP)))); lt = t - k * D / len(FLIP)
    fr = cream_bg()
    fr = paste_cut(fr, FLIP[k], W / 2, 1660, 1150 * (1.04 - 0.04 * ease(lt / 0.15)))
    fr = flash(fr, lt, 0.06, 0.5)
    fr = title(fr, 'BANYAK WARNA', 330, 104, 1.0, col=INK)
    d = ImageDraw.Draw(fr); tot = 6 * 46; x0 = W / 2 - tot / 2 + 23
    for j in range(6):
        r = 14 if j == k else 9
        d.ellipse([x0 + j * 46 - r, 450 - r, x0 + j * 46 + r, 450 + r], fill=YEL if j == k else (160, 150, 135), outline=INK if j == k else None, width=3)
    return fr

def s8(t, D):
    fr = blurbg(215, t / D)
    sc = 0.8 + 0.2 * back(t / 0.3) if t < 0.5 else 1 + 0.03 * (t - 0.5) / D
    fr = card(fr, photo(213), W / 2, 830, 900, sc=sc, r=28, border=0)
    fr = flash(fr, t, 0.08, 0.7)
    fr = pill(fr, W / 2, 300, 'S - 4XL', 100, sc=back(t / 0.22), rot=2)
    return fr

GRID = [214, 215, 217, 216, 218, 219]
def s9(t, D):
    fr = Image.new('RGB', (W, H), (16, 16, 20))
    gw, gh = 300, 380; gap = 18
    for j, n in enumerate(GRID):
        st = 0.06 * j
        if t < st: continue
        a = back((t - st) / 0.3) if t - st < 0.5 else 1.0
        im = photo(n); s = im.width; cw = s * 0.62; ch = cw * gh / gw
        c = im.resize((gw, gh), Image.LANCZOS, box=(s / 2 - cw / 2, (s - ch) / 2 + s * 0.05, s / 2 + cw / 2, (s + ch) / 2 + s * 0.05))
        cx = W / 2 + (j % 3 - 1) * (gw + gap); cy = 640 + (j // 3) * (gh + gap)
        fr = card(fr, c, cx, cy, gw, sc=a, r=24, border=6)
        if a > 0.6:
            d = ImageDraw.Draw(fr)
            d.ellipse([cx - gw / 2 + 4, cy - gh / 2 + 4, cx - gw / 2 + 76, cy - gh / 2 + 76], fill=YEL, outline=INK, width=4)
            d.text((cx - gw / 2 + 40, cy - gh / 2 + 42), str(j + 1), font=F(FB, 48), fill=INK, anchor='mm')
    fr = title(fr, 'PILIH NOMOR BERAPA?', 290, 84, t)
    T = TL[10][0] - TL[9][0] + 0.0
    if t > T - 0.05:
        pul = 1 + 0.05 * math.sin((t - T) * 9)
        a = back((t - T) / 0.3)
        fr = pill(fr, W / 2, 1640, 'KOMEN NOMORNYA 👇'.replace(' 👇', ''), 70, bg=(255, 255, 255), sc=a * pul)
        fr = pill(fr, W / 2, 1520, '🔗 LINK DI BIO'.replace('🔗 ', ''), 84, sc=a * pul, rot=-2)
    return fr

END = TL[-1][1] + 1.0
CUTS = [0, TL[1][0], TL[2][0], TL[3][0], TL[4][0], TL[5][0], TL[7][0], TL[8][0], TL[9][0], END]
SC = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
CAP_OFF = {0: False}

def frame_at(k, i):
    t0 = CUTS[k]; D = CUTS[k + 1] - t0; t = i / FPS; T = t0 + t
    fr = SC[k](t, D)
    return caption(fr, T)

def render(k):
    t0 = CUTS[k]; t1 = CUTS[k + 1]
    f0 = round(t0 * FPS); f1 = round(t1 * FPS); N = f1 - f0
    tmp = f'out2/{k:02d}.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(N):
        t = (f0 + i) / FPS - t0
        fr = SC[k](t, t1 - t0); fr = caption(fr, t0 + t)
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, f'out2/{k:02d}.mp4')
    return k

if __name__ == '__main__':
    os.makedirs('out2', exist_ok=True); os.makedirs('prev2', exist_ok=True)
    if sys.argv[1] == 'preview':
        fracs = [float(x) for x in sys.argv[2:]]
        for k in range(len(SC)):
            for fi, fr_ in enumerate(fracs):
                D = CUTS[k + 1] - CUTS[k]; t = D * fr_
                im = SC[k](t, D); im = caption(im, CUTS[k] + t)
                im.convert('RGB').resize((360, 640)).save(f'prev2/{k}_{fi}.jpg', quality=85)
        print(CUTS)
    else:
        with Pool(4) as pool: print(pool.map(render, range(len(SC))))
