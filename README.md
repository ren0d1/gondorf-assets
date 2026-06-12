# gondorf-assets

Public media assets for the **Gondorf** Roll20 character sheet.

The game's code lives in a separate **private** repository; only the media is
public, because Roll20 needs publicly-fetchable URLs to render sheet
backgrounds and icons. The sheet CSS references these files through
`raw.githubusercontent.com/ren0d1/gondorf-assets/main/...` URLs.

## Layout

- `Background/` — per-faction and per-tab sheet background images.
- `Icone/` — resource gauge icons + armour shields. `Icone/source/` holds the
  raw 1024² generations; `Icone/raton_v4/` holds the keyframes consumed by
  `build_raton_gauge.py` (the raccoon-gauge APNG assembler).
- `TokenMarkers-set-v4/` — the 13 PNG of the ACTIVE Roll20 token-marker set
  « Gondorf v4 » (file name = marker name, do not rename). `alternatives/`
  holds parked variants. Superseded v1/v2/v3 folders were removed 2026-06-12
  (git history keeps them).

## Provenance & rights

The project (owner: **ren0d1**) has fully taken over the Gondorf codebase and,
with the rights confirmed OK (2026-06-06), re-hosts the visual assets here to
own their storage and exposure rather than depend on the original developer's
account. New / regenerated artwork (e.g. the Souveraineté backdrop) is added
directly.

## Usage

Reference a file by its raw URL, e.g.:

```
https://raw.githubusercontent.com/ren0d1/gondorf-assets/main/Background/Fiche_background_Souverainete.png
```

The code repo pins URLs to the `main` branch (mutable) so new assets can be
added without a code change.
