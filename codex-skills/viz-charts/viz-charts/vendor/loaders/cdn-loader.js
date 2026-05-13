/**
 * viz-charts CDN Loader
 * jsdelivr → unpkg 双 fallback，自检 + self-host 兜底
 *
 * 使用方式 1（推荐）：直接 <script src="..../loader.js"></script>
 * 然后 await window.VizCharts.loadMermaid() / loadECharts()
 *
 * 使用方式 2：复制本文件到你的 HTML <script> 内联，无外部依赖
 */
(function (global) {
  'use strict';

  const CDN_TIERS = [
    { name: 'jsdelivr', base: 'https://cdn.jsdelivr.net/npm' },
    { name: 'unpkg',    base: 'https://unpkg.com' },
  ];

  // 当 self-host 时，把这个改成你的本地路径，例如 '/vendor'
  const SELF_HOST_BASE = global.VIZ_CHARTS_SELFHOST_BASE || null;

  // 版本固定（避免 latest 漂移）
  const VERSIONS = {
    mermaid: '10.9.1',
    echarts: '5.5.1',
  };

  const loaded = {}; // 已加载缓存

  function loadScript(url, integrityCheck) {
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = url;
      s.async = true;
      s.crossOrigin = 'anonymous';
      s.onload = () => {
        if (integrityCheck && !integrityCheck()) {
          reject(new Error(`Integrity check failed for ${url}`));
          return;
        }
        resolve(url);
      };
      s.onerror = () => reject(new Error(`Failed to load ${url}`));
      document.head.appendChild(s);
    });
  }

  function loadModule(url) {
    // ESM dynamic import — Mermaid v10+ 推荐 ESM
    return import(/* @vite-ignore */ url);
  }

  async function tryUrls(urls, integrityCheck, useEsm = false) {
    let lastErr;
    for (const url of urls) {
      try {
        if (useEsm) {
          return await loadModule(url);
        }
        await loadScript(url, integrityCheck);
        return url;
      } catch (e) {
        lastErr = e;
        console.warn(`[viz-charts] Failed: ${url}`, e.message);
      }
    }
    throw new Error(`All CDNs failed. Last: ${lastErr ? lastErr.message : 'unknown'}`);
  }

  /**
   * Load ECharts (UMD global)
   * @returns {Promise<typeof echarts>}
   */
  async function loadECharts() {
    if (loaded.echarts) return loaded.echarts;
    if (global.echarts) {
      loaded.echarts = global.echarts;
      return global.echarts;
    }

    const path = `echarts@${VERSIONS.echarts}/dist/echarts.min.js`;
    const urls = [];
    if (SELF_HOST_BASE) urls.push(`${SELF_HOST_BASE}/echarts.min.js`);
    CDN_TIERS.forEach(t => urls.push(`${t.base}/${path}`));

    await tryUrls(urls, () => typeof global.echarts !== 'undefined');
    loaded.echarts = global.echarts;
    return global.echarts;
  }

  /**
   * Load Mermaid (ESM module)
   * @returns {Promise<typeof mermaid>}
   */
  async function loadMermaid(themeVariables) {
    if (loaded.mermaid) {
      if (themeVariables) loaded.mermaid.initialize({ startOnLoad: false, ...themeVariables });
      return loaded.mermaid;
    }

    const path = `mermaid@${VERSIONS.mermaid}/dist/mermaid.esm.min.mjs`;
    const urls = [];
    if (SELF_HOST_BASE) urls.push(`${SELF_HOST_BASE}/mermaid.esm.min.mjs`);
    CDN_TIERS.forEach(t => urls.push(`${t.base}/${path}`));

    const mod = await tryUrls(urls, null, true);
    const mermaid = mod.default || mod;
    mermaid.initialize({ startOnLoad: false, ...(themeVariables || {}) });
    loaded.mermaid = mermaid;
    return mermaid;
  }

  /**
   * 给一个 Mermaid 容器渲染图（自动调用 loadMermaid）
   * @param {HTMLElement} container - 含 .mermaid-source 子节点的容器
   * @param {object} themeVariables - mermaid 主题变量（可选）
   */
  async function renderMermaidIn(container, themeVariables) {
    const m = await loadMermaid(themeVariables);
    const sources = container.querySelectorAll('.mermaid-source');
    for (const node of sources) {
      const code = node.textContent.trim();
      const id = `mmd-${Math.random().toString(36).slice(2, 9)}`;
      try {
        const { svg } = await m.render(id, code);
        const target = node.nextElementSibling;
        if (target && target.classList.contains('mermaid-output')) {
          target.innerHTML = svg;
        } else {
          const wrap = document.createElement('div');
          wrap.className = 'mermaid-output';
          wrap.innerHTML = svg;
          node.after(wrap);
        }
        node.style.display = 'none';
      } catch (e) {
        console.error('[viz-charts] mermaid render failed:', e);
        node.outerHTML = `<pre class="mermaid-error" style="color:#ff4444;border:1px solid #ff4444;padding:1em">Mermaid render failed: ${e.message}\n\n${code}</pre>`;
      }
    }
  }

  /**
   * 给一个 ECharts 容器初始化（容器需带 data-echarts-option 属性，值为 JSON string）
   * @param {HTMLElement} container
   * @param {object} themeObject - ECharts theme（可选）
   */
  async function renderEChartsIn(container, themeObject) {
    const ec = await loadECharts();
    if (themeObject && themeObject.name) {
      ec.registerTheme(themeObject.name, themeObject);
    }
    const targets = container.querySelectorAll('[data-echarts-option]');
    targets.forEach(el => {
      try {
        const optStr = el.getAttribute('data-echarts-option');
        const opt = JSON.parse(optStr);
        const inst = ec.init(el, themeObject ? themeObject.name : null, { renderer: 'svg' });
        inst.setOption(opt);
        // 响应式
        const ro = new ResizeObserver(() => inst.resize());
        ro.observe(el);
        el._echartsInstance = inst;
      } catch (e) {
        console.error('[viz-charts] echarts render failed:', e);
        el.innerHTML = `<pre class="echarts-error" style="color:#ff4444;border:1px solid #ff4444;padding:1em">ECharts render failed: ${e.message}</pre>`;
      }
    });
  }

  /**
   * 一键渲染整页所有图表
   * @param {object} opts - { mermaidTheme, echartsTheme }
   */
  async function renderAll(opts) {
    opts = opts || {};
    const tasks = [];
    if (document.querySelector('.mermaid-source')) {
      tasks.push(renderMermaidIn(document.body, opts.mermaidTheme));
    }
    if (document.querySelector('[data-echarts-option]')) {
      tasks.push(renderEChartsIn(document.body, opts.echartsTheme));
    }
    return Promise.allSettled(tasks);
  }

  global.VizCharts = {
    loadECharts,
    loadMermaid,
    renderMermaidIn,
    renderEChartsIn,
    renderAll,
    versions: VERSIONS,
    cdnTiers: CDN_TIERS,
  };

  // DOM ready 后自动跑（除非显式禁用）
  if (!global.VIZ_CHARTS_NO_AUTO) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => global.VizCharts.renderAll(global.VIZ_CHARTS_OPTS));
    } else {
      Promise.resolve().then(() => global.VizCharts.renderAll(global.VIZ_CHARTS_OPTS));
    }
  }
})(typeof window !== 'undefined' ? window : globalThis);
