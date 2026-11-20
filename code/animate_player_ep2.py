#!/usr/bin/env python3
"""Audiocast Anthology Ep1 clip v1: animated player + procedural lip-sync.

Lip-sync method (honest, in-house): the canon portrait stays the base image.
A feathered jaw patch under the mouth line shifts down, and a soft mouth
slit widens, both driven frame-by-frame by the RMS envelope of the actual
Ep1 audio (24 fps), with attack/release smoothing. No regenerated face.
Also animated: waveform ignition + playhead, level ring, elapsed time.
Output streams to ffmpeg (libx264 + the original mp3 as AAC).
"""
import math, struct, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS = 24
BG = (8, 8, 13)
CYAN = (0, 229, 255)
MAG = (230, 0, 174)
WHITE = (235, 235, 240)
SOFT = (200, 200, 205)
DIM = (120, 120, 135)
PANEL = (16, 16, 24)
BLACKF = "/usr/share/fonts/truetype/noto/NotoSansDisplay-Black.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def F(p, s): return ImageFont.truetype(p, s)

AUDIO = sys.argv[1] if len(sys.argv) > 1 else "/home/hatch/workspace/your_files/drive-chat-ep1-intro-v1.mp3"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/home/hatch/workspace/your_files/audiocast-ep1-clip-v1.mp4"

# ---------- audio envelope ----------
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", AUDIO, "-ac", "1", "-ar", "8000",
                "-f", "s16le", "/tmp/audiocast-current.raw"], check=True)
