# Narration & MP4 export for editable PPTX

After generating an editable PPTX with `export-editable-pptx.sh`, you can
attach per-slide narration audio and let PowerPoint export to MP4 with
synced narration + animations. No external ffmpeg pipeline required.

---

## TTS providers supported

ppt-master `notes_to_audio.py` supports five backends:

| Provider | Cost | Quality | Best for |
| --- | --- | --- | --- |
| `edge` (default) | Free | Good | Internal demos, drafts |
| `elevenlabs` | Paid | Best (clonable) | Founder voice, board decks |
| `minimax` | Paid (China) | Very good (Chinese) | 中文 decks |
| `qwen` | Paid (Aliyun) | Very good (Chinese) | 中文 decks, voice instructions |
| `cosyvoice` | Paid | Cloneable | Custom voice training |

Default is `edge-tts` (free, no API key). For everything else, set the
provider's API key env var (e.g., `ELEVENLABS_API_KEY`) and pass `--provider`.

---

## Pipeline

```bash
# Step 1 — generate the editable deck with speaker notes embedded
./export-editable-pptx.sh deck.json --with-notes --theme deep-space

# Step 2 — generate audio + rebuild with embedded narration
./embed-narration.sh ./deck_pptx_build \
  --voice zh-CN-XiaoxiaoNeural \
  --provider edge

# Step 3 — open in PowerPoint, export to video
# (Open the *_narrated.pptx)
# File → Export → Create a Video → Use Recorded Timings and Narrations → MP4
```

Output: `deck_pptx_build/exports/deck_narrated.pptx` (audio embedded, slide
timings synced) + manually-exported `.mp4`.

---

## Voice catalog (edge-tts, free)

Common voices:

| Locale | Voice | Style |
| --- | --- | --- |
| zh-CN | `zh-CN-XiaoxiaoNeural` | Friendly, female (default) |
| zh-CN | `zh-CN-YunyangNeural` | Authoritative, male |
| zh-CN | `zh-CN-XiaoyiNeural` | Warm, female |
| en-US | `en-US-AriaNeural` | Conversational, female |
| en-US | `en-US-GuyNeural` | Professional, male |
| en-US | `en-US-JennyNeural` | Friendly, female |

List all:

```bash
~/.claude/skills/ppt-master/.venv/Scripts/python.exe \
  ~/.claude/skills/ppt-master/skills/ppt-master/scripts/notes_to_audio.py \
  --list-voices | head -30
```

---

## Voice cloning (ElevenLabs example)

If you want the deck narrated in your own voice:

```bash
# 1) Clone your voice once at https://elevenlabs.io/app/voice-lab
# 2) Copy the voice_id from the console
# 3) Set env var
export ELEVENLABS_API_KEY=sk_...

# 4) Run with the voice_id
./embed-narration.sh ./deck_pptx_build \
  --provider elevenlabs \
  --voice-id <your_voice_id> \
  --elevenlabs-model eleven_multilingual_v2
```

---

## Timing rules

`notes_to_audio.py` writes per-slide timing metadata (audio duration). When
`svg_to_pptx.py` is re-run with `--use-narration-timings`, each slide auto-
advances when its audio finishes. This is what enables true "press F5, walk
away" presentation playback.

If a slide has no notes:
- No audio is generated for that slide
- It uses the default 5-second hold (or your `--auto-advance` value)
