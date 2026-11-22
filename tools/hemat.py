"""Mesin Video Hemat: merakit video edukasi 9:16 dari footage + narasi per kalimat + kotak teks.

Pakai:  python3 tools/hemat.py spec.json
Spec (JSON):
{
  "out": "hasil.mp4", "dir": "folder bahan", "gap": 0.3,
  "scenes": [
    {"vo": "vo_01.mp3", "head": "COKELAT vs PUTIH?", "color": "orange|white|teal",
     "sub": "teks kecil opsional", "sub_at": 2.0,
     "shots": [ {"clip": "a.mp4", "ss": 1.0, "fx": 0.5}  # fx = posisi crop horizontal 0..1
                {"split": ["a.mp4", "b.mp4"], "ss": [1, 2], "fx": [0.5, 0.5]} ] }
  ]
}
Durasi adegan = durasi narasi + gap; dibagi rata ke shot di adegan itu.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT_HEAD = "/usr/share/fonts/opentype/montserrat/Montserrat-ExtraBold.otf"
FONT_SUB = "/usr/share/fonts/opentype/montserrat/Montserrat-Bold.otf"
COLORS = {"orange": (247, 162, 27), "white": (255, 255, 255), "teal": (79, 209, 197)}
BOX = (31, 41, 58, 235)


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        sys.exit("ffmpeg gagal:\n" + r.stderr[-2000:])
    return r.stdout


def dur(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


def wrap(d, text, font, maxw):
    lines, line = [], ""
    for w in text.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            line = t
        else:
            lines.append(line); line = w
    lines.append(line)
    return lines


def box_png(path, head, color, sub=None, top=230):
    """Kotak teks gaya video ayam: kotak gelap lebar di atas, judul tebal, sub-kotak kecil."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fh = ImageFont.truetype(FONT_HEAD, 66)
    lines = wrap(d, head, fh, 840)
    lh = 80
    pad = 60
    h = pad * 2 + lh * len(lines) - 14
    d.rounded_rectangle([65, top, 1015, top + h], radius=10, fill=BOX)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    y = top + pad
    for ln in lines:
        sd.text((W / 2 + 2, y + 3), ln, font=fh, fill=(0, 0, 0, 160), anchor="ma")
        y += lh
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(im)
    y = top + pad
    for ln in lines:
        d.text((W / 2, y), ln, font=fh, fill=COLORS.get(color, color), anchor="ma")
        y += lh
    if sub:
        fs = ImageFont.truetype(FONT_SUB, 44)
        sl = wrap(d, sub, fs, 760)
        sy = top + h + 22
        sw = max(d.textlength(s, font=fs) for s in sl) + 70
        d.rounded_rectangle([W / 2 - sw / 2, sy, W / 2 + sw / 2, sy + 30 + 56 * len(sl)], radius=8, fill=BOX)
        yy = sy + 18
        for s in sl:
            d.text((W / 2, yy), s, font=fs, fill=(255, 255, 255), anchor="ma")
            yy += 56
    im.save(path)


def vchain(fx, zoom_from=1.0, zoom_to=1.06, n=60, width=W, height=H):
    """Crop sesuai rasio target dari footage horizontal + push-in pelan + penajaman."""
    return (f"crop='ih*{width}/{height}':ih:'(iw-ih*{width}/{height})*{fx}':0,"
            f"scale={int(width*1.1)}:{int(height*1.1)}:flags=lanczos,unsharp=5:5:0.6,"
            f"zoompan=z='{zoom_from}+({zoom_to}-{zoom_from})*on/{n}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={width}x{height}:fps={FPS},"
            f"setsar=1")


