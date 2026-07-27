---
name: produce-cinematic-video
description: Plan, research, edit, generate, repair, finish, validate, evaluate, and market professional video across animation, narrative shorts, documentary, film, trailers, branded content, social video, and educational media. Includes a recoverable production workflow and live SVG dashboard, rights-aware reference research, source separation and dialogue A/V alignment, emotional TTS and consented voice cloning with CPU/low-VRAM fallbacks, sound design and mixing, evidence-based creative scoring, and conservative first-party performance baselines. Use for footage ingest, shot detection, paper edits, story structure, hooks and pacing, beat-sync montage, transition grammar, temporal grounding of cut points, continuity, physical-motion integrity, generative fill, subtitles, delivery masters, platform variants, style studies, pre-publish audits, or post-release learning. 适用于动画、短片、纪录片、电影、宣传片、课程视频与短视频的策划、专业剪辑、生成、配音、音频分离与混音、声画同步、质检、营销评估和发布复盘。
---

# ZimaBlueAI Produce Cinematic Video

Designed and maintained by ZimaBlueAI. Third-party names identify optional
interoperability only; they do not imply sponsorship, endorsement, partnership,
or authorship of this skill.

Turn mixed footage, generated media, animation, stills, dialogue, music, and evidence into an auditable master and intentional release variants. Protect truth, performance, story, and audience experience before polish.

## Start safely

1. Determine whether the user asked for advice, diagnosis, a plan, an edit, a render, or publication. Do not mutate media for a review-only request.
2. Work non-destructively. Preserve camera originals, recordings, project files, timecodes, and metadata; create proxies, derivatives, and new versions instead.
3. Locate the per-user configuration before invoking local executables or providers. Run:

   `python <skill-dir>/scripts/configure.py validate`

   Planning and editorial analysis may continue without configured generation providers. Stop before a paid call, remote upload, render that overwrites a file, or external publication until the relevant configuration and authority are present.
4. State consequential assumptions once. Ask only when the missing choice changes truth, rights, budget, story direction, or delivery.

## Route by form

Read only the references needed for the current work:

