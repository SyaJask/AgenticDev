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
