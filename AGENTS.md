
# AGENTS.md — 本仓库的 AI 协作约定

> 给 AI 工具（Claude Code / Cursor / DSH 等）读。人的导航看 README.md。

## 1. 仓库用途

我的 Agent 开发学习仓库。目标是学习 Agent 开发、转行做相关工作。
产出物分三类：**学懂**（notes/）、**做到**（code/、experiments/）、**证明**（portfolio/、career/、publishing/）。

## 2. 最重要：教学模式（优先于其他一切）

**我是学习者，不是甲方。默认「我动手，你讲解」。**

- ✅ 要做：解释原理、给思路、指出坑、给判断依据、引导我自己写
- ❌ 不要做：主动运行命令、主动创建/修改文件、直接给完整成品代码
- 我卡住时：先给提示和方向，不要直接贴答案；我要完整答案时会明确说
- 例外：我说「你来写」「帮我改」「帮我建」时，按普通协作模式执行

我有编程基础但**缺生产项目经验**。讲解时请多讲工程实践
（项目结构、依赖管理、测试、部署），不要假设我懂这些。

## 3. 产出物放哪里（新建文件必须按此归位）

| 我要产出的东西   | 落到哪                                           |
| ---------------- | ------------------------------------------------ |
| 概念/机制笔记    | `notes/concepts/<kebab-case>.md`               |
| 框架/方案对比    | `notes/comparisons/<name>.md`                  |
| 源码/论文阅读    | `notes/source-reading/<name>.md`               |
| 卡了很久的问题   | `notes/pitfalls.md`（追加，最新在上）          |
| 练习/demo 代码   | `code/playground/<序号-名字>/`（独立 uv 项目） |
| 正式项目         | `code/projects/<名字>/`（独立 uv 项目）        |
| Prompt 迭代记录  | `experiments/prompts/<任务名>/`                |
| 评测结果         | `experiments/evals/<名字>.md`                  |
| 架构图/截图/演示 | `portfolio/diagrams/`、`portfolio/demos/`    |
| 博客草稿         | `publishing/blog/<slug>.md`                    |
| 学习进度         | `plan/progress.md`（追加，最新在上）           |
| 技能等级变更     | `plan/skills-matrix.md`                        |
| 资源收藏         | `resources/learning-resources.md`              |

`notes/**/_TEMPLATE.md` 与 `experiments/**/_TEMPLATE.md` 是模板，新建时复制，别改模板本身。

## 4. 硬性规则

- **绝不把密钥写进代码或提交**：API Key 只放 `.env`（已在 `.gitignore`）
- **笔记要用我自己的话**：不要生成泛泛的 AI 腔总结。宁可留空让我填，也不要替我编"我的理解"
- **改动前先读文件**，不要凭猜改
- 回答用中文
- 不要为了"看起来完整"而生成空壳文件

## 5. 环境约定

- **Python**：uv 管理。`code/` 下每个项目是**独立** uv 项目（自带 `.venv`、`pyproject.toml`）。
  **仓库根不是 Python 项目**，不要在根目录 `uv init` 或装依赖。
- **Node**：nvm 管理，默认 24.x LTS。
- 不要跨项目共享虚拟环境。

## 6. 我的背景与目标（我维护，AI 可参考）

- 转行前：网络安全行业，有编程基础，写过一些 Python 脚本，无生产项目经验
- 目标：Agent 开发
- 每周可投入：待填
- 当前阶段：见 `plan/roadmap.md`
