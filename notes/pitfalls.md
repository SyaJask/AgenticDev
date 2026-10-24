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

### [2026-10-24] 沙箱里 `pnpm why` 报 ERR_SQLITE_ERROR：store 索引库在工作区外

**现象**：在 DSH 沙箱里想确认某个包是谁带进来的，`pnpm why` 直接失败：

```text
PS ...\code\playground\01-hello-llm> pnpm why @google/genai
[ERR_SQLITE_ERROR] unable to open database file

pnpm: unable to open database file
    at file:///.../pnpm/11.3.0/dist/pnpm.mjs:16156 ... new StoreIndex ...
    at ... buildDependentsTree ...
```

对比：同一项目的 `pnpm install` 完全正常——但那是在**自己的 PowerShell（沙箱外）**里跑的。所以这不是项目坏了，是"沙箱里的命令碰了沙箱外的目录"。

**原因**：

1. `pnpm why` 要构建"谁依赖谁"的树，会打开 pnpm 的 **store 索引库**（SQLite）。栈里的 `new StoreIndex` → `buildDependentsTree` 就是这一步。
2. 本机这次安装实际用的 store 是 **`D:\.pnpm-store\v11`**（在工作区之外，`index.db` 28 MB）。权威记录在 `node_modules/.modules.yaml`：

   ```text
   "storeDir": "D:\\.pnpm-store\\v11",
   "virtualStoreDir": "D:\\ai2all\\...\\node_modules\\.pnpm",
   ```

3. 沙箱进程不能写工作区之外的目录，而 SQLite 打开库要建/锁日志文件 → 打不开 → pnpm 把它翻成 `[ERR_SQLITE_ERROR] unable to open database file`。
4. **容易看走眼的地方**：`pnpm store path` 打印的是"按当前目录算出来的 store 路径"，和这次安装实际用的 store 可能不是同一个（本机就出现过：`pnpm store path` 报工作区里的 `.pnpm-store\v11`，而 `.modules.yaml` 里记的是 `D:\.pnpm-store\v11`）。判断实际用的是哪一个，看 `.modules.yaml`。

验证这条判断的两个动作：

```powershell
# 看安装时实际用的 store
Select-String -Path node_modules\.modules.yaml -Pattern 'storeDir'

# 那个目录沙箱能不能写（这里会失败，就是它）
Set-Content 'D:\.pnpm-store\__p.tmp' x; Remove-Item 'D:\.pnpm-store\__p.tmp'
```

**解法**：查依赖关系根本不需要 pnpm，直接读 `pnpm-lock.yaml`：

```powershell
# 找到"谁声明了这个依赖"：命中行是依赖声明（缩进 6 空格），向上找最近的缩进 2 空格的快照名即为父包
Select-String -Path pnpm-lock.yaml -Pattern "'@google/genai': 2.21.0" -Context 10,0
```

实测读出链路：`@earendil-works/pi-coding-agent → @earendil-works/pi-ai@1.4.0 → @google/genai@2.21.0 → protobufjs@7.6.6`。

其他三条路：

- 把这类命令放到**沙箱外**自己的终端里跑（最省事）；
- 用 `npm ls <pkg>` 之类只读 lockfile 的方式（它不走 pnpm store）；
- 把 store 指到工作区内（`pnpm config set store-dir <工作区里的路径>`），代价是缓存多存一份、和别的项目不共享。

**教训**：看到 `unable to open database file` 先别怀疑 lockfile 损坏或配置错误——先问「**这条命令要写哪里**」。包管理器的 store / 缓存 / 索引默认都在工作区外，凡是需要读写 store 的命令（`why`、`store` 系列维护动作，以及可能包括在沙箱里跑 `install`）都会倒；只跟 lockfile 有关的结论，就直接读 `pnpm-lock.yaml`，比装一个能"解释"它的工具便宜。

### [2026-10-24] 沙箱进不了工作区子目录：Windows 完整性标记只对「新建」对象继承

**现象**：DSH 会话里让我提交代码，`git add/commit/status` 全部正常，但任何落到子目录的写操作都被系统拒绝：

