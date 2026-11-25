(() => {
  const boot = window.ZAL_BOOT || {};
  const state = {
    project: null,
    mode: "create",
    selected: null, // {type:'flow'|'material'|'stack', id}
    camera: { x: 40, y: 40, scale: 0.85 },
    dragging: null,
    panning: null,
    expandedStacks: new Set(), // `${stage}::${kind}`
    catalogs: {
      packs: [],
      accents: [],
      themes: [],
      masters: { director: [], supervisor: [], producer: [] },
    },
    draftLook: null, // local multi-select draft before save
    styleCategory: "all",
    review: {
      items: [],
      columns: {},
      counts: {},
      focusId: null,
      filter: "unreviewed",
      comment: "",
      cause: "unclear",
    },
    cut: {
      timeline: null,
      duration: 0,
      clipId: null,
      pickFilter: "approved",
      pickItems: [],
      stretchEdge: null, // { clipId, side: 'L'|'R', ox, startDur, startX }
    },
  };

  const KIND_LABEL = {
    character: "角色",
    scene: "场景",
    prop: "道具",
    concept: "概念",
    storyboard: "分镜",
    audio: "音频",
    render: "成片",
    deliverable: "交付",
    still: "静帧",
  };
  const MAT_W = 176;
  const MAT_H = 196;
  const MAT_GAP = 18;
  const MAT_X0 = 340;
  const ROW_H = 220;

  const $ = (id) => document.getElementById(id);
  const api = async (path, opts = {}) => {
    const res = await fetch(path, {
      ...opts,
      headers: {
        "Content-Type": "application/json",
        "X-ZAL-Token": boot.token || "",
        ...(opts.headers || {}),
      },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      cache: "no-store",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || res.statusText);
    return data;
  };

  function applyCamera() {
    $("canvas").style.transform = `translate(${state.camera.x}px, ${state.camera.y}px) scale(${state.camera.scale})`;
  }

  function applyUiTheme(themeId) {
    document.body.dataset.theme = themeId || "soft_classic";
  }

  function syncDraftLook() {
    const p = state.project || {};
    state.draftLook = {
      ui_theme: p.ui_theme || "soft_classic",
      style_pack: p.style_pack || "warm_school",
      style_accents: [...(p.style_accents || [])],
      masters: {
        director: p.masters?.director || "青禾",
        art: p.masters?.art || "砚舟",
        camera: p.masters?.camera || "静岚",
        editor: p.masters?.editor || "听桥",
        producer: p.masters?.producer || "灯塔",
      },
    };
  }

  async function loadCatalogs() {
    const [styles, themes, masters] = await Promise.all([
      api("/api/styles"),
      api("/api/ui-themes"),
      api("/api/masters"),
    ]);
    state.catalogs.packs = styles.packs || [];
    state.catalogs.accents = styles.accents || [];
    state.catalogs.categories = styles.categories || [];
    state.catalogs.lookbookCount = styles.lookbook_count || 61;
    state.catalogs.styleCount = styles.style_count || (styles.packs || []).length;
    state.catalogs.masterCount = styles.master_count || (masters.all || []).length;
    state.catalogs.themes = themes.themes || [];
    state.catalogs.masters = masters.catalog || state.catalogs.masters;
    for (const group of Object.values(state.catalogs.masters)) {
      for (const master of group) master.cover_url = `/masters/covers/${encodeURIComponent(master.id)}.webp`;
    }
    state.catalogs.roles = masters.roles || {};
    state.catalogs.allMasters = masters.all || [];
  }

  function choiceCard({ key, value, title, blurb, multi, selected, swatch, cover }) {
    const on = selected ? " on" : "";
    const mode = multi ? "multi" : "single";
    const chips = (swatch || []).map((c) => `<i style="background:${c}"></i>`).join("");
    const coverHtml = cover
      ? `<span class="choice-cover"><img src="${cover}" alt="" loading="lazy" /></span>`
      : (chips ? `<span class="swatch">${chips}</span>` : "");
    return `<button type="button" class="choice-card${cover ? " has-cover" : ""}${on}" data-choice-key="${key}" data-choice-value="${value}" data-choice-mode="${mode}">
      ${coverHtml}
      <span class="choice-copy">
        <b>${title}</b>
        <small>${blurb || ""}</small>
      </span>
    </button>`;
  }

  function masterCard(m, { selected = false, selectable = false, role = "" } = {}) {
    const cover = m.cover_url || (m.cover ? `/masters/${m.cover}` : "");
    const sig = (m.signature || []).slice(0, 3).map((s) => `<span class="chip">${escapeHtml(s)}</span>`).join("");
    const on = selected ? " on" : "";
    const attrs = selectable
      ? `data-pick-role="${role}" data-pick-name="${escapeHtml(m.name)}"`
      : "";
    return `<article class="master-card${on}" ${attrs}>
      <div class="master-cover">${cover ? `<img src="${cover}" alt="${escapeHtml(m.name)}" loading="lazy" />` : ""}</div>
      <div class="master-body">
        <div class="card-kicker">${escapeHtml(m.title || role || "")}</div>
        <h4>${escapeHtml(m.name)}</h4>
        <p class="tagline">${escapeHtml(m.tagline || "")}</p>
        <p class="intro">${escapeHtml(m.intro || m.blurb || "")}</p>
        <div class="row wrap">${sig}</div>
        <p class="muted"><b>适用</b> ${escapeHtml(m.fit || "—")}</p>
        <p class="muted"><b>不适用</b> ${escapeHtml(m.unfit || "—")}</p>
        ${selectable ? `<button type="button" class="neu-btn ${selected ? "primary on" : ""}" data-pick-role="${role}" data-pick-name="${escapeHtml(m.name)}">${selected ? "当前选用" : "选用"}</button>` : ""}
      </div>
    </article>`;
  }

  async function loadReview(refresh = false) {
    const path = refresh ? "/api/review?refresh=1" : "/api/review";
    const data = await api(path);
    state.review.items = data.items || [];
    state.review.columns = data.columns || {};
    state.review.counts = data.counts || {};
    if (!state.review.focusId || !state.review.items.some((i) => i.id === state.review.focusId)) {
      const pool = (state.review.columns.unreviewed || []).map((c) => c.id);
      state.review.focusId = pool[0] || state.review.items[0]?.id || null;
    }
    return data;
  }

  function reviewFocusItem() {
    const pool=reviewFilterList();
    const item=pool.find(i=>i.id===state.review.focusId) || pool[0] || null;
    state.review.focusId=item?.id || null;
    return item;
  }

  function reviewFilterList() {
    const filter = state.review.filter || "unreviewed";
    if (filter === "all") return state.review.items || [];
    const ids = new Set((state.review.columns[filter] || []).map((c) => c.id));
    return (state.review.items || []).filter((i) => ids.has(i.id));
  }

  function fmtTime(t) {
    const s = Math.max(0, Number(t) || 0);
    const m = Math.floor(s / 60);
    const r = (s - m * 60).toFixed(1);
    return `${m}:${r.padStart(4, "0")}`;
  }

  async function loadTimeline() {
    const data = await api("/api/timeline");
    state.cut.timeline = data.timeline || data;
    state.cut.duration = data.duration || 0;
    const clips = state.cut.timeline.clips || [];
    if (!state.cut.clipId || !clips.some((c) => c.id === state.cut.clipId)) {
      state.cut.clipId = clips[0]?.id || null;
    }
    return data;
  }

  async function timelineOp(action, body = {}) {
    const data = await api("/api/timeline", { method: "POST", body: { action, ...body } });
    state.cut.timeline = data.timeline || state.cut.timeline;
    state.cut.duration = data.duration ?? state.cut.duration;
    if (data.clip?.id) state.cut.clipId = data.clip.id;
    if (data.left?.id) state.cut.clipId = data.left.id;
    return data;
  }

  function cutFocusClip() {
    return (state.cut.timeline?.clips || []).find((c) => c.id === state.cut.clipId) || null;
  }

  async function loadCutPickItems() {
    const snap = await api("/api/review?refresh=1");
    const selected = Object.values(snap.selected || {});
    const approved = (snap.columns?.approved || []).map((r) => ({
      asset_id: r.asset_id,
      title: r.title,
      path: r.path,
      kind: r.kind || "image",
      decision: "approved",
    }));
    const mats = Object.entries(state.project?.materials || {})
      .filter(([, m]) => m.file)
      .map(([id, m]) => ({
        asset_id: id,
        title: m.title || id,
        path: m.file,
        kind: m.media_kind || "image",
        decision: m.approved ? "approved" : "material",
      }));
    const byId = new Map();
    [...approved, ...selected.map((r) => ({
      asset_id: r.asset_id,
      title: r.title,
      path: r.path,
      kind: r.kind || "image",
      decision: r.decision || "selected",
    })), ...mats].forEach((row) => {
      if (!row.asset_id || !row.path) return;
      if (!byId.has(row.asset_id)) byId.set(row.asset_id, row);
    });
    state.cut.pickItems = [...byId.values()];
  }

  function syncCutStageVisibility() {
    const cut = state.mode === "cut";
    if(!cut) monitors?.leave();
    document.body.classList.toggle("cut-mode", cut);
    const stage = $("cutStage");
    const scroll = $("canvasScroll");
    if (stage) stage.hidden = !cut;
    if (scroll) scroll.hidden = cut;
  }

  let monitors;
  function renderCutMonitor() {
    monitors ||= window.createEditMonitors($("cutMonitor"),
      c=>mediaPreviewHtml({media_kind:c.kind,file:c.path,title:c.title},{large:true}),fmtTime,
      t=>{
        if(state.cut.timeline)state.cut.timeline.playhead=t;
        document.querySelectorAll("#cutStage .playhead").forEach(el=>el.style.left=(t*tlZoom())+"px");
      }, async t=>{try{await timelineOp("playhead",{t});}catch(e){$("panelHint").textContent=e.message;}});
    monitors.update(state.cut.timeline || {},state.cut.duration,state.cut.source || cutFocusClip());
  }

  async function seekCut(t) {
    monitors?.pause();
    await timelineOp("playhead", {t});
    await renderCutPanel();
  }

  function renderCutToolbar() {
    const bar = $("cutToolbar");
    if (!bar) return;
    const clip = cutFocusClip();
    const hasClip = Boolean(clip);
    const hasBoard = Boolean(state.cut.timeline?.clipboard);
    const sound=hasClip && clip.kind!=="image";
    const speed=Number(clip?.speed || 1);
    const steps=[0.125,0.25,0.5,1,2,4,8];
    const slower=steps.filter(x=>x<speed).pop();
    const faster=steps.find(x=>x>speed);
    bar.innerHTML = `
      <button type="button" class="neu-btn" id="focusCut">${document.body.dataset.focus === "cut" ? "收回剪辑" : "全屏剪辑"}</button>
      <button type="button" class="neu-btn" data-cut="undo" ${state.cut.timeline?.can_undo?"":"disabled"} title="Ctrl/Cmd + Z">撤销</button>
      <button type="button" class="neu-btn" data-cut="redo" ${state.cut.timeline?.can_redo?"":"disabled"} title="Ctrl/Cmd + Shift + Z 或 Ctrl + Y">重做</button>
      <button type="button" class="neu-btn" data-cut="prevFrame">上一帧</button>
      <button type="button" class="neu-btn" data-cut="nextFrame">下一帧</button>
      <button type="button" class="neu-btn primary" data-cut="seed">从选片导入</button>
      <button type="button" class="neu-btn" data-cut="split" ${hasClip ? "" : "disabled"}>剪开</button>
      <div class="cut-speed-group" role="group" aria-label="片段速度">
        <button type="button" class="neu-btn" data-speed="${slower || speed}" ${hasClip && slower ? "" : "disabled"}>慢速${slower && hasClip ? " "+slower+"×" : ""}</button>
        <button type="button" class="neu-btn" data-speed="1" ${hasClip && speed!==1 ? "" : "disabled"}>原速 1×</button>
        <button type="button" class="neu-btn" data-speed="${faster || speed}" ${hasClip && faster ? "" : "disabled"}>加速${faster && hasClip ? " "+faster+"×" : ""}</button>
      </div><output id="cutSpeedStatus" aria-live="polite">${hasClip ? "当前 "+speed+"×" : "请选择片段"}</output>
      <button type="button" class="neu-btn" data-cut="copy" ${hasClip ? "" : "disabled"}>复制</button>
      <button type="button" class="neu-btn" data-cut="paste" ${hasBoard ? "" : "disabled"}>粘贴</button>
      <button type="button" class="neu-btn" data-cut="remove" ${hasClip ? "" : "disabled"}>删镜头</button>
      <label class="cut-zoom">缩放
        <input type="range" id="cutZoom" min="20" max="120" step="4" value="${tlZoom()}" />
      </label>
      <details class="clip-inspector"><summary>修剪与声音</summary>
        <div class="clip-inspector-form">
        <label>入点（素材秒）<input type="number" min="0" step="0.01" id="trimIn" value="${clip?.in_point || 0}"></label>
        <button class="neu-btn" data-mark-time="trimIn" ${sound?"":"disabled"}>播放头设入点</button>
        <label>出点（素材秒）<input type="number" min="0" step="0.01" id="trimOut" value="${clip?.out_point ?? clip?.duration ?? 0}"></label>
        <button class="neu-btn" data-mark-time="trimOut" ${sound?"":"disabled"}>播放头设出点</button>
        <button class="neu-btn" data-cut="trimRange" ${sound?"":"disabled"}>仅保留此段</button>
        <label>片段音量<input type="range" min="0" max="100" id="clipVolume" value="${Math.round((clip?.volume ?? 1)*100)}" ${sound?"":"disabled"}></label>
        <button class="neu-btn" data-cut="mute" ${sound?"":"disabled"}>${clip?.muted?"恢复声音":"静音"}</button>
        </div></details>
      <div class="cut-export"><select id="exportAspect" aria-label="成片画幅"><option value="landscape">横屏 16:9</option><option value="portrait">竖屏 9:16</option><option value="square">方形 1:1</option></select>
      <button class="neu-btn" id="exportCut" ${state.cut.exporting || !state.cut.timeline?.clips?.length?"disabled":""}>${state.cut.exporting?"正在导出":"导出 MP4"}</button>
      <span id="exportResult" role="status"></span></div>`;
    $("exportAspect").value=state.cut.aspect || "landscape";
    $("exportAspect").onchange=e=>state.cut.aspect=e.target.value;
    const exported=state.cut.lastExport;
    if(exported){
      const link=document.createElement("a");link.href=exported.file;link.download="";link.textContent="下载成片";$("exportResult").append(link);
    }
    if(state.cut.exporting)$("exportResult").textContent="正在导出…";
    window.cutIcon($("exportCut"),"export");
    $("exportCut").onclick=async()=>{
      if(state.cut.exporting)return;
      state.cut.exporting=true;renderCutToolbar();
      try{state.cut.lastExport=await api("/api/export-cut",{method:"POST",body:{aspect:state.cut.aspect || "landscape"}});}
      catch(err){state.cut.exportError=err.message;}
      finally{
        state.cut.exporting=false;
        if(state.mode==="cut"){renderCutToolbar();if(state.cut.exportError)$("exportResult").textContent=state.cut.exportError;}
        state.cut.exportError=null;
      }
    };
    window.cutIcon($("focusCut"),document.body.dataset.focus==="cut"?"collapse":"expand");
    bar.querySelectorAll("[data-cut]").forEach(b=>{
      const action=b.dataset.cut;
      window.cutIcon(b,action==="mute" && clip?.muted?"sound":action,b.textContent.trim(),
        ({undo:"Ctrl / ⌘ + Z",redo:"Ctrl / ⌘ + Shift + Z"})[action]);
    });
    bar.querySelectorAll("[data-speed]").forEach((b,i)=>window.cutIcon(b,["slow","normal","fast"][i]));
    bar.querySelectorAll("[data-mark-time]").forEach(b=>window.cutIcon(b,b.dataset.markTime));
    bar.querySelectorAll("[data-mark-time]").forEach(b=>b.onclick=()=>{
      const t=Number(state.cut.timeline.playhead || 0)-clip.start;
      if(t<0 || t>clip.duration){$("cutSpeedStatus").textContent="请把全片播放头移到所选片段内。";return;}
      $(b.dataset.markTime).value=((clip.in_point || 0)+t*(clip.speed || 1)).toFixed(3);
    });
    $("clipVolume").onchange=()=>runCutAction("volume").catch(e=>$("cutSpeedStatus").textContent=e.message);
    bar.querySelectorAll("[data-cut]").forEach((btn) => {
      btn.onclick = async () => {
        try {
          await runCutAction(btn.dataset.cut);
        } catch (err) {
          $("panelHint").textContent = String(err.message || err);
          $("cutSpeedStatus").textContent=err.message;
        }
      };
    });
    bar.querySelectorAll("[data-speed]").forEach(button=>button.onclick=()=>changeClipSpeed(clip,Number(button.dataset.speed)));
    $("focusCut").onclick = () => focusWorkspace(document.body.dataset.focus === "cut" ? "" : "cut");
    const zoom = $("cutZoom");
    if (zoom) {
      zoom.oninput = async () => {
        await timelineOp("zoom", { zoom: Number(zoom.value) });
        renderCutTracks();
      };
    }
  }

  function tlZoom() {
    return Number(state.cut.timeline?.zoom || 48);
  }

  async function changeClipSpeed(clip,speed) {
    if(!clip || state.cut.settingSpeed) return;
    const status=$("cutSpeedStatus");
    if(!Number.isFinite(speed) || speed<=0.05 || speed>8){
      status.textContent="速度需大于 0.05 且不超过 8 倍。";return;
    }
    state.cut.settingSpeed=true;
    try{
      await timelineOp("speed",{clip_id:clip.id,speed});
      if(state.mode==="cut") await renderCutPanel();
    }catch(error){status.textContent=error.message;}
    finally{state.cut.settingSpeed=false;}
  }

  function renderCutTracks() {
    const tracks = $("cutTracks");
    const ruler = $("cutRuler");
    if (!tracks || !ruler) return;
    const tl = state.cut.timeline || { clips: [], playhead: 0 };
    const zoom = tlZoom();
    const dur = Math.max(state.cut.duration || 0, 8);
    const width = Math.max(480, Math.ceil(dur * zoom) + 80);
    const ticks = [];
    for (let t = 0; t <= dur + 0.01; t += 1) {
      ticks.push(`<span class="tick" style="left:${t * zoom}px">${fmtTime(t)}</span>`);
    }
    ruler.innerHTML = `<div class="ruler-inner" style="width:${width}px">${ticks.join("")}
      <i class="playhead" style="left:${(tl.playhead || 0) * zoom}px"></i></div>`;
    const lanes=new Set(["V1",...(tl.clips || []).map(c=>c.track || "V1")]);
    tracks.innerHTML = [...lanes].map(track=>`
      <div class="track-label">${escapeHtml(track)}</div>
      <div class="track-lane" style="width:${width}px">
        ${(tl.clips || []).filter(c=>(c.track || "V1")===track).map((c) => {
          const w = Math.max(28, Number(c.duration) * zoom);
          const on = c.id === state.cut.clipId ? " on" : "";
          return `<div class="tl-clip${on}" data-clip="${c.id}" style="left:${Number(c.start) * zoom}px;width:${w}px" title="${escapeHtml(c.title || c.id)}">
            <i class="edge L" data-edge="L"></i>
            <span>${escapeHtml(c.title || c.id)}<small>${Number(c.duration).toFixed(1)}s · ${Number(c.speed || 1).toFixed(2)}×</small></span>
            <i class="edge R" data-edge="R"></i>
          </div>`;
        }).join("")}
        <i class="playhead" style="left:${(tl.playhead || 0) * zoom}px"></i>
      </div>`).join("");
    ruler.onclick = async (ev) => {
      const inner = ruler.querySelector(".ruler-inner");
      if (!inner) return;
      const rect = inner.getBoundingClientRect();
      const t = Math.max(0, (ev.clientX - rect.left) / zoom);
      await seekCut(t);
    };
    tracks.querySelectorAll(".tl-clip").forEach((el) => {
      el.onclick = (ev) => {
        if (ev.target.closest(".edge")) return;
        state.cut.source=null;
        state.cut.clipId = el.dataset.clip;
        renderCutMonitor();
        renderCutToolbar();
        renderCutTracks();
        renderCutPanel();
      };
      el.querySelectorAll(".edge").forEach((edge) => {
        edge.onpointerdown = (ev) => {
          ev.preventDefault();
          ev.stopPropagation();
          const clip = (state.cut.timeline?.clips || []).find((c) => c.id === el.dataset.clip);
          if (!clip) return;
          state.cut.stretchEdge = {
            clipId: clip.id,
            side: edge.dataset.edge,
            ox: ev.clientX,
            startDur: Number(clip.duration),
            startStart: Number(clip.start),
          };
          edge.setPointerCapture(ev.pointerId);
        };
      });
    });
  }

  async function runCutAction(action) {
    const clip = cutFocusClip();
    const tl = state.cut.timeline || {};
    if (action === "prevFrame" || action === "nextFrame") {
      const frame = Math.round((tl.playhead || 0) * tl.fps) + (action === "prevFrame" ? -1 : 1);
      return seekCut(frame / tl.fps);
    }
    monitors?.pause();
    if(action==="undo" || action==="redo"){
      await timelineOp(action);
      if(!cutFocusClip())state.cut.clipId=state.cut.timeline.clips[0]?.id || null;
      state.cut.source=null;
    }else if(action==="trimRange" && clip){
      const start=Number($("trimIn").value),end=Number($("trimOut").value);
      if(start<0 || end-start<0.1)throw Error("出点须在入点之后，至少保留 0.1 秒。");
      await timelineOp("trim",{clip_id:clip.id,in_point:start,out_point:end});
    }else if((action==="volume" || action==="mute") && clip){
      const change=action==="volume"?{volume:Number($("clipVolume").value)/100}:{muted:!clip.muted};
      await timelineOp("mix",{clip_id:clip.id,...change});
    }else if (action === "seed") {
      await timelineOp("seed");
    } else if (action === "split") {
      if (!clip) return;
      const at = Number(tl.playhead);
      const inside = at > clip.start + 0.05 && at < clip.start + clip.duration - 0.05;
      const splitAt = inside ? at : clip.start + clip.duration / 2;
      await timelineOp("split", { clip_id: clip.id, at: splitAt });
    } else if (action === "copy") {
      if (!clip) return;
      await timelineOp("copy", { clip_id: clip.id });
    } else if (action === "paste") {
      await timelineOp("paste", { after_id: clip?.id });
    } else if (action === "remove") {
      if (!clip) return;
      await timelineOp("remove", { clip_id: clip.id });
      state.cut.clipId = null;
    }
    renderCutStage();
    await renderCutPanel();
  }

  function renderCutStage() {
    syncCutStageVisibility();
    if (state.mode !== "cut") return;
    renderCutMonitor();
    renderCutToolbar();
    renderCutTracks();
  }

  async function renderCutPanel() {
    $("panelTitle").textContent = "剪辑 · 时间线";
    $("panelHint").textContent = "选片进轨 · 拖边缘拉伸 · 播放头处剪开 · 复制粘贴 · 调速加减镜头";
    if (!state.cut.timeline) await loadTimeline();
    if (!state.cut.pickItems.length) await loadCutPickItems();
    if(state.mode!=="cut")return;
    const clip = cutFocusClip();
    const filter = state.cut.pickFilter;
    const pool = state.cut.pickItems.filter((it) => {
      if (filter === "approved") return it.decision === "approved" || it.decision === "selected";
      return true;
    });
    const body = $("panelBody");
    body.innerHTML = `
      <div class="row">
        <button type="button" class="neu-btn${filter === "approved" ? " on primary" : ""}" data-pick-filter="approved">已选/通过</button>
        <button type="button" class="neu-btn${filter === "all" ? " on primary" : ""}" data-pick-filter="all">全部素材</button>
        <button type="button" class="neu-btn" id="btnRefreshPick">刷新</button>
      </div>
      <h3 class="subhead">选片入库</h3>
      <div class="review-list cut-pick">${pool.slice(0, 48).map((it) => `
        <div class="cut-pick-item"><button type="button" class="review-card" data-preview-asset="${it.asset_id}">
          ${mediaPreviewHtml({ media_kind: it.kind, file: it.path, title: it.title })}
          <b>${escapeHtml(it.title || it.asset_id)}</b>
          <small>${escapeHtml(it.decision || "")}</small>
        </button><button type="button" class="neu-btn" data-add-asset="${it.asset_id}">加入时间线</button>
        ${it.kind==="audio"?`<button type="button" class="neu-btn" data-add-asset="${it.asset_id}" data-track="A1">在播放头叠加声音</button>`:""}</div>`).join("") || `<p class="muted">暂无可选素材。先去「选片」通过几张，或点全部素材。</p>`}</div>
      <h3 class="subhead">镜头属性</h3>
      ${clip ? `
        <label>时长（秒）拉伸</label>
        <div class="row">
          <input type="number" id="cutDur" min="0.2" step="0.1" value="${Number(clip.duration).toFixed(1)}" />
          <button type="button" class="neu-btn" id="btnStretch">应用拉伸</button>
        </div>
        <label>速度</label>
        <div class="row">
          <input type="number" id="cutSpeed" min="0.1" max="8" step="0.05" value="${Number(clip.speed || 1).toFixed(2)}" />
          <button type="button" class="neu-btn" id="btnSpeed">调速</button>
        </div>
        <div class="row">
          <button type="button" class="neu-btn" id="btnMoveLeft">← 前移</button>
          <button type="button" class="neu-btn" id="btnMoveRight">后移 →</button>
        </div>
        <p class="muted">入点 ${Number(clip.in_point || 0).toFixed(2)} · 出点 ${Number(clip.out_point || 0).toFixed(2)}</p>
      ` : `<p class="muted">点时间线上的镜头，或从上方选片加一条。</p>`}`;
    body.querySelectorAll("[data-pick-filter]").forEach((btn) => {
      btn.onclick = () => {
        state.cut.pickFilter = btn.dataset.pickFilter;
        renderCutPanel();
      };
    });
    const refresh = $("btnRefreshPick");
    if (refresh) {
      refresh.onclick = async () => {
        await loadCutPickItems();
        await renderCutPanel();
      };
    }
    body.querySelectorAll("[data-preview-asset]").forEach(btn=>btn.onclick=()=>{
      state.cut.source=state.cut.pickItems.find(it=>it.asset_id===btn.dataset.previewAsset);
      renderCutMonitor();
    });
    body.querySelectorAll("[data-add-asset]").forEach((btn) => {
      btn.onclick = async () => {
        const row = state.cut.pickItems.find((i) => i.asset_id === btn.dataset.addAsset);
        if (!row) return;
        const card=btn.closest(".cut-pick-item");
        const duration=card?.querySelector("audio,video")?.duration;
        await timelineOp("add", {
          asset_id: row.asset_id,
          path: row.path,
          kind: row.kind,
          title: row.title,
          after_id: state.cut.clipId,
          track:btn.dataset.track || "V1",
          start:btn.dataset.track ? state.cut.timeline?.playhead || 0 : 0,
          source_duration:Number.isFinite(duration) && duration>0 ? duration : undefined,
        });
        renderCutStage();
        await renderCutPanel();
      };
    });
    const btnStretch = $("btnStretch");
    if (btnStretch) {
      btnStretch.onclick = async () => {
        await timelineOp("stretch", { clip_id: clip.id, duration: Number($("cutDur").value) });
        renderCutStage();
        await renderCutPanel();
      };
    }
    const btnSpeed = $("btnSpeed");
    if (btnSpeed) {
      btnSpeed.onclick = () => changeClipSpeed(clip,Number($("cutSpeed").value));
    }
    const clips = state.cut.timeline?.clips || [];
    const idx = clips.findIndex((c) => c.id === clip?.id);
    const btnL = $("btnMoveLeft");
    const btnR = $("btnMoveRight");
    for(const [id,icon] of Object.entries({btnRefreshPick:"refresh",btnStretch:"stretch",btnSpeed:"fast",btnMoveLeft:"left",btnMoveRight:"right"}))window.cutIcon($(id),icon);
    body.querySelectorAll("[data-add-asset]").forEach(b=>window.cutIcon(b,b.dataset.track?"addAudio":"add"));
    if (btnL) {
      btnL.onclick = async () => {
        if (idx <= 0) return;
        await timelineOp("move", { clip_id: clip.id, index: idx - 1 });
        renderCutStage();
        await renderCutPanel();
      };
    }
    if (btnR) {
      btnR.onclick = async () => {
        if (idx < 0 || idx >= clips.length - 1) return;
        await timelineOp("move", { clip_id: clip.id, index: idx + 1 });
        renderCutStage();
        await renderCutPanel();
      };
    }
    renderCutStage();
  }

  async function renderReviewPanel() {
    try {
      if (!state.review.items.length) await loadReview(true);
    } catch (err) {
      $("panelTitle").textContent = "选片";
      $("panelHint").textContent = String(err);
      return;
    }
    if(state.mode!=="edit")return;
    const item = reviewFocusItem();
    const counts = state.review.counts || {};
    const list = reviewFilterList();
    $("panelTitle").textContent = "选片 · 审片台";
    $("panelHint").textContent = "检查完整画面和声音。点「通过」后，此版本将用于制作。";

    const stageHtml = item ? `
      <div class="review-stage">
        ${mediaPreviewHtml({
          media_kind: item.kind,
          file: item.path,
          title: item.title,
        }, { large: true })}
        <div class="row wrap">
          <span class="chip on">${mediaLabel(item.kind)}</span>
          <span class="chip">v${item.version || 0}</span>
          <span class="chip">${item.decision || "未审"}</span>
          <span class="chip">${escapeHtml(item.asset_id || "")}</span>
          <a href="${escapeHtml(mediaUrl(item.path))}" target="_blank" rel="noopener">查看原文件</a>
        </div>
        <p class="muted">${escapeHtml(item.task || "")} · ${escapeHtml(item.path || "")}</p>
        ${item.note ? `<p class="muted">版本备注：${escapeHtml(item.note)}</p>` : ""}
      </div>` : `<p class="muted">队列为空。点「刷新素材」从 materials/ 同步。</p>`;

    const listHtml = list.map((it) => `
      <button type="button" class="review-card${it.id === state.review.focusId ? " on" : ""}" data-review-id="${it.id}">
        ${mediaPreviewHtml({ media_kind: it.kind, file: it.path, title: it.title })}
        <span><b>${escapeHtml(it.title || it.asset_id || "")}</b>
        <small>v${it.version || 0} · ${it.decision || "未审"}</small></span>
      </button>`).join("") || `<p class="muted">这一栏没有条目。</p>`;

    const filters = [
      ["unreviewed", "未审", counts.unreviewed || 0],
      ["deferred", "待定", counts.deferred || 0],
      ["approved", "通过", counts.approved || 0],
      ["rejected", "不通过", counts.rejected || 0],
      ["archived", "存档", counts.archived || 0],
      ["all", "全部", state.review.items.length],
    ];

    $("panelBody").innerHTML = `
      <div class="row wrap">
        ${filters.map(([id, label, n]) =>
          `<button type="button" class="neu-btn${state.review.filter === id ? " on primary" : ""}" data-review-filter="${id}">${label} ${n}</button>`
        ).join("")}
        <button type="button" class="neu-btn" id="btnReviewRefresh">刷新素材</button>
      </div>
      ${stageHtml}
      <label>审片意见</label>
      <textarea id="reviewComment" rows="3" placeholder="写一句为什么通过/不通过……">${escapeHtml(state.review.comment || "")}</textarea>
      <label for="reviewCause">需要改哪里</label>
      <select id="reviewCause">
        ${["unclear", "model", "keyframe", "prompt", "pipeline"].map((c) =>
          `<option value="${c}" ${state.review.cause === c ? "selected" : ""}>${({unclear:"还说不清",model:"人物或造型",keyframe:"关键画面",prompt:"创作描述",pipeline:"制作流程"})[c]}</option>`).join("")}
      </select>
      <div class="row sticky-actions">
        <button type="button" class="neu-btn primary" data-review-decision="approved" ${item ? "" : "disabled"}>通过</button>
        <button type="button" class="neu-btn" data-review-decision="rejected" ${item ? "" : "disabled"}>不通过</button>
        <button type="button" class="neu-btn" data-review-decision="deferred" ${item ? "" : "disabled"}>待定</button>
        <button type="button" class="neu-btn" data-review-decision="archived" ${item ? "" : "disabled"}>存档</button>
      </div>
      <h3 class="subhead">队列</h3>
      <div class="review-list">${listHtml}</div>`;

    const reviewVideo=$("panelBody").querySelector(".review-stage video");
    if(reviewVideo){reviewVideo.controls=true;reviewVideo.muted=false;}
    $("btnReviewRefresh").onclick = async () => {
      await loadReview(true);
      await renderReviewPanel();
    };
    $("panelBody").querySelectorAll("[data-review-filter]").forEach((btn) => {
      btn.onclick = async () => {
        state.review.filter = btn.dataset.reviewFilter;
        const pool = reviewFilterList();
        if (pool.length && !pool.some((i) => i.id === state.review.focusId)) {
          state.review.focusId = pool[0].id;
        }
        await renderReviewPanel();
      };
    });
    $("panelBody").querySelectorAll("[data-review-id]").forEach((btn) => {
      btn.onclick = async () => {
        state.review.focusId = btn.dataset.reviewId;
        await renderReviewPanel();
      };
    });
    const commentEl = $("reviewComment");
    const causeEl = $("reviewCause");
    if (commentEl) commentEl.oninput = () => { state.review.comment = commentEl.value; };
    if (causeEl) causeEl.onchange = () => { state.review.cause = causeEl.value; };
    $("panelBody").querySelectorAll("[data-review-decision]").forEach((btn) => {
      btn.onclick = async () => {
        const focus = reviewFocusItem();
        if (!focus) return;
        const decision = btn.dataset.reviewDecision;
        const resp = await api("/api/review", {
          method: "POST",
          body: {
            action: "decide",
            id: focus.id,
            decision,
            comment: $("reviewComment")?.value || "",
            cause: decision === "rejected" ? ($("reviewCause")?.value || "unclear") : undefined,
            sha256: focus.sha256,
            previous_event_id: focus.latest_event?.event_id || null,
            bind_on_approve: true,
          },
        });
        state.review.items = resp.items || [];
        state.review.columns = resp.columns || {};
        state.review.counts = resp.counts || {};
        state.review.comment = "";
        // auto-advance like PCV desk
        const nextPool = (state.review.columns.unreviewed || []).map((c) => c.id);
        state.review.focusId = nextPool[0] || focus.id;
        await renderReviewPanel();
        if (decision === "approved") await reload();
      };
    });
  }

  async function renderAgentsPanel() {
    if (!state.catalogs.allMasters?.length) {
      try { await loadCatalogs(); } catch (_) { /* ignore */ }
    }
    const current = state.project.masters || {};
    const roles = state.catalogs.roles || {};
    const cats = state.catalogs.masters || {};
    $("panelTitle").textContent = "助手 · 多大师";
    $("panelHint").textContent = "参考 zima-anima：每位大师有封面与介绍；点选用写入当前阵容。";
    const creativeRoles = ["director","art","camera","editor","producer"];
    const lineup = creativeRoles.map((role) => {
      const name = current[role] || "";
      const m = (cats[role] || []).find((x) => x.name === name) || { name, title: roles[role]?.title || role };
      return masterCard(m, { selected: true, role });
    }).join("");
    const galleries = creativeRoles.map((role) => {
      const label = roles[role]?.title || role;
      const blurb = roles[role]?.blurb || "";
      const cards = (cats[role] || []).map((m) => masterCard(m, {
        selected: current[role] === m.name,
        selectable: true,
        role,
      })).join("");
      return `<h3 class="subhead">${label}</h3><p class="muted">${blurb}</p><div class="master-grid">${cards}</div>`;
    }).join("");
    $("panelBody").innerHTML = `
      <div class="row">
        <span class="chip on">风格 ${state.project.style_pack || "—"}</span>
        <span class="chip">界面 ${state.project.ui_theme || "soft_classic"}</span>
      </div>
      <h3 class="subhead">当前阵容</h3>
      <div class="master-grid lineup">${lineup}</div>
      <div class="row">
        <button type="button" class="neu-btn" id="btnGotoLook">去风格与大师节点</button>
      </div>
      <h3 class="subhead">全部大师（封面 · 介绍 · 适用）</h3>
      ${galleries}`;
    $("btnGotoLook").onclick = () => {
      state.mode = "create";
      [...$("modeTabs").children].forEach((b) => b.classList.toggle("on", b.dataset.mode === "create"));
      select("flow", "look");
    };
    $("panelBody").querySelectorAll("[data-pick-role]").forEach((el) => {
      el.onclick = async (ev) => {
        ev.stopPropagation();
        const role = el.dataset.pickRole;
        const name = el.dataset.pickName;
        if (!role || !name) return;
        await api("/api/masters", { method: "POST", body: { [role]: name } });
        await reload();
        state.mode = "agents";
        [...$("modeTabs").children].forEach((b) => b.classList.toggle("on", b.dataset.mode === "agents"));
        await renderAgentsPanel();
      };
    });
  }

  async function renderStoryPanel(node) {
    $("panelTitle").textContent = "故事剧本";
    $("panelHint").textContent = state.project.legacy?.source_title || state.project.title;
    let story = { text: "", annotations: [], comments: [], open_feedback: [], draft: null, version: 0, beats: [], history: [] };
    try {
      story = await api("/api/story");
    } catch (error) { $("panelHint").textContent = error.message; return; }
    const documents = [{label:"Light 工作稿",text:story.text || ""}];
    if (state.project.legacy?.source_root) {
      try {
        const response = await fetch("/media/development/screenplay-v001.md");
        if (response.ok) documents.push({label:"原工程 · 改编剧本 v001",text:await response.text(),source:true});
      } catch (_) { /* The local working script remains available offline. */ }
    }
    if (state.selected?.id !== "story" || !["materials","create"].includes(state.mode)) return;
    if (documents.length > 1 && !state.storyEdited) documents.reverse();
    const openN = (story.open_feedback || []).length;
    const annHtml = (story.annotations || []).slice().reverse().map((a) => `
      <div class="feedback-card ${a.status}">
        <div class="row"><span class="chip on">${a.kind}</span><span class="chip">${a.status}</span><span class="chip">${a.author || ""}</span></div>
        ${a.quote ? `<p class="quote">「${escapeHtml(a.quote)}」</p>` : ""}
        <p>${escapeHtml(a.body || "")}</p>
        ${a.suggestion ? `<p class="muted">建议改写：${escapeHtml(a.suggestion)}</p>` : ""}
        ${a.status === "open" ? `<div class="row">
          <button type="button" class="neu-btn" data-resolve="${a.id}" data-status="accepted">采纳</button>
          <button type="button" class="neu-btn" data-resolve="${a.id}" data-status="dismissed">忽略</button>
        </div>` : ""}
      </div>`).join("") || `<p class="muted">还没有注解。选中正文片段后点「加注解」。</p>`;
    const comHtml = (story.comments || []).slice().reverse().map((c) => `
      <div class="feedback-card ${c.status}">
        <div class="row"><span class="chip on">评论</span><span class="chip">${c.status}</span><span class="chip">${c.author || ""}</span></div>
        <p>${escapeHtml(c.body || "")}</p>
        ${c.status === "open" ? `<button type="button" class="neu-btn" data-resolve="${c.id}" data-status="resolved">标为已解决</button>` : ""}
      </div>`).join("") || `<p class="muted">还没有评论。</p>`;
    const beatHtml = (story.beats || []).map((b) => `<span class="chip">${b.id} · ${escapeHtml(b.text || "")}</span>`).join("")
      || `<span class="muted">保存剧本后会自动抽出节拍。</span>`;
    const draft = story.draft;
    $("panelBody").innerHTML = `
      <section id="screenplayReader"></section>
      <details class="script-edit" id="storyEdit"><summary>工作稿编辑与批注</summary>
      <div class="row">
        <span class="chip on">v${story.version || 0}</span>
        <span class="chip">开放反馈 ${openN}</span>
        <span class="chip">${node.status}</span>
      </div>
      <label for="storyEditor">工作稿正文</label>
      <textarea id="storyEditor" rows="12" placeholder="写下 logline、场次与对白……">${escapeHtml(story.text || "")}</textarea>
      <div class="row">
        <button type="button" class="neu-btn primary" id="btnSaveStory">保存剧本</button>
        <button type="button" class="neu-btn" id="btnAnnotate">加注解</button>
        <button type="button" class="neu-btn" id="btnComment">加评论</button>
      </div>
      </details><details class="script-edit"><summary>节拍与反馈 · ${openN} 条待处理</summary>
      <h3 class="subhead">节拍</h3>
      <div class="row wrap">${beatHtml}</div>
      <h3 class="subhead">注解</h3>
      <div class="feedback-list">${annHtml}</div>
      <h3 class="subhead">评论</h3>
      <div class="feedback-list">${comHtml}</div>
      <h3 class="subhead">迭代创作</h3>
      <p class="muted">把开放注解/评论收成修订草稿（先草稿，再采纳，不直接覆盖）。</p>
      <div class="row">
        <button type="button" class="neu-btn primary" id="btnIterate">根据反馈迭代</button>
        ${draft ? `<button type="button" class="neu-btn" id="btnApplyDraft">采纳草稿</button>
        <button type="button" class="neu-btn" id="btnDiscardDraft">丢弃草稿</button>` : ""}
        <button type="button" class="neu-btn" id="btnApproveStory">确认本节点</button>
      </div>
      ${draft ? `<label>迭代草稿</label><textarea id="draftEditor" rows="10">${escapeHtml(draft.text || "")}</textarea>
        <p class="muted">草稿基于反馈 ${(draft.based_on_feedback || []).join(", ") || "—"} · ${draft.created_at || ""}</p>` : ""}
      </details><details class="script-edit"><summary>版本记录</summary>
      <div class="version-list">${(story.history || []).slice().reverse().slice(0, 8).map((h) =>
        `<div class="version-row"><div><b>v${h.version}</b> · ${escapeHtml(h.note || "")}</div><span class="muted">${h.at || ""}</span></div>`
      ).join("") || '<p class="muted">尚无历史版本。</p>'}</div></details>`;

    const editor = $("storyEditor");
    if (state.storyBuffer?.base === story.text) {
      editor.value = state.storyBuffer.text;
      $("storyEdit").open = true;
    }
    editor.oninput = () => { state.storyBuffer = {base:story.text,text:editor.value}; };
    window.mountScreenplay($("screenplayReader"), documents, doc => {
      if (doc.source && editor.value !== doc.text) {
        if (editor.value !== story.text && !confirm("用原工程剧本替换编辑框中尚未保存的文字？")) return;
        editor.value = doc.text;
        editor.oninput();
      }
      $("storyEdit").open = true;
      editor.focus();
      editor.scrollIntoView({block:"center"});
    }, [...story.annotations, ...story.comments], async (type, anchor, note) => {
      const data = await api("/api/story",{method:"POST",body:{
        action:type, kind:"note", quote:anchor.quote, anchor, body:note
      }});
      return data.annotation || data.comment;
    }, id=>api("/api/story",{method:"POST",body:{action:"resolve",id,status:"dismissed"}}), (doc,title)=>{
      const scene=title.match(/^(?:S\d+|第[零〇一二三四五六七八九十百\d]+场)/i)?.[0] || title;
      state.sceneContext={scene,script:doc.source?"source":"working",title};
      $("modeTabs").querySelector('[data-mode="generate"]').click();
    });
    $("btnSaveStory").onclick = async () => {
      await api("/api/story", { method: "POST", body: { action: "save", text: editor.value, note: "edit" } });
      state.storyEdited = true;
      state.storyBuffer = null;
      await renderStoryPanel(node);
    };
    $("btnAnnotate").onclick = async () => {
      const sel = window.getSelection && editor === document.activeElement
        ? { start: editor.selectionStart, end: editor.selectionEnd, quote: editor.value.slice(editor.selectionStart, editor.selectionEnd) }
        : { start: editor.selectionStart, end: editor.selectionEnd, quote: editor.value.slice(editor.selectionStart, editor.selectionEnd) };
      if (!sel.quote) {
        alert("先在正文里选中要注解的句子。");
        return;
      }
      const kind = prompt("注解类型：note / edit / question", "edit") || "note";
      const body = prompt("注解说明", kind === "question" ? "这里动机清楚吗？" : "请改得更具体") || "";
      if (!body.trim()) return;
      const suggestion = kind === "edit" ? (prompt("建议改写成（可选）", sel.quote) || "") : "";
      await api("/api/story", {
        method: "POST",
        body: {
          action: "annotate",
          kind,
          body,
          quote: sel.quote,
          start: sel.start,
          end: sel.end,
          suggestion,
        },
      });
      await renderStoryPanel(node);
    };
    $("btnComment").onclick = async () => {
      const body = prompt("评论内容", "这一场转折还不够硬。") || "";
      if (!body.trim()) return;
      await api("/api/story", { method: "POST", body: { action: "comment", body } });
      await renderStoryPanel(node);
    };
    $("btnIterate").onclick = async () => {
      const note = prompt("迭代备注（可选）", "消化开放反馈") || "";
      await api("/api/story", { method: "POST", body: { action: "iterate", note } });
      await renderStoryPanel(node);
    };
    const applyBtn = $("btnApplyDraft");
    if (applyBtn) {
      applyBtn.onclick = async () => {
        const draftText = $("draftEditor")?.value;
        await api("/api/story", { method: "POST", body: { action: "apply_draft", text: draftText, accept_feedback: true } });
        await renderStoryPanel(node);
      };
    }
    const discardBtn = $("btnDiscardDraft");
    if (discardBtn) {
      discardBtn.onclick = async () => {
        await api("/api/story", { method: "POST", body: { action: "discard_draft" } });
        await renderStoryPanel(node);
      };
    }
    $("btnApproveStory").onclick = async () => {
      await api("/api/story", { method: "POST", body: { action: "save", text: editor.value, note: "pre-approve" } });
      await api("/api/approve", { method: "POST", body: { node: "story", note: "story collab" } });
      await reload();
    };
    $("panelBody").querySelectorAll("[data-resolve]").forEach((btn) => {
      btn.onclick = async () => {
        await api("/api/story", {
          method: "POST",
          body: { action: "resolve", id: btn.dataset.resolve, status: btn.dataset.status },
        });
        await renderStoryPanel(node);
      };
    });
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function renderLookPanel() {
    if (!state.draftLook) syncDraftLook();
    const draft = state.draftLook;
    const cats = state.catalogs;
    const packCats = ["all", ...(cats.categories || [])];
    const catLabel = {
      all: "全部",
      campus: "校园",
      daily: "日常",
      city: "城市",
      lyric: "抒情",
      edu: "科普",
      craft: "动画工艺",
      genre: "题材气质",
      format: "成片格式",
    };
    $("panelTitle").textContent = "风格与大师";
    $("panelHint").textContent = `青少年向 Lookbook ${cats.lookbookCount || 61}：风格 ${cats.styleCount || 40} + 大师 ${cats.masterCount || 21}；单选风格包/大师，调性可多选。`;
    const themeHtml = (cats.themes || []).map((t) => choiceCard({
      key: "ui_theme",
      value: t.id,
      title: t.title,
      blurb: t.blurb,
      selected: draft.ui_theme === t.id,
      swatch: t.swatch,
    })).join("");
    const filteredPacks = (cats.packs || []).filter((p) =>
      state.styleCategory === "all" || p.category === state.styleCategory);
    const packHtml = filteredPacks.map((p) => choiceCard({
      key: "style_pack",
      value: p.id,
      cover: `/static/style-covers/${encodeURIComponent(p.id)}.webp`,
      title: p.title || p.id,
      blurb: `${p.preview || p.prompt_zh || p.prompt_prefix || ""}${(p.signature || []).length ? " · " + p.signature.slice(0, 2).join(" / ") : ""}`,
      selected: draft.style_pack === p.id,
    })).join("");
    const accentHtml = (cats.accents || []).map((a) => choiceCard({
      key: "style_accents",
      value: a.id,
      title: a.title || a.id,
      blurb: "可多选",
      multi: true,
      selected: draft.style_accents.includes(a.id),
    })).join("");
    const masterBlock = (role, label) => {
      const list = cats.masters?.[role] || [];
      return `<h3 class="subhead">${label} · ${list.length}</h3>
        <div class="choice-grid master-choices">${list.map((m) => choiceCard({
          key: `master_${role}`,
          value: m.name,
          title: m.name,
          blurb: `${m.tagline || ""} · ${(m.intro || m.blurb || "").slice(0, 72)}`,
          selected: draft.masters[role] === m.name,
          cover: m.cover_url || (m.cover ? `/masters/${m.cover}` : ""),
        })).join("")}</div>`;
    };
    const selectedPack = (cats.packs || []).find((p) => p.id === draft.style_pack);
    $("panelBody").innerHTML = `
      <h3 class="subhead">界面质感（单选）</h3>
      <div class="choice-grid">${themeHtml || '<p class="muted">暂无主题</p>'}</div>
      <h3 class="subhead">风格包（单选 · ${filteredPacks.length}/${(cats.packs || []).length}）</h3>
      <div class="row wrap" id="styleCatFilters">
        ${packCats.map((c) =>
          `<button type="button" class="neu-btn${state.styleCategory === c ? " on primary" : ""}" data-style-cat="${c}">${catLabel[c] || c}</button>`
        ).join("")}
      </div>
      <div class="choice-grid pack-choices">${packHtml || '<p class="muted">该分类暂无风格包</p>'}</div>
      ${selectedPack ? `<div class="look-agent-card">
        <b>当前风格设计 Agent</b>
        <p>${escapeHtml(selectedPack.agent || "按风格签名写光、形、动作。")}</p>
        <p class="muted">EN：${escapeHtml((selectedPack.prompt_prefix || "").slice(0, 160))}</p>
      </div>` : ""}
      <h3 class="subhead">调性标签（多选）</h3>
      <div class="choice-grid compact">${accentHtml}</div>
      ${masterBlock("director", "导演（单选）")}
      ${masterBlock("art", "艺术总监（单选）")}
      ${masterBlock("camera", "摄影 · 灯光 · 运镜（单选）")}
      ${masterBlock("editor", "剪辑大师（单选）")}
      ${masterBlock("producer", "监制（单选）")}
      <div class="row sticky-actions">
        <button type="button" class="neu-btn primary" id="btnSaveLook">保存选择</button>
        <button type="button" class="neu-btn" id="btnApproveLook">确认并进入下一步</button>
      </div>`;

    $("panelBody").querySelectorAll("[data-style-cat]").forEach((btn) => {
      btn.onclick = () => {
        state.styleCategory = btn.dataset.styleCat;
        renderLookPanel();
      };
    });
    $("panelBody").querySelectorAll(".choice-card").forEach((btn) => {
      btn.onclick = async () => {
        const key = btn.dataset.choiceKey;
        const value = btn.dataset.choiceValue;
        if (key === "ui_theme" || key === "style_pack") {
          const choices = btn.closest(".choice-grid").querySelectorAll("button");
          choices.forEach(b => b.disabled = true);
          try {
            await api("/api/setup", { method: "POST", body: { [key]: value } });
          } catch (error) {
            $("panelHint").textContent = error.message;
            return;
          } finally {
            choices.forEach(b => b.disabled = false);
          }
          state.project[key] = draft[key] = value;
          if (key === "ui_theme") applyUiTheme(value);
        } else if (key === "style_accents") {
          const set = new Set(draft.style_accents);
          if (set.has(value)) set.delete(value);
          else set.add(value);
          draft.style_accents = [...set];
        } else if (key.startsWith("master_")) {
          draft.masters[key.slice(7)] = value;
        }
        renderLookPanel();
      };
    });
    $("btnSaveLook").onclick = async () => {
      await api("/api/setup", {
        method: "POST",
        body: {
          style_pack: draft.style_pack,
          style_accents: draft.style_accents,
          ui_theme: draft.ui_theme,
          masters: draft.masters,
        },
      });
      await reload();
      state.selected = { type: "flow", id: "look" };
      syncDraftLook();
      await renderLookPanel();
    };
    $("btnApproveLook").onclick = async () => {
      await api("/api/setup", {
        method: "POST",
        body: {
          style_pack: draft.style_pack,
          style_accents: draft.style_accents,
          ui_theme: draft.ui_theme,
          masters: draft.masters,
        },
      });
      await api("/api/approve", { method: "POST", body: { node: "look", note: "style+masters" } });
      await reload();
      state.selected = { type: "flow", id: "intake" };
      await renderPanel();
    };
  }

  function statusLabel(s) {
    return ({ locked: "未解锁", ready: "可开始", in_progress: "进行中", approved: "已通过" })[s] || s;
  }

  function mediaLabel(kind) {
    return ({ image: "图", video: "视频", audio: "音频", document: "文档" })[kind] || kind || "素材";
  }

  function kindLabel(kind) {
    return KIND_LABEL[kind] || kind || "素材";
  }

  function groupKind(m) {
    return m.kind || m.media_kind || "item";
  }

  function stackKey(stage, kind) {
    return `${stage}::${kind}`;
  }

  function buildStageGroups(mats) {
    /** stage -> ordered Map(kind -> [[id, meta], ...]) */
    const byStage = new Map();
    Object.entries(mats || {}).forEach(([id, m]) => {
      const stage = m.stage || "assets";
      const kind = groupKind(m);
      if (!byStage.has(stage)) byStage.set(stage, new Map());
      const kinds = byStage.get(stage);
      if (!kinds.has(kind)) kinds.set(kind, []);
      kinds.get(kind).push([id, m]);
    });
    byStage.forEach((kinds) => {
      kinds.forEach((list) => list.sort((a, b) => String(a[0]).localeCompare(String(b[0]))));
    });
    return byStage;
  }

  function computeMaterialLayout(nodes, mats) {
    const positions = {};
    const stacks = {};
    const groups = buildStageGroups(mats);
    nodes.forEach((n, index) => {
      const y = (state.project.canvas?.nodes?.[n.id]?.y) ?? (64 + index * ROW_H);
      let col = 0;
      const kinds = groups.get(n.id) || new Map();
      kinds.forEach((items, kind) => {
        const key = stackKey(n.id, kind);
        const x = MAT_X0 + col * (MAT_W + MAT_GAP);
        const expanded = items.length === 1 || state.expandedStacks.has(key);
        stacks[key] = {
          stage: n.id,
          kind,
          ids: items.map(([id]) => id),
          x,
          y,
          count: items.length,
          expanded,
        };
        if (expanded) {
          items.forEach(([id], offset) => {
            positions[id] = { x: x + offset * (MAT_W + MAT_GAP), y, w: MAT_W, h: MAT_H, stack: key };
          });
          col += items.length;
        } else {
          items.forEach(([id]) => {
            positions[id] = { x, y, w: MAT_W, h: MAT_H, stack: key, stacked: true };
          });
          col += 1;
        }
      });
    });
    return { positions, stacks };
  }

  function toggleStack(key) {
    if (state.expandedStacks.has(key)) state.expandedStacks.delete(key);
    else state.expandedStacks.add(key);
    renderCanvas();
    renderPanel();
  }

  function collapseStack(key) {
    state.expandedStacks.delete(key);
    if (state.selected?.type === "material") {
      const m = state.project?.materials?.[state.selected.id];
      if (m && stackKey(m.stage || "assets", groupKind(m)) === key) {
        state.selected = { type: "stack", id: key };
      }
    }
    renderCanvas();
    renderPanel();
  }

  function expandStack(key) {
    state.expandedStacks.add(key);
    state.selected = { type: "stack", id: key };
    renderCanvas();
    renderPanel();
  }

  function mediaUrl(file) {
    if (!file) return "";
    const rel = String(file).replace(/\\/g, "/").replace(/^\/+/, "");
    return `/media/${rel.split("/").map(encodeURIComponent).join("/")}`;
  }

  function mediaPreviewHtml(m, { large = false } = {}) {
    const kind = m.media_kind || "image";
    const file = m.file || m.preview || "";
    const url = mediaUrl(file);
    const cls = large ? "media-preview large" : "media-preview";
    if (!url) {
      return `<div class="${cls} empty">${mediaLabel(kind)}</div>`;
    }
    if (kind === "video" || /\.(mp4|mov|webm|mkv)$/i.test(file)) {
      return `<div class="${cls}"><video src="${url}" muted playsinline preload="metadata"></video></div>`;
    }
    if (kind === "audio" || /\.(wav|mp3|m4a|aac|flac)$/i.test(file)) {
      return `<div class="${cls} audio"><span>♪</span><audio src="${url}" preload="metadata" controls></audio></div>`;
    }
    return `<div class="${cls}"><img src="${url}" alt="${escapeHtml(m.title || "")}" loading="lazy" /></div>`;
  }

  function select(type, id) {
    state.selected = { type, id };
    if (type === "flow" && id === "story") {
      state.mode = "create";
      for (const button of $("modeTabs").children) button.classList.toggle("on", button.dataset.mode === "create");
      focusWorkspace("panel");
    }
    if (type === "material") {
      const m = state.project?.materials?.[id];
      if (m) {
        const key = stackKey(m.stage || "assets", groupKind(m));
        const siblings = Object.entries(state.project.materials || {}).filter(([, meta]) =>
          (meta.stage || "assets") === (m.stage || "assets") && groupKind(meta) === groupKind(m));
        if (siblings.length > 1) state.expandedStacks.add(key);
      }
    }
    renderRail();
    renderCanvas();
    renderPanel();
  }

  function renderRail() {
    const rail = $("workflowRail");
    const nodes = state.project.nodes || [];
    const agentBadge = node => {
      if (!["ready", "active", "in_progress"].includes(node.status)) return "";
      const role = ({intake:"producer", deliver:"producer", qc:"editor", continuity_lock:"art", assets:"art",storyboard:"camera",generate_stills:"art",generate_video:"camera",audio:"editor",edit:"editor"})[node.id] || "director";
      const master = state.catalogs.masters[role]?.find(m => m.name === state.project.masters?.[role]);
      return master ? `<span class="node-agent"><img src="${escapeHtml(master.portrait || master.cover_url)}" alt="">${escapeHtml(master.name)} · ${node.status === "ready" ? "待开工" : "进行中"}</span>` : "";
    };
    const selectedFlow = state.selected?.type === "flow" ? state.selected.id : null;
    rail.innerHTML = `<h3>制作步骤</h3>` + nodes.map((n) => `
      <button type="button" class="step ${n.status}${selectedFlow === n.id ? " selected" : ""}" data-node="${n.id}">
        <b>${n.title}</b>${agentBadge(n)}
        <small>${statusLabel(n.status)}${n.gate ? " · 需确认" : ""}</small>
      </button>`).join("");
    rail.querySelectorAll("[data-node]").forEach(btn=>btn.onclick=()=>{
      state.mode="create";
      for(const tab of $("modeTabs").children) tab.classList.toggle("on",tab.dataset.mode==="create");
      focusWorkspace(["look","story"].includes(btn.dataset.node) || matchMedia("(max-width: 760px)").matches ? "panel" : "");
      select("flow",btn.dataset.node);
    });
  }

  function flowPath(a, b) {
    const x1 = a.x + (a.w || 230) / 2;
    const y1 = a.y + (a.h || 118);
    const x2 = b.x + (b.w || 230) / 2;
    const y2 = b.y;
    const mid = (y1 + y2) / 2;
    return `M ${x1} ${y1} C ${x1} ${mid}, ${x2} ${mid}, ${x2} ${y2}`;
  }

  function renderCanvas() {
    const canvas = $("canvas");
    const nodes = state.project.nodes || [];
    const flowPos = state.project.canvas?.nodes || {};
    const mats = state.project.materials || {};
    const selected = state.selected;
    const { positions, stacks } = computeMaterialLayout(nodes, mats);

    const lines = [];
    for (let i = 0; i < nodes.length - 1; i += 1) {
      const a = flowPos[nodes[i].id] || { x: 72, y: 64 + i * ROW_H, w: 230, h: 118 };
      const b = flowPos[nodes[i + 1].id] || { x: 72, y: 64 + (i + 1) * ROW_H, w: 230, h: 118 };
      const approved = nodes[i].status === "approved";
      lines.push(`<path class="flow-line${approved ? " done" : ""}" d="${flowPath(a, b)}" />`);
    }
    nodes.forEach((n, i) => {
      const stageStacks = Object.values(stacks).filter((s) => s.stage === n.id);
      if (!stageStacks.length) return;
      const a = flowPos[n.id] || { x: 72, y: 64 + i * ROW_H, w: 230, h: 118 };
      const first = stageStacks[0];
      const y = a.y + 59;
      lines.push(`<path class="flow-line branch" d="M ${a.x + 230} ${y} L ${first.x} ${y}" />`);
    });

    const flowCards = nodes.map((n) => {
      const p = flowPos[n.id] || { x: 72, y: 64 };
      const on = selected?.type === "flow" && selected.id === n.id;
      const lookSummary = n.id === "look"
        ? `${state.project.style_pack || "风格"} · ${state.project.masters?.director || "导演"} / ${state.project.ui_theme || "soft_classic"}`
        : (n.notes || "纵向主轴 · 可确认推进");
      return `<article class="card flow ${n.status}${on ? " selected" : ""}" data-type="flow" data-id="${n.id}" style="left:${p.x}px;top:${p.y}px">
        <div class="card-kicker">流程</div>
        <h4>${n.title}</h4>
        <p>${lookSummary}</p>
        <span class="badge">${statusLabel(n.status)}</span>
        ${n.id === "look" ? "" : `<button type="button" class="ghost-add" data-add-stage="${n.id}" title="在此阶段新建素材">＋素材</button>`}
      </article>`;
    }).join("");

    const matCards = [];
    Object.values(stacks).forEach((stack) => {
      const items = stack.ids.map((id) => [id, mats[id]]).filter(([, m]) => m);
      if (!items.length) return;

      if (!stack.expanded && items.length > 1) {
        const peeks = items.slice(0, 3);
        const on = selected?.type === "stack" && selected.id === `${stack.stage}::${stack.kind}`;
        matCards.push(`<article class="card material stack${on ? " selected" : ""}" data-type="stack" data-stack="${stack.stage}::${stack.kind}" style="left:${stack.x}px;top:${stack.y}px">
          <div class="stack-deck" aria-hidden="true">
            ${peeks.map(([id, m], i) => {
              const depth = peeks.length - 1 - i;
              return `<div class="stack-layer" style="transform:translate(${depth * 7}px, ${depth * 7}px);z-index:${i + 1}">${mediaPreviewHtml(m)}</div>`;
            }).join("")}
          </div>
          <div class="card-meta">
            <div class="card-kicker">${kindLabel(stack.kind)} · ${stack.count} 张</div>
            <h4>点击展开</h4>
          </div>
          <span class="stack-count">${stack.count}</span>
        </article>`);
        return;
      }

      if (items.length > 1) {
        const key = `${stack.stage}::${stack.kind}`;
        matCards.push(`<div class="stack-rail" data-collapse="${key}" style="left:${stack.x}px;top:${stack.y - 40}px">
          <span><b>${kindLabel(stack.kind)}</b> · ${stack.count} 张已展开</span>
          <button type="button" class="neu-btn stack-collapse-all" data-collapse="${key}">一键收起</button>
        </div>`);
      }

      items.forEach(([id, m]) => {
        const p = positions[id] || { x: stack.x, y: stack.y };
        const on = selected?.type === "material" && selected.id === id;
        const media = m.media_kind || "image";
        const key = `${stack.stage}::${stack.kind}`;
        const collapseBtn = items.length > 1
          ? `<button type="button" class="stack-collapse" data-collapse="${key}" title="收起整组堆叠">收起</button>`
          : "";
        matCards.push(`<article class="card material ${media}${on ? " selected" : ""}${items.length > 1 ? " in-stack" : ""}" data-type="material" data-id="${id}" data-stack="${key}" style="left:${p.x}px;top:${p.y}px">
          ${mediaPreviewHtml(m)}
          <div class="card-meta">
            <div class="card-kicker">${kindLabel(stack.kind)} · v${m.version || 0}</div>
            <h4>${m.title || id}</h4>
          </div>
          ${collapseBtn}
        </article>`);
      });
    });

    canvas.innerHTML = `
      <svg class="flow-svg" width="4200" height="${Math.max(2200, 80 + nodes.length * ROW_H)}">${lines.join("")}</svg>
      ${flowCards}${matCards.join("")}
      <button type="button" class="fab-create neu-btn primary" id="btnCreateAnywhere">＋ 创建素材</button>
    `;

    canvas.querySelectorAll(".card").forEach((card) => {
      card.onpointerdown = (ev) => {
        if (ev.target.closest(".ghost-add, .stack-collapse, .stack-collapse-all, .stack-rail") || ev.button !== 0) return;
        if (card.dataset.type === "stack") {
          expandStack(card.dataset.stack);
          return;
        }
        select(card.dataset.type, card.dataset.id);
        state.dragging = {
          type: card.dataset.type,
          id: card.dataset.id,
          ox: ev.clientX,
          oy: ev.clientY,
          x: parseFloat(card.style.left),
          y: parseFloat(card.style.top),
        };
        card.setPointerCapture(ev.pointerId);
      };
    });
    canvas.querySelectorAll("[data-collapse]").forEach((el) => {
      el.onpointerdown = (ev) => {
        ev.stopPropagation();
        ev.preventDefault();
      };
      el.onclick = (ev) => {
        ev.stopPropagation();
        collapseStack(el.dataset.collapse);
      };
    });
    canvas.querySelectorAll("[data-add-stage]").forEach((btn) => {
      btn.onclick = (ev) => {
        ev.stopPropagation();
        openCreate(btn.dataset.addStage);
      };
    });
    const fab = $("btnCreateAnywhere");
    if (fab) fab.onclick = () => openCreate(state.selected?.type === "flow" ? state.selected.id : "assets");
  }

  async function openCreate(stage) {
    const mediaKind = prompt("素材类型：image / video / audio", "image") || "image";
    const title = prompt("素材名称", "新素材") || "新素材";
    const id = `${mediaKind.slice(0, 3).toUpperCase()}-${Math.random().toString(36).slice(2, 7).toUpperCase()}`;
    await api("/api/material/create", {
      method: "POST",
      body: { id, kind: title, title, media_kind: mediaKind, stage },
    });
    await reload();
    select("material", id);
  }

  function renderLegacyBanner() {
    const banner = $("legacyBanner");
    const legacy = state.project.legacy;
    if (!legacy || !banner) return;
    banner.hidden = false;
    banner.textContent = `关联工程 · ${legacy.source_title || state.project.title} · ${legacy.shot_count || 0} 镜`;
  }

  async function renderPanel() {
    const body = $("panelBody");
    syncCutStageVisibility();
    if (state.mode==="materials" && !state.materialDetail) {
      $("panelTitle").textContent="素材库";
      $("panelHint").textContent="按类型找素材，点开可以查看版本或移到其他制作步骤。";
      const entries=Object.entries(state.project.materials || {});
      body.innerHTML='<div class="library-tools"><input type="search" aria-label="搜索素材" placeholder="搜索名称或编号"><select aria-label="素材类型"><option value="">所有类型</option></select></div><div class="library-grid"></div>';
      const filter=body.querySelector("select"), search=body.querySelector("input"), grid=body.querySelector(".library-grid");
      for(const kind of new Set(entries.map(([,m])=>groupKind(m))))filter.add(new Option(kindLabel(kind),kind));
      const list=()=>{
        const matches=entries.filter(([id,m])=>(!filter.value || groupKind(m)===filter.value) && (id+" "+m.title).toLowerCase().includes(search.value.toLowerCase().trim()));
        grid.innerHTML=matches.map(([id,m])=>`<button class="mat-thumb" data-item="${escapeHtml(id)}">${mediaPreviewHtml(m)}<span>${escapeHtml(m.title || id)}</span></button>`).join("") || '<p class="muted">没有找到素材。</p>';
        grid.querySelectorAll("button").forEach(b=>b.onclick=()=>{state.materialDetail=true;select("material",b.dataset.item);});
      };
      filter.onchange=list;search.oninput=list;list();return;
    }
    if (state.mode === "queue") {
      $("panelTitle").textContent = "守衡 · 工作流监工";
      $("panelHint").textContent = "跟踪节点与生成队列。等待付费确认的任务单独排队。";
      const next = state.project.nodes.filter(n=>["ready","in_progress"].includes(n.status));
      body.innerHTML = `<div class="queue-supervisor"><img src="/masters/covers/shouheng.webp" alt="守衡">
        <div><strong id="queueSummary">正在检查队列</strong><p>当前节点 · ${next.map(n=>escapeHtml(n.title)).join("、") || "暂无待执行节点"}</p></div></div>
        <form id="queueCommand"><label>调整队列<input required placeholder="让 S01 的分镜图插队"></label><button class="neu-btn">发送</button></form>
        <p id="queueNotice" role="status"></p><div id="queueList"></div>`;
      const list=$("queueList"), notice=$("queueNotice"), form=$("queueCommand");
      const labels={waiting:"等待付费确认",queued:"已确认 · 排队中",running:"正在提交或生成",remote:"供应商制作中",failed:"制作失败",blocked:"需要核对",done:"已完成",cancelled:"已取消"};
      const update=async()=>{
        const rows=await api("/api/work-queue");
        if (!list.isConnected) return;
        const active=rows.filter(r=>["running","remote"].includes(r.state)).length;
        const waiting=rows.filter(r=>r.state==="waiting").length;
        const held=rows.filter(r=>r.state==="blocked" || r.slow).length;
        $("queueSummary").textContent=`制作中 ${active} · 待确认 ${waiting} · 需关注 ${held}`;
        list.replaceChildren();
        if (!rows.length) list.textContent="队列为空。";
        for(const row of rows){
          const card=document.createElement("article");card.className="feedback-card";
          const title=document.createElement("b");title.textContent="#"+row.id+" "+row.title;
          const status=document.createElement("p");status.textContent=labels[row.state]+(row.slow?" · 已超过五分钟，监工持续跟踪":"")+(row.priority?" · 优先":"");
          card.append(title,status);
          if(row.result.message){const msg=document.createElement("p");msg.textContent=row.result.message;card.append(msg);}
          if(row.result.asset){const link=document.createElement("a");link.href=row.result.asset;link.textContent="打开作品";link.target="_blank";link.rel="noopener";card.append(link);}
          if(["waiting","queued"].includes(row.state)){
            const actions=row.state==="waiting"?[["approve","确认付费生成"],["promote","提前"],["cancel","取消"]]:[["promote","提前"],["cancel","取消"]];
            for(const [action,label] of actions){
              const b=document.createElement("button");b.type="button";b.className="neu-btn";b.textContent=label;
              b.onclick=async()=>{b.disabled=true;try{notice.textContent=(await api("/api/work-queue",{method:"POST",body:{id:row.id,action,approve_cost:action==="approve"}})).message;await update();}catch(e){notice.textContent=e.message;}};
              card.append(b);
            }
          }
          list.append(card);
        }
      };
      form.onsubmit=async e=>{e.preventDefault();try{notice.textContent=(await api("/api/work-queue",{method:"POST",body:{message:form.querySelector("input").value}})).message;await update();}catch(err){notice.textContent=err.message;}};
      const refresh=async()=>{if(!list.isConnected)return;try{await update();}catch(err){notice.textContent=err.message;}setTimeout(refresh,3500);};
      refresh();
      return;
    }
    if (state.mode === "generate") {
      $("panelTitle").textContent = "生成作品";
      const scene=state.selected?.id==="story" ? state.sceneContext : null;
      $("panelHint").textContent = scene?.title || state.project.title;
      const continuity=state.project.continuity ||= {};
      window.renderCreativeChat(body, api, {...state.selected,...scene}, boot.project,continuity.notebook ||= {});
      return;
    }
    if (state.mode === "agents") {
      await renderAgentsPanel();
      return;
    }
    if (state.mode === "edit") {
      await renderReviewPanel();
      return;
    }
    if (state.mode === "cut") {
      await loadTimeline();
      await renderCutPanel();
      return;
    }

    if (state.selected?.type === "stack") {
      const [stage, kind] = String(state.selected.id).split("::");
      const items = Object.entries(state.project.materials || {}).filter(([, m]) =>
        (m.stage || "assets") === stage && groupKind(m) === kind);
      $("panelTitle").textContent = `${kindLabel(kind)}堆叠`;
      $("panelHint").textContent = `同质素材 ${items.length} 张 · 点击画布堆叠可展开 / 收起`;
      body.innerHTML = `
        <div class="row">
          <button type="button" class="neu-btn primary" id="btnExpandStack">展开堆叠</button>
          <button type="button" class="neu-btn" id="btnCollapseStack">收起</button>
        </div>
        <div class="mat-mini">${items.map(([id, m]) =>
          `<button type="button" class="mat-thumb" data-mat="${id}">
            ${mediaPreviewHtml(m)}
            <span>${m.title || id}<small>v${m.version || 0}</small></span>
          </button>`).join("")}</div>`;
      $("btnExpandStack").onclick = () => expandStack(state.selected.id);
      $("btnCollapseStack").onclick = () => collapseStack(state.selected.id);
      body.querySelectorAll("[data-mat]").forEach((btn) => btn.onclick = () => select("material", btn.dataset.mat));
      return;
    }

    if (state.selected?.type === "material") {
      const id = state.selected.id;
      const m = state.project.materials?.[id] || {};
      $("panelTitle").textContent = m.title || id;
      $("panelHint").textContent = `${mediaLabel(m.media_kind)} · ${kindLabel(groupKind(m))} · 挂在流程「${m.stage || "assets"}」· 支持版本回溯`;
      let versions = [];
      try {
        const resp = await api("/api/material/versions", { method: "POST", body: { id } });
        versions = resp.versions || [];
      } catch (_) {
        versions = [];
      }
      body.innerHTML = `
        ${mediaPreviewHtml(m, { large: true })}
        <div class="row">
          <span class="chip on">${mediaLabel(m.media_kind)}</span>
          <span class="chip">v${m.version || 0}</span>
        </div>
        <label>所属流程阶段</label>
        <select id="matStage">${(state.project.nodes || []).map((n) =>
          `<option value="${n.id}" ${n.id === m.stage ? "selected" : ""}>${n.title}</option>`).join("")}</select>
        <div class="row">
          <button type="button" class="neu-btn" id="btnMoveStage">移动到该阶段</button>
          <button type="button" class="neu-btn" id="btnNewMatHere">同阶段再建一个</button>
        </div>
        <h3 class="subhead">版本历史</h3>
        <div class="version-list" id="versionList">
          ${versions.length ? versions.map((v) => `
            <div class="version-row${v.current ? " current" : ""}">
              ${mediaPreviewHtml({ ...m, file: v.file, media_kind: m.media_kind })}
              <div class="version-copy">
                <div><b>v${v.version}</b> · ${v.note || "无备注"}${v.current ? " · 当前" : ""}</div>
                ${v.current ? "" : `<button type="button" class="neu-btn" data-restore="${v.version}">恢复</button>`}
              </div>
            </div>`).join("") : `<p class="muted">还没有图片/文件版本。导入或生成后会出现在这里。</p>`}
        </div>`;
      $("btnMoveStage").onclick = async () => {
        await api("/api/material/stage", { method: "POST", body: { id, stage: $("matStage").value } });
        await reload();
        select("material", id);
      };
      $("btnNewMatHere").onclick = () => openCreate(m.stage || "assets");
      if(state.mode==="materials"){
        const back=document.createElement("button");back.className="neu-btn";back.textContent="返回素材库";
        back.onclick=()=>{state.materialDetail=false;renderPanel();};body.prepend(back);
      }
      body.querySelectorAll("[data-restore]").forEach((btn) => {
        btn.onclick = async () => {
          await api("/api/material/restore", { method: "POST", body: { id, version: Number(btn.dataset.restore) } });
          await reload();
          select("material", id);
        };
      });
      return;
    }

    const node = (state.project.nodes || []).find((n) => n.id === state.selected?.id)
      || (state.project.nodes || []).find((n) => n.status === "ready")
      || state.project.nodes?.[0];
    if (!node) return;
    if (!state.selected) state.selected = { type: "flow", id: node.id };
    if (node.id === "look") {
      await renderLookPanel();
      return;
    }
    if (node.id === "story") {
      await renderStoryPanel(node);
      return;
    }
    $("panelTitle").textContent = node.title;
    $("panelHint").textContent = node.notes || "流程节点：确认后解锁下一阶段；右侧横铺本阶段素材。";
    const stageMats = Object.entries(state.project.materials || {}).filter(([, m]) => (m.stage || "assets") === node.id);
    const groups = new Map();
    stageMats.forEach(([id, m]) => {
      const kind = groupKind(m);
      if (!groups.has(kind)) groups.set(kind, []);
      groups.get(kind).push([id, m]);
    });
    const groupHtml = [...groups.entries()].map(([kind, items]) => {
      const key = stackKey(node.id, kind);
      const open = state.expandedStacks.has(key) || items.length === 1;
      return `<div class="stack-group">
        <button type="button" class="stack-group-head" data-stack-toggle="${key}">
          <b>${kindLabel(kind)}</b>
          <span>${items.length} 张 · ${open ? "收起" : "展开"}</span>
        </button>
        <div class="mat-mini">${items.map(([id, m]) =>
          `<button type="button" class="mat-thumb" data-mat="${id}">
            ${mediaPreviewHtml(m)}
            <span>${m.title || id}<small>v${m.version || 0}</small></span>
          </button>`).join("")}</div>
      </div>`;
    }).join("") || '<p class="muted">暂无素材，点创建。</p>';
    body.innerHTML = `
      <p class="muted">本阶段 ${stageMats.length} 个素材，同质已堆叠；点堆叠展开。</p>
      <div class="row">
        <button type="button" class="neu-btn" id="btnAddMat">＋ 创建素材</button>
        <button type="button" class="neu-btn primary" id="btnApprove">确认本节点</button>
      </div>
      ${groupHtml}`;
    $("btnAddMat").onclick = () => openCreate(node.id);
    $("btnApprove").onclick = async () => {
      await api("/api/approve", { method: "POST", body: { node: node.id, note: "studio" } });
      await reload();
    };
    body.querySelectorAll("[data-mat]").forEach((btn) => btn.onclick = () => select("material", btn.dataset.mat));
    body.querySelectorAll("[data-stack-toggle]").forEach((btn) => {
      btn.onclick = () => toggleStack(btn.dataset.stackToggle);
    });
  }

  async function reload() {
    state.project = await api("/api/project");
    if (!state.selected) {
      const ready = (state.project.nodes || []).find((n) => n.status === "ready");
      state.selected = { type: "flow", id: ready?.id || state.project.nodes?.[0]?.id };
      const entry = location.hash.slice(1);
      if (["story","look"].includes(entry) && state.project.nodes.some(n => n.id === entry)) {
        state.selected.id = entry;
        focusWorkspace("panel");
      }
      if (["queue","generate","agents","edit","materials","cut"].includes(entry)) {
        state.mode=entry;
        for (const tab of $("modeTabs").children) tab.classList.toggle("on",tab.dataset.mode===entry);
        focusWorkspace(entry==="cut" ? "cut":"panel");
      }
    }
    if (state.project.canvas?.camera) state.camera = { ...state.project.canvas.camera };
    $("projectTitle").textContent = state.project.title;
    applyUiTheme(state.project.ui_theme);
    syncDraftLook();
    applyCamera();
    renderLegacyBanner();
    renderRail();
    renderCanvas();
    await renderPanel();
  }

  function focusWorkspace(target) {
    document.body.dataset.focus = target;
    $("focusPanel").textContent = target === "panel" ? "返回工作区" : "在中央打开";
    $("focusPanel").setAttribute("aria-expanded", String(target === "panel"));
    if (state.mode === "cut") renderCutToolbar();
    const el = target === "panel" ? $("sidePanel") : document.querySelector(".stage-shell");
    if (!matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.animate([{opacity: .5, transform: "translateX(18px)"}, {opacity: 1, transform: "none"}], {duration: 230});
    }
  }
  $("focusPanel").onclick = () => focusWorkspace(document.body.dataset.focus === "panel" ? "" : "panel");
  window.addEventListener("keydown", ev => {
    if (ev.key === "Escape" && document.body.dataset.focus) focusWorkspace("");
    if(state.mode==="cut" && (ev.ctrlKey || ev.metaKey) && !ev.target.closest("input,textarea,select,[contenteditable=true]")){
      const key=ev.key.toLowerCase();
      const action=key==="z"?(ev.shiftKey?"redo":"undo"):key==="y"?"redo":"";
      if(action){ev.preventDefault();const btn=$("cutToolbar").querySelector(`[data-cut="${action}"]`);if(!ev.repeat && !btn.disabled)btn.click();}
    }
  });
  $("modeTabs").onclick = (ev) => {
    const btn = ev.target.closest("button[data-mode]");
    if (!btn) return;
    state.mode = btn.dataset.mode;
    state.materialDetail=false;
    focusWorkspace(["materials","agents","queue","edit","generate"].includes(state.mode) ? "panel" : "");
    [...$("modeTabs").children].forEach((b) => b.classList.toggle("on", b === btn));
    syncCutStageVisibility();
    renderPanel();
  };

  window.addEventListener("pointermove", (ev) => {
    const edge = state.cut.stretchEdge;
    if (!edge) return;
    const zoom = tlZoom();
    const dx = (ev.clientX - edge.ox) / zoom;
    const el = document.querySelector(`.tl-clip[data-clip="${edge.clipId}"]`);
    if (!el) return;
    let next = edge.startDur;
    if (edge.side === "R") next = Math.max(0.2, edge.startDur + dx);
    else next = Math.max(0.2, edge.startDur - dx);
    el.style.width = `${Math.max(28, next * zoom)}px`;
    edge._preview = next;
  });
  window.addEventListener("pointerup", async () => {
    const edge = state.cut.stretchEdge;
    if (!edge) return;
    state.cut.stretchEdge = null;
    if (edge._preview == null) return;
    try {
      await timelineOp("stretch", { clip_id: edge.clipId, duration: edge._preview });
      state.cut.clipId = edge.clipId;
      renderCutStage();
      if (state.mode === "cut") await renderCutPanel();
    } catch (err) {
      $("panelHint").textContent = String(err.message || err);
      renderCutTracks();
    }
  });

  $("btnFit").onclick = async () => {
    await api("/api/canvas", { method: "POST", body: { auto_layout: true, camera: { x: 24, y: 24, scale: 0.82 } } });
    await reload();
  };
  $("btnSaveCanvas").onclick = async () => {
    const nodes = {};
    const materials = {};
    $("canvas").querySelectorAll(".card").forEach((card) => {
      const box = { x: parseFloat(card.style.left), y: parseFloat(card.style.top), w: card.offsetWidth, h: card.offsetHeight };
      if (card.dataset.type === "flow") nodes[card.dataset.id] = box;
      else materials[card.dataset.id] = box;
    });
    await api("/api/canvas", { method: "POST", body: { camera: state.camera, nodes, materials } });
  };

  const scroll = $("canvasScroll");
  scroll.onwheel = (ev) => {
    ev.preventDefault();
    const factor = Math.exp(-ev.deltaY * 0.0015);
    const rect = scroll.getBoundingClientRect();
    const lx = (ev.clientX - rect.left - state.camera.x) / state.camera.scale;
    const ly = (ev.clientY - rect.top - state.camera.y) / state.camera.scale;
    state.camera.scale = Math.min(2.2, Math.max(0.35, state.camera.scale * factor));
    state.camera.x = ev.clientX - rect.left - lx * state.camera.scale;
    state.camera.y = ev.clientY - rect.top - ly * state.camera.scale;
    applyCamera();
  };
  scroll.onpointerdown = (ev) => {
    if (ev.target.closest(".card") || ev.button !== 0) return;
    state.panning = { x: ev.clientX, y: ev.clientY, cx: state.camera.x, cy: state.camera.y };
    scroll.setPointerCapture(ev.pointerId);
  };
  scroll.onpointermove = (ev) => {
    if (state.dragging) {
      const dx = (ev.clientX - state.dragging.ox) / state.camera.scale;
      const dy = (ev.clientY - state.dragging.oy) / state.camera.scale;
      const card = $("canvas").querySelector(`.card[data-id="${state.dragging.id}"][data-type="${state.dragging.type}"]`);
      if (card) {
        // flow cards keep vertical order feel: allow free drag but materials snap-feel horizontal
        let nx = state.dragging.x + dx;
        let ny = state.dragging.y + dy;
        if (state.dragging.type === "flow") nx = Math.min(nx, 120);
        card.style.left = nx + "px";
        card.style.top = ny + "px";
      }
      return;
    }
    if (state.panning) {
      state.camera.x = state.panning.cx + (ev.clientX - state.panning.x);
      state.camera.y = state.panning.cy + (ev.clientY - state.panning.y);
      applyCamera();
    }
  };
  scroll.onpointerup = () => { state.dragging = null; state.panning = null; };

  loadCatalogs()
    .then(() => reload())
    .catch((err) => { $("panelHint").textContent = String(err); });
})();
