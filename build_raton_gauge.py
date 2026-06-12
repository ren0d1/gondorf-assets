#!/usr/bin/env python3
"""Jauge de mana homme-raton — assemblage APNG v4 (recette panel design #2, 2026-06-12).

Réponse aux 6 griefs v3 : (1) au repos la frame EST la statique (octets) ;
(2-3) fond/ornements/anneau ne bougent JAMAIS (gates mécaniques) ; (5) seule
la zone spirale tourne — et seule sa composante HAUTE FRÉQUENCE (la basse
fréquence fixe porte les gradients qui trahiraient la rotation) ; (4)
émergence par TRANSLATION à travers une « lèvre de trappe » + dissolves
étagés sur 5 keyframes ; (6) gag : banane brandie → gueule ouverte → GULP
(smear) → joues ballon → grimace langue rose → aspiré par le vortex
(« chasse d'eau » : le vortex ré-accélère au flush).

Sprites = matte différentiel (|KF − statique| seuillé) ∧ masque-flamme de la
statique : le raton/banane ne peuvent JAMAIS recouvrir le fond sombre, les
ornements ou l'anneau. Le clip radial disque du panel est remplacé par ce
masque-flamme (mesure : la banane des KF vit au-dessus du portail, un clip
r54 l'aurait amputée — grief v2 « crop »).

Entrées : Icone/Gauge_Magie_v2.webp (statique 256², JAMAIS resamplée) +
Icone/raton_v4/KF{1..5}.raw.png (1024², chaîne gpt-image-2).
Sortie : Icone/Gauge_Magie_Raton_v4.png (APNG 256², 64 frames, délais
variables, cycle ≈ 10,2 s).
"""
import math
import numpy as np
from PIL import Image, ImageChops, ImageFilter

W = H = 256
CX, CY = 128, 166          # coeur de la spirale (portail)
R_ROT_IN, R_ROT_OUT = 44, 58   # feather raised-cosine de la couche tournante
SIGMA_LP = 6                   # split basse/haute fréquence
Y_LIP, LIP_W = 178, 16         # lèvre de trappe (occluder fixe, coords statiques)
DIFF_T = 84                    # seuil matte (somme 3 canaux)
N = 64

static_img = Image.open('Icone/Gauge_Magie_v2.webp').convert('RGB')
static = np.asarray(static_img, dtype=np.float32)

yy, xx = np.mgrid[0:H, 0:W]
r_c = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)      # rayon depuis le portail
r_img = np.sqrt((xx - 128) ** 2 + (yy - 128) ** 2)  # rayon depuis le centre image


def raised_cosine(r, a, b):
    t = np.clip((r - a) / (b - a), 0, 1)
    return 0.5 + 0.5 * np.cos(math.pi * t)


def smoothstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def smootherstep(t):
    t = np.clip(t, 0, 1)
    return t * t * t * (t * (t * 6 - 15) + 10)


def blur(arr, sigma):
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(sigma)), dtype=np.float32)


# ── Masque-flamme de la statique : zone lumineuse bleue, anneau exclu ──────
val = static.max(axis=2)
fm = (val > 64) & (r_img <= 100)
fm_img = Image.fromarray((fm * 255).astype(np.uint8)) \
    .filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(4))
flame_mask = np.asarray(fm_img, dtype=np.float32) / 255.0
flame_mask *= np.clip((100 - r_img) / 6.0, 0, 1)   # garde dure : zéro vers l'anneau

# ── Split fréquentiel du disque tournant ───────────────────────────────────
low = np.stack([blur(static[..., c], SIGMA_LP) for c in range(3)], axis=2)
high = static - low
rot_alpha = raised_cosine(r_c, R_ROT_IN, R_ROT_OUT)[..., None]


def rotated_disc(theta):
    """low fixe + high tourné de theta autour du portail. Jamais rotate(0)."""
    if abs(theta % 360.0) < 1e-6:
        return static.copy()
    enc = Image.fromarray(np.clip(high + 128, 0, 255).astype(np.uint8))
    rot = enc.rotate(theta, resample=Image.BICUBIC, center=(CX, CY),
                     fillcolor=(128, 128, 128))
    return np.clip(low + np.asarray(rot, dtype=np.float32) - 128, 0, 255)


