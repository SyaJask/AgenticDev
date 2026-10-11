#! /usr/bin/env python3
# from langchain.chat_models import ChatOpenAI

import openai

# 加载 .env 文件
# from dotenv import load_dotenv
# load_dotenv()

# # 拿到 .env API Key
# import os
# base_url = os.getenv("OPENAI_BASE_URL")
# api_key = os.getenv("OPENAI_API_KEY")
# # 建client
# client = openai.OpenAI(base_url=base_url, api_key=api_key)

client = openai.OpenAI()

# 发送请求
response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ],
)

# 打印结果
print(response.choices[0].message.content)

# 发送流式请求
stream_response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ],
    stream=True
)

# 逐段打印模型返回的内容
for chunk in stream_response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)

