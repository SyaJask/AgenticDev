# 依赖构建脚本审批（install / build scripts approval）

> 📌 机制部分由 AI 协助整理（依据 npm v12、pnpm 官方文档 + 本机实测：pnpm 11.3.0、npm 12.2.1、Node 24.21.0）。**「我的理解 / 类比」一节必须你自己写**。

---

## 一句话定义

包管理器在安装时**默认不执行依赖自带的安装/构建脚本**（`preinstall` / `install` / `postinstall`），只把"这棵树里哪些包想跑脚本"列出来；你逐个批准、写进项目的白名单之后，它们才会被执行。

## 它解决什么问题 / 为什么需要

`install` 脚本的可怕之处在于**执行时机**：`npm/pnpm install` 一跑，它就以**你的身份**执行任意代码，而你连那个包的名字都未必听说过（传递依赖也算）。这份代码能联网、能读写文件、能读环境变量里的 token（包括 CI 的凭据）。历史上的供应链攻击基本都走这条路：恶意版本塞进 postinstall 偷密钥、挖矿，或者上游包被接管后发一版恶意代码。

所以旧方案里只有两个极端：

| 方案 | 做法 | 代价 |
| --- | --- | --- |
| 默认信任 | 装什么都跑脚本 | 一装就中招 |
| `--ignore-scripts` | 整棵树全禁 | 原生模块（node-gyp、esbuild、sharp、canvas）装不全，得手动 rebuild |

「审批」是第三条路：**默认不跑 + 白名单放行**。把"信任整棵树"换成"信任你审过的那几个包"。

## 核心机制 / 工作流程

### npm（v12 起默认拦截）

1. 依赖的 install 脚本被**静默跳过**，`npm install` 结束时列出"脚本被跳过"的包名，提示你审阅。
2. 批准状态记在 `package.json` 的 **`allowScripts`** 字段。
3. `npm approve-scripts <pkg...>` 批准；默认写入**带版本**的条目（`pkg@1.2.3`），把授权绑定到你审过的那个版本。
4. 辅助开关：`--all`（全批，等于关掉审核）、`--allow-scripts-pending`（只列未审的，只读）、`--no-allow-scripts-pin`（写 name-only）。
5. 全局安装 / `npx` 没有项目 `package.json` 可写 → `approve-scripts` 直接报 `EGLOBAL`，改用 `npm install -g --allow-scripts=canvas,sharp` 或 `npm config set allow-scripts=... --location=user`。
6. `npm deny-scripts` 显式拒绝；**已拒绝的条目不会被再次悄悄放行**。
7. 更早的 `ignore-scripts`（全禁）仍然存在，适合"环境里一律不许跑依赖脚本"的场合。

### pnpm（v10 起「默认安全」，v11 用 `allowBuilds`）

1. v10.0 起不再隐式信任依赖：默认不跑 `preinstall` / `postinstall`。
2. v10.26 起用 `pnpm-workspace.yaml` 的 **`allowBuilds`** 映射取代旧的 `onlyBuiltDependencies`（pnpm 11 起后者彻底失效）：

   ```yaml
   allowBuilds:
     esbuild: true
     nx@21.6.4: true        # 也能按版本授权
     protobufjs: false      # 显式拒绝
   ```

3. `pnpm approve-builds`：不带参数走交互式；也能直接带包名，`!pkg` 表示拒绝，`--all` 全批。只有被点名的包会变，其余不动。
4. **关键行为**：安装时若有包"有待批准的构建、又没写进 allowBuilds"，pnpm 会**自动往 `pnpm-workspace.yaml` 补一条占位符**（值是字符串 `set this to true or false`），等你手动改成 `true` / `false`。**占位符不是有效配置，等于仍未批准。**
5. 一次性放行：`pnpm add --allow-build=esbuild bundle`（同时把 `esbuild` 写进白名单）。
6. 兜底开关 `dangerouslyAllowAllBuilds`（v10.9 引入）：全放行，等于回到老行为，别在正经项目里开。
7. 同族的纵深防御：`minimumReleaseAge`（拒绝太新的版本）、`trustPolicy: no-downgrade`、`blockExoticSubdeps`。

### 两者对照

