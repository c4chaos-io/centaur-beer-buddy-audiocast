#!/usr/bin/env python3
"""Audiocast Anthology player design v1 (static frame mockup).
TPS theme: near-black, neon cyan + magenta, mono labels, // markers, HUD frame.
Avatar: canon self-portrait composited (not regenerated), face crop in a
circular medallion ringed by a level-meter arc.
Waveform: real peaks decoded from the Ep1 intro mp3.
"""
import math, struct
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
BG = (8, 8, 13)
CYAN = (0, 229, 255)
CYAN_DIM = (0, 110, 135)
MAG = (230, 0, 174)
WHITE = (235, 235, 240)
SOFT = (200, 200, 205)
DIM = (120, 120, 135)
PANEL = (16, 16, 24)

BLACK = "/usr/share/fonts/truetype/noto/NotoSansDisplay-Black.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img, "RGBA")

# subtle vertical glow bands
for x in range(0, W, 4):
    a = int(10 + 8 * math.sin(x / 300.0))
    d.line([(x, 0), (x, H)], fill=(0, 60, 80, a))
# faint grid
for gx in range(0, W, 96):
    d.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 10))
for gy in range(0, H, 96):
    d.line([(0, gy), (W, gy)], fill=(255, 255, 255, 10))

# HUD frame: cyan left/top, magenta right/bottom corner brackets
def bracket(x, y, dx, dy, color):
    L = 54
    d.line([(x, y), (x + dx * L, y)], fill=color, width=5)
    d.line([(x, y), (x, y + dy * L)], fill=color, width=5)
bracket(28, 28, 1, 1, CYAN)
bracket(W - 28, 28, -1, 1, MAG)
bracket(28, H - 28, 1, -1, MAG)
bracket(W - 28, H - 28, -1, -1, CYAN)
d.rectangle([14, 14, W - 14, H - 14], outline=(70, 70, 90), width=2)

# ---- header bar ----
d.text((64, 48), "// BEER BUDDY ANTHOLOGY", font=font(MONOB, 34), fill=CYAN)
hdr_r = "EP.01 // AUDIOCAST"
f = font(MONOB, 34)
tw = d.textlength(hdr_r, font=f)
d.text((W - 64 - tw, 48), hdr_r, font=f, fill=MAG)
d.line([(64, 108), (W - 64, 108)], fill=(60, 60, 78), width=2)

# ---- avatar medallion (left) ----
cx, cy, R = 360, 470, 252
portrait = Image.open("/home/hatch/workspace/profile-images/fluffy-self-portrait-v1.webp").convert("RGB")
# face crop: head occupies roughly x 150..1050, y 430..1300 in the 1120x2240 portrait
crop = portrait.crop((140, 420, 1060, 1340)).resize((2 * R, 2 * R), Image.LANCZOS)
mask = Image.new("L", (2 * R, 2 * R), 0)
md = ImageDraw.Draw(mask)
md.ellipse([0, 0, 2 * R, 2 * R], fill=255)
img.paste(crop, (cx - R, cy - R), mask)
d = ImageDraw.Draw(img, "RGBA")
# level-meter ring: segmented arc, cyan sweeping to magenta near the top right
seg = 72
for i in range(seg):
    a0 = -90 + i * (360 / seg)
    frac = i / seg
    col = CYAN if frac < 0.62 else (MAG if frac < 0.8 else (60, 60, 75))
    d.arc([cx - R - 18, cy - R - 18, cx + R + 18, cy + R + 18], a0, a0 + 3.2, fill=col, width=9)
d.ellipse([cx - R - 34, cy - R - 34, cx + R + 34, cy + R + 34], outline=(50, 50, 66), width=2)
# ON AIR tag under medallion
tag = "● ON AIR // FLUFFY"
f = font(MONOB, 30)
tw = d.textlength(tag, font=f)
d.rounded_rectangle([cx - tw / 2 - 22, cy + R + 52, cx + tw / 2 + 22, cy + R + 108], radius=14, outline=CYAN, width=2, fill=(0, 40, 50, 160))
d.text((cx - tw / 2, cy + R + 66), tag, font=f, fill=WHITE)
# voice label
sub = "VOICE: FRETUL OAK // VERY DEEP BRITISH"
sub = "THE VOICE OF THE CENTAUR"
f = font(MONO, 24)
tw = d.textlength(sub, font=f)
d.text((cx - tw / 2, cy + R + 128), sub, font=f, fill=DIM)

# ---- right column: title ----
x0 = 730
title = "THE CENTAUR NOW HAS A VOICE."
# glitch offsets
for off, col in [((-4, 0), CYAN), ((4, 0), MAG)]:
    d.text((x0 + off[0], 150), title, font=font(BLACK, 64), fill=col)
