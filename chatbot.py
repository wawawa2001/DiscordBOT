import discord
from discord.ext import commands
import requests
import json
import asyncio
from settings import TOKEN, LLM_HOST, LLM_PORT, LLM_MODEL, CHATBOT_CH_ID

# Intentsの設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を受け取るために必要

# BOTのプレフィックスを設定
bot = commands.Bot(command_prefix='!', intents=intents)

class LLM_Model:
    def __init__(self):
        self.url = f"http://{LLM_HOST}:{LLM_PORT}/api/generate"

    async def send_prompt(self, prompt):
        data = {
            "model": LLM_MODEL,
            "prompt": prompt
        }

        queue = asyncio.Queue()

        async def generate():
            buffer = ""
            with requests.post(self.url, headers={"Content-Type": "application/json"}, data=json.dumps(data), stream=True) as response:
                if response.status_code == 200:
                    for chunk in response.iter_lines(decode_unicode=True):
                        if chunk:
                            try:
                                decoded_json = json.loads(chunk)
                                text = decoded_json.get("response", "")
                                buffer += text
                            except json.JSONDecodeError:
                                continue

                            i = 0
                            while i < len(buffer):
                                char = buffer[i]
                                if i + 3 < len(buffer) and buffer[i:i+4] == "\\n\\n":
                                    await queue.put("\n")
                                    i += 4
                                else:
                                    await queue.put(char)
                                    i += 1
                                await asyncio.sleep(0.05)
                            buffer = ""
                else:
                    await queue.put(f'Error: {response.status_code}')

            await queue.put(None)  # Sentinel value to indicate completion

        asyncio.create_task(generate())
        return queue

model = LLM_Model()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def chat(ctx, *, prompt: str):
    # コマンドの後に続く文字列を取得
    if int(ctx.channel.id) == CHATBOT_CH_ID:  # 特定のチャンネルIDを設定
        response = await ctx.send('Processing...')

        queue = await model.send_prompt(prompt)
        text = ""

        # 1文字ずつ追加する処理
        while True:
            char = await queue.get()
            if char is None:  # Sentinel value indicates completion
                break
            text += char
            # 一時的な更新をスキップ（必要ならこの部分を調整）
            if len(text) % 15 == 0:
                await response.edit(content=text)

        # 全体のテキストが完了した後に最終的にメッセージを更新
        await response.edit(content=text)

        await queue.put(None)  # Ensure queue is properly closed
    else:
        await ctx.send('This command can only be used in the specified channel.')

bot.run(TOKEN)
