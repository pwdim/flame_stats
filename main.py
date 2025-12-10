import discord
from discord.ext import commands
import requests
from discord import app_commands
import logging
import json
import asyncio
import sys

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['TOKEN']
PREFIX = config['PREFIX']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True 

bot = commands.Bot(command_prefix=PREFIX, intents=intents) 

@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} conectado!")
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ {len(synced)} comandos sincronizados.")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos slash: {e}")

    guild_names = [guild.name for guild in bot.guilds]
    logger.info(f"🚀 Bot iniciado em {len(bot.guilds)} servidores:")
    for guild_name in guild_names:
        logger.info(f"   - {guild_name}")

@bot.event
async def on_command_completion(ctx):
    user_id = ctx.author.id
    user_name = ctx.author.display_name
    channel_id = ctx.channel.id
    channel_name = ctx.channel.name
    
    guild_id = ctx.guild.id if ctx.guild else "DM"
    guild_name = ctx.guild.name if ctx.guild else "Mensagem Direta"
    
    command_name = ctx.command.qualified_name
    
    logger.info(f"Comando de Prefixo Executado - Usuário: {user_name} (ID: {user_id}), Canal: {channel_name} (ID: {channel_id}), Servidor: {guild_name} (ID: {guild_id}), Comando: {command_name}")

@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command):
    user_id = interaction.user.id
    user_name = interaction.user.display_name
    
    channel_id = interaction.channel.id if interaction.channel else "ID Desconhecido"
    
    if isinstance(interaction.channel, discord.TextChannel):
        channel_name = interaction.channel.name
    elif isinstance(interaction.channel, discord.DMChannel):
        channel_name = "Mensagem Direta"
    else:
        channel_name = "Canal Desconhecido"
    
    guild_id = interaction.guild.id if interaction.guild else "DM"
    guild_name = interaction.guild.name if interaction.guild else "Mensagem Direta"
    
    command_name = command.qualified_name
    
    logger.info(f"Comando Slash Executado - Usuário: {user_name} (ID: {user_id}), Canal: {channel_name} (ID: {channel_id}), Servidor: {guild_name} (ID: {guild_id}), Comando: {command_name}")

@bot.event
async def on_guild_join(guild):
    owner_info = f"Dono: {guild.owner.name} (ID: {guild.owner.id})" if guild.owner else "Dono Desconhecido"
    logger.info(f"➕ Bot entrou no servidor: {guild.name} (ID: {guild.id}). Membros: {guild.member_count}. {owner_info}")

@bot.event
async def on_guild_remove(guild):
    logger.info(f"➖ Bot saiu do servidor: {guild.name} (ID: {guild.id}).")

@bot.event
async def on_member_join(member):
    if member.guild:
        logger.info(f"👤 Membro {member.display_name} (ID: {member.id}) entrou no servidor: {member.guild.name} (ID: {member.guild.id}).")
    else:
        logger.info(f"👤 Membro {member.display_name} (ID: {member.id}) entrou em um servidor desconhecido (sem guild associada).")

async def load_cogs():
    await bot.load_extension("cogs.commands.moderation.allowed_channels")
    await bot.load_extension("cogs.commands.general.info")
    await bot.load_extension("cogs.commands.general.status")
    await bot.load_extension("cogs.commands.general.invite")
    await bot.load_extension("cogs.commands.leaderboards.competitive")
    await bot.load_extension("cogs.commands.leaderboards.league")
    await bot.load_extension("cogs.commands.leaderboards.arena")
    await bot.load_extension("cogs.commands.leaderboards.fps")
    await bot.load_extension("cogs.commands.leaderboards.hungergames")
#    await bot.load_extension("cogs.commands.leaderboards.academy")
    
async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())