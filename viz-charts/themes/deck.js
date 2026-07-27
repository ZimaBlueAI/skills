/**
 * Deck Theme — for viz-deck integration
 * 深空蓝紫青、玻璃拟态、含微动效
 *
 * 用法：
 *   import { deckTheme } from './themes/deck.js'
 *   echarts.init(el, deckTheme.echartsThemeName);
 */

export const deckTheme = {
  name: 'deck',

  colors: {
    bg: '#030711',
    bgElev: '#07111f',
    panel: 'rgba(12, 26, 46, 0.72)',
    panelStrong: 'rgba(16, 36, 62, 0.92)',
    line: 'rgba(151, 209, 255, 0.16)',
    lineStrong: 'rgba(151, 209, 255, 0.34)',
    text: '#edf7ff',
    muted: '#a8bdd5',
    faint: '#688096',
    cyan: '#42e8ff',
    blue: '#6ca5ff',
    silver: '#d8e8f4',
    gold: '#ffd987',
    green: '#78f7c5',
    red: '#ff8c8c',
    violet: '#b893ff',
  },

  // 数据系列调色板 — 深空风允许彩色，但仍以青/蓝/金为主
  series: [
    '#42e8ff', '#6ca5ff', '#ffd987', '#78f7c5',
    '#b893ff', '#ff8c8c', '#d8e8f4', '#a8bdd5',
  ],

  fonts: {
    sans: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif",
    mono: "'JetBrains Mono', 'SF Mono', 'Consolas', monospace",
  },

  echartsTheme: {
    color: ['#42e8ff', '#6ca5ff', '#ffd987', '#78f7c5', '#b893ff', '#ff8c8c', '#d8e8f4'],
    backgroundColor: 'transparent',
    textStyle: {
      color: '#edf7ff',
      fontFamily: "Inter, system-ui, 'PingFang SC', sans-serif",
    },
    title: {
      textStyle: {
        color: '#edf7ff',
        fontFamily: 'Inter, system-ui, sans-serif',
        fontSize: 16,
        fontWeight: 700,
      },
      subtextStyle: { color: '#a8bdd5' },
    },
    line: {
      itemStyle: { borderWidth: 2 },
      lineStyle: { width: 2.5 },
      symbolSize: 6,
      symbol: 'circle',
      smooth: true,
    },
    bar: {
      itemStyle: {
        barBorderWidth: 0,
        // 深空风允许带圆角和渐变
        borderRadius: [3, 3, 0, 0],
      },
    },
    pie: {
      itemStyle: { borderWidth: 2, borderColor: '#030711' },
    },
    categoryAxis: {
      axisLine: { lineStyle: { color: 'rgba(151, 209, 255, 0.34)' } },
      axisTick: { lineStyle: { color: 'rgba(151, 209, 255, 0.34)' } },
      axisLabel: { color: '#a8bdd5', fontFamily: 'Inter, system-ui, sans-serif', fontSize: 11 },
      splitLine: { show: false },
    },
    valueAxis: {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#a8bdd5', fontFamily: 'Inter, system-ui, sans-serif', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(151, 209, 255, 0.16)', type: 'dashed' } },
    },
    timeAxis: {
      axisLine: { lineStyle: { color: 'rgba(151, 209, 255, 0.34)' } },
      axisLabel: { color: '#a8bdd5', fontFamily: 'Inter, system-ui, sans-serif', fontSize: 11 },
    },
    legend: {
      textStyle: { color: '#edf7ff', fontFamily: 'Inter, system-ui, sans-serif', fontSize: 12 },
      icon: 'roundRect',
      itemWidth: 12,
      itemHeight: 8,
    },
    tooltip: {
      backgroundColor: 'rgba(7, 17, 31, 0.92)',
      borderColor: 'rgba(151, 209, 255, 0.34)',
      borderWidth: 1,
      textStyle: { color: '#edf7ff', fontFamily: 'Inter, sans-serif', fontSize: 12 },
      extraCssText: 'backdrop-filter: blur(12px); border-radius: 12px; box-shadow: 0 12px 40px rgba(0,0,0,0.5);',
      axisPointer: {
        lineStyle: { color: '#42e8ff', width: 1 },
        crossStyle: { color: '#42e8ff', width: 1 },
      },
    },
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
    radar: {
      axisLine: { lineStyle: { color: 'rgba(151, 209, 255, 0.34)' } },
      splitLine: { lineStyle: { color: 'rgba(151, 209, 255, 0.16)' } },
      splitArea: { areaStyle: { color: ['transparent'] } },
      axisName: { color: '#a8bdd5', fontFamily: 'Inter, sans-serif', fontSize: 11 },
    },
    visualMap: {
      textStyle: { color: '#a8bdd5' },
      inRange: { color: ['#07111f', '#42e8ff'] },
    },
  },
};

