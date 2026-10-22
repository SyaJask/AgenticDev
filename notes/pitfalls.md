# 踩坑记录（金矿）

> 任何"卡了很久才解决"的问题，立刻记进来。
> 写清：**现象 → 原因 → 解法 → 一句话教训**。
>
> 面试时这些是最值钱的谈资，也是你自己最实用的备忘录。

---

## 使用说明

每条记录用以下格式：

```
### [日期] 一句话标题

**现象**：发生了什么表现（报错信息、异常行为）

**原因**：根因是什么

**解法**：怎么解决的（贴出关键代码/命令）

**教训**：一句话总结，避免再犯
```

---

## 记录

<!-- 在此追加新记录，最新的放最上面 -->

### [2026-10-22] Python 默认参数在「函数定义时」求值 —— 可变/副作用默认参数是坑

**现象**：学习代码里写了这样的签名：

```python
def openai_client(client = OpenAI(), model = "agnes-3.0-flash"):
```

看着像"没传就用默认值"，实际行为是：**模块 `import` 的那一瞬间就执行了 `OpenAI()`**。

**原因**：Python 的默认参数表达式在**函数定义时求值一次**，结果存进函数的 `__defaults__`，之后每次调用都复用同一个对象。于是：

1. 三个 provider 的 client 在 `import` 时全部被创建 —— 哪怕你只用一个；
2. 创建 client 需要 API Key，所以"只想 import 看看"也会因为缺 Key 直接抛异常；
3. 若默认值是可变对象（`def f(xs=[])`），所有调用会**共享并累积**同一个列表 —— 这是最经典的版本。

**解法**：默认给 `None`，在函数体里创建。

```python
def openai_client(client=None, model="agnes-3.0-flash"):
    if client is None:
        client = OpenAI()
```

**教训**：**默认参数只放不可变、无副作用的字面量**。要建对象、要读环境变量、要取当前时间 —— 一律放进函数体。看到 `def f(x=SomeObj())` 或 `def f(xs=[])` 就该警觉。

> ⚠️ 同一个写法在 JavaScript / TypeScript 里**是对的**，原因见下一条。

### [2026-10-22] 同一份语法形状，两套语义 —— 跨语言迁移的隐性坑

**现象**：从 Python 抄到 TypeScript 的一段代码，长得几乎一样，行为却不同。

```python
def f(client=OpenAI()): ...             # Python：import 时就建好
```

```ts
function f(client = new OpenAI()) { }   // TS：每次调用才建
```

**原因**：**默认参数的求值时机**两种语言不同。

| | 求值时机 | 后果 |
|---|---|---|
| Python | 函数**定义**时（一次） | 副作用提前发生，对象被共享 |
| JavaScript / TypeScript | 每次**调用**时 | 行为符合直觉 |

**这不是孤例。**「形状一样、语义不同」是跨语言最大的一类陷阱。同类还有：

| 形状 | Python | JavaScript / TS |
|---|---|---|
| 默认参数求值 | 定义时一次 | 每次调用 |
| `a / b`（两整数） | 真除法，`1/2 == 0.5` | 需 `Math.floor` 才得整数 |
| 空值真假 | 空列表 / 空字典是 falsy | 空数组 / 空对象是 truthy |
| 变量作用域 | 函数级，靠 `nonlocal` | 块级 `let` / `const` |
| 字符串 | `str` 与 `bytes` 严格分开 | 统一 `string`（UTF-16） |

**解法**：跨语言搬代码时，对每一处都问一遍"**这里的语义和原来一样吗**"，重点是默认值、真值判断、作用域、数值这四类。

**教训**：**"看起来一样"不等于"行为一样"。** 换语言最容易踩的不是写不出的语法，而是写得特别顺、但语义已悄悄变了的那部分。

### [2026-10-11] `uv run <命令>` 是「项目内执行」，不是全局命令查找

**现象**：在 `code/playground/`（非项目目录）执行 `uv run 01-hello-llm`：

```
error: Failed to spawn: 01-hello-llm
  cause: program not found
```

**原因**：`uv run` 的语义是「在**当前项目**里运行东西」，不是"去系统 PATH 里找命令"。`code/playground/` 下没有 `pyproject.toml`，uv 找不到项目，于是退化成把 `01-hello-llm` 当成一个系统可执行程序去 spawn，自然找不到。项目本身、依赖、`.venv` 全都正常，纯粹是「站错了地方」。

**解法**：先进入项目目录（`pyproject.toml` 所在处）再执行：

```bash
cd 01-hello-llm
uv run 01-hello-llm
```