| Work | Required reference |
|---|---|
| 面向安装者的首次安装、最小配置、TUI、测试、安全边界或完整中文使用说明 | `references/user-guide.zh-CN.md` |
| Making an animation/animated short from a story ("把这个故事做成动画"), or any multi-role production (screenplay → design → storyboard → sound → final cut) | `references/animation-pipeline.md` + the station cards in `agents/animation/` (read each card in full when its station runs) |
| End-to-end orchestration, stage dependencies, pause/revise/resume behavior, recovery, or workflow dashboard | `references/workflow-orchestration.md` |
| Similar-theme research, lawful OmniGet exports, benchmark videos, creative planning, original script ideation, or avoiding imitation | `references/creative-research-and-planning.md` |
| Character model sheets, turnarounds (三视图), expression/pose sheets, sprite cutouts, or character identity validation | `engines/character-model-pack/SKILL.md` (incorporated engine) |
| Mode selection (trailer / concept / montage / narrative short / promo), mixed sources (AI, live action, animation, game capture, stock), plain-language kickoff vs. professional-script priority, director-review-first QC, per-cut sound bridges | `references/director-modes.md` |
| Any edit, paper edit, scene, sequence, montage, or trailer | `references/editorial-core.md` |
| Choosing narrative structure and act/segment durations | `references/story-structures.md` |
| Opening hooks, pacing curves, ASL design, beat-sync editing | `references/hooks-and-pacing.md` |
| Choosing the transition for each cut point | `references/transition-grammar.md` |
| Color script, camera-move semantics, sound design vocabulary | `references/visual-and-sound.md` |
| Narrative film, documentary, animation, educational/physical media, trailer, brand, or social short | Matching section in `references/form-playbooks.md` |
| Filling any material gap with generation (transitions, inserts, extensions, audio) | `references/gen-fill-playbook.md` then `references/generative-media.md` |
| Keeping one generated character identical across frames/shots, or animating a generated still as cel-style multi-frame motion | Continuity-fingerprint and multi-frame cel sections of `references/gen-fill-playbook.md` |
| Recovering voice/music/effects stems, dereverb, dialogue placement from visible mouth motion, or stem mixing | `references/audio-separation-and-sync.md` and `references/audio-post.md` |
| Platform-specific packaging for Douyin, Xiaohongshu, or Bilibili | `references/platform-playbooks.md` and `references/marketing-release.md` |
| AI-generated shots, pickups, inpainting, continuity repair, extension, or physical motion | `references/generative-media.md` |
| GPT Image 2, OpenAI Images, Gemini Nano Banana, image generation, or image editing | `references/generative-image-providers.md` and `references/generative-media.md` |
| Seedance, ModelArk/Ark, text-to-video, image-to-video, first/last frame, or model-generated video | `references/seedance-video.md` and `references/generative-media.md` |
| Local LTX-Video service, private/child imagery that must stay on-machine, or loopback image-to-video | `references/ltx-video.md` and `references/generative-media.md` |
| Dialogue, VO, TTS, Foley, ambience, music, stems, mix, or loudness | `references/audio-post.md` |
| IndexTTS2, emotional TTS, local voice cloning, emotion reference/vector/text, or its setup | `references/index-tts2.md` and `references/audio-post.md` |
| Multi-character dubbing, re-voicing footage in another language, or an ensemble line spoken by several cloned voices | Voice-bank section of `references/index-tts2.md` plus `assets/voice-roles.template.json` |
| Qwen3-TTS, free-form voice design, CustomVoice, local multilingual TTS, or Qwen voice cloning | `references/qwen3-tts.md` and `references/audio-post.md` |
| Low-spec CPU/low-VRAM TTS, Pocket TTS, or LuxTTS | `references/lightweight-tts.md` and `references/audio-post.md` |
| Generated score, transition audio, ambience, Foley, or SFX prompts for Suno, Udio, or ElevenLabs | `references/generated-music-and-sfx.md` and `references/audio-post.md` |
| Audience strategy, style study, platform variant, packaging, CTA, or pre-publish audit | `references/marketing-release.md` |
| Creative scoring, comparable-content learning, like/lead/customer-rate estimation, A/B learning, or forecast limits | `references/evaluation-and-forecasting.md` and `references/marketing-release.md` |
| Mastering, captions, technical QC, accessibility, provenance, rights, or delivery | `references/qc-and-delivery.md` |
| One-stop local engine setup (LTX-Video, Qwen3-Image/Z-Image, Hunyuan3D + Blender, Qwen3-TTS, IndexTTS-2, Pocket TTS, LuxTTS) or Suno/Udio/ElevenLabs prompt-package delivery | `references/local-stack.md` |
| First installation, provider/tool setup, or configuration failure | `references/configuration.md` |

## Run the production workflow

Use the recoverable stage graph in `references/workflow-orchestration.md` as the project spine. Animation-from-story projects also run the specialist stations in `references/animation-pipeline.md`. Store stage state in `project.json`; mutate it through `scripts/workflow_control.py` so every transition, redo, or restore first creates a project-local history snapshot. Regenerate the offline, interactive SVG dashboard with `scripts/pipeline_dashboard.py` after each accepted state change. The steps below remain the editorial law every station obeys.

### 0. Research before prescribing

When the task includes strategy, audience growth, style study, or a new original story, use `references/creative-research-and-planning.md`. Build a dated, rights-aware sample set that includes both strong and ordinary comparables, extract mechanisms rather than protected expression, and turn findings into an original creative brief. A user may collect authorized samples in OmniGet, but PCV only reads the explicitly exported folder through `scripts/research_ingest.py`; it never reads browser/OmniGet credentials or treats downloadability as reuse rights. Keep observation, inference, decision, and experiment separate. Do not claim that a visible feature caused performance merely because it appeared in a successful example.

### 1. Define the editorial contract

