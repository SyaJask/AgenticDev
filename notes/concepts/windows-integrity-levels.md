# Windows 完整性级别（Integrity Levels / MIC）

> 📌 机制部分由 AI 协助整理（依据 Microsoft Learn + 本机实测）。**「我的理解 / 类比」一节必须你自己写**。

---

## 一句话定义

Windows 的**强制完整性控制**（Mandatory Integrity Control, MIC）：给**进程令牌**和**安全对象**各贴一个完整性级别（Low / Medium / High / System），每次访问时**先于 DACL** 判断——级别不够就写不了，哪怕权限清单里明明允许你写。

## 它解决什么问题 / 为什么需要

DACL 只回答"**谁**被允许"，它有两个缺口：

1. 用户自己能写的东西（临时目录、下载目录、用户配置文件），一旦被低可信代码（浏览器标签页、下载的脚本、Agent 执行的命令）拿到，照样能改；
2. 一个被入侵的低权限进程可以顺着这些"用户可写"的位置去篡改更有价值的东西（启动项、凭据文件、输入法、其他进程）。

MIC 加的是**第二道闸门**：DACL 允许 + 级别够，才放行。它服务的现实场景：

| 场景 | 怎么用 MIC |
| --- | --- |
| 浏览器渲染进程 / IE 保护模式 | 渲染进程跑在 Low，写不到 Medium 的用户数据 |
| UWP / AppContainer / Windows 沙箱 | 应用容器化，数据隔离到自己的地盘 |
| 系统服务 | 跑 System 级别，普通进程动不了 |
| **DSH 这类 Agent 工具** | 把 Agent 的 shell 关进 Low，让它只能写"被明确打过 Low 标记"的工作区 |

最后一行就是本仓这次踩坑的来由：Agent 的写权限不是"能不能访问这个路径"，而是"进程级别够不够碰这个对象"。

## 核心机制 / 工作流程

1. **令牌带级别**：进程的访问令牌里带完整性 SID。标准用户 = Medium，管理员提权 = High，系统服务 = System。
2. **对象带标记**：对象把完整性 SID 存在 **SACL** 的 `SYSTEM_MANDATORY_LABEL_ACE` 里。`icacls` 显示成：

   ```text
   Mandatory Label\Low Mandatory Level:(OI)(CI)(NW)
   ```

   `NW` = **NO_WRITE_UP** 策略（默认值），意思是"级别比我低的进程禁止写我"。
3. **判定顺序：MIC → DACL**。官方文档原话：完整性检查在 DACL 检查之前完成。
4. **默认策略 NO_WRITE_UP：只挡写，不挡读**。另有 `NO_READ_UP` / `NO_EXECUTE_UP`，默认不开。
5. **⚠️ 没有标记的对象按 Medium 处理**。这是最反直觉也最关键的一条：一个"没打过标记的老目录"对 Low 进程就是只读的。
6. **继承只发生在创建时**。新文件/目录继承父目录的标记；**改父目录的标记不会回溯已存在的子对象**。所以给仓库根目录打标记，并不等于整个仓库都能写了。
7. **进程创建取较低者**：`新进程级别 = min(用户级别, 可执行文件级别)`。管理员去跑一个 Low 级别的程序，新进程也是 Low。
8. **怎么设置**：`icacls <path> /setintegritylevel`。它写的是 SACL，需要 **WRITE_OWNER**（本机实测：目标上只有 Modify 权限时被拒，补 `(WO)` 后成功）或 SeSecurityPrivilege。

**完整性级别与 SID**（`icacls` / `whoami` 里看到的数字）

| 级别 | 完整性 SID | 谁拿到 | 说明 |
| --- | --- | --- | --- |
| Untrusted | `S-1-16-0` | 极少见 | 比 Low 还低，一般只用于特定进程 |
| **Low** | `S-1-16-4096` | 沙箱进程、浏览器渲染进程 | 只能写 Low 对象 |
| **Medium** | `S-1-16-8192` | 普通用户进程、**无标记对象** | 默认级别 |
| High | `S-1-16-12288` | 管理员提权进程 | 能写 Medium 及以下 |
| System | `S-1-16-16384` | 系统服务 | 最高 |

## 关键概念 / 术语

| 术语 | 是什么 |
| --- | --- |
| **MIC** | Mandatory Integrity Control，本文主题；**M**andatory 对应"你说了不算"，DACL 的 **D**iscretionary 是"所有者说了算" |
| **SACL / DACL** | 系统 ACL（审计 + 完整性标签） / 自主 ACL（谁有什么权限）。两者是对象安全描述符里不同的部分 |
| **ACE** | ACL 里的一条规则；完整性标记是 `SYSTEM_MANDATORY_LABEL_ACE` 这一种 |
| **NO_WRITE_UP（NW）** | 默认策略：低级别不能写高级别对象 |
| **无标记 = Medium** | 缺省按 Medium 处理，防止低完整性代码改到没打标记的老文件 |
| **标记继承** | 只在对象创建时继承，改了父级不回溯——**本仓这次踩的坑** |
| **WRITE_OWNER（WO）** | 改所有者的权限；打完整性标记需要它（实测） |
| **能力 / 包 SID** | `S-1-4-*`（本机 ACL 里 DSH 用的授权 SID）、`S-1-15-2-*`（AppContainer 包 SID）。它们属于 DACL 世界的授权，和完整性级别是两套机制 |

