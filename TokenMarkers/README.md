# Set de marqueurs de token custom — Gondorf

Marqueurs custom pour les 5 status markers écrits par le mod. `tread`
(Botte / compte de blessures) reste volontairement sur le marqueur Roll20
par défaut (décision user 2026-06-10).

| Fichier | Nom de marqueur (OBLIGATOIRE, exact) | État de jeu |
|---|---|---|
| `overdrive.png` | `overdrive` | Transcendance (transe Pouvoir), badge = durée |
| `aura.png` | `aura` | Aura du Saigneur — porteur (source de vérité du cycle de vie, ADR-025) |
| `death-zone.png` | `death-zone` | Aura du Saigneur — cible à ≤ 9 m (+1d4 dégâts mêlée subis) |
| `angel-outfit.png` | `angel-outfit` | Harnais Blanc — badge de connexion du Récepteur (0-2) |
| `bolt-shield.png` | `bolt-shield` | Peau de Caillou — buff (+3 PP / +1 PM, retrait manuel) |

## Installation (MJ, une seule fois par partie)

1. Roll20 → **Game Settings → Token Markers → Create a new set**
   (ex. nom du set : `Gondorf`).
2. Uploader les 5 PNG de ce dossier.
3. Renommer chaque marqueur avec le nom EXACT de la colonne 2 — **le nom
   est l'API** : le mod écrit `status_<nom>` ; un nom différent casse
   silencieusement l'affichage (le code continue d'écrire l'ancien nom).
4. Dans la partie : **Game Settings → Token Markers → activer le set**.
   Garder le set par défaut actif aussi (pour `tread` et les marqueurs
   posés à la main par le MJ).

Aucun changement de code n'est requis : même nom ⇒ `setMarker()` (double
écriture `status_<nom>` + chaîne legacy `statusmarkers`,
`lib/Roll20/statusMarkers.js`) résout le marqueur custom dès que le set
est actif. Si un nom de marqueur custom entre en collision avec un défaut
actif, Roll20 préfixe le tag custom (`nom::id`) — dans ce cas, préférer
désactiver le marqueur par défaut homonyme du set défaut si l'affichage
choisit le mauvais visuel.

Source d'inventaire : `docs/audits/2026-06-06-token-markers-inventory.md`
(repo principal).