First select the director mode (trailer, concept piece, montage, narrative short, or promo) per `references/director-modes.md` — auto-detect from the request and material, state the verdict and reasoning in the brief, and let one user sentence overrule it. A plain-language request is enough to start the full workflow with mode defaults; a professional script, shot list, or edit plan from the user is a **higher-priority constraint** that overrides mode defaults wherever it speaks.

Capture the following in a project brief or the project manifest:

- intended audience, viewing context, viewer promise, desired feeling, and desired action;
- form, target duration, aspect ratio, frame rate, resolution, language, captions, and delivery profiles;
- story thesis, factual claims, must-use material, forbidden material, and acceptance criteria;
- deadline, generation budget, review owner, and approval points;
- rights, releases, source labels, AI/simulation/reenactment disclosure, privacy, and safety constraints.

Choose the priority order explicitly. Default to:

1. truth, consent, and evidence;
2. performance and emotional truth;
3. story and comprehension;
4. rhythm and attention;
5. continuity;
6. surface polish.

Override that order only when the form requires it and record why.

### 2. Ingest and inventory

Never rename, transcode, or alter originals in place.

1. Assign stable asset, scene, shot, character, location, prop, and audio-cue IDs.
2. Inventory codecs, duration, frame rate, raster, color metadata, rotation, audio layout, and file health with `scripts/media_inventory.py`.
3. Preserve checksums when custody, documentary evidence, handoff, or long projects make identity important.
4. Split source footage into shots with `scripts/shot_detect.py` — a two-stage pipeline (PySceneDetect coarse pass, TransNetV2 neural refinement for gradual transitions) that emits `shots.json` with second-level and frame-level boundaries. When TransNetV2 is absent the script degrades to coarse-only and warns; install the refinement layer for production work.
5. Sync sound, create transcripts with source timecodes, mark selects/rejects, and generate contact sheets with `scripts/contact_sheet.py`.
6. Record source type as live action, archival, animation, simulation, generated, reenactment, game capture, stock, still, title, or audio; mixed-source projects tag every asset. Record rights and provenance separately from aesthetic quality. Source type steers per-asset QC focus (game capture: dropped frames and HUD remnants; generated: anatomy/text corruption and identity drift; stock: license verification).
7. Create proxies for editing; keep camera originals and high-quality audio untouched.

Use `assets/project-manifest.template.json` as the source of truth.

### 3. Find the cut before rendering

Read the applicable form playbook, then:

1. Write a one-sentence editorial thesis: what should the viewer understand, feel, or do when the cut ends?
2. Build a radio cut first when speech, interview, narration, or sync sound carries the story.
3. Map evidence and claims for documentary, educational, scientific, or product-demonstration work.
4. Create a beat sheet with scene purpose, information release, emotional movement, tension, payoff, breath, and ending.
5. Draw the rhythm curve rather than imposing one average shot length. Let performance, comprehension, motion, and sound determine cut points. Use `references/story-structures.md` and `references/hooks-and-pacing.md` to choose structure and pacing deliberately.
6. Ground critical cut points instead of eyeballing them. For hooks, climaxes, and action-match cuts, run `scripts/moment_ground.py` (Qwen3-VL temporal grounding over DashScope) with a natural-language query, then apply the three-stage precision funnel: semantic localization → dense-frame inspection of ±4 s around each boundary → snap to the shot boundaries in `shots.json`. Write frame-accurate in/out points into the edit plan from this funnel, never from a glance at a contact sheet.
7. Make a sound map and, when useful, a color script before committing to expensive picture work. `references/visual-and-sound.md` carries the camera-move and sound-design vocabulary.
8. Separate absent material from weak editorial thinking. A gap list is not permission to generate.

### 4. Create and approve the edit plan

Copy `assets/edit-plan.template.json` and validate it against `schemas/edit-plan.schema.json`.

For every timeline item, record source ID, source in/out, timeline in/duration, narrative or evidence function, audio intent, transition, and decision note. For each non-cut transition, state its semantic or continuity purpose; use a cut when no purpose exists.