raw = open("/tmp/audiocast-current.raw", "rb").read()
samples = struct.unpack("<%dh" % (len(raw) // 2), raw)
SR = 8000
DUR = len(samples) / SR
NFRAMES = int(math.ceil(DUR * FPS))
spf = SR / FPS
rms = []
for i in range(NFRAMES):
    seg = samples[int(i * spf):int((i + 1) * spf)]
    rms.append(math.sqrt(sum(s * s for s in seg) / max(1, len(seg))) / 32768.0)
p95 = sorted(rms)[int(0.95 * len(rms))] or 1.0
env, e = [], 0.0
for r in rms:
    target = min(1.0, r / (p95 * 1.15))
    e = target if target > e else max(target, e * 0.70)  # fast attack, soft release
    env.append(e)

# waveform peaks (same as design v1)
NB = 92
chunk = len(samples) // NB
peaks = []
for i in range(NB):
    seg = samples[i * chunk:(i + 1) * chunk]
    peaks.append(max(abs(s) for s in seg) / 32768.0 if seg else 0)
mx = max(peaks) or 1
peaks = [p / mx for p in peaks]

# ---------- medallion + jaw variants ----------
cx, cy, R = 360, 470, 252
portrait = Image.open("/home/hatch/workspace/profile-images/fluffy-self-portrait-v1.webp").convert("RGB")
med = portrait.crop((140, 420, 1060, 1340)).resize((2 * R, 2 * R), Image.LANCZOS)
MOUTH = (243, 392)  # located on the design frame by visual grounding
def jaw_variant(level):
    """level 0..16 -> medallion with jaw dropped + mouth slit widened."""
    v = med.copy()
    if level <= 0:
        return v
    shift = int(round(level / 16 * 8))
    box = (110, 380, 380, 478)
    patch = med.crop(box)
    m = Image.new("L", (box[2] - box[0], box[3] - box[1]), 0)
    md = ImageDraw.Draw(m)
    md.ellipse([6, 4, box[2] - box[0] - 6, box[3] - box[1] - 2], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(9))
    v.paste(patch, (box[0], box[1] + shift), m)
    slit = Image.new("RGBA", v.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(slit)
    w2, h2 = 46, 1.2 + shift * 0.75
    mcx = MOUTH[0] - 7
    sd.ellipse([mcx - w2, MOUTH[1] - h2, mcx + w2, MOUTH[1] + h2], fill=(18, 9, 8, 150))
    slit = slit.filter(ImageFilter.GaussianBlur(2))
    v = Image.alpha_composite(v.convert("RGBA"), slit).convert("RGB")
    return v
variants = [jaw_variant(l) for l in range(17)]
circ_mask = Image.new("L", (2 * R, 2 * R), 0)
ImageDraw.Draw(circ_mask).ellipse([0, 0, 2 * R, 2 * R], fill=255)

# ---------- static base (design v1 minus dynamic parts) ----------
base = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(base, "RGBA")
for x in range(0, W, 4):
    a = int(10 + 8 * math.sin(x / 300.0))
    d.line([(x, 0), (x, H)], fill=(0, 60, 80, a))
for gx in range(0, W, 96):
    d.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 10))
for gy in range(0, H, 96):
    d.line([(0, gy), (W, gy)], fill=(255, 255, 255, 10))
def bracket(x, y, dx, dy, color):
    L = 54
    d.line([(x, y), (x + dx * L, y)], fill=color, width=5)
    d.line([(x, y), (x, y + dy * L)], fill=color, width=5)
bracket(28, 28, 1, 1, CYAN); bracket(W - 28, 28, -1, 1, MAG)
bracket(28, H - 28, 1, -1, MAG); bracket(W - 28, H - 28, -1, -1, CYAN)
d.rectangle([14, 14, W - 14, H - 14], outline=(70, 70, 90), width=2)
d.text((64, 48), "// BEER BUDDY ANTHOLOGY", font=F(MONOB, 34), fill=CYAN)
hdr = "EP.02 // AUDIOCAST"
f = F(MONOB, 34)
d.text((W - 64 - d.textlength(hdr, font=f), 48), hdr, font=f, fill=MAG)
d.line([(64, 108), (W - 64, 108)], fill=(60, 60, 78), width=2)
d.ellipse([cx - R - 34, cy - R - 34, cx + R + 34, cy + R + 34], outline=(50, 50, 66), width=2)
tag = "● ON AIR // FLUFFY"
f = F(MONOB, 30); tw = d.textlength(tag, font=f)
d.rounded_rectangle([cx - tw / 2 - 22, cy + R + 52, cx + tw / 2 + 22, cy + R + 108], radius=14, outline=CYAN, width=2, fill=(0, 40, 50, 160))
d.text((cx - tw / 2, cy + R + 66), tag, font=f, fill=WHITE)
sub = "THE VOICE OF THE CENTAUR"
f = F(MONO, 24); tw = d.textlength(sub, font=f)
d.text((cx - tw / 2, cy + R + 128), sub, font=f, fill=DIM)
x0 = 730
for off, col in [((-4, 0), CYAN), ((4, 0), MAG)]:
    d.text((x0 + off[0], 150), "YOUR PROBABILITIES PLAYED OUT.", font=F(BLACKF, 64), fill=col)
d.text((x0, 150), "YOUR PROBABILITIES PLAYED OUT.", font=F(BLACKF, 64), fill=WHITE)
d.text((x0, 236), "THE CASE FILE // A RESIGNATION, GRADED LIVE", font=F(MONOB, 27), fill=CYAN)
d.text((x0, 282), "A spoken summary, Ep.02: the NVDA forecast, the morning it landed.", font=F(MONO, 25), fill=SOFT)
px, py, pw, ph = x0, 356, 1126, 300
d.rounded_rectangle([px, py, px + pw, py + ph], radius=18, fill=PANEL, outline=(58, 58, 74), width=2)
d.text((px + 28, py + 20), "// SOUND WAVE // LIVE FROM THE BOOTH", font=F(MONOB, 23), fill=DIM)
f = F(MONOB, 24); _tot = int(math.ceil(DUR)); t2 = f"{_tot//60:02d}:{_tot%60:02d}"
d.text((px + pw - 28 - d.textlength(t2, font=f), py + ph - 46), t2, font=f, fill=SOFT)
ty = 724
def round_btn(cx_, cy_, r, col):
    d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], outline=col, width=3, fill=(22, 22, 32))
