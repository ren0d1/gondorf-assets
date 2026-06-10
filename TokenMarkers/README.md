# Set de marqueurs de token custom — Gondorf

8 marqueurs custom aux **noms maison** (français — aucun nom du set par
défaut Roll20 n'est français, collision impossible). `tread` (Botte /
compte de blessures) reste volontairement sur le marqueur Roll20 par
défaut (décision user 2026-06-10).

| Fichier | Nom de marqueur (OBLIGATOIRE, exact) | État de jeu | Fallback défaut |
|---|---|---|---|
| `transcendance.png` | `transcendance` | Transcendance (transe Pouvoir), badge = durée | overdrive |
| `aura-saigneur.png` | `aura-saigneur` | Aura du Saigneur — porteur (vérité du cycle de vie, ADR-025) | aura |
| `zone-de-mort.png` | `zone-de-mort` | Aura du Saigneur — cible ≤ 9 m (+1d4 dégâts mêlée) | death-zone |
| `harnais-blanc.png` | `harnais-blanc` | Harnais Blanc — badge de connexion Récepteur (0-2) | angel-outfit |
| `peau-de-caillou.png` | `peau-de-caillou` | Peau de Caillou — buff (+3 PP / +1 PM) | bolt-shield |
| `renforcement.png` | `renforcement` | Renforcement du Corps — Force=75 tant que marqué | strong |
| `destabilise.png` | `destabilise` | Suture Vive — déstabilisé (−5 prochaine action, MJ) | snail |
| `inconscient.png` | `inconscient` | Scellement des Chaires — KO 2 tours (jet Rési raté) | sleepy |

## Installation (MJ, une seule fois par partie)

1. Roll20 → **Game Settings → Token Markers → Create a new set**
   (ex. nom du set : `Gondorf`).
2. Uploader les 8 PNG de ce dossier.
3. Renommer chaque marqueur avec le nom EXACT de la colonne 2.
4. Dans la partie : **Game Settings → activer le set** (garder aussi le
   set par défaut actif — pour `tread` et les marqueurs posés à la main).

## Comment le mod résout les noms (zéro action code)

`lib/Roll20/statusMarkers.js` (repo principal) référence les marqueurs
par **nom logique** (colonne 2) et résout au runtime via
`Campaign().get('token_markers')` :

- **Set custom installé** → le mod écrit le tag custom
  (`<nom>::<id>`) dans la chaîne `statusmarkers` du token.
- **Pas de set custom** → fallback automatique sur le marqueur par
  défaut de la colonne 4 (comportement historique inchangé).

Les LECTURES acceptent les deux formes : un token marqué avant
l'installation du set continue de fonctionner. Le cache de résolution
est de 30 s — après l'upload du set, le mod bascule sur les customs en
moins d'une minute (ou immédiatement après un restart sandbox).

Source d'inventaire : `docs/audits/2026-06-06-token-markers-inventory.md`
(+ `renforcement`/`destabilise`/`inconscient` ajoutés depuis).
