import os
import json
import asyncio
import discord
from discord.ext import commands

GOAL_FILE = 'data/goals.json'

TOKEN = os.getenv('DISCORD_TOKEN')
DEFAULT_CYCLE = [(50, '集中'), (10, '休憩')]

# Intentsの設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を取得するために必要

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def start(ctx, cycles: int = 1):
    await ctx.send(f'✅ もくもく会を開始します！（サイクル: {cycles}回）')
    bot.loop.create_task(run_cycles(ctx, cycles, DEFAULT_CYCLE))

async def run_cycles(ctx, cycles, pattern):
    for cycle in range(1, cycles + 1):
        for minutes, phase in pattern:
            await ctx.send(f'▶ サイクル{cycle}: **{phase}** を{minutes}分間開始します！')
            await asyncio.sleep(minutes * 60)
            await ctx.send(f'⏰ サイクル{cycle}: **{phase}** 終了！')
    await ctx.send('🎉 もくもく会がすべて終了しました！お疲れさまでした！')

def load_goals():
    if os.path.exists(GOAL_FILE):
        with open(GOAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_goals(goals):
    with open(GOAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(goals, f, ensure_ascii=False, indent=2)

@bot.command()
async def goal(ctx, *, text: str):
    """ユーザーの目標を設定します。"""
    goals = load_goals()
    user_id = str(ctx.author.id)
    goals[user_id] = text
    save_goals(goals)
    await ctx.reply(f'🎯 目標を設定しました: 「{text}」')

@bot.command()
async def mygoal(ctx):
    """設定した目標を表示します。"""
    goals = load_goals()
    user_id = str(ctx.author.id)
    goal = goals.get(user_id)
    if goal:
        await ctx.reply(f'📌 あなたの目標: 「{goal}」')
    else:
        await ctx.reply('⚠️ まだ目標が設定されていません。`!goal` コマンドで設定してください。')

async def main():
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
