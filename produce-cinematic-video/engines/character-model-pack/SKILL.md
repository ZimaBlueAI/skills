---
name: build-character-model-pack
description: Build a production-ready 2D character pack from a child’s drawing, generated character image, existing turnaround, or sprite sheet. Use for 三视图、Model Sheet、角色标准设定稿、表情表、动作表、透明切片、sprite/cutout assets, animation character consistency, or checking whether front/side/back views still depict the same character.
---

# Build Character Model Pack

Turn one approved character design into a small, traceable animation asset pack without sanding away the author’s unusual ideas.

## Protect the character before producing assets

1. Treat the child or original author as the final decision-maker.
2. Record three identity anchors before generating anything: one silhouette anchor, one face/body anchor, and one color/material/accessory anchor.
3. Record every left/right asymmetry, including patches, pockets, scars, antennae, eye colors, shoes, or carried objects.
4. Use an alias rather than a child’s full name in filenames and manifests.
5. Change only what the author has approved. A cleaner drawing is not automatically a better character.
6. Present generated results as candidates. Use green/yellow/red review: keep, change, or reject.

If identity anchors or the intended pose are unclear, inspect the source and make a provisional card. Ask only for decisions that materially change the character.

## Choose the shortest valid path

- **One approved character image only:** lock the canonical front view, generate a coherent neutral turnaround, then normalize it.
- **Separate front/side/back images:** skip generation and normalize them with `scripts/prepare_character_views.py`.
- **A contact sheet or sprite sheet:** define regions, extract transparent cutouts with `scripts/extract_cutout_sheet.py`, then validate.
- **A finished pack:** run `scripts/validate_character_pack.py` and repair only failed gates.

Read [references/workflow.md](references/workflow.md) for the full classroom and production workflow. Read [references/prompt-templates.md](references/prompt-templates.md) only when images must be generated or edited. Read [references/asset-contract.md](references/asset-contract.md) before naming or handing off files.

## Build in this order

### 1. Freeze a canonical character card

Write down:

- creator alias and character name;
- three identity anchors;
- body proportions and approximate height in heads;
- five or fewer base colors or material descriptions;
- left/right asymmetries;
- neutral pose family and foot line;
- style language stated as observable traits, not only a film or artist name.

Do not begin a turnaround from a busy action pose if a neutral pose can be approved first.

### 2. Create one coherent turnaround

Make `front`, `left`, and `back` mandatory. Add `right` when the design is asymmetric or the production needs both sides.

Keep all views in the same pose family. A sitting front, running side, and crouching back are three actions, not a turnaround. Select front, side, and back views that share the same body state; keep directional running sprites in a separate action family.

Mirror left into right only when the character and its clothing are genuinely symmetric and the author agrees. Pass `--mirror-right-from-left` explicitly; never mirror by default.

### 3. Normalize canvas, scale, and baseline

Run:

```bash
python scripts/prepare_character_views.py \
  --front path/to/front.png \
  --left path/to/left.png \
  --back path/to/back.png \
  --output-dir path/to/character-pack \
  --character-name "角色名" \
  --anchor "轮廓锚点" --anchor "脸或身体锚点" --anchor "颜色或配件锚点"
```

The script crops transparent margins, uses one scale across every view, aligns a common foot baseline, resizes in premultiplied alpha to avoid dark fringes, and writes a contact sheet plus a manifest.

If an input has an even solid background, add `--background auto`. Inspect the result; automatic background removal is a convenience, not an approval gate.

### 4. Make expressions and actions after the turnaround is approved

Keep expression sheets focused on the face and action sheets focused on silhouette. Start small:

- expressions: neutral, happy, worried, angry, surprised, thinking;
- poses: idle, walk, run, jump, interact, rest.

Keep cells separate, uncropped, and non-overlapping. Give props their own cell unless the prop is essential to reading the action.

### 5. Extract transparent cutouts

Copy `assets/templates/regions.example.json`, edit the boxes and names, then run:

```bash
python scripts/extract_cutout_sheet.py \
  --sheet path/to/action-sheet.png \
  --regions path/to/regions.json \
  --output-dir path/to/character-pack/poses \
  --key-background auto
```

The extractor can remove a uniform corner background or green screen, isolate the main connected subject, keep meaningful props above a relative area threshold, trim transparent margins, and produce a contact sheet and manifest.

Use `"isolate": "none"` for a deliberately disconnected composition. Use `"isolate": "main"` when neighboring sprites leak into a region. Use `"isolate": "main+props"` when an action includes a ball, wand, bowl, or similar object.

### 6. Validate before animation

Run:

```bash
python scripts/validate_character_pack.py --pack path/to/character-pack
```

Do not hand off a pack with validation errors. Automated checks cover files, alpha, canvas, baseline, naming, and unsafe mirroring. A human or the author must still check silhouette, identity anchors, colors, proportions, limb count, expression readability, and whether the character still feels like theirs.

## Acceptance gates

Require all of these:

- the same character is recognizable when each view is shown alone;
- three identity anchors survive every view and action;
- proportions, limb count, clothing, markings, and accessories do not drift;
- front/left/back use one neutral pose family and one foot line;
- asymmetric details land on the correct side;
- no neighboring sprite fragments or green/gray halo remain;
- every cutout has transparent margins and a stable, descriptive filename;
- the author has marked the pack green, yellow, or red and yellow notes are recorded.

## Keep generation and slicing separate

Do not ask an image model to both redesign the character and deliver final production cutouts in one unreviewed step. First approve the design, then the turnaround, then expressions/actions, then perform deterministic slicing and validation. This makes errors visible and repairable.

## Deliver

Follow [references/asset-contract.md](references/asset-contract.md). Include source provenance, prompts or edit notes, manifests, contact sheets, and `validation-report.json`. Preserve original drawings and rejected candidates; do not overwrite them.