| | npm | pnpm |
| --- | --- | --- |
| 默认行为 | v12 起拦截 | v10 起拦截 |
| 白名单位置 | `package.json` 的 `allowScripts` | `pnpm-workspace.yaml` 的 `allowBuilds` |
| 审批命令 | `npm approve-scripts` / `npm deny-scripts` | `pnpm approve-builds` |
| 版本粒度 | 默认 pin 到安装的版本 | 支持 `pkg@version` |
| 一次性放行 | `--allow-scripts=...` | `--allow-build=...` |
| 未批准时 | install 结束列出被跳过的包 | 自动往 workspace.yaml 写占位符 |
| 全禁开关 | `ignore-scripts` | `dangerouslyAllowAllBuilds`（全放） |

## 关键概念 / 术语

| 术语 | 是什么 |
| --- | --- |
| **install scripts / lifecycle scripts** | `preinstall`、`install`、`postinstall`，以及非 registry 来源的 `prepare`。在依赖自己的 `package.json` 里定义，装依赖时执行 |
| **allowScripts** | npm 的白名单字段（`package.json`），记录哪些依赖被允许跑 install 脚本 |
| **allowBuilds** | pnpm 的白名单映射（`pnpm-workspace.yaml`），包名/`包@版本` → `true`/`false` |
| **onlyBuiltDependencies** | pnpm 10 时代的旧白名单字段，pnpm 11 被 `allowBuilds` 取代 |
| **pin（版本绑定）** | 授权绑定到具体版本（`pkg@1.2.3`）；包升级后授权不自动延续，需要重新批准 |
| **原生模块构建** | 需要编译或用 postinstall 下载二进制的包（node-gyp 系、esbuild、sharp、canvas、fsevents）。它们是最常被批准的一类 |
| **传递依赖** | 你直接写的依赖所依赖的包。攻击面往往在它们身上——你没主动装过，但脚本会跑 |

## 代码示例

**本仓实际产物**（`code/playground/01-hello-llm/pnpm-workspace.yaml`，pnpm 11.3.0 安装后自动生成）：

```yaml
allowBuilds:
  '@google/genai': set this to true or false
  protobufjs: set this to true or false
```

这两条就是"待批准"占位符，改或不改，行为上都是"没批准"。

**安装时的实际输出**（2026-10-24，本机 pnpm 11.3.0）：

```text
PS D:\ai2all\projects\AgenticDev> cd code\playground\01-hello-llm; pnpm install
Downloading @earendil-works/pi-coding-agent@1.4.0: 7.61 MB/7.61 MB, done
Packages: +122
Progress: resolved 122, reused 21, downloaded 101, added 122, done

dependencies:
+ @anthropic-ai/sdk 0.135.0 (1.3.0 is available)
+ @earendil-works/pi-coding-agent 1.4.0
+ openai 7.43.0

[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: @google/genai@2.21.0, protobufjs@7.6.6

Run "pnpm approve-builds" to pick which dependencies should be allowed to run scripts.
```

怎么读这段输出：

- `Packages: +122 ... done` → 依赖树已经装完，**安装本身是成功的**；
- `[ERR_PNPM_IGNORED_BUILDS]` 虽然以 `ERR_` 开头，但出现在安装完成**之后**，是一条"报告级"提示：告诉你哪两个包的脚本被跳过，而且**带了具体版本**（`@google/genai@2.21.0`、`protobufjs@7.6.6`）——版本号正是之后批准时要核对的粒度；
- 同一次安装顺带把这两个包写进了 `pnpm-workspace.yaml` 的 `allowBuilds`，值留成占位符，等你去改；
- 对比：npm 在这一步是"静默跳过 + 结尾列清单"，pnpm 用 `ERR_PNPM_IGNORED_BUILDS` 加 `Run "pnpm approve-builds"` 直接把下一步命令告诉你。

```bash
# 先看清单（npm，只读，不动 package.json）
npm approve-scripts --allow-scripts-pending

# 批准（默认写入 pkg@版本；加 --all 就是全批，不建议）
npm approve-scripts protobufjs

# 明确拒绝
npm deny-scripts protobufjs
```

```bash
# pnpm：交互式逐个决定
pnpm approve-builds

# 只批指定的、拒绝指定的（! 前缀），其余不动
pnpm approve-builds protobufjs '!@google/genai'

# 批准后触发重建（已装过的话）
pnpm rebuild protobufjs
```

**批准前先看清楚这个包为什么需要构建**：

```bash
npm view protobufjs scripts          # 看它定义了什么脚本
# 或直接读 node_modules/protobufjs/package.json 里的 scripts
```

## 常见坑 & 注意事项