def shot_clip(shot, d, folder, out):
    n = int(round(d * FPS))
    if "vsplit" in shot:
        a, b = [os.path.join(folder, c) for c in shot["vsplit"]]
        ssa, ssb = shot.get("ss", [0, 0]); fa, fb = shot.get("fx", [0.5, 0.5])
        la, lb = shot.get("labels", ["", ""])
        lab = lambda t, y: (f",drawtext=fontfile={FONT_HEAD}:text='{t}':fontsize=64:fontcolor=white:borderw=5:bordercolor=black@0.7:x=(w-tw)/2:y={y}" if t else "")
        fc = (f"[0:v]{vchain(fa, n=n, height=H//2)}{lab(la, 'h-240')}[a];[1:v]{vchain(fb, n=n, height=H//2)}{lab(lb, 'h-110')}[b];"
              f"[a][b]vstack,drawbox=x=0:y={H//2-3}:w={W}:h=6:color=white@0.9:t=fill[v]")
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(ssa), "-t", str(d + 0.5), "-i", a,
             "-ss", str(ssb), "-t", str(d + 0.5), "-i", b, "-filter_complex", fc, "-map", "[v]",
             "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", out])
    elif "split" in shot:
        a, b = [os.path.join(folder, c) for c in shot["split"]]
        ssa, ssb = shot.get("ss", [0, 0]); fa, fb = shot.get("fx", [0.5, 0.5])
        fc = (f"[0:v]{vchain(fa, n=n, width=W//2)}[a];[1:v]{vchain(fb, n=n, width=W//2)}[b];"
              f"[a][b]hstack,drawbox=x={W//2-3}:y=0:w=6:h={H}:color=white@0.9:t=fill[v]")
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(ssa), "-t", str(d + 0.5), "-i", a,
             "-ss", str(ssb), "-t", str(d + 0.5), "-i", b, "-filter_complex", fc, "-map", "[v]",
             "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", out])
    else:
        src = os.path.join(folder, shot["clip"])
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(shot.get("ss", 0)), "-t", str(d + 0.5), "-i", src,
             "-vf", vchain(shot.get("fx", 0.5), n=n), "-frames:v", str(n), "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", out])


def build(spec):
    folder, gap = spec["dir"], spec.get("gap", 0.3)
    tmp = tempfile.mkdtemp()
    scene_files, audio_parts = [], []
    for i, sc in enumerate(spec["scenes"]):
        vo = os.path.join(folder, sc["vo"])
        sd = round((dur(vo) + gap) * FPS) / FPS
        shots = sc["shots"]
        per = sd / len(shots)
        parts = []
        for j, sh in enumerate(shots):
            p = f"{tmp}/s{i}_{j}.mp4"
            shot_clip(sh, per, folder, p); parts.append(p)
        lst = f"{tmp}/l{i}.txt"
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        raw = f"{tmp}/raw{i}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw])
        # teks: judul muncul cepat, sub muncul di sub_at
        t1, t2 = f"{tmp}/t{i}a.png", f"{tmp}/t{i}b.png"
        box_png(t1, sc["head"], sc.get("color", "white"), top=sc.get("box_y", 230))
        inputs = ["-i", raw, "-loop", "1", "-t", str(sd), "-i", t1]
        fc = "[1]format=rgba,fade=in:st=0.1:d=0.25:alpha=1[ta];[0][ta]overlay=0:0[v1]"
        last = "v1"
        if sc.get("sub"):
            box_png(t2, sc["head"], sc.get("color", "white"), sc["sub"], top=sc.get("box_y", 230))
            st = sc.get("sub_at", 0.1)
            inputs += ["-loop", "1", "-t", str(sd), "-i", t2]
            fc += f";[2]format=rgba,fade=in:st={st}:d=0.25:alpha=1[tb];[v1][tb]overlay=0:0:enable='gte(t,{st})'[v2]"
            last = "v2"
        sf = f"{tmp}/scene{i}.mp4"
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", f"[{last}]", "-t", str(sd),
             "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", sf])
        scene_files.append(sf)
        audio_parts.append((vo, sd))
    lst = f"{tmp}/all.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in scene_files))
    video = f"{tmp}/video.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
    # audio: tiap narasi diberi jeda agar pas dengan adegan, lalu dinormalkan
    ains, fc = [], ""
    for k, (vo, sd) in enumerate(audio_parts):
        ains += ["-i", vo]
        fc += f"[{k}:a]aresample=48000,apad=whole_dur={sd}[a{k}];"
    fc += "".join(f"[a{k}]" for k in range(len(audio_parts))) + f"concat=n={len(audio_parts)}:v=0:a=1,loudnorm=I=-15:TP=-1.5:LRA=11[a]"
    audio = f"{tmp}/audio.m4a"
    run(["ffmpeg", "-y", "-v", "error", *ains, "-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "192k", audio])
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
         "-movflags", "+faststart", spec["out"]])
    print(spec["out"], round(dur(spec["out"]), 2), "detik")


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])))