```text
Set-Content: 对路径"D:\ai2all\projects\AgenticDev\notes\__probe.tmp"的访问被拒绝。
Remove-Item: 对路径"...\code\playground\01-hello-llm\main.ts"的访问被拒绝。
```

而**在仓库根目录**建文件、删文件都正常。同一会话里 `git clean` 删子目录文件也失败（`failed to remove ...: Invalid argument`）。顺带症状：`git add` 一直警告 `CRLF will be replaced by LF`，`git checkout -f`、`git checkout-index -f -a` 都返回成功，但工作区文件行尾不变。

**原因**（三层，缺一层都解释不通）：

1. **沙箱进程是低完整性令牌**。`whoami /groups` 显示 `Mandatory Label\Low Mandatory Level  S-1-16-4096`。
2. **Windows 的 MIC 先于 DACL 判断**：低完整性进程不能写比它级别高的对象，而且**没有标记的对象按 Medium 处理**（Microsoft Learn 原文）。工作区根目录被打了 `Mandatory Label\Low Mandatory Level:(OI)(CI)(NW)`，所以根下可写。
3. **完整性标记只在对象创建时继承**，改了父目录的标记**不会回溯**已经存在的子对象。`code/`、`notes/`、`plan/`、`portfolio/` 都是在打标记之前就存在的，全都"无标记 = Medium"→ 被拒。

验证方式：在根目录新建一个临时子目录，里面立刻可写可删；同样的写操作搬到 `code/` 就失败。这就把"根目录行、子目录不行"锁死在标记继承上。

另外**权限条目本身是正常的**（owner 是自己、`protected=False`、DACL 继承正常、没有 deny），所以 DSH 自带的 ACL 诊断脚本给出 `VERDICT=NOT_THIS_CLASS`、`FIXED=0`——它负责的是另一类问题（缺 WRITE_DAC/WRITE_OWNER、外部应用留下的包 ACE）。**ACL 正常 ≠ 能写**。

**解法**：

```powershell
$sid = '*' + ((whoami /user /fo csv | ConvertFrom-Csv)[0].SID)

# 1) 打完整性标记要写 SACL，需要 WRITE_OWNER。
#    目标上只有 Modify 时 /setintegritylevel 会被拒：Access is denied。
icacls 'D:\ai2all\projects\AgenticDev' /grant "${sid}:(OI)(CI)(WO)" /t /c

# 2) 给已存在的整棵子树补 Low 标记（此后新建对象会自动继承）
icacls 'D:\ai2all\projects\AgenticDev' /setintegritylevel '(OI)(CI)Low' /t /c
```

三步自检，以后遇到同类问题直接照抄：

```powershell
whoami /groups | findstr 'S-1-16'                        # 我自己的完整性级别
icacls <目录> | findstr 'Mandatory Label'                 # 对象有没有标记（空 = 无标记 = Medium）
Set-Content <目录>\__p.tmp x; Remove-Item <目录>\__p.tmp   # 到底能不能写
```

**坑里的坑**：

- `icacls /grant "${me}:..."` 里变量取空时，icacls 会写进一条指向 `S-1-5-32`（内建域本身，不是任何真实账号）的垃圾权限项。用 SID、先在终端 `echo` 确认变量非空。事后清理：`icacls <root> /remove:g '*S-1-5-32' /t /c`。
- **管理员终端里跑过 `npm install`**，`node_modules` 的 owner 会变成 `BUILTIN\Administrators`，普通进程和沙箱进程之后都改不动它（等价于 Linux 里 `sudo npm install` 留下的 root 属主文件）。本仓这类对象有 2 万多个，补标记时全部 `Access is denied`；只能删掉在以自己身份运行的环境里重装。
- **不要用 `icacls /reset` 修这个**：它把对象 ACL 还原成"继承自父级"，会把根目录上 DSH 加的授权项一起冲掉。

**教训**：Windows 上"写不进去"要分三道闸门查——**完整性级别**（`whoami /groups`）→ **对象标记**（`icacls` 里的 `Mandatory Label`）→ **DACL 权限条目**。而且记住：**标记不会回溯已存在的对象**，无标记等于 Medium。另外，装依赖永远用自己的身份，别抬权。

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