Record gaps with:

- story need and acceptance evidence;
- zero-cost and pickup alternatives;
- proposed medium and provider capability;
- factual/disclosure risk;
- estimated cost, approval state, and actual cost.

Run `scripts/validate_project.py` before generation or rendering. Present the beat sheet, material gaps, risks, and cost summary for approval when the work introduces paid generation, material factual reconstruction, or a substantial render. Treat an explicit user request to proceed directly as approval only within its stated scope and budget.

### 5. Fill gaps with the least risky medium

Read `references/gen-fill-playbook.md` before repairing any gap; it holds four standard repair routes (transition stitching, inserts or stills with approved parallax processing, shot extension through retiming, interpolation, or a declared provider capability, and audio fill), the reference-image role protocol, current-cost rules, and per-route QC checklist.

Use this order unless evidence shows another route is better:

1. alternate take, re-trim, crop, speed change, sound bridge, insert, or motivated omission;
2. live-action pickup, Foley, ADR, or new recording;
3. deterministic animation, compositing, or conventional VFX;
4. still generation or local frame repair;
5. generative video, extension, or transformation.

For generated or repaired material:

- complete `assets/continuity-sheet.template.md`;
- use `assets/physical-shot-card.template.md` when quantity, forces, contacts, mechanisms, or measurable outcomes matter;
- validate one object and one complete path before crowds or repeated motion;
- give the first and last frames separate, testable duties;
- change one structural assumption per iteration and freeze the last accepted version;
- switch medium when the same core deviation repeats three times or a later version regresses;
- log provider, model, prompt, seed when available, references, task ID, cost, rights, disclosure, and acceptance timecodes.

When the user explicitly requests a Seedance-like or other generative-video model, use an actual declared `text_to_video`/`image_to_video` provider for the requested shots. Deterministic pan/zoom, HTML2Video, Pillow/OpenCV animation, or an NLE motion preset may be used for an animatic, local composite, fallback preview, or finishing layer, but must be labelled as such and must not be represented as model-generated footage. Stop at the configuration/approval gate if the required provider is unavailable instead of silently substituting a different medium.

If a provider rejects recognizable protected characters or brand imagery, preserve the failed task record and do not evade the policy through renamed prompts or repeated submissions. Require an original, materially distinct character redesign through an approved image provider before spending another video-generation attempt; see `references/seedance-video.md`.

Do not generate documentary evidence or product proof that could be mistaken for captured fact.

### 6. Cut and finish in passes

Keep editorial decisions separate from rendering:

1. assembly pass — verify coverage and synchronization;
2. structure pass — remove repetition and clarify causality or argument;
3. performance/evidence pass — protect truthful moments, reactions, demonstrations, and readable results;
4. rhythm pass — shape acceleration, holds, silence, anticipation, and release;
5. continuity/graphics pass — repair screen direction, eyelines, action, geography, labels, titles, and captions;
6. sound pass — dialogue, room tone, ambience, Foley, effects, music, dynamics, and stems;
7. color/delivery pass — color management, legal levels where required, codecs, metadata, and release variants.

Prefer motivated edits: action, gaze, sound, idea, shape, light, color, or cause and effect. For every non-cut transition, pass the decision tree in `references/transition-grammar.md` and record the semantic reason in the edit plan; if no reason survives the tree, use a cut. Do not enforce a universal transition ratio, hook length, or loudness target across films, documentaries, animation, and social ads.

Respect the frame-accuracy law of video encoding: stream-copy (`-c copy`) can only cut on keyframes and may drift by seconds. Fine cuts must re-encode with output seeking (`-ss` after `-i`); use smart-cut (re-encode only the boundary GOP) for fast lossless pre-trims; never deliver a fine cut made with stream-copy trimming.

When rendering changes the approved plan, update the plan and revision note. The timeline contract and the master must agree.

### 7. Validate independently

Run:

