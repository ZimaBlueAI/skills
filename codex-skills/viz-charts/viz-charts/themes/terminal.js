/**
 * Terminal Theme — for biz-html-viz integration
 * 黑底酸黄、零动效、Bloomberg 终端感
 *
 * 用法：
 *   import { terminalTheme } from './themes/terminal.js'
 *   echarts.init(el, terminalTheme.echartsThemeName, { renderer: 'svg' });
 *   或：const opt = applyTerminalTheme(baseOption);
 */

export const terminalTheme = {
  name: 'terminal',

  // 调色板（与 biz-html-viz design-system.md 保持一致）
  colors: {
    bg: '#0a0a0a',
    bgElev: '#141414',
    bgHover: '#1c1c1c',
    border: '#2a2a2a',
    borderStrong: '#3a3a3a',
    fg: '#e8e8e8',
    fgDim: '#888888',
    fgFaint: '#555555',
    accent: '#d4ff00',         // 主强调
    accentDim: '#8a9e0a',
    danger: '#ff4444',
    warn: '#ffaa00',
    ok: '#44dd88',
    info: '#44aaff',
  },

  // 数据系列调色板（5+ 系列时循环）
  // 终端风纪律：少用花哨，黄→白→灰阶为主
  series: [
    '#d4ff00', '#e8e8e8', '#888888', '#44dd88',
    '#ffaa00', '#44aaff', '#ff4444', '#b893ff',
  ],

  fonts: {
    mono: "'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace",
    sans: "'Inter Tight', 'PingFang SC', 'Source Han Sans SC', system-ui, sans-serif",
  },

  // ECharts 主题对象
  echartsTheme: {
    color: ['#d4ff00', '#e8e8e8', '#888888', '#44dd88', '#ffaa00', '#44aaff', '#ff4444', '#b893ff'],
    backgroundColor: 'transparent',
    textStyle: {
      color: '#e8e8e8',
      fontFamily: "'Inter Tight', 'PingFang SC', system-ui, sans-serif",
    },
    title: {
      textStyle: {
        color: '#e8e8e8',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 12,
        fontWeight: 700,
        // letterSpacing 在 ECharts 不直接支持，靠 text 全大写实现
      },
      subtextStyle: { color: '#888' },
    },
    line: {
      itemStyle: { borderWidth: 1 },
      lineStyle: { width: 2 },
      symbolSize: 4,
      symbol: 'circle',
      smooth: false,
    },
    bar: {
      itemStyle: { barBorderWidth: 0, barBorderColor: '#2a2a2a' },
    },
    pie: {
      itemStyle: { borderWidth: 1, borderColor: '#0a0a0a' },
    },
    categoryAxis: {
      axisLine: { lineStyle: { color: '#3a3a3a' } },
      axisTick: { lineStyle: { color: '#3a3a3a' } },
      axisLabel: { color: '#888', fontFamily: "'JetBrains Mono', monospace", fontSize: 11 },
      splitLine: { show: false, lineStyle: { color: '#2a2a2a' } },
      splitArea: { show: false },
    },
    valueAxis: {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#888', fontFamily: "'JetBrains Mono', monospace", fontSize: 11 },
      splitLine: { lineStyle: { color: '#2a2a2a', type: 'dashed' } },
      splitArea: { show: false },
    },
    timeAxis: {
      axisLine: { lineStyle: { color: '#3a3a3a' } },
      axisLabel: { color: '#888', fontFamily: "'JetBrains Mono', monospace", fontSize: 11 },
      splitLine: { show: false },
    },
    legend: {
      textStyle: { color: '#e8e8e8', fontFamily: "'JetBrains Mono', monospace", fontSize: 11 },
      icon: 'rect',
      itemWidth: 10,
      itemHeight: 10,
    },
    tooltip: {
      backgroundColor: '#141414',
      borderColor: '#3a3a3a',
      borderWidth: 1,
      textStyle: { color: '#e8e8e8', fontFamily: "'JetBrains Mono', monospace", fontSize: 12 },
      axisPointer: {
        lineStyle: { color: '#d4ff00', width: 1 },
        crossStyle: { color: '#d4ff00', width: 1 },
      },
    },
    grid: {
      left: 50, right: 20, top: 30, bottom: 30,
    },
    radar: {
      axisLine: { lineStyle: { color: '#3a3a3a' } },
      splitLine: { lineStyle: { color: '#2a2a2a' } },
      splitArea: { areaStyle: { color: ['transparent'] } },
      axisName: { color: '#888', fontFamily: "'JetBrains Mono', monospace", fontSize: 11 },
    },
    visualMap: {
      textStyle: { color: '#888', fontFamily: "'JetBrains Mono', monospace" },
      inRange: { color: ['#1c1c1c', '#d4ff00'] },
    },
  },
};

