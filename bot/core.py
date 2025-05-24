import os
import json
import asyncio
from pathlib import Path
import discord
from discord.ext import commands, tasks

# 定数
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
GOAL_FILE = DATA_DIR / 'goals.json'
TOKEN = os.getenv('DISCORD_TOKEN')
DEFAULT_CYCLE = [(50, '集中'), (10, '休憩')]

# ディレクトリとファイル準備
DATA_DIR.mkdir(exist_ok=True)
if not GOAL_FILE.exists():
    GOAL_FILE.write_text('{}', encoding='utf-8')

# Intents設定
intents = discord.Intents.default()
intents.message_content = True

# Bot起動
bot = commands.Bot(command_prefix='!', intents=intents)

# ヘルパー関数
def load_goals() -> dict:
    return json.loads(GOAL_FILE.read_text(encoding='utf-8'))

def save_goals(goals: dict):
    GOAL_FILE.write_text(json.dumps(goals, ensure_ascii=False, indent=2), encoding='utf-8')

# イベント
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

# コマンド: 疎通確認
@bot.command()
async def ping(ctx: commands.Context):
    await ctx.reply('Pong!')

# コマンド: もくもく会開始
@bot.command()
async def start(ctx: commands.Context, cycles: int = 1):
    """もくもく会を開始します。サイクル数を指定可能。"""
    await ctx.reply(f'✅ もくもく会を開始します！（サイクル: {cycles}回）')
    # バックグラウンド実行
    asyncio.create_task(run_cycles(ctx, cycles, DEFAULT_CYCLE))

async def run_cycles(ctx: commands.Context, cycles: int, pattern: list[tuple[int, str]]):
    for cycle in range(1, cycles + 1):
        for minutes, phase in pattern:
            await ctx.send(f'▶ サイクル{cycle}: **{phase}** を{minutes}分間開始します！')
            await asyncio.sleep(minutes * 60)
            await ctx.send(f'⏰ サイクル{cycle}: **{phase}** 終了！')
    await ctx.send('🎉 もくもく会がすべて終了しました！お疲れさまでした！')

# コマンド: 目標設定
@bot.command()
async def goal(ctx: commands.Context, *, text: str):
    """ユーザーの目標を設定します。"""
    goals = load_goals()
    goals[str(ctx.author.id)] = text
    save_goals(goals)
    await ctx.reply(f'🎯 目標を設定しました: 「{text}」')

# コマンド: 目標確認
@bot.command()
async def mygoal(ctx: commands.Context):
    """設定した目標を表示します。"""
    goals = load_goals()
    goal_text = goals.get(str(ctx.author.id))
    if goal_text:
        await ctx.reply(f'📌 あなたの目標: 「{goal_text}」')
    else:
        await ctx.reply('⚠️ 目標が未設定です。`!goal` で設定してください。')

# メインループ
async def main():
    await bot.start(TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Botを停止します…')