1. **install 成功 ≠ 依赖可用**。被跳过的原生构建要到**运行时**才炸（`Cannot find module`、缺 `.node` 二进制、`sharp` 相关报错）。装完是绿的，跑起来才发现。同理，pnpm 的 `[ERR_PNPM_IGNORED_BUILDS]` 出现在 `Packages: +122 ... done` 之后，是提醒不是安装失败——重跑一遍 `pnpm install` 不会让它消失。
2. **占位符不是配置**。`set this to true or false` 是字符串，看着像"已经处理过"，其实永远算未批准。要改就改成布尔值。
3. **CI 里最阴**。本地因为手滑批准过、能跑；CI 新装一棵树静默跳过 → 构建/测试挂了，而 install 是绿色的。批准状态要进版本库（`allowBuilds` / `allowScripts` 都应该提交）。
4. **别顺手 `--all`**。等于把审核环节整个关掉，风险回到"默认信任"。
5. **pin 是双刃**。默认按版本授权，包升级后在清单里又会出现——这正是它的价值（防"接管包名后发新版本"），但记得升级后重新审一遍。
6. **全局安装 / npx 没有项目可写**。`approve-scripts` 会 `EGLOBAL` 报错；用 `--allow-scripts=` / `--allow-build=` 或 user 级配置。
7. **换包管理器要重批**。npm 的 `allowScripts` 和 pnpm 的 `allowBuilds` 互不相认；同一个项目切换工具时，白名单不会跟着走。
8. **先跑再说也是一种策略**，但要留个回头查的钩子——见下一节。

## 本仓现状（2026-10-24）

- `code/playground/01-hello-llm` 用 `pnpm install` 装了 122 个包（2026-10-24），结果：`@anthropic-ai/sdk 0.135.0`、`@earendil-works/pi-coding-agent 1.4.0`、`openai 7.43.0`。
- 同一次安装报出两个待批准构建，`pnpm-workspace.yaml` 里对应两条占位符：
  - `@google/genai@2.21.0` → `set this to true or false`
  - `protobufjs@7.6.6` → `set this to true or false`
- 两者都是**传递依赖**，从 `pnpm-lock.yaml` 读出来的链路是：
  `@earendil-works/pi-coding-agent` → `@earendil-works/pi-ai@1.4.0` → `@google/genai@2.21.0` → `protobufjs@7.6.6`。
  （即：项目自己 `package.json` 里一个字都没写，但它们的构建脚本照样会被执行——这正是审批机制要解决的场景。）
- **决定：暂不批准**，先按现状跑；如果运行相关代码时出现异常，再回头处理。
- 回头的触发条件（出现任一条就去批）：
  - 运行时报错指向这两个包（protobufjs 缺构建产物、`@google/genai` 初始化或 protobuf 相关报错）；
  - `node main.ts` 或 `pnpm start` 在用到 pi-coding-agent 时异常；
  - 引入新依赖后又冒出新占位符，且行为不对。
- 最小处理步骤：`pnpm approve-builds` → 只勾报错涉及的那个包 → 若已装过则 `pnpm rebuild <pkg>`，或重跑 `pnpm install`。改完把 `pnpm-workspace.yaml` 一起提交。

## 我的理解 / 类比

<!-- 不要抄上面的定义。写"如果我要给同事讲清楚，我会怎么说"，并想一个你自己的类比 -->

提示（写完删掉）：

- 这像不像"入职背调"和"一个都不招"之间的第三条路？为什么默认值要从"信任"翻成"不信任"？
- 为什么 npm 默认把授权 **pin 到版本**，而不是允许整个包名？
- 那些"靠 postinstall 偷偷干正事"的包（下载二进制、生成代码）在新规则下怎么活？
- 你觉得这个机制真正的成本在哪：多点几次批准，还是"批准时你得有能力看懂那段脚本"？

（⬜ 待你填写）

## 参考链接

- [npm approve-scripts（v12 文档）](https://docs.npmjs.com/cli/v12/commands/npm-approve-scripts) —— 默认拦截、`allowScripts`、pin、`--allow-scripts-pending`、`EGLOBAL`
- [pnpm approve-builds](https://pnpm.io/cli/approve-builds) —— `allowBuilds` 写入规则、占位符自动补齐、`!pkg` 拒绝、`--allow-build`
- [pnpm 2025 年度回顾（默认安全 / allowBuilds / 纵深防御）](https://pnpm.io/zh/blog/2025/12/29/pnpm-in-2025) —— 为什么 v10 起默认不信任依赖
- [pnpm: Mitigating supply chain attacks](https://pnpm.io/10.x/supply-chain-security) —— 供应链风险的完整说明与 `dangerouslyAllowAllBuilds` 的取舍
