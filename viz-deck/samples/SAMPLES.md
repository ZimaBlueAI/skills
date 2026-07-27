# viz-deck samples

Four categories: keynote HTML/MP4 (v2), 5-dim critique (v2), editable PPTX decks (v3), and v4 cross-pollination samples (Speaker Mode / 3-variant preview / Doc→Deck / Academic Talk / Bento / Reflective Loop).

## v4 · 26-skill cross-pollination samples (NEW)

Each sample is a runnable artifact that demonstrates one of the seven v4 enhancements. **Open the `.html` files in a browser** — no build step.

| Sample | Demonstrates | Inspired by |
|---|---|---|
| **`speaker-mode-sample.html`** + **`speaker-window-sample.html`** | 8-slide ZimaBlueAI v0.4 walkthrough. Press **S** in the deck to pop the speaker window with current/next preview + teleprompter + timer. Two windows sync via BroadcastChannel. | html-ppt-skill (3.8k★) |
| **`preview-shotgun-sample.html`** | Show-Don't-Tell 3-variant direction board for "Q4 投资人简报". Three hero mockups (Pentagram / Build / Takram) side-by-side; click PICK to copy slug. | frontend-slides (17.5k★) |
| **`doc-source-sample.md`** + **`doc-to-deck-sample.json`** | Long-form investor brief (~600 words, 4 sections) and the deck spec produced by `doc-to-spec.mjs` — chapters auto-detected, tables → kpi-grid, quote → pullquote. | odin-slides + colloquium |
| **`academic-talk-sample.html`** | Filled academic talk: "Reflective Loops Measurably Improve LLM-Generated Decks". Action titles, numbered citations, 2×2 results table, Q&A (incl. limitations), 6-entry references. | academic-pptx-skill (387★) |
| **`bento-layout-sample.html`** | Apple-inspired bento grid — "Six product bets" with 8 unequal-span tiles, 4 accent colours, hero halo on the 2×2 tile. | apple-bento-grid (171★) |
| **`reflect-input-flawed-sample.json`** + **`reflect-report-sample.html`** + **`reflect-redo-prompts-sample.txt`** | A deliberately flawed 9-slide spec (10-bullet slide, missing units, `{{placeholder}}` left behind, empty KPI grid). `reflect-and-redo.mjs` catches the issues, flags slide #2 in red on the report, and writes a redo prompt. | PPTAgent (4.4k★) |

### Try the samples yourself

```bash
# 1. Speaker Mode — open in a same-origin context (a local http server)
cd claude-code-skills/viz-deck/samples
python3 -m http.server 8080
# then visit http://localhost:8080/speaker-mode-sample.html and press S

# 2. Direction preview — open as a file
open preview-shotgun-sample.html

# 3. Doc→Deck — re-run the conversion on the sample markdown
node ~/.claude/skills/viz-deck/scripts/doc-to-spec.mjs \
  --input doc-source-sample.md --output ./out.json --verbose
diff out.json doc-to-deck-sample.json   # should match (within timestamps)

# 4. Academic — direct open
open academic-talk-sample.html

# 5. Bento — direct open
open bento-layout-sample.html

# 6. Reflective Loop — re-run on the flawed spec
node ~/.claude/skills/viz-deck/scripts/reflect-and-redo.mjs \
  --spec reflect-input-flawed-sample.json \
  --output ./out-report.html \
  --threshold 7.0 \
  --redo-prompts ./out-redo.txt
# console will show "Flagged: 1 slides below threshold 7"
```

### Replay against your own content

The samples double as starter inputs. To turn the bento layout into your own product recap, copy `bento-layout-sample.html` to `my-bento.html` and replace the tile values — the CSS handles the rest. Same pattern for `academic-talk-sample.html` (replace action titles + exhibit table + references) and `doc-source-sample.md` (your own report).

---

## v3 · pptx-deck mode (真正可编辑 PPTX)

Open any `.pptx` in PowerPoint — every text frame, accent bar, KPI tile, and divider is an independently clickable native shape. Tab through the slide to walk shapes individually.

| Sample | Theme | Slides | Demonstrates |
|---|---|---|---|
| **`editable-deck-sample.pptx`** + `.spec.json` | deep-space | 9 | Canonical Q3 board update — verdict, KPIs, options, tradeoff, pullquote, closing. The reference spec for `pptx-deck-spec.example.json`. |
| **`product-launch-deck-sample.pptx`** + `.spec.json` | **deck-light** | 10 | Product launch keynote (Mingjing AI public release). Shows the corporate-friendly indigo-on-white theme. |
| **`all-layouts-showcase-sample.pptx`** + `.spec.json` | deep-space | 8 | One slide per layout — `title-cover`, `agenda`, `section-divider`, `title-bullets`, `two-column`, `kpi-grid`, `pullquote`, `closing`. Use as visual reference when picking a layout. v4 adds `bento-grid` — see the example spec at `templates/pptx-deck-spec.example.json` for the new 9th layout in action. |

### Verify they're truly editable

```bash
# Each slide should contain ≥10 independent <p:sp> shapes
unzip -p editable-deck-sample.pptx ppt/slides/slide1.xml | grep -c "<p:sp>"
```

If you see a number ≥10, every visual element is clickable in PowerPoint.

### Reuse the specs as templates

```bash
cp samples/product-launch-deck-sample.spec.json my-launch.json
# edit my-launch.json — change title, slides, kpis
~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh my-launch.json \
  --theme deck-light --anim fade --trans fade
```

---

## v2 · motion-stage (HTML + MP4)

| Sample | Format | Demonstrates |
|---|---|---|
| `motion-stage-sample.html` | HTML stage | 8s motion narrative with `window.__ready` signal |
| `motion-stage-sample.mp4` | 1920×1080 H.264 | The same stage rendered to video via huashu `render-video.js` |

---

## v2 · 5-dim critique

| Sample | Demonstrates |
|---|---|
| `design-critique-sample.html` | Keynote-style 5-dim critique (deep-space palette) — radar + Keep/Fix/Quick-Wins |
| `design-critique-sample.scores.json` | Source scores used to render the critique HTML |