# ── Sprites : keyframes histogram-matchées + matte différentiel ∧ flamme ───
ann = (r_c >= 30) & (r_c <= 50)   # anneau de flamme autour du portail (ancre du match)


def load_sprite(i):
    kf_img = Image.open(f'Icone/raton_v4/KF{i}.raw.png').convert('RGB').resize((W, H), Image.LANCZOS)
    kf = np.asarray(kf_img, dtype=np.float32)
    out = kf.copy()
    for c in range(3):
        m_s, s_s = static[..., c][ann].mean(), static[..., c][ann].std() + 1e-5
        m_k, s_k = kf[..., c][ann].mean(), kf[..., c][ann].std() + 1e-5
        # 35 % matché seulement : à 60 % le raton entier virait bleu lavande
        # (l'ancre anneau-de-flamme est très saturée) et perdait son identité
        # gris/masque-noir/museau-blanc — illisible à taille de jeu.
        out[..., c] = np.clip(0.35 * ((kf[..., c] - m_k) * (s_s / s_k) + m_s)
                              + 0.65 * kf[..., c], 0, 255)
    diff = np.abs(out - static).sum(axis=2)
    m = Image.fromarray(((diff > DIFF_T) * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))   # close
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))   # open
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(3)), dtype=np.float32) / 255.0
    # NB: flame_mask est appliqué APRÈS transformation (un sprite translaté
    # déborderait sinon du blob de flamme — fuite détectée par le gate).
    ys, xs = np.nonzero((a * flame_mask) > 0.3)
    print(f'  KF{i}: matte bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}] '
          f'centroid=({xs.mean():.0f},{ys.mean():.0f})')
    return out, a


SPR = {i: load_sprite(i) for i in range(1, 6)}


def transform_sprite(i, dx, dy, sc):
    """Translate/scale (autour du portail) le sprite i et son alpha — bilinéaire."""
    kf, a = SPR[i]
    if dx == 0 and dy == 0 and sc == 1.0:
        return kf, a
    rgba = np.dstack([kf, a * 255]).astype(np.uint8)
    img = Image.fromarray(rgba, 'RGBA')
    # mapping inverse dst->src : src = (dst - C - d)/sc + C
    mat = (1 / sc, 0, CX - (CX + dx) / sc, 0, 1 / sc, CY - (CY + dy) / sc)
    out = img.transform((W, H), Image.AFFINE, mat, resample=Image.BILINEAR,
                        fillcolor=(0, 0, 0, 0))
    arr = np.asarray(out, dtype=np.float32)
    return arr[..., :3], arr[..., 3] / 255.0


def vblur(arr3, alpha):
    """Smear vertical ±2 px (frame de gulp)."""
    acc3, acca = np.zeros_like(arr3), np.zeros_like(alpha)
    for s in (-2, -1, 0, 1, 2):
        acc3 += np.roll(arr3, s, axis=0)
        acca += np.roll(alpha, s, axis=0)
    return acc3 / 5, acca / 5


lip_mask = np.clip((Y_LIP + LIP_W / 2 - yy) / LIP_W, 0, 1).astype(np.float32)  # 1 au-dessus, 0 sous
core_glow = raised_cosine(r_c, 36, 44)
band = np.clip(1 - np.abs(yy - 181) / 9.0, 0, 1) * (r_c <= 46)   # volutes de jonction y172-190