不想 `cd` 时可用 `--directory` / `-C` 显式指定项目目录：

```bash
uv run -C ./01-hello-llm 01-hello-llm
```

**教训**：看到 `program not found` 先自问「**我在项目根吗**」，而不是去查命令拼写或 PATH。uv / poetry / npm 这类工具都遵循「按当前目录定位项目」的规则，跨目录操作必须显式指定项目。

### [2026-10-11] Python 包名不能以数字开头（`01_hello_llm` 是非法标识符）

**现象**：`uv init 01-hello-llm` 生成了 `src/01_hello_llm/`。项目能建、依赖能装、命令有时也能跑，看不出毛病。但只要写 `import` 就炸：

```python
from 01_hello_llm import main   # SyntaxError: invalid syntax
import 01_hello_llm             # SyntaxError: invalid syntax
```

**原因**：Python 的**导入包名**必须是合法标识符（字母或下划线开头，只能含字母/数字/下划线）。uv 会把目录名 `01-hello-llm` 规范化成包名 `01_hello_llm`（`-` → `_`），但**开头那个数字规范不掉**，于是生成了一个语法上无法 `import` 的包名。之所以"看起来没事"，只是因为当时还没写过任何 import 语句——坑埋在那里，等写测试或拆模块时才炸。

要分清两个名字：

|          | 名称                           | 你的例子            | 命名规则                           |
| -------- | ------------------------------ | ------------------- | ---------------------------------- |
| 分发包名 | `pyproject.toml` 的 `name` | `01-hello-llm`    | 可以带`-`，PyPI 内唯一即可       |
| 导入包名 | `src/` 下的目录名            | `01_hello_llm` ❌ | **必须是合法 Python 标识符** |

两者本来就该"同名不同形"，所以 `src/` 下多一层**不是**冗余，是标准布局。

**解法**：目录名可以带序号（便于排序），但**包名必须合法**。两条路：

```bash
# A. playground 实验不需要打包 —— 删掉 [build-system] / [project.scripts] 与 src/，代码放根目录 main.py
uv run main.py

# B. 要保留打包 —— 用 --name 指定合法的包名
uv init 01-hello-llm --name hello-llm    # 得到 src/hello_llm/
uv run hello-llm
```

**教训**：**目录名随便起，包名守规矩**。起名前先自问「这个名字要拿去 `import` 吗」，要的话必须以字母或下划线开头。同类陷阱还有：包名撞标准库（`email`、`json`、`types`）、含中文/空格/点号。

### [2026-10-10] 沙箱内 git push 失败：凭据助手起不来（命名管道被拒）

**现象**：在受限沙箱里执行 `git push`，TLS 握手已通过，却卡在取凭据环节：

```
sh.exe: *** fatal error - couldn't create signal pipe, Win32 error 5
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

**原因**：`credential.helper=manager` 需要启动凭据助手进程去读 Windows 凭据管理器，而该助手依赖创建命名管道；受限沙箱禁止进程创建命名管道，助手启动即失败，git 自然拿不到用户名/密码。与仓库配置、网络、GitHub 权限都无关。

**解法**：把「需要凭据的网络动作」放到沙箱之外执行（一次性放宽权限），或在自己终端手动 `git push`。同一环境里 `git add / commit / log / status` 等纯本地操作完全正常，只有依赖凭据助手的推送会被挡住。

**教训**：看到 `could not read Username` 先别急着改凭据配置——先判断进程有没有权限创建管道、访问凭据存储，「认证失败」有时是权限边界而不是凭据本身。

### [2026-10-10] git push 报 schannel SEC_E_NO_CREDENTIALS，换 TLS 后端即恢复

**现象**：`git push` 与 `git ls-remote` 都报：

```
fatal: unable to access 'https://github.com/<owner>/<repo>.git/':
schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030E)
```

**原因**：Windows 版 git 默认走 SChannel 后端（`http.sslBackend=schannel`，来自系统级 `D:/apps/Git/etc/gitconfig`），在本机该环境下无法取得客户端凭据。把后端换成 openssl 后，同一地址、同一份凭据立即握手成功，证明网络和凭据都没问题，纯粹是 TLS 后端差异。

**解法**：

```bash
# 仅本条命令生效，不改动任何配置
git -c http.sslBackend=openssl push origin main

# 若长期需要再自行固化（改用 git 自带 CA 包，而非 Windows 证书库）
git config --global http.sslBackend openssl
```

**教训**：HTTPS 连不上时用 `git ls-remote` 做二分——换个 TLS 后端就通，说明问题在后端，别去折腾代理、DNS 或权限。
