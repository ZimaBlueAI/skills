# Taste Dials — token & behavior mapping

Three dials set on the root element drive the whole look. CSS reads them via attribute
selectors; JS reads `document.documentElement.dataset` to gate animation.

```html
<html data-variance="1" data-motion="2" data-density="1">
```

Values are `0 | 1 | 2`. Defaults per deliverable are in `SKILL.md`.

---

## 1. VISUAL_DENSITY — spacing, scale, columns

Controls how much breathes vs. how much fits.

```css
:root{
  --pad: clamp(22px,5vw,72px);
  --gap: 24px; --leading: 1.55; --scale: 1; --maxw: 1180px;
}
html[data-density="0"]{ --gap:46px; --leading:1.75; --scale:1.14; --maxw:980px;  } /* 一屏一念 */
html[data-density="1"]{ --gap:24px; --leading:1.55; --scale:1;    --maxw:1180px; } /* 平衡 */
html[data-density="2"]{ --gap:13px; --leading:1.38; --scale:.9;   --maxw:1320px; } /* 仪表盘 */
```

Bind grid column counts to it too:

```css
html[data-density="0"] .bento{ --cols:2; }
html[data-density="1"] .bento{ --cols:3; }
html[data-density="2"] .bento{ --cols:4; }
```

| Dial | whitespace | type | columns | use |
|---|---|---|---|---|
| 0 | huge | +14% | fewer | one idea per screen |
| 1 | balanced | base | medium | bento balance |
| 2 | tight | −10% | more | dashboard density |

---

## 2. DESIGN_VARIANCE — rhythm & layout tension

Controls symmetry vs. editorial break.

```css
/* 0 — centered, safe */
html[data-variance="0"] .head{ text-align:center; margin-inline:auto; }
/* 1 — asymmetric golden split, offset header */
html[data-variance="1"] .head{ max-width:78%; }
/* 2 — editorial break: oversized type, diagonal flow, broken grid */
html[data-variance="2"] .head{ max-width:88%; transform:translateX(-1.5%); }
html[data-variance="2"] h2.title{ font-size:calc(clamp(30px,5.6vw,68px)*var(--scale)); letter-spacing:-.02em; }
html[data-variance="2"] .bento .card:nth-child(4n+1){ grid-column:span 2; }
```

| Dial | grid | header | type | feel |
|---|---|---|---|---|
| 0 | symmetric | centered | base | calm, predictable |
| 1 | golden split | offset | base | modern |
| 2 | broken | shifted | oversized | expressive editorial |

Rule of thumb: raise variance for hero/landing, keep it low for scan-read reports.

---

## 3. MOTION_INTENSITY — animation depth

Controls stillness vs. cinematic. **Read in JS** to gate behavior; CSS only freezes ambient.

```css
/* CSS: freeze ambient + guarantee content visible at level 0 */
html[data-motion="0"] .aurora{ animation:none !important; }
html[data-motion="0"] .reveal{ opacity:1 !important; transform:none !important; filter:none !important; }
```

```js
const motion = +document.documentElement.dataset.motion;
if (motion === 0){
  // instant: reveal everything, no scroll triggers, graphs static
} else {
  // 1: entrance reveals (opacity+translate, stagger), count-up, bar-fill
  // 2: + scroll parallax, pinned sections, spring physics, 3D drift, flowing gradients
}
```

| Dial | what runs | notes |
|---|---|---|
| 0 | nothing | honors `prefers-reduced-motion`; content must be visible without JS |
| 1 | entrance only | reveal on scroll-in, number count-up, bar fill |
| 2 | cinematic | + parallax, pin, spring, 3D camera drift, gradient flow |

**Two hard rules at every level:**
- Always ship a `@media (prefers-reduced-motion:reduce)` downgrade.
- Content is visible by default (progressive enhancement). Never let an animation strand
  an element at `opacity:0` if JS or a CDN fails — start visible, let JS hide-then-reveal.

---

## 4. Putting it together (live dials)

The three dials can be exposed as sliders that re-theme the page in real time. Pattern:

```js
function setDial(key, attr){ document.documentElement.dataset[attr] = dials[key].value; }
// variance/density → pure CSS reflow; motion → re-run the gate function
dials.m.addEventListener('input', ()=>{ setDial('m','motion'); applyMotion(); });
```

Working implementation: `../demo/taste-demo.html` (panel + `applyMotion()`), including three
presets that snap all three dials to the per-deliverable defaults.