# ── Profil d'angle : poids par frame, cumsum normalisé à 720° exact ────────
w = np.zeros(N)
w[1:9] = (np.arange(1, 9) / 8.0) ** 3            # spin-up ease-in³
w[9:13] = 1.0                                     # cruise
w[13:21] = np.linspace(1.0, 0.35, 8)              # rise (décélère)
w[21:50] = 0.12                                   # drift (jeu d'acteur)
w[50:55] = np.linspace(0.3, 0.9, 5)               # flush (ré-accélère)
w[55:63] = 0.9 * (1 - smootherstep(np.arange(8) / 7.0))   # spin-down
theta = np.concatenate([[0], np.cumsum(w)[:-1]])
theta = theta * (720.0 / (theta[-1] + w[-1]))     # theta[63]+w[63] boucle à 720
theta[0] = 0.0

# opacité de la couche tournante / glow
rot_op = np.ones(N)
rot_op[0] = 0.0
rot_op[1:5] = np.linspace(0.25, 1.0, 4)
rot_op[59:63] = np.linspace(0.75, 0.0, 4)
rot_op[63] = 0.0

glow = np.zeros(N)
glow[1:9] = np.linspace(0, 0.12, 8)
glow[9:50] = 0.12 + 0.03 * np.sin(2 * math.pi * np.arange(41) / 20.0)  # respiration
glow[50:53] = 0.12
glow[53:55] = 0.27                                # éclaboussure du flush
glow[55:63] = np.linspace(0.12, 0, 8)

# ── Délais (ms) par frame ─────────────────────────────────────────────────
delays = [100] * N
delays[0] = 3000
for f in range(1, 9): delays[f] = 90
for f in range(21, 25): delays[f] = 110
delays[31] = 300
for f in range(32, 35): delays[f] = 90
delays[35] = 250
for f in range(36, 39): delays[f] = 80
delays[39] = 300
for f in range(47, 50): delays[f] = 160
for f in range(50, 55): delays[f] = 80
for k, f in enumerate(range(55, 63)): delays[f] = 90 + round(k * 40 / 7)
delays[63] = 400


def poses(f):
    """[(kf, weight, dx, dy, scale, lip, smear)] pour la frame f."""
    if 13 <= f <= 20:      # RISE : translation à travers la lèvre
        al = min((f - 13) / 3.0, 1.0)
        dy = 36 * (1 - float(smoothstep((f - 13) / 7.0)))
        return [(1, al, 0, dy, 1.0, True, False)]
    if 21 <= f <= 24:      # HOLD « qui, moi ? » + bob
        return [(1, 1, 0, round(math.sin(2 * math.pi * (f - 21) / 4.0)), 1.0, False, False)]
    if 25 <= f <= 28:      # dissolve tête -> banane brandie
        u = float(smoothstep((f - 24) / 4.0))
        return [(1, 1 - u, 0, 0, 1.0, False, False), (2, u, 0, 0, 1.0, False, False)]
    if 29 <= f <= 31:      # PRÉSENTATION
        return [(2, 1, 0, 0, 1.0, False, False)]
    if 32 <= f <= 34:      # dissolve -> gueule ouverte
        u = float(smoothstep((f - 31) / 3.0))
        return [(2, 1 - u, 0, 0, 1.0, False, False), (3, u, 0, 0, 1.0, False, False)]
    if f == 35:            # ANTICIPATION
        return [(3, 1, 0, 0, 1.0, False, False)]
    if 36 <= f <= 38:      # GULP rapide, smear sur la frame entrante
        u = (f - 35) / 3.0
        return [(3, 1 - u, 0, 0, 1.0, False, f == 36), (4, u, 0, 0, 1.0, False, f == 36)]
    if 39 <= f <= 42:      # BEAT SACRÉ joues ballon + micro-bounce
        sc = {39: 1.00, 40: 1.03, 41: 1.01, 42: 1.00}[f]
        return [(4, 1, 0, 0, sc, False, False)]
    if 43 <= f <= 46:      # dissolve -> grimace
        u = float(smoothstep((f - 42) / 4.0))
        return [(4, 1 - u, 0, 0, 1.0, False, False), (5, u, 0, 0, 1.0, False, False)]
    if 47 <= f <= 49:      # BEURK + jitter
        return [(5, 1, [1, -1, 1][f - 47], 0, 1.0, False, False)]
    if 50 <= f <= 54:      # FLUSH : aspiré par le vortex
        t = (f - 49) / 5.0
        return [(5, 1 - t, 0, 40 * t * t, 1 - 0.08 * t, True, False)]
    return []


