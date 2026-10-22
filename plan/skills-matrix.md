# 技能矩阵

> 用这张表追踪你在 Agent 开发各技术栈上的熟练度。
>
> 等级定义：
>
> - **0 — 不了解**：没听过或只是听说过名字
> - **1 — 了解概念**：能说清楚是什么、大概怎么用
> - **2 — 动手用过**：跟着教程写过 demo
> - **3 — 能独立开发**：不看文档可以写出一个功能
> - **4 — 能讲清楚原理**：面试水平，能讲"为什么"和"底层怎么实现"
> - **5 — 能设计系统**：可做架构决策、选型和权衡

---

**目标方向（草稿，待你校正）**：安全方向的 Agent 应用开发 —— 用「网络安全领域理解」做差异化，
而不是拿通用 Agent 能力和科班/大厂背景的人硬拼。

**每周可投入**：约 14 小时（暂定）。

> ⚠️ `plan/roadmap.md` 里的「预计时长」是在不知道投入量的前提下写的，按 14h/周 需放宽约 1.5–2 倍。
> 建议先按「Phase 0–1 用一个月」试跑一轮，拿到真实速度再回头校准排期。

**关于「目标」列**：`—` 表示还没设目标。**别为了填满而填** —— 目前只有约 11 项设了目标，
足够支撑 Phase 0–2；等走到 RAG / Agent 框架阶段再补。

> 本表是**等级的唯一权威来源**（方案 B：不设第二份副本，物理上不可能漂移）。

---

## LLM 基础

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| LLM 工作原理（Token、Context、Temperature） | 1 | — | `code/playground/01-hello-llm` 跑通 API 调用 | 会调 API 了；机制（token 计费、context 上限、temperature 影响）待系统学 |
| Few-shot / 示例驱动 | 0 | 3 | | 出效果最快的一招，优先补 |
| CoT（思维链）/ 推理提示 | 0 | 3 | | 搞清何时该"让它想"、何时别浪费 token |
| 结构化输出（JSON Mode / `response_format`） | 2 | 4 | Python 侧用 Pydantic `response_format` + `.parse()`，含流式下的结构化事件 | 已到 2 级；补 TS 侧 + 失败重试与 schema 演进 |
| Embedding & 语义搜索 | 0 | — | | |
| LLM 成本模型与选型 | 0 | — | | 已接触 3 家 SDK，但没算过成本 / 延迟，谈不上选型 |
| 流式输出与 SSE | 3 | 4 | Python：OpenAI / Anthropic / pi-agent 均覆盖流式；TS：OpenAI / Anthropic 有流式，pi-coding-agent 只跑了非流式。笔记：`notes/concepts/llm-response-modes.md`、`notes/concepts/sse.md` | 多家 SDK 的形状差异已摸清；**SSE 服务端尚未自己实现过**；前端对接待补 |

## RAG

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| 文档解析与预处理 | 0 | — | | |
| Chunking 策略 | 0 | — | | |
| 向量数据库（Chroma / FAISS / Pinecone） | 0 | — | | |
| 检索策略（关键词 / 混合 / 重排序） | 0 | — | | |
| RAG 效果评测 | 0 | 3 | | 能独立搭一条链路并给出评测数字 |

## Tool Use & Function Calling

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| Function Calling（OpenAI / Anthropic） | 0 | 4 | | 结构化输出是它的一半，可顺路切入 |
| Tool 定义与 Schema 设计 | 0 | — | | |
| Tool 执行与错误处理 | 0 | — | | |
| 工具组合与编排 | 0 | — | | |

## Agent 框架

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| LangChain | 0 | — | | |
| LangGraph | 0 | 4 | | 深入一个，别贪多 |
| CrewAI | 0 | — | | |
| AutoGen | 0 | — | | |
| 手写 Agent Loop（不依赖框架） | 0 | — | | |
| pi-coding-agent（TS，Agent Session API） | 2 | — | `@earendil-works/pi-coding-agent`：`createAgentSession` / `session.prompt` / `getLastAssistantText` / `dispose` | **第一个真正带工具的 Agent**（能读当前目录），不是 chat API；工具集与内部循环还没搞清 |

## Agent 设计模式

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| ReAct | 0 | — | | |
| Plan-Execute | 0 | — | | |
| Reflection / Self-Critique | 0 | — | | |
| Multi-Agent 协作 | 0 | — | | |
| Memory 管理 | 0 | — | | |

## 评测与可观测性

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| Agent 评测方法论 | 0 | 3 | | 面试高频，也是你做「量化结果」的手段 |
| Tracing（LangSmith / LangFuse） | 0 | — | | |
| 成本分析与优化 | 0 | — | | |
| A/B 实验设计 | 0 | — | | |

## 工程能力

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| Python | 2 | 4 | 用到 async/await、Pydantic 模型、异常处理、类型注解 | 仍有反模式（默认参数在定义时求值）；缺模块拆分、测试、日志规范 |
| 异步编程（asyncio） | 2 | — | `AsyncOpenAI` / `AsyncPiClient`；`asyncio.run`、`async for`、`async with` | 写法已上手；并发编排（gather / 限流 / 取消）与阻塞调用混用未练 |
| TypeScript / Node 生态 | 2 | — | `openai` + `@anthropic-ai/sdk` + `@earendil-works/pi-coding-agent`；ESM（`"type": "module"`）、top-level await、`for await...of`、可选链；识别并替换了占位包 | 能跑通；类型系统（泛型 / 联合类型 / 严格模式）没练，无 tsconfig；npm 与 uv 两套工具链混在同一目录 |
| uv / 依赖与虚拟环境管理 | 2 | — | `uv init / add / run / python pin`，读懂 `pyproject.toml` | 日常够用；workspace、锁文件机制、发布待学 |
| Git / GitHub | 2 | — | 仓库拆分提交、`.gitattributes`、`.gitignore` 例外规则、`git check-ignore` | 日常够用；分支策略、PR 流程待练 |
| API 设计（FastAPI / Flask） | 0 | — | | |
| 容器化（Docker） | 0 | — | | |
| CI/CD | 0 | — | | |

## 安全 × AI（你的差异化方向）

| 技能 | 等级 (0-5) | 目标 | 证据 / 项目 | 备注 |
|------|-----------|------|------------|------|
| 安全领域知识（作为 Agent 场景理解） | 3 | 4 | 网络安全从业经验 | **已有的领域优势，不是待补项**，等级请按实际校正 |
| Prompt Injection 攻防 / OWASP LLM Top 10 | 0 | 4 | | **你的差异化标签**，攻防背景可直接迁移 |
| Agent 权限与工具边界 / 威胁建模 | 0 | 4 | | 工具调用 = 把执行权限交给 LLM，本质是权限管理问题 |
| Agent 红队测试 | 0 | 3 | | |
| 安全日志/告警的 Agent 化（研判、降噪、响应） | 0 | 4 | | **目标求职场景** |

---

> **更新规则**：每点亮一个新技能就及时更新等级，别等月底一次性补。
