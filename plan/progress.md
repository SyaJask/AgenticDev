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
| 2026-10-11 | 0 | 在 `code/playground/01-hello-llm` 建 uv 项目，用 openai SDK + `base_url` 接入 DeepSeek，跑通**非流式**与**流式**两种调用；补齐 `.env` / `.env.example`，并在 `.gitignore` 加 `!.env.example` 例外规则；整理出流式 / SSE 两篇概念笔记 | 踩坑两条：`uv run` 的目录语义（非全局命令查找）、Python 包名不能以数字开头（详见 `notes/pitfalls.md`）。概念收获：流式靠 SSE 逐块返回 `delta`，**总耗时不变**，但首字时间从数秒降到亚秒 | 填完 `resources/environment.md` 环境表（Key/模型/价格）→ 系统学 Prompt Engineering → 在 `experiments/prompts/` 做第一次 Prompt 实验 |
| 2026-10-10 | 0 | 整理 Git 仓库：按目录逻辑把骨架拆成 9 个提交；新增 `.gitattributes`（`* text=auto eol=lf` + bat/cmd 例外 + 二进制声明） | 踩坑：schannel TLS 取不到凭据、沙箱内凭据助手无法创建命名管道（两条详见 `notes/pitfalls.md`） | 填 `resources/environment.md` 环境表，拿到 API Key 跑通 hello world |
| 2026-10-10 | 0 | 通读仓库骨架，确认它是「证据链」容器：21 个文件全是模板与占位，尚无代码和产出 | 明确三层结构（学懂 `notes/` · 做到 `code/`+`experiments/` · 证明 `portfolio/`+`career/`+`publishing/`）与「量化优先」原则 | 补齐 README 承诺但缺失的目录（`portfolio/demos`、`portfolio/diagrams`、`publishing/blog`、`publishing/talks`） |