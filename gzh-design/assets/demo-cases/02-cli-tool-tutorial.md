# 10 分钟搭好一个本地日志扫描 CLI

> 这个小工具只做一件事：从一堆日志里找出最值得先处理的错误。

## 安装依赖

先准备一个独立目录，并安装最少依赖。这里用 Node.js 举例，Python 或 Go 也可以做同样的事情。

```bash
mkdir log-scout
cd log-scout
npm init -y
npm install fast-glob picocolors
```

## 写第一个扫描命令

我们先扫描 `logs/**/*.log`，把包含 `ERROR`、`Timeout`、`ECONNRESET` 的行取出来。

```js
import fg from "fast-glob";
import fs from "node:fs";

const files = await fg("logs/**/*.log");
for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const hits = text.split("\n").filter(line =>
    /ERROR|Timeout|ECONNRESET/.test(line)
  );
  if (hits.length) console.log(file, hits.length);
}
```

## 加一个优先级规则

不是所有错误都同样重要。支付失败、数据丢失、权限异常应该排在最前面，普通超时可以放后面。

- P0：支付失败、数据写入失败、权限绕过。
- P1：接口超时、第三方服务不可用。
- P2：重试成功、缓存未命中、非核心任务失败。

## 输出一份可读报告

最终命令建议长这样：

```bash
node scout.js --input logs --since 24h --format markdown
```

输出里只保留文件、错误类型、出现次数和建议处理人。工具越小，越容易被团队每天使用。

## 总结

这个 CLI 的价值不在技术复杂度，而在它把“谁先看哪个错误”变成了一个稳定答案。
