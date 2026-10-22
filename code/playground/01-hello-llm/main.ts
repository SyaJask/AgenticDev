#! /usr/bin/env node

import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import { createAgentSession } from "@earendil-works/pi-coding-agent";


export async function openai_client(client: OpenAI = new OpenAI(), model: string = 'agnes-3.0-flash') {
    // const client = new OpenAI({
    //     baseURL: process.env['OPENAI_BASE_URL'],
    //     apiKey: process.env['OPENAI_API_KEY'],
    // });
    const messages = [{ content: 'Hello, OpenAI,how are you?', role: 'system' }]

    // 发送请求
    const response = await client.chat.completions.create({
        model: model,
        messages: messages,
    })
    console.log(response.choices[0].message.content);

    // 发送流式请求
    const stream = await client.chat.completions.create({
        model: 'agnes-3.0-flash',
        messages: messages,
        stream: true,
    });
    for await (const chunk of stream){
        const text = chunk.choices[0].delta?.content;
        if (text) process.stdout.write(text);
    }
}


export async function anthropic_client(client: Anthropic = new Anthropic(), model: string = 'agnes-3.0-flash') {
    // const client = new Anthropic({
    //     baseURL: process.env['ANTHROPIC_BASE_URL'],
    //     apiKey: process.env['ANTHROPIC_API_KEY']
    // })
    const messages = [{role: 'user', content: 'Hello, Claude'}]

    // 发送请求
    const message = await client.messages.create({
        max_tokens: 1024,
        messages: messages,
        model: model,
    });
    console.log(message.content[0].text)

    // 发送流式请求
    const stream = await client.messages.create({
        max_tokens: 1024,
        messages: messages,
        model: model,
        stream: true,
    });
    for await (const chunk of stream){
        if (
            chunk.type === 'content_block_delta' &&
            chunk.delta.type === 'text_delta'
        ) {
            process.stdout.write(chunk.delta.text);
        }
    }
}


export async function pi_client(model: string = 'agnes-3.0-flash') {
    const { session } = await createAgentSession({
        model,
        thinkingLevel: 'high',
    });
    try {
        await session.prompt("What files are in the current directory?");
        console.log(session.getLastAssistantText());
    } finally {
        session.dispose();
    }
}

// openai_client()
anthropic_client()
pi_client()
