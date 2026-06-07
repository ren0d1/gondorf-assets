# gondorf-assets

Public media assets for the **Gondorf** Roll20 character sheet.

The game's code lives in a separate **private** repository; only the media is
public, because Roll20 needs publicly-fetchable URLs to render sheet
backgrounds and icons. The sheet CSS references these files through
`raw.githubusercontent.com/ren0d1/gondorf-assets/main/...` URLs.

## Layout

- `Background/` — per-faction and per-tab sheet background images.
- `Icone/` — resource icons (vitalité, énergie, pouvoir, munitions) and the
  three armour shields (physique / magique / énergie).

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