- `scripts/validate_project.py` for schemas, timeline semantics, provenance, disclosure, and budget gates;
- `scripts/qc_media.py` for container, duration, raster, frame rate, black/freeze/silence segments, and loudness when the installed FFmpeg supports them;
- `scripts/contact_sheet.py` for representative-frame review.
- `scripts/av_sync_align.py` for a mouth-motion A/V offset candidate when a visible speaker is present;
- `scripts/evaluate_video.py` for evidence-backed creative scoring and, only with sufficient comparable first-party history, empirical rate intervals.

Then perform separate story, performance, factual, continuity, sound, color, accessibility, rights, and marketing reviews using `references/qc-and-delivery.md`. A contact sheet cannot validate motion, sync, rhythm, or a claim by itself; review the relevant passage in real time.

### 8. Design release variants

Finish one editorial master before deriving platform versions unless the project was commissioned for one platform only.

For each version, define:

- audience and viewing context;
- promise, proof, payoff, and next action;
- first-frame comprehension, title/thumbnail, captions, safe zones, and ending;
- what is shortened, reordered, reformatted, or newly packaged;
- the current official delivery specification and the evidence behind any marketing recommendation.

Use owned analytics and controlled A/B variants to learn. Run the evaluation contract in `references/evaluation-and-forecasting.md`; return `not_estimable` when comparables or denominators are insufficient. Treat platform folklore and viral-score predictions as hypotheses. Never promise views, likes, sales, or conversion without a defensible model and enough first-party data.

### 9. Deliver an evidence chain

Deliver only what the brief requires, choosing from:

- review file, clean master, captioned master, mezzanine/archive master, and platform variants;
- caption/transcript files and audio-description materials;
- dialogue, music, effects, ambience, and M&E stems;
- final edit plan, EDL/FCPXML/AAF when available, manifest, checksums, cue sheet, and project file;
- rights/releases/credits log, source and AI provenance, QC report, and retrospective.

Keep large media outside Git. Track paths, IDs, checksums, prompts, task records, approvals, and acceptance evidence.

## Protect form-specific integrity

- **Documentary:** preserve quotation context and chronology; distinguish observation, archival source, reenactment, simulation, and generated imagery; never manufacture causal proof.
- **Narrative film:** prefer the truthful performance over geometric continuity when they conflict, then repair continuity invisibly with reaction, insert, sound, or coverage.
- **Animation:** approve storyboard and animatic timing before final animation; judge pose, silhouette, staging, arcs, spacing, holds, and sound together.
- **Scientific or educational media:** keep measurable outcomes inspectable; use deterministic animation for quantities, collisions, parameters, and repeatable mechanisms.
- **Marketing:** connect every claim to proof, every edit to audience comprehension, and every CTA to the promised value; do not disguise advertising or synthetic demonstrations.

## Configuration contract

Install the skill for one user at `~/.codex/skills/produce-cinematic-video` (Codex) or `~/.claude/skills/produce-cinematic-video` (Claude Code) on Windows, macOS, or Linux. A project-local installation (`.codex/skills/...` or `.claude/skills/...`) is allowed when isolation or version pinning is required. Both hosts share this one skill package and the same user configuration file. Runtime configuration is a user-only dotenv file outside the skill, so an upgrade cannot overwrite personal settings:

- Windows: `%APPDATA%\produce-cinematic-video\.env.local`
- macOS: `~/Library/Application Support/produce-cinematic-video/.env.local`
- Linux: `${XDG_CONFIG_HOME:-~/.config}/produce-cinematic-video/.env.local`
- macOS also honors `XDG_CONFIG_HOME` when the user explicitly sets it.
- Override: `CINEMATIC_VIDEO_ENV_FILE`; legacy `CINEMATIC_VIDEO_CONFIG` remains readable for migration.

