#! /usr/bin/env python3
# from langchain.chat_models import ChatOpenAI

import os

from loguru import logger

from openai import OpenAI
from anthropic import Anthropic
from pi_agent import PiClient, PiRunError

# from dotenv import load_dotenv
# load_dotenv()  # 加载 .env 文件


def openai_client(client = OpenAI(), MODEL_NAME = "agnes-3.0-flash"):
    # base_url = os.environ.get("OPENAI_BASE_URL")
    # api_key = os.environ.get("OPENAI_API_KEY")  # 拿到 .env API Key
    # MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME")  # 拿到 .env MODEL_NAME
    # client = OpenAI(base_url=base_url, api_key=api_key)  # 建client

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, OpenAI,how are you?"},
    ]

    # 发送请求
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )
    # 打印结果
    print(response.choices[0].message.content)

    # 发送流式请求
    stream_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=True
    )
    # 逐段打印模型返回的内容
    for chunk in stream_response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()  # 换行

    # 也可以使用 with 语法来处理流式请求
    with client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=True
    ) as stream:
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print()  # 换行


def anthropic_client(client = Anthropic(), MODEL_NAME = "agnes-3.0-flash"):
    # base_url = os.environ.get("ANTHROPIC_BASE_URL")
    # api_key = os.environ.get("ANTHROPIC_API_KEY")  # 拿到 .env API Key
    # client = Anthropic(base_url=base_url, api_key=api_key)  # 建client

    # 发送请求
    message = client.messages.create(
        max_tokens=1024,
        model=MODEL_NAME,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Hello, Claude, how are you?"},],
    )
    # 打印结果
    print(message.content[0].text)

    # 发送流式请求
    stream_response = client.messages.create(
        max_tokens=1024,
        model=MODEL_NAME,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Hello, Claude, how are you?"},],
        stream=True
    )
    # 逐段打印模型返回的内容
    for stream in stream_response:
        # event.type 可能是 message_start / content_block_start /
        #                  content_block_delta / content_block_stop / message_delta / message_stop
        if stream.type == "content_block_delta" and stream.delta.type == "text_delta":
            print(stream.delta.text, end="", flush=True)
    print()  # 换行

    # 也可以使用 with 语法来处理流式请求
    with client.messages.stream(
        max_tokens=1024,
        model=MODEL_NAME,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Hello, Claude, how are you?"},],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        print()  # 换行


def pi_client(client = PiClient(), provider = None, MODEL_NAME = "agnes-3.0-flash"):
    # 发送请求
    with PiClient(provider=provider, model=MODEL_NAME) as client:
        result = client.run("Hello, Pi, how are you?")
        print(result)

    # 发送流式请求
    with PiClient(provider=provider, model=MODEL_NAME) as client:
        with client.stream("Hello, Pi, how are you?") as stream:
            for text in stream:
                print(text.text_delta, end="", flush=True)
            result = stream.result()
        print(result.stop_reason)


if __name__ == "__main__":
    # openai_client()
    # anthropic_client()
    pi_client(provider=os.environ.get("OPENAI_BASE_URL"))