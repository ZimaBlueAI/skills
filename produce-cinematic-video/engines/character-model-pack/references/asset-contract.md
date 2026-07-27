# Character pack asset contract

## Contents

- [Folder layout](#folder-layout)
- [Naming](#naming)
- [Required files](#required-files)
- [PNG requirements](#png-requirements)
- [Manifest requirements](#manifest-requirements)
- [Versioning](#versioning)
- [Human visual checks](#human-visual-checks-that-scripts-cannot-prove)

## Folder layout

Use this layout for a production handoff:

```text
character-alias/
├─ character-pack.json
├─ source/
│  ├─ original.png
│  └─ style-reference.png
├─ views/
│  ├─ front.png
│  ├─ left.png
│  ├─ back.png
│  ├─ right.png              # optional unless asymmetric/required
│  └─ manifest.json
├─ expressions/
│  ├─ neutral.png
│  ├─ happy.png
│  └─ manifest.json
├─ poses/
│  ├─ idle.png
│  ├─ run.png
│  └─ manifest.json
├─ sheets/
│  ├─ expressions-source.png
│  └─ poses-source.png
├─ previews/
│  ├─ views-contact-sheet.png
│  └─ poses-contact-sheet.png
└─ validation-report.json
```

The supplied scripts may place contact sheets beside the folders they describe. Moving them into `previews/` for final delivery is allowed as long as manifests are updated or the originals remain traceable.

## Naming

- Use lowercase ASCII slugs for machine-facing filenames: `front.png`, `surprised.png`, `repair_tool.png`.
- Use Chinese display names inside manifests if helpful.
- Use a child-safe alias in directory names, not a full real name.
- Never encode an unapproved diagnosis, personality judgment, or ranking in a filename.
- Add sequence numbers only when order matters: `walk_01.png`, `walk_02.png`.

## Required files

Every pack requires:

- `views/front.png`;
- `views/left.png`;
- `views/back.png`;
- `views/manifest.json`;
- at least one contact sheet or preview;
- `validation-report.json`;
- source provenance and author review state in `character-pack.json`.

`right.png`, expressions, and poses are optional until the story needs them.

## PNG requirements

- RGBA PNG;
- transparent outer margin;
- no baked caption, border, grid, or drop shadow;
- one character per cutout unless the interaction explicitly requires a group;
- consistent canvas for turnaround views;
- common baseline for turnaround views;
- sufficient edge padding so ears, hair, tails, tools, and motion cues are not clipped.

## Manifest requirements

Record:

- character and creator aliases;
- three identity anchors;
- asymmetry notes;
- source paths or source asset IDs;
- generation/edit prompt or human edit note;
- model/tool name when known;
- whether a view was mirrored;
- canvas, scale, crop, offsets, and hashes for normalized views;
- region boxes, isolation mode, and background treatment for extracted sprites;
- author review state and requested changes;
- timestamp in ISO 8601.

Start from `assets/templates/character-pack.example.json`.

## Versioning

Preserve approved milestones:

- `v01-canonical-front`;
- `v02-turnaround-approved`;
- `v03-expressions-approved`;
- `v04-animation-pack`.

Do not overwrite the original drawing or a previously approved pack. Put experimental candidates in a separate `candidates/` or `rejects/` folder.

## Human visual checks that scripts cannot prove

- identity and emotional feel;
- side-specific details;
- limb count and joint logic;
- pose readability;
- expression clarity;
- whether the rendering style still matches the agreed style language;
- whether the child recognizes and accepts the result.
