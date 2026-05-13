/**
 * viz-charts · motion timing presets
 *
 * 集中管理所有 motion 图表的动画时长 / 缓动 / 帧率配置，
 * 让同一份报告的多个动效图表节奏一致。
 *
 * 与 terminal.js / deck.js 平级——terminal 主题禁用 motion；
 * deck 主题允许 motion，可结合本文件使用。
 */

export const motionPresets = {
  // 录制画布默认尺寸
  stage: {
    width: 1920,
    height: 1080,
    background: 'transparent', // 由 deck.js 决定底色
  },

  // 帧率档位
  fps: {
    base: 25,         // 录制基准
    interpolated: 60, // ffmpeg minterpolate 目标
    gif: 12,          // GIF 降帧
  },

  // 时长档位（秒）—— 强制节奏感
  duration: {
    micro: 2,    // 单个数字 / sparkline reveal
    short: 4,    // 多 series reveal
    medium: 6,   // 时间扫过
    long: 10,    // KG 轨道运镜
    max: 12,     // 上限 —— 超出考虑分段
  },

  // ECharts animation 配置
  echarts: {
    duration: 600,
    delayStep: 250,        // 多 series 错峰间隔
    easing: 'cubicOut',
    updateDuration: 400,
    updateEasing: 'cubicInOut',
  },

  // Mermaid 节点 fade-in（SVG 后处理）
  mermaid: {
    initialDelay: 100,     // ms
    stepDelay: 300,        // 节点之间
    fadeDuration: 500,
  },

  // 3D KG 轨道运镜
  kg3d: {
    orbitRadius: 400,
    orbitPeriodMs: 9000,   // 一圈 9 秒
    tickInterval: 30,      // ~33fps 内部
    autoRotate: true,
  },

  // hold-on-last-frame —— 录制末尾停顿，避免 MP4 突然结束
  holdFrames: {
    short: 0.5,  // 秒
    long:  1.0,
  },
};

export function recordSeconds(kind = 'short') {
  const base = motionPresets.duration[kind] || motionPresets.duration.short;
  return base + motionPresets.holdFrames.short;
}

export default motionPresets;
