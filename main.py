import discord
from discord.ext import commands
import discord
import requests
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

import json

# Carregar configurações do arquivo config.json
with open('config.json', 'r') as f:
    config = json.load(f)

# Usar o token e prefixo carregados do arquivo
TOKEN = config['TOKEN']
PREFIX = config['PREFIX']

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('bot.log', encoding='utf-8')])

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} conectado!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados.")
    except Exception as e:
        print(f"Erro ao sincronizar: {e}")

# Carregar o cog
async def load_cogs():
    await bot.load_extension("cogs.commands.mcstats")
    await bot.load_extension("cogs.commands.status")
    await bot.load_extension("cogs.commands.hg")
    await bot.load_extension("cogs.commands.fl")
    await bot.load_extension("cogs.commands.cxc")
#    await bot.load_extension("cogs.commands.bw")
#    await bot.load_extension("cogs.commands.sopa")
    await bot.load_extension("cogs.commands.leaderboard_hg")
    await bot.load_extension("cogs.commands.leaderboard_cxc")
    await bot.load_extension("cogs.commands.leaderboard_fl")
    await bot.load_extension("cogs.commands.leaderboard_pvp")
#    await bot.load_extension("cogs.leaderboard")
    
import asyncio
asyncio.run(load_cogs())

bot.run(TOKEN)
