#! /usr/bin/env python3
# from langchain.chat_models import ChatOpenAI

import os
import asyncio
from typing import List

from loguru import logger

from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from anthropic import Anthropic
from pi_agent import PiClient, AsyncPiClient, PiRunError

# from dotenv import load_dotenv
# load_dotenv()  # 加载 .env 文件


def openai_client(client = OpenAI(), model = "agnes-3.0-flash"):
    # base_url = os.environ.get("OPENAI_BASE_URL")
    # api_key = os.environ.get("OPENAI_API_KEY")  # 拿到 .env API Key
    # model = os.environ.get("OPENAI_MODEL")  # 拿到 .env model
    # client = OpenAI(base_url=base_url, api_key=api_key)  # 建client

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, OpenAI,how are you?"},
    ]

    # 发送请求
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    # 打印结果
    print(response.choices[0].message.content)

    # 发送流式请求
    stream_response = client.chat.completions.create(
        model=model,
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
        model=model,
        messages=messages,
        stream=True
    ) as stream:
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print()  # 换行


async def async_openai_client(client = AsyncOpenAI(), model = "agnes-3.0-flash"):
    class Step(BaseModel):
        explanation: str
        output: str


    class MathResponse(BaseModel):
        steps: List[Step]
        final_answer: str

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, OpenAI,1024*1024?"},
    ]

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
    )
    print(response.choices[0].message.content)

    stream_response = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    async for chunk in stream_response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()

    response = await client.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=MathResponse,
    )
    message = response.choices[0].message
    if message.parsed:
        print(message.parsed.steps)
        print("answer: ", message.parsed.final_answer)

    
    async with client.chat.completions.stream(
        model=model,
        messages=messages,
        response_format=MathResponse,
    ) as stream:
        async for event in stream:
            if event.type == "content.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "content.done":
                print("\nparsed:", event.parsed)


def anthropic_client(client = Anthropic(), model = "agnes-3.0-flash"):
    # base_url = os.environ.get("ANTHROPIC_BASE_URL")
    # api_key = os.environ.get("ANTHROPIC_API_KEY")  # 拿到 .env API Key
    # client = Anthropic(base_url=base_url, api_key=api_key)  # 建client

    # 发送请求
    message = client.messages.create(
        max_tokens=1024,
        model=model,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Hello, Claude, how are you?"},],
    )
    # 打印结果
    print(message.content[0].text)

    # 发送流式请求
    stream_response = client.messages.create(
        max_tokens=1024,
        model=model,
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
        model=model,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Hello, Claude, how are you?"},],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        print()  # 换行


def pi_client(provider = "agnes", model = "agnes-3.0-flash"):
    # https://pypi.org/project/pi-agent-python-sdk/#1
    # 发送请求
    with PiClient(provider=provider, model=model) as client:
        try:
            print(client.run("hi").text)
        except PiRunError as exc:
            print("stop_reason:", exc.result.stop_reason)

    # 发送流式请求
    with PiClient(provider=provider, model=model) as client:
        levels = client.get_available_thinking_levels()
        # print("available:", levels)
        if "high" in levels:
            client.set_thinking_level("high")
        # print(client.get_state()["thinkingLevel"])
        # print(client.get_state()["sessionId"])
        # print(client["provider"], client["id"])
        # selected = client.set_model("agnes", "agnes-2.5-flash")
        with client.stream("Hello, Pi, how are you?") as stream:
            for event in stream:
                if event.text_delta is not None:
                    print(event.text_delta, end="", flush=True)
            result = stream.result()
        print(f"\nStop reason: {result.stop_reason}")


async def async_pi_client(provider = "agnes", model = "agnes-3.0-flash") -> None:
    async with AsyncPiClient(provider=provider, model=model) as client:
        result = await client.run("Hello, Pi, how are you?")
        print(result.text)


if __name__ == "__main__":
    # openai_client()
    asyncio.run(async_openai_client())
    # anthropic_client()
    # pi_client()
    # asyncio.run(async_pi_client())