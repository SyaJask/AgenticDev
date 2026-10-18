# 非流式 vs 流式（LLM 响应模式）

> 📌 机制与权衡部分由 AI 协助整理（客观内容）。**「我的理解 / 类比」一节必须你自己写** —— 那才是你的学习证据，抄来的不算。

---

## 一句话定义

- **非流式**：服务端把模型生成的全部内容**缓冲好**，一次性返回。
- **流式**：服务端**边生成边把增量片段推给客户端**。

## 它解决什么问题 / 为什么需要

前提认知：**模型本身就是逐 token 生成的。** 所以流式不是"特殊模式"，**非流式才是那个额外动作**（攒完再发）。

- 非流式的问题：用户必须等到全部生成完才看到第一个字，**感知延迟 = 总耗时**。
- 流式解决的是**感知延迟**（首字时间 TTFT）和**长任务的进度可见性**——**不是**总耗时。两者总耗时几乎相同。
- 在 Agent 场景（`LLM 调用 → 工具执行 → 再 LLM 调用` 的循环）里，没有流式，用户面对的是几十秒黑屏，会以为程序卡死。

## 核心机制 / 工作流程

**非流式**

1. 客户端发请求（不带 stream 参数）
2. 服务端等模型生成完整内容，全部攒在内存里
3. 一次性返回一个 JSON，正文在 `choices[0].message.content`
4. 客户端直接拿到完整字符串

**流式**

1. 客户端发请求，带 `stream: true`
2. 响应头变成 `Content-Type: text/event-stream` + `Transfer-Encoding: chunked`
3. 模型每生成一小段，服务端立刻写出一帧 SSE
4. 每帧正文在 `choices[0].delta.content`（**delta = 增量**，不是完整消息）
5. 最后一帧为 `data: [DONE]`
6. **客户端必须自己把增量拼成完整内容**

## 关键概念 / 术语

| 术语                                       | 含义                                                               |
| ------------------------------------------ | ------------------------------------------------------------------ |
| **TTFT**（Time To First Token）      | 从发请求到看到第一个 token 的时间。用户感知的"快慢"主要由它决定    |
| **tokens/sec**                       | 稳定生成阶段的吞吐速度                                             |
| **delta vs message**                 | 流式给增量 `delta`，非流式给完整 `message`                     |
| **SSE**                              | 流式的实际承载协议，单独一篇：`sse.md`                           |
| **`stream_options.include_usage`** | OpenAI 兼容接口在流式下**默认不回传 token 用量**，需显式开启 |

## 代码示例

```python
# 非流式：一次拿到完整内容
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
)
print(resp.choices[0].message.content)

# 流式：逐帧累积增量
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:                       # 很多帧的 content 是 None，必须判空
        print(delta, end="", flush=True)
```

## 常见坑 & 注意事项

1. **`delta.content` 常为 `None`** —— 首帧可能只带 `role`，末帧只带 `finish_reason`。不判空直接拼字符串会抛 `TypeError`。
2. **流式下拿不到 usage** —— 需加 `stream_options={"include_usage": True}`。做成本核算时必踩。
3. **代理把流式变回非流式** —— Nginx 默认缓冲整个响应体，表现成"卡很久然后一次性刷出来"。需关闭 `proxy_buffering`，或让上游发 `X-Accel-Buffering: no`。
4. **半截 JSON 无法解析** —— 结构化输出 / Function Calling 的参数生成，流到一半是残的。这类场景通常仍用非流式，或"边流边累积、攒完再 parse"。
5. **流出去就收不回** —— 无法像非流式那样"生成完 → 审核/脱敏 → 再展示"。安全敏感场景要把这个**时序问题**当成设计约束，而不是事后补。
6. **断流后的部分状态** —— 连接中途断了，界面上已有半段内容，要决定回滚、提示重试还是保留。

## 决策规则

| 场景                               | 选择           | 原因                   |
| ---------------------------------- | -------------- | ---------------------- |
| 面向用户的对话 / 内容生成          | **流式** | 感知延迟               |
| Agent 主循环、长任务               | **流式** | 需要透出进度           |
| 输出要被程序解析（JSON / FC 参数） | 非流式         | 半截 JSON 没法 parse   |
| 输出必须先过审核/脱敏再展示        | 非流式         | 流出去收不回           |
| 批处理、后台任务、无人在看         | 非流式         | 简单，且结果完整好处理 |
| 跑评测、批量生成数据集             | 非流式         | 便于统一处理和存储     |

**一句话记**：有人在等着看 → 流式；给机器吃 → 非流式。

## 我的理解 / 类比

<!-- 不要抄上面的定义。写"如果我要给同事讲清楚，我会怎么说"，并想一个你自己的类比 -->

（⬜ 待你填写 —— 不要跳过这一节）

在 completions 这一层，流式和非流式调用走的是同一个 POST /chat/completions 入口；区别是请求里是否要求服务端分段返回，以及 SDK 是否把响应包装成可迭代的流

- 非流式

```
create(...)
  → 组装请求参数
  → _post("/chat/completions", stream=False)
  → HTTP 客户端读取完整响应
  → 解析 JSON，构造成 ChatCompletion
  → create(...) 返回完整对象
```

- 流式

```
create(..., stream=True)
  → 请求参数中包含 stream=True
  → _post("/chat/completions", stream=True)
  → HTTP 客户端以流式方式接收响应
  → SDK 返回 Stream[ChatCompletionChunk]
  → 迭代时逐段解析 SSE 事件，产出 ChatCompletionChunk
```

## 参考链接

<!-- 待你补充，建议：OpenAI API 文档的 Streaming 一节、DeepSeek API 文档 -->
