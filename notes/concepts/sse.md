# SSE（Server-Sent Events）

> 📌 协议部分由 AI 协助整理（客观内容）。**「我的理解 / 类比」一节必须你自己写**。

---

## 一句话定义

SSE 是一种基于**纯 HTTP** 的、**单向**（服务端 → 客户端）持续推送协议，用 `text/event-stream` 媒体类型承载。它是 LLM 流式输出的实际承载协议。

## 它解决什么问题 / 为什么需要

HTTP 是"一问一答"：客户端请求 → 服务端响应 → 结束。它**没有**"服务端主动多次推送"的原生能力。

打破它历史上主要有三种办法：

| 方案 | 方向 | 代价 |
|------|------|------|
| 轮询（polling） | 客户端反复问 | 延迟高、大量无用请求 |
| **SSE** | 服务端 → 客户端**单向** | 只能单向 |
| WebSocket | **双向** | 协议重、要升级握手、重连要自己实现 |

SSE 的定位：**比轮询实时，比 WebSocket 轻**。它完全跑在 HTTP 上（不升级协议），浏览器原生 `EventSource` 还自带断线重连。

## 核心机制 / 工作流程

1. 响应头：`Content-Type: text/event-stream`，配合 `Transfer-Encoding: chunked`（让响应体可以持续写入，不必写完才收尾）
2. 服务端按帧写入，**帧之间用空行分隔**
3. 帧的格式是 `字段名: 值`

**帧的字段**

| 字段 | 作用 |
|------|------|
| `data` | 载荷。可跨多行，多行会被拼成一条（行间补 `\n`） |
| `event` | 事件类型名，客户端可按类型分别监听；不写则触发默认的 `message` |
| `id` | 事件 ID。断线重连时客户端带 `Last-Event-ID` 请求头，服务端可据此补发 |
| `retry` | 重连等待毫秒数 |
| `:` 开头 | **注释**，客户端忽略。常用来定期发心跳，防止代理/网关掐掉空闲连接 |

**OpenAI 兼容接口的实际帧**

```
data: {"choices":[{"delta":{"content":"你"},"index":0}]}

data: {"choices":[{"delta":{"content":"好"},"index":0}]}

data: [DONE]
```

⚠️ **`data: [DONE]` 不是 SSE 标准**，是 OpenAI 的约定，用来告诉客户端"流结束了"。别的厂商可能用别的方式，或者干脆直接关闭连接。

## 关键概念 / 术语

- **单向 vs 双向**：SSE 只有服务端 → 客户端。客户端要发数据得另开一个普通请求（LLM 场景正好够用，因为你只需要把生成的文字推下来）
- **`[DONE]`**：OpenAI 约定的终止标记，**非** SSE 标准
- **Last-Event-ID / 自动重连**：`EventSource` 断线后默认自动重连，并带上最后收到的 `id`
- **心跳**：用注释行定期发送，防止中间设备判定连接空闲而断开
- **与 chunked 的关系**：chunked 提供"能持续写"的**传输能力**，SSE 提供"写了怎么分帧"的**格式约定**，两者配合使用

## 代码示例

**原始帧格式（服务端实际写出的内容）**

```
event: message
id: 1
data: {"content":"你"}

data: {"content":"好"}

: keep-alive

data: [DONE]

```

**浏览器端消费（EventSource）**

```javascript
const es = new EventSource("/api/chat");
es.onmessage = (e) => {
  if (e.data === "[DONE]") { es.close(); return; }
  render(e.data);            // 把这一片追加到页面上
};
es.onerror = () => { /* EventSource 会自动重连 */ };
```

**Python 侧消费（httpx 流式读）**

```python
with httpx.stream("POST", url, json=payload, headers=headers) as r:
    for line in r.iter_lines():
        if not line or not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        # json.loads(data) ...
```

**用 curl 肉眼观察（调试利器）**

```bash
curl -N -X POST https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","stream":true,"messages":[{"role":"user","content":"hi"}]}'
```

`-N` 关闭 curl 自己的缓冲，能直接看到帧一帧帧刷出来。

## 常见坑 & 注意事项

1. **代理/网关缓冲 → "假流式"** ⚠️ 最常见。Nginx 默认缓冲整个响应体，表现是"卡很久然后一次性刷出来"。需关闭 `proxy_buffering`，或让上游发 `X-Accel-Buffering: no`。
2. **压缩中间件干扰**：gzip 可能让分帧边界变糊，某些代理会因此攒批。排查流式问题时值得怀疑。
3. **HTTP/1.1 连接数上限**：浏览器对同一域名默认只开 6 个连接，而一个 SSE 会长期占住一个。多开几个标签页容易耗尽。HTTP/2 多路复用能缓解。
4. **重连可能导致重复**：自动重连会重发请求。服务端要考虑幂等，或用 `Last-Event-ID` 补发，否则可能**重复生成内容（既费钱又重复输出）**。
5. **只能单向**：客户端要上传内容必须走另一个请求。
6. **不是所有中间件都友好**：SSE 是纯文本协议，用 `curl -N` 能直接验伪，比读日志快得多。

## 我的理解 / 类比

<!-- 不要抄上面的定义。写"如果我要给同事讲清楚，我会怎么说"，并想一个你自己的类比 -->

（⬜ 待你填写）

## 参考链接

<!-- 待你补充，建议：MDN 的 Server-sent events、HTML Living Standard 中 SSE 一节 -->