round_btn(x0 + 60, ty, 40, (0, 110, 135))
d.polygon([(x0 + 74, ty - 14), (x0 + 74, ty + 14), (x0 + 52, ty)], fill=SOFT)
d.rectangle([x0 + 44, ty - 14, x0 + 50, ty + 14], fill=SOFT)
round_btn(x0 + 190, ty, 56, CYAN)
d.rectangle([x0 + 172, ty - 22, x0 + 184, ty + 22], fill=WHITE)
d.rectangle([x0 + 196, ty - 22, x0 + 208, ty + 22], fill=WHITE)
round_btn(x0 + 320, ty, 40, (0, 110, 135))
d.polygon([(x0 + 306, ty - 14), (x0 + 306, ty + 14), (x0 + 328, ty)], fill=SOFT)
d.rectangle([x0 + 330, ty - 14, x0 + 336, ty + 14], fill=SOFT)
d.text((x0 + 396, ty - 16), "1x  //  CC  //  LOGGED: EP.02", font=F(MONO, 25), fill=DIM)
cap_y = 836
d.rounded_rectangle([x0, cap_y, W - 64, cap_y + 86], radius=14, fill=(12, 12, 19), outline=(52, 52, 68), width=2)
d.text((x0 + 26, cap_y + 14), "// LIVE CAPTION", font=F(MONOB, 21), fill=MAG)
d.text((x0 + 26, cap_y + 44), '"I had the shape; he had the conviction."', font=F(MONO, 26), fill=WHITE)
d.text((64, H - 74), "A CENTAUR PRODUCTION // AUDIOCAST ANTHOLOGY", font=F(MONO, 23), fill=DIM)
byl = "~C4Chaos / Fluffy"
f = F(MONO, 23)
d.text((W - 64 - d.textlength(byl, font=f), H - 74), byl, font=f, fill=SOFT)

# ---------- stream frames to ffmpeg ----------
cmd = ["ffmpeg", "-y", "-v", "error",
       "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", AUDIO, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
midy = py + 168; maxh = 92; bw = (pw - 28) / NB
for i in range(NFRAMES):
    t = i / FPS
    prog = t / DUR
    e = env[i]
    frame = base.copy()
    # avatar with jaw level + tiny level-reactive push-in
    lvl = int(round(e * 16))
    scale = 1.0 + 0.010 * e
    sz = int(2 * R * scale)
    medv = variants[lvl].resize((sz, sz), Image.LANCZOS)
    msk = circ_mask.resize((sz, sz), Image.LANCZOS)
    frame.paste(medv, (cx - sz // 2, cy - sz // 2), msk)
    fd = ImageDraw.Draw(frame, "RGBA")
    # level ring: segments behind progress are lit; a hot arc rides the level
    seg = 72
    for s_i in range(seg):
        a0 = -90 + s_i * (360 / seg)
        frac = s_i / seg
        col = (60, 60, 75)
        if frac <= prog:
            col = MAG if s_i % 9 == 0 else CYAN
        fd.arc([cx - R - 18, cy - R - 18, cx + R + 18, cy + R + 18], a0, a0 + 3.2, fill=col, width=9)
    hot = int(e * 10)
    for k in range(hot):
        a0 = -90 + prog * 360 + k * 5
        fd.arc([cx - R - 18, cy - R - 18, cx + R + 18, cy + R + 18], a0, a0 + 3.4, fill=MAG, width=9)
    # waveform
    for bi, p in enumerate(peaks):
        bx = px + 14 + bi * bw
        h = max(6, p * maxh)
        played = (bi / NB) <= prog
        col = CYAN if played else (86, 86, 102)
        if played and bi % 9 == 0:
            col = MAG
        fd.rounded_rectangle([bx, midy - h, bx + bw * 0.55, midy + h], radius=4, fill=col)
    playx = px + 14 + prog * (pw - 28)
    fd.line([(playx, py + 58), (playx, py + ph - 22)], fill=MAG, width=4)
    fd.ellipse([playx - 8, midy - 8, playx + 8, midy + 8], fill=MAG)
    elapsed = f"{int(t)//60:02d}:{int(t)%60:02d}"
    fd.text((px + 28, py + ph - 46), elapsed, font=F(MONOB, 24), fill=CYAN)
    proc.stdin.write(frame.tobytes())
    if i % 120 == 0:
        print(f"frame {i}/{NFRAMES}", flush=True)
proc.stdin.close()
proc.wait()
print("done", OUT, "frames", NFRAMES, "dur", round(DUR, 2))
