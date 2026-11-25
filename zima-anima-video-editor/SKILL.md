---
name: zima-anima-video-editor
description: Research, develop, generate and edit short videos or films with Grok Bot and available AI tools. Use for audience research, story, shot prompts, AI-generated or supplied footage, voice, captions, edits and delivery QC; no workbench required.
---

# Zima Anima video editor

Develop a user-requested video from supplied material or a creative brief, and produce a reviewable cut when suitable tools are available. This is a self-contained production playbook; no workbench or named external platform is required. Work in the user's language. Make the opening, story and packaging compelling for the intended audience, but never guarantee virality or fabricate evidence, testimonials or analytics.

## Start

Establish the story, audience, target duration and aspect ratio, must-keep material, source locations and intended output. Infer ordinary choices from context; ask only when missing information prevents a sound edit. Inspect available files and probe durations, dimensions, frame rates, audio streams and rotation with `ffprobe`. Check actual access and tools (`ffmpeg`, `ffprobe`, and any available transcription capability). Do not assume a local desktop path is visible on the Bot's cloud computer. If assets are missing, explain precisely what is needed and prepare an edit outline without inventing footage or transcripts.

For a brief without footage, first research the subject and audience, develop a verifiable hook and story, and map each shot to an achievable source or generation route. Read [references/creative-research.md](references/creative-research.md). For requested AI image/video generation or video-to-video editing, inspect available tools, access, model capabilities, fees and input handling; use [references/ai-production.md](references/ai-production.md). Produce a short representative test when helpful, inspect the actual result, then continue within the user's stated scope and budget. Preserve user-selected providers; do not silently switch or invent a tool call. If generation is unavailable, provide a clear shot/prompt package and report that no video was generated.

Use a fresh project output directory. Preserve originals, original sound and existing exports. Record input paths and source timecodes. If transcription is available, use it to locate candidates, then listen to the actual audio to verify names, wording and cut points. Identify the strongest opening, maintain narrative coherence, preserve necessary context and cut away repetition without changing the speaker's meaning. Avoid inventing quotations, visuals, claims, footage or permissions. If research is needed for a claim, footage or music, follow [references/research.md](references/research.md); check primary sources and record rights before use.

## Edit

Write one sentence describing what the audience should understand or feel. For speech-led material, assemble a coherent audio-first cut before covering edits with picture. Build a concise edit decision list: source, source in/out, timeline position, role, audio intent and reason; include target duration, format, captions and audio treatment. Don't force uniform shot lengths. Preserve breaths, pauses and reactions that carry meaning. Honor the user's review preference: an explicitly requested render authorizes a review cut; otherwise present the plan first when creative direction is materially uncertain. For changes, preserve a versioned previous cut and describe what changed.

Cut on natural speech and motion; check jump cuts and transitions. Use B-roll only when supplied or properly sourced for the requested usage; annotate source and license and avoid implying unrelated footage documents an actual event. Captions must match audible speech and remain inside platform-safe margins; validate timing and readability on extracted frames. Use music only when supplied or cleared for the requested use; keep dialogue intelligible and preserve a no-music alternative where useful. Don't claim precise sync or loudness without measuring it. If an edit requires a tool that isn't available, offer an executable plan or a simpler actual deliverable and label the limitation.

## Finish and hand off

Render a new file using settings suitable for the requested platform and original material; avoid silent cropping or a frame-rate change that damages the edit. Verify the produced file exists, decodes end to end, has the expected duration, dimensions and audio streams; inspect representative frames and listen to the opening, transitions and ending. Review the actual full export at normal speed when tools permit; check captions against audio and inspect cut boundaries for black frames, freezes, abrupt audio or sync drift. Automated checks and stills cannot establish rhythm or sync. Report checks actually performed and any unverified portions. Deliver the video, source/timecode edit list, transcript/captions when requested, sources for added media, and a brief change log. Never publish or send to third parties unless explicitly instructed.

For practical editing decisions and checks, read [references/editing.md](references/editing.md); for Grok Bot setup and sourced lessons, read [references/grok-bot.md](references/grok-bot.md); for interview, music-video and documentary examples, read [references/recipes.md](references/recipes.md).

## Specialist collaboration and advanced finishing

For complex work use the independent professional roles, style lenses, handoff contracts and copyable prompts in [references/specialists-and-prompts.md](references/specialists-and-prompts.md). When multiple Bots are already available or the user asks for them, coordinate actual Bots; otherwise one Bot may perform the roles sequentially and must say so. Do not claim simulated roles are independent reviewers. Preserve an editable decision list and name one owner for each output.

For voiceover, breath, dialogue, transcription, TTS, lip sync or character continuity use [references/voice-and-continuity.md](references/voice-and-continuity.md). Check the actual provider, available tool, input rights, language and output evidence before using a capability. A written prompt or installed package does not mean the result has been rendered or validated. For camera and transitions, follow the shot-bridge prompts and edit checks in the specialist reference. Never imply that an edit alone can change a camera path or repair identity; if generation or specialist software is unavailable, return the precise repair brief and mark execution blocked.
