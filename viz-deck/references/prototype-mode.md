# prototype-mode: HTML 高保真原型协议

> v2 新增。viz-deck 的第 4 种产出模式——HTML 高保真原型（hi-fi prototype）。区别于"演示报告"和"幻灯片"，这是给客户/PM/设计评审用的**可点击 demo**。

## 何时启用

| 用户说什么 | 启用 |
|---|:---:|
| "做个原型"、"hi-fi 原型"、"高保真"、"做个 demo" | ✅ |
| "iOS 原型"、"安卓原型"、"App mockup" | ✅ |
| "macOS 应用"、"桌面 demo"、"浏览器原型" | ✅ |
| "做个可点击的 demo"、"能交互的样机" | ✅ |
| "做个演示" / "做个汇报"（含演示意图） | ❌ → keynote-report 模式 |
| "做个幻灯片" / "做个 PPT" | ❌ → slide-deck 模式 |

## 与原 viz-deck（keynote-report）的区别

| 维度 | keynote-report | prototype |
|---|---|---|
| 受众 | 投资人、客户、全员 | PM、设计评审、内部客户 |
| 目的 | 60-90 分钟走读、视觉记忆 | 5-15 分钟交互试用 |
| 视觉边界 | 报告内全部章节连贯 | 每屏一个独立 App 状态 |
| 设备外壳 | 无 | **必须有**（iPhone / Android / macOS / browser） |
| 真实数据 | 真值 + 估值标 [ESTIMATED] | 真实素材：Wikimedia / Met / Unsplash 取图 |
| 交互 | reveal 滚动入场 | 点击切屏、状态切换、表单回填 |
| 输出文件 | 单 HTML | 单 HTML，含 AppPhone 状态管理 |

## 设备外壳（必选其一）

调用 huashu-design 自带的设备 frame，**不要自己画外壳**：

```jsx
// iOS 15 Pro
import IPhoneFrame from '~/.claude/skills/huashu-design/assets/ios_frame.jsx';
<IPhoneFrame>
  <YourAppScreen />
</IPhoneFrame>

// Android
import AndroidFrame from '~/.claude/skills/huashu-design/assets/android_frame.jsx';

// macOS 窗口
import MacOSWindow from '~/.claude/skills/huashu-design/assets/macos_window.jsx';

// 浏览器
import BrowserWindow from '~/.claude/skills/huashu-design/assets/browser_window.jsx';
```

外壳尺寸对照：

- `ios_frame.jsx` → 390×844（iPhone 15 Pro 设计稿尺寸）
- `android_frame.jsx` → 412×915
- `macos_window.jsx` → 1280×800（窗口内可调）
- `browser_window.jsx` → 1440×900（Chrome 标签栏样式）

## AppPhone 状态管理（iOS/Android 原型必须）

每台 iPhone/Android 外壳里**包一个 AppPhone 状态管理器**，保证可交互：

```jsx
function AppPhone({ initialScreen = 'home', screens = {} }) {
  const [screen, setScreen] = React.useState(initialScreen);
  const [state, setState] = React.useState({});
  return (
    <IPhoneFrame>
      <ScreenContext.Provider value={{ screen, setScreen, state, setState }}>
        {screens[screen]}
      </ScreenContext.Provider>
    </IPhoneFrame>
  );
}

// 用法：
<AppPhone
  initialScreen="home"
  screens={{
    home: <HomeScreen />,
    detail: <DetailScreen />,
    settings: <SettingsScreen />,
  }}
/>
```

任何按钮点击 → `setScreen('detail')` 切屏，**不要用 `window.location.hash`**（外壳是嵌入式的）。

## 多屏并排展示（design canvas）

如果要让用户**对比多屏**或**对比变体**，用 huashu 的 design_canvas.jsx：

```jsx
import DesignCanvas from '~/.claude/skills/huashu-design/assets/design_canvas.jsx';

<DesignCanvas
  variants={[
    { name: 'Variant A', phone: <AppPhoneA /> },
    { name: 'Variant B', phone: <AppPhoneB /> },
    { name: 'Variant C', phone: <AppPhoneC /> },
  ]}
/>
```

## 真实素材来源（不要用 emoji 占位）

| 素材类型 | 来源 | 注意 |
|---|---|---|
| 人物头像 | unsplash.com/portrait | 商用前确认许可 |
| 产品图 | wikimedia.org / picsum.photos | 抠图后再用 |
| 艺术作品 | metmuseum.org（公共领域） | 注明出处 |
| 风景 | unsplash.com | 默认免费商用 |
| 图标 | 用真实 Apple SF Symbols / Material Icons name，不画 emoji | iOS 上加载 `bx-` 或 SF webfonts |

**默认审美禁区**：

- ❌ 用 emoji 当图标（🚀⭐️📊）
- ❌ 用 placeholder.com 灰色占位图
- ❌ 用 SVG 简笔人物剪影
- ❌ 用 Lorem ipsum（用真实业务文案）

## 交付前 QA：Playwright 点击测试

每份 prototype 交付前**必须**用 huashu 的 Playwright 验证：

```bash
node ~/.claude/skills/huashu-design/scripts/verify.py prototype.html
```

或手动 Playwright 脚本：

```js
import { chromium } from 'playwright';
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('file:///abs/path/to/prototype.html');
// 点遍所有 [data-action] 按钮，验证状态切换
const buttons = await page.$$('[data-action]');
for (const btn of buttons) {
  await btn.click();
  await page.waitForTimeout(200);
}
await browser.close();
```

期待：**所有按钮都有响应**——点击后画面变化（screen 切换、state 更新、loading 出现）。

## 模板：prototype-shell.html

`templates/prototype-shell.html` 是骨架，内含：

1. CDN 加载 React + Babel（开发态）
2. 一个 `<AppPhone>` 包裹的 iPhone 外壳
3. 3 个示例 screen（home / detail / settings）
4. ScreenContext 状态管理
5. 默认 SF Pro 字体 + iOS 系统色（不是 deck 主题，因为是设备内 UI）

复制后修改 `{{占位}}`：

- `{{APP_NAME}}` — 应用名
- `{{SCREENS_JSON}}` — 屏幕配置
- `{{ASSETS_SPEC}}` — 资源清单（图片/字体）

## 反模式

- ❌ 把 viz-deck 的"深空蓝紫青"塞进 prototype——那是讲演主题，不是 App UI 主题
- ❌ prototype 里加 reveal 滚动入场动画——App 没有"滚动入场"这个概念
- ❌ 单一 prototype 文件超过 100KB（含图）——split 成多文件或用 base64 控制
- ❌ 不带设备外壳就交付（"裸"页面）——给客户看的时候上下文丢失
- ❌ 不跑 Playwright 验证就交付——按钮可能是装饰
