# Editing field guide

1. Probe each input: `ffprobe -v error -show_format -show_streams -of json INPUT`.
2. Create a select list using source-relative times; distinguish speech from transcription guesses. With variable-frame-rate material or mixed sources, check actual timing before joining clips.
3. Pick a clear hook and build a coherent beginning, middle and end. Remove dead air only where the thought and emotion survive. Check hard cuts at normal speed and with sound.
4. For reframing, track the subject and avoid cutting off faces or text. Keep captions above platform interface overlays; check actual output on a small screen. Time subtitles from speech, not estimated word counts.
5. Keep dialogue peaks below clipping. Compare music under speech by listening; use measured loudness only when delivery requires it. Measure with `ffmpeg -i OUTPUT -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -`; the values are a measurement setup, not a universal platform standard.
6. Decode the entire output with `ffmpeg -v error -i OUTPUT -f null -`; check exit status and stderr. This verifies decode, not visual quality, audio sync or truthfulness. Extract representative frames and listen to the actual export. Report issues and repair before delivery.

Prefer cuts motivated by action, gaze, sound or meaning; use a transition when it serves a clear purpose. Check identity, screen direction, action start/end and spatial continuity across cuts. Record detected issues by output timecode, severity and evidence, then replace only the affected segment while preserving the prior export. Separate narrative review, factual accuracy, technical decode, picture continuity, sound, captions and rights; a pass in one category does not imply the others passed.

For speech, retain audible context and listen for misleading sentence joins. Crossfade or use room tone only when it sounds natural; excessive denoising can create artifacts. Check voice/music balance on speakers or headphones. If a voice track is replaced, recheck lip synchronization against the actual new audio.

Do not interpolate shell commands from untrusted file names; use argument arrays. Never overwrite inputs; give each export a unique path. `-ss` placed before `-i` can cut faster but may not be frame-accurate with stream copy; re-encode and inspect boundaries when precise cuts matter.
