# Specialist collaboration and directing prompts

This open skill offers original, general-purpose professional roles and style lenses. It does not bundle the separate zima-anima master-persona catalogue, proprietary orchestration, private prompts or project data. It is not an implementation of those internal agents. A user may supply their own approved role card or style direction.

## Assign work

For a small task one editor can cover all roles. On a complex task use the available team, if the user requests or authorizes actual Bot delegation; otherwise apply these perspectives sequentially and label them as perspectives, not independent agents. Each handoff specifies inputs, owned artifact, timecodes, assumptions, unresolved issues and checks actually performed. Keep source files and final timeline owned by one editor; collaborators write separate versioned artifacts. Bots can share the same computer, so concurrent changes to the same file can collide; coordinate resource usage and never treat Bots as separate security boundaries. See [Grok Bot FAQ](https://docs.x.ai/grok-bot/faq).

| Role | Output and responsibility |
|---|---|
| Director / story editor | audience, thesis, treatment, emotional arc, must-preserve facts and acceptance notes |
| Research / rights | current source links, claim evidence and asset license status |
| Picture editor | source selects, EDL, sequence, motivated cut points and versioned export |
| Cinematography / transitions | shot geography, camera movement observations, boundary options and matching evidence |
| Dialogue / voice | verified transcript, voice direction, delivery and breath timing |
| Sound / music | dialogue cleanup, ambience, effects, music balance and audio provenance |
| Continuity / identity | character reference sheet, discrepancies by timecode and minimum-scope repair brief |
| Finishing / QC | actual output metadata, picture/audio/caption checks and unresolved defects |

Resolve conflicts using the user's stated intent and sourced facts; preserve the rationale and avoid replacing an approved asset without instruction. A real independent review is one performed by another available reviewer with its own findings; sequential self-review must be labelled as such.

## Style lenses

Choose one or two concrete, non-persona lenses and explain the choice: observational (hold reactions and real time); kinetic (action-led cuts and varied shot scales); lyrical (space, texture, breath and sound bridges); explanatory (visual evidence and reading time); comedic (setup, reaction and pause); restrained commercial (product clarity, readable claims, decisive ending). Adapt to the material rather than applying fixed timing. These are creative options, not a recreation of the internal master lineup.

## Copyable prompts

Replace brackets with actual material and constraints; omit unknowns rather than inventing them. When a prompt asks a tool to act, first check the tool supports the task and that it is authorized.

**Director**: “For [audience], shape [source material] into [duration/format]. The audience should [understand/feel]. Preserve [facts, exact lines, must-keep moments]. Propose a beginning, turning point and ending using source timecodes; identify missing material and two specific review risks.”

**Editor**: “Build a timecoded EDL from [source IDs]. For each cut list source in/out, output position, narrative function, audio transition and reason. Protect performance and quotation context, vary pacing and flag repeated shots. Do not claim the EDL is a rendered video.”

**Camera**: “For [shot] describe current framing, subject position and observed camera movement. Desired endpoint: [frame]. Explain whether reframing existing footage is sufficient; if new footage or generation is needed, describe its start/end framing, direction, subject motion, spatial constraints and references. Do not assert a move was performed until footage is inspected.”

**Transition**: “Compare the last visible action and sound of [outgoing shot] with the first of [incoming shot], citing timecodes. Propose a hard cut, action match or sound bridge with a reason and continuity risks. Specify overlap and handles only if both sources contain them.”

**Dialogue / voice**: “For [exact text], language [language], direct [speaker] with [emotion]. Mark phrase groups, natural breaths, relative volume, pace and pitch movement; preserve wording. Fit [duration] without unnatural acceleration. Return the direction and a test plan; do not claim audio exists before synthesis or recording.”

**Continuity**: “Compare [approved reference] and [shot / timecodes] for face, hair, proportions, clothing, position and props; list observed differences and confidence. Suggest the smallest repair and state its required tool, reference, affected range and review method. Do not claim identity is fixed from a prompt alone.”

**QC**: “Inspect [actual rendered file] for [specification]. Report metadata, decode result, what was watched and heard, caption and lip-sync checks by timecode, visible identity discrepancies, evidence and unverified items. Never infer motion or speech quality from a still image alone.”