一句话把两套机制分开：

```text
能不能进这个门（谁被允许）  → DACL / ACE / 账户 SID   → icacls 里那些 "用户:(权限)"
我这一层能不能改这一层的东西 → 完整性级别 / 标记      → icacls 里那条 "Mandatory Label"
两者串联，MIC 先判。
```

## 代码示例

```powershell
# 1) 我是几级？（找 S-1-16-xxxx）
whoami /groups | findstr 'S-1-16'

# 2) 这个对象几级？（输出里没有 Mandatory Label 行 = 无标记 = 按 Medium 处理）
icacls 'D:\ai2all\projects\AgenticDev'

# 3) 实测能不能写（比推理可靠）
Set-Content 'D:\ai2all\projects\AgenticDev\notes\__p.tmp' -Value x
Remove-Item 'D:\ai2all\projects\AgenticDev\notes\__p.tmp'

# 4) 给已存在的子树补标记；新对象此后自动继承
icacls 'D:\ai2all\projects\AgenticDev' /setintegritylevel '(OI)(CI)Low' /t /c

# 5) 如果第 4 步报 Access is denied：先补 WRITE_OWNER 再试
$sid = '*' + ((whoami /user /fo csv | ConvertFrom-Csv)[0].SID)
icacls 'D:\ai2all\projects\AgenticDev' /grant "${sid}:(OI)(CI)(WO)" /t /c

# 6) 校验：Level 可用 L / M / H / S 或 Low / Medium / High / System
icacls 'D:\ai2all\projects\AgenticDev' | findstr 'Mandatory Label'
```

`icacls` 的权限简写（看输出时会用到）：简单权限 `F`(完全)、`M`(修改)、`RX`(读+执行)、`R`(只读)、`W`(只写)、`D`(删除)；高级权限 `WO`(改所有者)、`WDAC`(改权限)、`DC`(删子项)。

## 常见坑 & 注意事项

1. **"无标记"不是"无限制"**，是 Medium。老项目、老 `node_modules`、老 `.venv` 全都没标记，对 Low 进程一律只读。
2. **改父目录的标记不回溯已存在的子对象**。要么递归 `/t`，要么重建目录。这是本次坑的根。
3. **DACL 正常 ≠ 能写**。三道闸门串联：完整性级别 → 对象标记 → DACL。排查顺序就按这个来，别一上来就翻权限条目。
4. **打标记需要 WRITE_OWNER**。普通账号对"别人拥有的对象"没有这个权限（`node_modules` 若被管理员装过，owner 就是 `BUILTIN\Administrators`），于是 `/setintegritylevel` 报 `Access is denied`。
5. **管理员终端装的依赖归属会变**。`sudo npm install` / 管理员 PowerShell 里的 `npm install` 都会留下管理员属主的目录，之后普通进程和沙箱进程都改不动。装依赖永远用自己的身份。
6. **Low 标记是"全放行"**：任何低完整性进程都能写这些文件。沙箱工具的取舍就在这——隔离的是"别的进程"，不是"沙箱里的进程"。
7. **`icacls /reset` 不是修法**。它把 ACL 还原为"继承自父级"，会把根目录上的自定义授权项一起冲掉。
8. **变量为空会写垃圾 ACE**。`icacls /grant "${me}:..."` 里 `$me` 为空时，会写进一条指向 `S-1-5-32`（内建域本身）的无效权限项。先 `echo` 再执行。

## 我的理解 / 类比

<!-- 不要抄上面的定义。写"如果我要给同事讲清楚，我会怎么说"，并想一个你自己的类比 -->

提示（写完删掉）：

- DACL 是"**名单**"（谁被允许），完整性级别是"**楼层**"（你只能在自己这层及以下作业）；两道门先后过。
- 为什么要规定"**无标记按 Medium**"？如果反过来按 Low 处理，会出什么事？
- DSH 为什么要把工作区根目录打成 Low，而不是给沙箱进程提权？
- 你能想到你日常用过的哪个软件，明显用了这套机制？

（⬜ 待你填写）

## 参考链接

- [Mandatory Integrity Control mechanism（Microsoft Learn）](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control) —— 级别定义、NO_WRITE_UP、无标记按 Medium、进程创建取较低值
- [icacls（Microsoft Learn）](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls) —— `/setintegritylevel`、`/grant`、`/remove:g` 的语法与权限简写
- 本仓的实操记录见 [pitfalls.md 2026-10-24 那条](../pitfalls.md)