Treat `.env.local` as a secret-bearing file: keep it outside repositories, restrict it to the current user, never paste or print it, and never include it in a project archive. Put credentials only in the adapter's declared secret variable, including `PCV_OPENAI_IMAGE_API_KEY`, `PCV_GEMINI_IMAGE_API_KEY`, `PCV_SEEDANCE_API_KEY`, or the backward-compatible generic `PCV_IMAGE_API_KEY`, `PCV_VIDEO_API_KEY`, and `PCV_AUDIO_API_KEY`; never put a raw credential into a field whose name ends in `_ENV`. If a credential is printed, committed, pasted into chat, or appears in a validation error, stop remote calls and rotate it at the provider before continuing. `configure.py show` must redact credential values.

Keep large local models and isolated runtimes in the platform data directory rather than the skill or roaming config: `%LOCALAPPDATA%\produce-cinematic-video` on Windows, `~/Library/Application Support/produce-cinematic-video` on macOS, and `${XDG_DATA_HOME:-~/.local/share}/produce-cinematic-video` on Linux. Override with `CINEMATIC_VIDEO_DATA_HOME`. Run `python <skill-dir>/scripts/configure.py paths` to print all resolved locations.

Initialize once with:

`python <skill-dir>/scripts/configure.py init`

Users who prefer guided setup can run `python <skill-dir>/scripts/configure.py tui`. The dependency-free terminal UI exposes only required choices, hides secret input, and keeps optional tuning values out of the normal path.

Use `configure.py compact` to preview the minimal retained key set; only `compact --confirm` writes it, after archiving the current dotenv. It must retain every enabled provider/runtime, migrate only recognized legacy aliases whose canonical fields are already present, and refuse unknown keys rather than silently dropping them.

For remote providers, prefer the one-at-a-time local wizard—`configure.py setup-provider seedance`, `openai-image`, or `gemini-image`—so the key is entered with terminal echo disabled and never placed in chat or shell arguments.

For a local GPT-SoVITS installation with UVR5, the user normally supplies only its repository directory:

`python <skill-dir>/scripts/configure.py setup-local gpt-sovits --repo-dir <path>`

The adapter reuses the repository's isolated runtime, prefers CUDA automatically when its Torch build can see a GPU, and keeps source audio local. Configure `PCV_GPT_SOVITS_PYTHON` or `PCV_GPT_SOVITS_DEVICE` only for a non-standard installation or troubleshooting.

Migrate an existing JSON configuration with `python <skill-dir>/scripts/configure.py migrate`; the command archives the old file and does not copy suspect credentials. Store executable paths, provider settings, policy, profiles, and optional credentials in the user-only `.env.local`. Process environment variables override the file. Do not write API keys into the skill, project manifest, edit plan, prompt, provenance, logs, or terminal summaries.

Run `scripts/environment_doctor.py` after installation. A full FFmpeg plus FFprobe and Python 3.10+ are core requirements. ImageMagick, Pillow, OpenCV, PySceneDetect, jsonschema, and SoX for local-TTS audio chains are task-dependent helpers documented in `references/configuration.md`; do not pretend a missing optional dependency is installed. Keep IndexTTS2, Qwen3-TTS, Pocket TTS, and LuxTTS in separate official project environments. Qwen3-TTS and IndexTTS2 use GPU-first auto routing; LuxTTS uses CUDA → Apple MPS → CPU; Pocket TTS intentionally remains CPU-first and must not receive Chinese text. Verify the actual selection with the provider doctor instead of trusting host-level GPU detection. Add only the runtime/model variables for the local provider and task actually enabled; do not copy every optional setting into `.env.local`.

Resolve settings in this order: explicit command argument, environment override, user config, bundled safe defaults. Never assume a provider supports first/last-frame generation, reference images, synchronized audio, extension, or editing; select only declared capabilities.

## Hard gates

- Never alter source media in place.
- Never spend beyond the approved generation budget.
- Never upload private media or call a remote provider without the user's scope and configured credentials.
- Never represent generated, simulated, or reenacted material as documentary evidence.
- Never publish or send externally without explicit authorization.
- Never hide a material deviation from the edit plan, factual record, rights status, or QC result.
- Never make pseudo-precise performance forecasts.