export const deckMermaidTheme = {
  theme: 'base',
  themeVariables: {
    darkMode: true,
    background: '#030711',
    primaryColor: '#07111f',
    primaryTextColor: '#edf7ff',
    primaryBorderColor: 'rgba(151, 209, 255, 0.34)',
    secondaryColor: '#0c1a2e',
    tertiaryColor: '#030711',
    lineColor: '#a8bdd5',
    textColor: '#edf7ff',
    mainBkg: 'rgba(12, 26, 46, 0.92)',
    nodeBorder: 'rgba(151, 209, 255, 0.34)',
    clusterBkg: 'rgba(7, 17, 31, 0.6)',
    clusterBorder: 'rgba(151, 209, 255, 0.16)',
    edgeLabelBackground: '#030711',
    fontFamily: 'Inter, sans-serif',
    fontSize: '13px',
    sectionBkgColor: 'rgba(12, 26, 46, 0.5)',
    altSectionBkgColor: 'rgba(16, 36, 62, 0.5)',
    sectionBkgColor2: 'rgba(12, 26, 46, 0.5)',
    taskBkgColor: '#42e8ff',
    taskTextColor: '#030711',
    taskTextDarkColor: '#edf7ff',
    taskTextLightColor: '#030711',
    activeTaskBkgColor: '#42e8ff',
    activeTaskBorderColor: '#42e8ff',
    doneTaskBkgColor: '#78f7c5',
    doneTaskBorderColor: '#78f7c5',
    critBorderColor: '#ff8c8c',
    critBkgColor: '#ff8c8c',
    todayLineColor: '#ffd987',
    actorBkg: 'rgba(12, 26, 46, 0.92)',
    actorBorder: 'rgba(151, 209, 255, 0.34)',
    actorTextColor: '#edf7ff',
    actorLineColor: 'rgba(151, 209, 255, 0.34)',
    signalColor: '#a8bdd5',
    signalTextColor: '#edf7ff',
    activationBorderColor: '#42e8ff',
    activationBkgColor: 'rgba(66, 232, 255, 0.15)',
    labelColor: '#edf7ff',
    errorBkgColor: '#ff8c8c',
    errorTextColor: '#030711',
  },
};

export const deckComponentTheme = {
  kpiBg: 'rgba(12, 26, 46, 0.72)',
  kpiBorder: 'rgba(151, 209, 255, 0.16)',
  kpiLabel: '#688096',
  kpiValue: '#edf7ff',
  kpiValueGradient: 'linear-gradient(135deg, #42e8ff, #d8e8f4)',
  kpiValueUp: '#78f7c5',
  kpiValueDown: '#ff8c8c',
  kpiDelta: '#a8bdd5',
  sparklineLine: '#42e8ff',
  sparklineFill: 'rgba(66, 232, 255, 0.18)',
  sparklineDot: '#42e8ff',
  sparklineGrid: 'rgba(151, 209, 255, 0.16)',
  gaugeTrack: 'rgba(151, 209, 255, 0.16)',
  gaugeFill: '#42e8ff',
  gaugeFillGradient: ['#42e8ff', '#6ca5ff'],
  gaugeText: '#edf7ff',
  progressTrack: 'rgba(151, 209, 255, 0.16)',
  progressFill: '#42e8ff',
  progressFillGradient: 'linear-gradient(90deg, #42e8ff, #6ca5ff)',
  progressLabel: '#a8bdd5',
};

export function applyDeckTheme(option) {
  return {
    ...option,
    color: deckTheme.echartsTheme.color,
    backgroundColor: deckTheme.echartsTheme.backgroundColor,
    textStyle: { ...deckTheme.echartsTheme.textStyle, ...(option.textStyle || {}) },
  };
}