GLOW_COLOR = np.array([170, 195, 255], dtype=np.float32)
neutral_zone = (flame_mask < 0.02) & (r_c > R_ROT_OUT)   # ni flamme ni portail
ring_zone = r_img >= 103

frames = []
for f in range(N):
    if f in (0, N - 1):
        frames.append(static_img.copy())
        continue
    disc = rotated_disc(theta[f])
    a_rot = rot_alpha * rot_op[f]
    img = static * (1 - a_rot) + disc * a_rot
    if glow[f] > 0:    # screen du glow bleuté au coeur
        g = core_glow[..., None] * glow[f]
        img = 255 - (255 - img) * (255 - GLOW_COLOR * g) / 255
    for (i, wgt, dx, dy, sc, lip, smear) in poses(f):
        spr, al = transform_sprite(i, dx, dy, sc)
        if smear:
            spr, al = vblur(spr, al)
        if lip:
            al = al * lip_mask
        a = (al * flame_mask * wgt)[..., None]
        img = img * (1 - a) + spr * a
    vb = (band * 0.25)[..., None]                  # volutes tournées par-dessus la jonction
    img = img * (1 - vb) + disc * vb
    leak = np.abs(img - static)[neutral_zone].max()
    rleak = np.abs(img - static)[ring_zone].max()
    assert leak < 6 and rleak < 6, f'masque fuyard frame {f}: flamme {leak:.0f} / anneau {rleak:.0f}'
    img = np.where((neutral_zone | ring_zone)[..., None], static, img)   # ré-imposition
    frames.append(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)))

assert abs(theta[-1] + w[-1] - 720.0) < 1e-6 and np.all(np.diff(theta) >= 0)
print(f'theta[63]={theta[-1]:.1f}+w -> 720 ; frames={len(frames)}')

# ── Export : palette maîtresse partagée (échantillon incluant banane+langue)
sample_ids = list(range(0, N, 4)) + [30, 37, 40, 48]
sample = Image.new('RGB', (W * len(sample_ids), H))
for k, idx in enumerate(sample_ids):
    sample.paste(frames[idx], (k * W, 0))
master = sample.quantize(256, method=Image.MEDIANCUT)
frames_p = [fr.quantize(palette=master, dither=Image.FLOYDSTEINBERG) for fr in frames]
frames_p[0].save('Icone/Gauge_Magie_Raton_v4.png', format='PNG', save_all=True,
                 append_images=frames_p[1:], duration=delays, loop=0)
data = open('Icone/Gauge_Magie_Raton_v4.png', 'rb').read()
print(f'frames: {N} | acTL: {b"acTL" in data} | fcTL: {data.count(b"fcTL")} | '
      f'taille: {len(data)/1e6:.2f} Mo | cycle: {sum(delays)/1000:.1f} s')

# ── Frames de contrôle + contact sheets ───────────────────────────────────
TMP = r'C:\Users\Renaud\AppData\Local\Temp'
for f in (6, 10, 16, 22, 30, 35, 37, 40, 45, 48, 52, 58):
    frames[f].save(rf'{TMP}\rv4-f{f:02d}.png')
sheet = Image.new('RGB', (8 * 128, 8 * 128))
for f in range(N):
    sheet.paste(frames[f].resize((128, 128), Image.LANCZOS), ((f % 8) * 128, (f // 8) * 128))
sheet.save(rf'{TMP}\rv4-sheet.png')
mini = Image.new('RGB', (16 * 36, 4 * 36), (24, 24, 24))
for k, f in enumerate(range(0, N)):
    mini.paste(frames[f].resize((32, 32), Image.LANCZOS), ((k % 16) * 36 + 2, (k // 16) * 36 + 2))
mini.save(rf'{TMP}\rv4-gamesize.png')
print('contrôles exportés')
