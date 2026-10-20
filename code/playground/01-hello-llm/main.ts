#! /usr/bin/env node

import OpenAI from 'openai';
import Anthropic from 'anthropic';

const client = new OpenAI({
    baseURL: process.env['OPENAI_BASE_URL'],
    apiKey: process.env['OPENAI_API_KEY'],
});

const response = await client.chat.completions.create({
    model: 'agnes-3.0-flash',
    messages: [{ content: 'Hello, OpenAI,how are you?', role: 'developer' }]
})

console.log(response.choices[0].message.content);


const stream = await client.chat.completions.create({
    model: 'agnes-3.0-flash',
    messages: [{ content: 'Hello, OpenAI,how are you?', role: 'developer' }],
    stream: true,
});

for await (const chunk of stream){
    const text = chunk.choices[0].delta?.content;
    if (text) process.stdout.write(text);
}