// Mermaid 主题变量
export const terminalMermaidTheme = {
  theme: 'base',
  themeVariables: {
    darkMode: true,
    background: '#0a0a0a',
    primaryColor: '#141414',
    primaryTextColor: '#e8e8e8',
    primaryBorderColor: '#3a3a3a',
    secondaryColor: '#1c1c1c',
    tertiaryColor: '#0a0a0a',
    lineColor: '#888',
    textColor: '#e8e8e8',
    mainBkg: '#141414',
    nodeBorder: '#3a3a3a',
    clusterBkg: '#0a0a0a',
    clusterBorder: '#2a2a2a',
    edgeLabelBackground: '#0a0a0a',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '12px',
    // Gantt
    sectionBkgColor: '#141414',
    altSectionBkgColor: '#1c1c1c',
    sectionBkgColor2: '#141414',
    taskBkgColor: '#d4ff00',
    taskTextColor: '#0a0a0a',
    taskTextDarkColor: '#e8e8e8',
    taskTextLightColor: '#0a0a0a',
    activeTaskBkgColor: '#d4ff00',
    activeTaskBorderColor: '#d4ff00',
    doneTaskBkgColor: '#44dd88',
    doneTaskBorderColor: '#44dd88',
    critBorderColor: '#ff4444',
    critBkgColor: '#ff4444',
    todayLineColor: '#d4ff00',
    // Sequence
    actorBkg: '#141414',
    actorBorder: '#3a3a3a',
    actorTextColor: '#e8e8e8',
    actorLineColor: '#3a3a3a',
    signalColor: '#888',
    signalTextColor: '#e8e8e8',
    activationBorderColor: '#d4ff00',
    activationBkgColor: '#1c1c1c',
    // State
    labelColor: '#e8e8e8',
    errorBkgColor: '#ff4444',
    errorTextColor: '#ffffff',
  },
};

// 自研组件配色（KPI/sparkline/gauge）
export const terminalComponentTheme = {
  kpiBg: '#141414',
  kpiBorder: '#2a2a2a',
  kpiLabel: '#888',
  kpiValue: '#e8e8e8',
  kpiValueUp: '#44dd88',
  kpiValueDown: '#ff4444',
  kpiDelta: '#888',
  sparklineLine: '#d4ff00',
  sparklineFill: 'rgba(212, 255, 0, 0.15)',
  sparklineDot: '#d4ff00',
  sparklineGrid: '#2a2a2a',
  gaugeTrack: '#2a2a2a',
  gaugeFill: '#d4ff00',
  gaugeText: '#e8e8e8',
  progressTrack: '#2a2a2a',
  progressFill: '#d4ff00',
  progressLabel: '#888',
};

/**
 * 运行时给一个 ECharts option 套终端主题（不用全局注册）
 * 适用于：用户已经有了一份 ECharts JSON 配置，临时换皮
 */
export function applyTerminalTheme(option) {
  return {
    ...option,
    color: terminalTheme.echartsTheme.color,
    backgroundColor: terminalTheme.echartsTheme.backgroundColor,
    textStyle: { ...terminalTheme.echartsTheme.textStyle, ...(option.textStyle || {}) },
  };
}
