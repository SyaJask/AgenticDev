# Agent 开发学习路线图

> 最后更新：2026-10-10
> 当前阶段：第 0 阶段 — 环境搭建 & 宏观认知

---

## 阶段总览

| 阶段 | 目标 | 预计时长 | 状态 |
|------|------|----------|------|
| 0 | 环境搭建 & 宏观认知：能跑 demo、知道 Agent 生态全景 | 1 周 | ⬜ |
| 1 | LLM 基础扎实：Prompt Engineering、Token、Context Window、完成一个调用封装 | 2 周 | ⬜ |
| 2 | RAG 与工具调用：Function Calling、Tool Use、向量数据库 | 3 周 | ⬜ |
| 3 | Agent 框架：LangChain / LangGraph / CrewAI / AutoGen 择一深入 | 4 周 | ⬜ |
| 4 | Agent 架构与设计模式：ReAct、Plan-Execute、Multi-Agent、Memory | 3 周 | ⬜ |
| 5 | 评测与可观测性：Agent Eval、Tracing、成本控制 | 2 周 | ⬜ |
| 6 | 实战项目：端到端的 Agent 应用（MVP → 迭代 → 交付） | 4 周 | ⬜ |
| 7 | 作品集打磨 & 面试冲刺 | 持续 | ⬜ |

---

## 第 0 阶段：环境搭建 & 宏观认知

### 目标
- 搭建 Python/Node 开发环境
- 拿到至少一个 LLM API Key（OpenAI / Claude / 国产大模型）
- 跑通第一个 LLM 调用 demo
- 知道 Agent 领域的大图：哪些框架、哪些公司、哪些典型应用

### 任务清单
- [ ] 配置开发环境（IDE、包管理、虚拟环境）
- [ ] 注册并获取 API Key，跑通 `hello world`
- [ ] 阅读 1-2 篇 Agent 综述/趋势文章，画出生态全景图（放 `portfolio/diagrams/`）
- [ ] 列出当前 Agent 领域的 10 个典型应用场景
- [ ] 在 `plan/skills-matrix.md` 填入当前能力基线

---

## 第 1 阶段：LLM 基础扎实

### 目标
- 理解 LLM 工作原理（Token、Embedding、Temperature、Context Window）
- 掌握 Prompt Engineering 方法论（Few-shot、CoT、结构化输出）
- 封装一个自己的 LLM 调用工具类

### 任务清单
- [ ] 系统学习 Prompt Engineering Guide
- [ ] 动手做 10+ 个 Prompt 实验（记录在 `experiments/prompts/`）
- [ ] 封装 LLM 调用类（支持流式、重试、多模型切换）
- [ ] 笔记：`notes/concepts/token-embedding-context.md`

---

## 第 2 阶段：RAG 与工具调用

### 目标
- 理解 RAG 完整链路：文档解析 → 切片 → 向量化 → 检索 → 增强生成
- 掌握 Function Calling / Tool Use 机制
- 实现一个带 RAG 和 Tool Use 的 demo

### 任务清单
- [ ] 搭建向量数据库（本地：Chroma / FAISS / LanceDB）
- [ ] 实现文档解析 → Embedding → 检索 → 生成 全链路
- [ ] 实现至少 3 个 Tool（如搜索 API、计算器、数据库查询）
- [ ] 笔记：`notes/concepts/rag.md`、`notes/concepts/function-calling.md`

---

## 第 3 阶段：Agent 框架深入

### 目标
- 选择一个主流 Agent 框架深入使用
- 理解 Agent 循环本质：Observe → Plan → Act → Observe
- 能自己写出一个 minimal agent loop（不依赖框架）

### 框架选项
- **LangGraph**（推荐，图式编排，可观测性好）
- **CrewAI**（Multi-Agent 上手快）
- **AutoGen**（对话式 Multi-Agent）
- **纯手写**（理解最深，建议第四阶段回头做）

### 任务清单
- [ ] 选一个框架，完成官方教程
- [ ] 改造第二阶段 RAG 应用为 Agent
- [ ] 手写一个 minimal agent loop（`code/projects/minimal-agent/`）
- [ ] 对比笔记：`notes/comparisons/agent-frameworks.md`

---

## 第 4 阶段：Agent 架构与设计模式

### 目标
- 掌握经典 Agent 设计模式
- 理解 Multi-Agent 编排与通信
- 掌握 Memory 管理

### 设计模式清单
- ReAct（Reasoning + Acting）
- Plan-Execute（规划先行）
- Reflection（自我反思）
- Router（意图路由）
- Multi-Agent Collaboration

### 任务清单
- [ ] 每种模式实现一个 demo
- [ ] 设计一个 Multi-Agent 协作场景并实现
- [ ] 笔记：`notes/concepts/agent-patterns.md`

---

## 第 5 阶段：评测与可观测性

### 目标
- 建立 Agent 评测思维方式
- 能够用 Tracing 工具调试 Agent
- 能分析 Agent 的成本构成

### 任务清单
- [ ] 了解常用评测框架（LangSmith / Braintrust / 自建）
- [ ] 对第四阶段项目跑评测，记录基线
- [ ] 搭建 Tracing（LangSmith / LangFuse / Phoenix）
- [ ] 成本分析：Token 消耗、模型选型、延迟

---

## 第 6 阶段：实战项目

### 项目思路（择一深入）
1. **个人知识助手**：RAG + Agent 驱动的第二大脑
2. **客服 Agent**：意图路由 + 工具调用 + 人工接管
3. **代码审查 Agent**：自动 Review PR，给出建议
4. **数据分析 Agent**：自然语言 → SQL/图表/报告
5. **竞品监控 Agent**：定时抓取 → 总结 → 推送

### 项目交付标准
- [ ] README（业务问题 → 方案设计 → 架构图 → 量化结果）
- [ ] 可运行 Demo（在线或本地）
- [ ] 评测数据（准确率/召回率/延迟/成本）
- [ ] 复盘笔记（哪里做得好、哪里可以改进）

---

## 第 7 阶段：作品集打磨 & 面试冲刺

详见 `career/` 目录。

---

## 学习资源索引

👉 `resources/learning-resources.md`