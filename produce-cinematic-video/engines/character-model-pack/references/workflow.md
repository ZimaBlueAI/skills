# Character model pack workflow

## What this workflow is for

Use this workflow to turn a child-authored or otherwise approved 2D character into assets that can survive repeated animation work. It separates creative decisions from mechanical preparation so a model cannot quietly redesign the character during production.

The minimum useful pack is a neutral front, left, and back view. Expressions and action cutouts are later layers, not prerequisites for letting a child tell a story.

## Contents

- [Stage 0 — Intake and authorship](#stage-0--intake-and-authorship)
- [Stage 1 — Canonical front](#stage-1--canonical-front)
- [Stage 2 — Turnaround](#stage-2--turnaround)
- [Stage 3 — Deterministic normalization](#stage-3--deterministic-normalization)
- [Stage 4 — Expressions](#stage-4--expressions)
- [Stage 5 — Actions](#stage-5--actions)
- [Stage 6 — Cutout extraction](#stage-6--cutout-extraction)
- [Stage 7 — Validation and author review](#stage-7--validation-and-author-review)
- [Suggested classroom pacing](#suggested-classroom-pacing)

## Stage 0 — Intake and authorship

Create a short character card with the author. Use an alias in digital files.

Record:

1. character name and one-sentence idea;
2. three identity anchors;
3. body proportions;
4. base colors or materials;
5. left/right asymmetries;
6. an approved neutral pose;
7. observable style traits;
8. any detail the model is allowed to simplify;
9. author review status: green, yellow, or red.

Good identity anchors are concrete: “one ear is triangular and one is round,” “the belly has a blue spiral window,” or “the left boot is much larger.” “Cute” and “cool” are wishes, not anchors.

For younger authors, let them point, circle, or place stickers instead of explaining everything aloud.

## Stage 1 — Canonical front

Start from the author’s drawing or the strongest previously approved image. Make one full-body front image with a calm, readable pose. Preserve deliberate oddities.

Check the front view before creating more images:

- silhouette reads at thumbnail size;
- face and hands are not hidden;
- feet or base are visible;
- key accessory is attached consistently;
- background is transparent or plain and removable;
- no caption, border, shadow, or second character is present.

If the front view fails, repair it before asking for more views. Four inconsistent views are harder to fix than one canonical view.

## Stage 2 — Turnaround

Generate or draw front, left, back, and optionally right as one coherent neutral pose family.

Keep constant:

- head-to-body ratio;
- eye, ear, hand, foot, and tail sizes;
- clothing seams and accessory attachment points;
- palette and material rendering;
- vertical foot line and approximate camera height;
- line weight and level of detail.

Allow only the information that must change with viewpoint: overlap, foreshortening, visible side, and rear construction.

### Separate pose families before selecting views

Group source assets by body state before building a turnaround: neutral standing,
sitting, running/directional, expressions, and actions are separate families. A
front sitting view and a side running view do not form a valid turnaround even
when they depict the same character.

Mirroring a strong side view is valid only for a symmetric design and with author
approval. A patch, pocket, colored eye, mechanical arm, or side-specific prop
makes mirroring unsafe.

## Stage 3 — Deterministic normalization

Run `prepare_character_views.py` after the views are approved.

The script uses this deterministic normalization method:

1. find visible content from alpha;
2. crop with a small safety margin;
3. calculate one scale from the largest view;
4. resize with premultiplied alpha to prevent dark edge fringes;
5. center horizontally;
6. align every foot/base to a common baseline;
7. export a contact sheet and machine-readable manifest.

Inspect the contact sheet, not only individual PNGs. Scale drift and a floating foot are easier to notice side by side.

## Stage 4 — Expressions

Approve a small vocabulary before asking for dozens of faces. Six expressions are usually enough for a first short film:

1. neutral;
2. happy;
3. worried;
4. angry or determined;
5. surprised;
6. thinking.

Keep head angle, crop, ear shape, markings, and lighting constant. Change expression through brows, eyes, mouth, cheek tension, and small head/body cues. Avoid changing age, species, or face proportions.

## Stage 5 — Actions

Select actions from the story, not from a generic demonstration list. A character who repairs robots may need “inspect,” “hold tool,” and “celebrate repair” before “fight” or “dance.”

For the first production pack, use no more than six actions:

- idle;
- walk;
- run;
- jump or startle;
- one signature interaction;
- rest or listen.

Each cell should have generous space around the subject. Avoid overlapping tails, props, speed lines, or neighboring characters.

## Stage 6 — Cutout extraction

Create a regions JSON file. Regions may use normalized coordinates from 0 to 1 or pixel coordinates. Choose isolation mode per cell:

- `main`: keep only the largest connected subject;
- `main+props`: also keep disconnected pieces at least the configured fraction of the main subject;
- `none`: preserve every visible pixel in the crop.

Use this extraction strategy: trim by alpha, remove an even background or green
screen, find connected components, keep the main sprite and meaningful props,
discard neighboring fragments and specks, then trim again.

After extraction, inspect ears, antennae, whiskers, strings, sparkles, held tools, and tails. Thin features are the first to disappear during background removal.

## Stage 7 — Validation and author review

Run `validate_character_pack.py`, then perform a visual review.

Use two passes:

### Production pass

- required files exist;
- dimensions and baseline match;
- alpha is valid;
- filenames are stable;
- no accidental mirrored asymmetry;
- no neighboring fragments or background halo.

### Author pass

- green: “This is my character. Keep it.”
- yellow: “Mostly right; change these marked parts.”
- red: “This is not my character. Go back to the last approved stage.”

Do not negotiate a red into a green because generation took time. Save rejected candidates in a separate review folder so the author’s reasoning remains visible.

## Suggested classroom pacing

For children around ages 9–10:

- Session A: identify three anchors and approve one canonical view;
- Session B: choose or create front/side/back, then compare as a game;
- Session C: select expressions and actions from the group story;
- adult-assisted production: normalize, slice, and validate;
- next session: children approve, rename, and test the assets in a tiny animation.

Children may draw, act, point, arrange cards, or ask a partner to speak. A polished oral presentation is not required to prove authorship.