d.text((x0, 150), title, font=font(BLACK, 64), fill=WHITE)
d.text((x0, 236), "MORNING DRIVE // RAIN, TRAFFIC, TWO BEER BUDDIES", font=font(MONOB, 27), fill=CYAN)
d.text((x0, 282), "A spoken summary, Ep.01: the first drive chat, logged.", font=font(MONO, 25), fill=SOFT)

# ---- waveform panel ----
px, py, pw, ph = x0, 356, 1126, 300
d.rounded_rectangle([px, py, px + pw, py + ph], radius=18, fill=PANEL, outline=(58, 58, 74), width=2)
d.text((px + 28, py + 20), "// SOUND WAVE // LIVE FROM THE BOOTH", font=font(MONOB, 23), fill=DIM)
# real peaks from the decoded mp3
raw = open("/tmp/ep1.raw", "rb").read()
samples = struct.unpack("<%dh" % (len(raw) // 2), raw)
NB = 92
chunk = len(samples) // NB
peaks = []
for i in range(NB):
    segd = samples[i * chunk:(i + 1) * chunk]
    peaks.append(max(abs(s) for s in segd) / 32768.0 if segd else 0)
mx = max(peaks) or 1
peaks = [p / mx for p in peaks]
midy = py + 168
maxh = 92
play_frac = 0.38
bw = (pw - 28) / NB
for i, p in enumerate(peaks):
    bx = px + 14 + i * bw
    h = max(6, p * maxh)
    played = (i / NB) <= play_frac
    col = CYAN if played else (86, 86, 102)
    if played and i % 9 == 0:
        col = MAG
    d.rounded_rectangle([bx, midy - h, bx + bw * 0.55, midy + h], radius=4, fill=col)
playx = px + 14 + play_frac * (pw - 28)
d.line([(playx, py + 58), (playx, py + ph - 22)], fill=MAG, width=4)
d.ellipse([playx - 8, midy - 8, playx + 8, midy + 8], fill=MAG)
# progress + times
d.text((px + 28, py + ph - 46), "00:09", font=font(MONOB, 24), fill=CYAN)
f = font(MONOB, 24)
t2 = "00:25"
d.text((px + pw - 28 - d.textlength(t2, font=f), py + ph - 46), t2, font=f, fill=SOFT)

# ---- transport controls ----
ty = 724
# skip back
def round_btn(cx_, cy_, r, outline_col):
    d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], outline=outline_col, width=3, fill=(22, 22, 32))
round_btn(x0 + 60, ty, 40, CYAN_DIM)
d.polygon([(x0 + 74, ty - 14), (x0 + 74, ty + 14), (x0 + 52, ty)], fill=SOFT)
d.rectangle([x0 + 44, ty - 14, x0 + 50, ty + 14], fill=SOFT)
# main play/pause (paused state = playing)
round_btn(x0 + 190, ty, 56, CYAN)
d.rectangle([x0 + 172, ty - 22, x0 + 184, ty + 22], fill=WHITE)
d.rectangle([x0 + 196, ty - 22, x0 + 208, ty + 22], fill=WHITE)
# skip fwd
round_btn(x0 + 320, ty, 40, CYAN_DIM)
d.polygon([(x0 + 306, ty - 14), (x0 + 306, ty + 14), (x0 + 328, ty)], fill=SOFT)
d.rectangle([x0 + 330, ty - 14, x0 + 336, ty + 14], fill=SOFT)
d.text((x0 + 396, ty - 16), "1x  //  CC  //  LOGGED: EP.01", font=font(MONO, 25), fill=DIM)

# ---- caption strip ----
cap_y = 836
d.rounded_rectangle([x0, cap_y, W - 64, cap_y + 86], radius=14, fill=(12, 12, 19), outline=(52, 52, 68), width=2)
d.text((x0 + 26, cap_y + 14), "// LIVE CAPTION", font=font(MONOB, 21), fill=MAG)
d.text((x0 + 26, cap_y + 44), '"The Centaur now has a voice. And we BOTH get to be useful."', font=font(MONO, 26), fill=WHITE)

# ---- footer ----
d.text((64, H - 74), "A CENTAUR PRODUCTION // AUDIOCAST ANTHOLOGY", font=font(MONO, 23), fill=DIM)
byl = "~C4Chaos / Fluffy"
f = font(MONO, 23)
d.text((W - 64 - d.textlength(byl, font=f), H - 74), byl, font=f, fill=SOFT)

img.save("/home/hatch/workspace/your_files/audiocast-player-design-v1.png")
img.save("/home/hatch/workspace/audiocast/design/audiocast-player-design-v1.png")
print("saved", img.size)
