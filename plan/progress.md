# 学习进度日志

> 格式：`YYYY-MM-DD | 阶段-任务 | 做了什么 | 学到什么 | 下一步`
>
> 每次学习/开发后花 2 分钟追加一行，别攒着补。

---

## 使用说明

每条记录用一行表格，按日期倒序排列（最新的在上）。

**示例**：

| 日期 | 阶段 | 做了什么 | 收获 / 踩坑 | 下一步 |
|------|------|----------|-------------|--------|
| 2025-01-15 | 0 | 搭建 Python 环境，拿到 OpenAI Key | venv 命名不要有空格 | 跑通 Hello World |
| 2025-01-14 | 0 | 阅读 Agent 综述文章 | Agent = LLM + Tools + Memory + Planning | 搭环境 |

---

## 日志

| 日期 | 阶段 | 做了什么 | 收获 / 踩坑 | 下一步 |
|------|------|----------|-------------|--------|
| 2026-10-22 | 0 | TS 侧把三家 SDK 都接上：① 占位包 `anthropic` 换成官方 `@anthropic-ai/sdk`，补齐非流式 + 流式；② 接入 `@earendil-works/pi-coding-agent`（`createAgentSession` / `session.prompt` / `getLastAssistantText` / `dispose`）；③ 删掉未使用的 `parseMessage` 深导入；`package.json` 加 `scripts.start`；Python 侧把 `system` / `messages` 提为变量、`role: 'developer'` 改回 `'system'` | ① **依赖混淆**：`anthropic` 是占位包，官方是 `@anthropic-ai/sdk`，装包前必须核对包名；② 深导入 `pkg/lib/*.mjs` 内部路径不可用，升级即碎；③ **同一厂商名在 Python 和 TS 下是两个包、两套 API** —— Python 是 `PiClient.run/stream`（chat 形态），TS 是 Agent Session（`createAgentSession` + `prompt`），后者带工具、能读文件，这是**第一次真正跑起一个 Agent** | 搞清 pi-coding-agent 的工具集与 agent 循环；把 TS 拆出独立目录 |
| 2026-10-20 | 0 | 用 `openai` npm SDK 写 TS 版 hello-llm：`"type": "module"` 开 ESM 才支持 top-level await；流式用 `for await...of` + `delta?.content` 可选链；建立 `package.json` / `package-lock.json` | 同一件事在 JS 里更"轻"：不用 async 包装函数就能 top-level await；`delta?.content` 可选链天然处理"空帧"；对照两份代码时发现 **Python 与 JS 的默认参数求值时机不同**（详见 `notes/pitfalls.md`） | 补 Anthropic SDK；注意 TS 工程寄生在 Python 项目目录里的结构问题 |
| 2026-10-19 | 0 | 给 `01-hello-llm` 加异步与结构化输出：`AsyncOpenAI` + Pydantic `response_format`，覆盖 `.parse()`（非流式）与 `.stream()`（流式事件 `content.delta` / `content.done`）；补 `AsyncPiClient`；`.env` 的 `MODEL_NAME` 改名 `MODEL`；在 `llm-response-modes.md` 补写「我的理解」（`create()` → `_post()` 调用链） | 结构化输出是「让模型稳定吐 JSON」的正解，比在 prompt 里求它注意格式可靠得多；流式下拿结构化结果要**监听事件类型**，不能拼完字符串再 parse | 删掉笔记里残留的占位提示；系统学 Few-shot / CoT，把 Prompt Engineering 从 1 级拉起来 |
| 2026-10-16 | 0 | 把 `01-hello-llm` 扩成三家 SDK 对比：OpenAI / Anthropic / pi-agent，各写非流式、流式、以及 `with` 语法两版；补 `.env.example` 的 Anthropic 变量；新增 `main.ts` 空桩 | 三家流式形态不同：OpenAI 看 `delta.content`，Anthropic 要判 `content_block_delta` + `text_delta`，pi-agent 用 `text_delta` + `stream.result()` 收尾——**同名概念、不同形状，对比着写一遍比只读文档清楚** | 试结构化输出与异步；搞清 pi-agent 的 `provider` 参数真正期望什么 |
| 2026-10-11 | 0 | 在 `code/playground/01-hello-llm` 建 uv 项目，用 openai SDK + `base_url` 接入 DeepSeek，跑通**非流式**与**流式**两种调用；补齐 `.env` / `.env.example`，并在 `.gitignore` 加 `!.env.example` 例外规则；整理出流式 / SSE 两篇概念笔记 | 踩坑两条：`uv run` 的目录语义（非全局命令查找）、Python 包名不能以数字开头（详见 `notes/pitfalls.md`）。概念收获：流式靠 SSE 逐块返回 `delta`，**总耗时不变**，但首字时间从数秒降到亚秒 | 填完 `resources/environment.md` 环境表（Key/模型/价格）→ 系统学 Prompt Engineering → 在 `experiments/prompts/` 做第一次 Prompt 实验 |
| 2026-10-10 | 0 | 整理 Git 仓库：按目录逻辑把骨架拆成 9 个提交；新增 `.gitattributes`（`* text=auto eol=lf` + bat/cmd 例外 + 二进制声明） | 踩坑：schannel TLS 取不到凭据、沙箱内凭据助手无法创建命名管道（两条详见 `notes/pitfalls.md`） | 填 `resources/environment.md` 环境表，拿到 API Key 跑通 hello world |
| 2026-10-10 | 0 | 通读仓库骨架，确认它是「证据链」容器：21 个文件全是模板与占位，尚无代码和产出 | 明确三层结构（学懂 `notes/` · 做到 `code/`+`experiments/` · 证明 `portfolio/`+`career/`+`publishing/`）与「量化优先」原则 | 补齐 README 承诺但缺失的目录（`portfolio/demos`、`portfolio/diagrams`、`publishing/blog`、`publishing/talks`） |
