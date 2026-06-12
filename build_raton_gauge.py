#!/usr/bin/env python3
"""Jauge de mana homme-raton — assemblage APNG (recette panel design 2026-06-12).

Concept « la flamme EST le portail » : vortex face-caméra en rotation
CONTINUE (le fond vit en permanence, boucle parfaite 360°/N), le raton
émerge À TRAVERS l'énergie via des keyframes GÉNÉRÉES plein-cadre
(gpt-image-2, volutes peintes devant la fourrure — pas de découpage),
fondues en blend smoothstep pendant que le vortex tourne. L'anneau
d'argent de la jauge ORIGINALE est ré-imposé bit-identique sur chaque
frame (tue le ghosting inter-générations).

Entrées (1024², harvest codex) : /tmp/vortex-base.png, /tmp/kf-S1.png,
/tmp/kf-S2a.png, /tmp/kf-S2b.png + Icone/Gauge_Magie_v2.webp (base).
Sortie : Icone/Gauge_Magie_Raton_v3.png (APNG 256², 72 frames @ 83 ms).
"""
import math
import numpy as np
from PIL import Image, ImageChops, ImageFilter

BASE = Image.open('Icone/Gauge_Magie_v2.webp').convert('RGBA').resize((256, 256), Image.LANCZOS)
W = H = 256
CX = CY = 128


def load(p):
    return Image.open(p).convert('RGBA').resize((W, H), Image.LANCZOS)


vortex = load(r'C:\Users\Renaud\AppData\Local\Temp\vortex-base.png')
S1 = load(r'C:\Users\Renaud\AppData\Local\Temp\kf-S1.png')
S2a = load(r'C:\Users\Renaud\AppData\Local\Temp\kf-S2a.png')
S2b = load(r'C:\Users\Renaud\AppData\Local\Temp\kf-S2b.png')

# ── Histogram-match doux de chaque keyframe vers le vortex (contention de
#    dérive chromatique inter-générations) : moyenne/σ par canal, intérieur.
yy, xx = np.mgrid[0:H, 0:W]
rr = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
disc = rr <= 110


def match(img, ref):
    a = np.asarray(img, dtype=np.float32)
    b = np.asarray(ref, dtype=np.float32)
    out = a.copy()
    for c in range(3):
        am, asd = a[..., c][disc].mean(), a[..., c][disc].std() + 1e-5
        bm, bsd = b[..., c][disc].mean(), b[..., c][disc].std() + 1e-5
        matched = (a[..., c] - am) * (bsd / asd) + bm
        out[..., c] = np.clip(0.6 * matched + 0.4 * a[..., c], 0, 255)  # 60 % matché
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


S1, S2a, S2b = match(S1, vortex), match(S2a, vortex), match(S2b, vortex)

# ── Masques (une fois) ──────────────────────────────────────────────────
# Disque interne r=112, feather 5.
disc_mask = Image.new('L', (W, H), 0)
d = np.zeros((H, W), dtype=np.uint8)
d[rr <= 112] = 255
disc_mask = Image.fromarray(d).filter(ImageFilter.GaussianBlur(5))

# Anneau de la BASE : r>116 OU (luminance>70 ET 86<r<118), dilaté + adouci.
lum = np.asarray(BASE.convert('L'), dtype=np.float32)
ring = (rr > 116) | ((lum > 70) & (rr > 86) & (rr < 118))
ring_mask = Image.fromarray((ring * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))
ring_img = BASE.copy()
ring_img.putalpha(ring_mask)


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


N = 48
DUR = 100  # fallback poids du panel (72@83 -> 3,2 Mo)
frames = []

# Timeline (panel) : rotation continue 360°/N ; raton S1 in f18-26 ;
# S1→S2a f26-32 ; vague S2a↔S2b f32-48 ; retrait f48-60 ; vortex nu sinon.
for i in range(N):
    ang = 360.0 * i / N
    # couche intérieure courante : vortex tourné
    rot_v = vortex.rotate(ang, resample=Image.BICUBIC, center=(CX, CY))

    # poids des keyframes raton (elles aussi tournent LÉGÈREMENT moins —
    # le raton ne doit pas tournoyer : on tourne seulement le vortex, le
    # raton-keyframe reste droit ; la transition se noie dans le blend).
    interior = rot_v
    def blend_to(img, w):
        return Image.blend(interior, img, w)

    if 12 <= i < 17:
        interior = blend_to(S1, smoothstep((i - 12) / 5))
    elif 17 <= i < 21:
        interior = Image.blend(S1, S2a, smoothstep((i - 17) / 4))
    elif 21 <= i < 32:
        ph = (i - 21) / 11.0
        w = 0.5 - 0.5 * math.cos(2 * math.pi * 2 * ph)  # 2 allers-retours
        interior = Image.blend(S2a, S2b, w)
    elif 32 <= i < 36:
        interior = Image.blend(S2a, S1, smoothstep((i - 32) / 4))
    elif 36 <= i < 40:
        interior = Image.blend(S1, rot_v, smoothstep((i - 36) / 4))

    # compose : base (fond) ← intérieur via disque ← anneau ré-imposé
    frame = BASE.copy()
    frame.paste(interior, (0, 0), disc_mask)

    # glow pulsé loop-safe (3 cycles entiers) + flash sur les morphs
    amp = 0.22 + 0.18 * math.sin(2 * math.pi * 3 * i / N)
    if 10 <= i < 13 or 38 <= i < 41:
        amp += 0.35
    glow = frame.filter(ImageFilter.GaussianBlur(8))
    glow = Image.eval(glow, lambda v: int(v * amp))
    frame = ImageChops.screen(frame, glow)

    frame.alpha_composite(ring_img, (0, 0))
    frames.append(frame.convert('RGBA'))

# ── Export palettisé (parade poids du panel) : palette maîtresse partagée,
#    P-mode opaque — les coins carrés sont masqués par le border-radius:50%
#    du CSS .icone, l'alpha est inutile ici.
sample = Image.new('RGB', (W * 18, H))
for k, idx in enumerate(range(0, N, 4)):
    sample.paste(frames[idx].convert('RGB'), (k * W, 0))
master = sample.quantize(256, method=Image.MEDIANCUT)
frames_p = [f.convert('RGB').quantize(palette=master, dither=Image.FLOYDSTEINBERG) for f in frames]
frames_p[0].save('Icone/Gauge_Magie_Raton_v3.png', format='PNG', save_all=True,
                 append_images=frames_p[1:], duration=DUR, loop=0)
data = open('Icone/Gauge_Magie_Raton_v3.png', 'rb').read()
print(f'frames: {N} | acTL: {b"acTL" in data} | fcTL: {data.count(b"fcTL")} | taille: {len(data)/1e6:.2f} Mo')
# exports de contrôle
frames[0].save(r'C:\Users\Renaud\AppData\Local\Temp\rg-f0.png')
frames[15].save(r'C:\Users\Renaud\AppData\Local\Temp\rg-f22.png')
frames[26].save(r'C:\Users\Renaud\AppData\Local\Temp\rg-f38.png')
frames[38].save(r'C:\Users\Renaud\AppData\Local\Temp\rg-f57.png')
