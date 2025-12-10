import discord
from discord.ext import commands
from discord import app_commands
import json
import os

ALLOWED_CHANNELS_FILE = 'data/allowed_channels.json'

class AllowedChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channel_ids = self.load_allowed_channels()

    def load_allowed_channels(self):
        if not os.path.exists('data'):
            os.makedirs('data')

        if os.path.exists(ALLOWED_CHANNELS_FILE):
            with open(ALLOWED_CHANNELS_FILE, 'r') as f:
                try:
                    
                    return json.load(f)
                except json.JSONDecodeError:
                    return {} 
        return {} 

    def save_allowed_channels(self):
        with open(ALLOWED_CHANNELS_FILE, 'w') as f:
            json.dump(self.allowed_channel_ids, f, indent=4)

    channels_group = app_commands.Group(name="canais", description="Gerencia os canais onde os comandos do bot podem ser usados.")

    @channels_group.command(name="adicionar", description="Adiciona um canal à lista de canais permitidos para os comandos do bot.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(canal="O canal a ser adicionado.")
    async def add_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        guild_id = str(interaction.guild_id)
        if guild_id not in self.allowed_channel_ids:
            self.allowed_channel_ids[guild_id] = []

        if canal.id in self.allowed_channel_ids[guild_id]:
            await interaction.response.send_message(f"O canal {canal.mention} já está na lista de canais permitidos para este servidor.", ephemeral=True)
            return

        self.allowed_channel_ids[guild_id].append(canal.id)
        self.save_allowed_channels()
        await interaction.response.send_message(f"O canal {canal.mention} foi adicionado à lista de canais permitidos para este servidor.", ephemeral=False)

    @channels_group.command(name="remover", description="Remove um canal da lista de canais permitidos para os comandos do bot.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(canal="O canal a ser removido.")
    async def remove_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        guild_id = str(interaction.guild_id)
        if guild_id not in self.allowed_channel_ids or canal.id not in self.allowed_channel_ids[guild_id]:
            await interaction.response.send_message(f"O canal {canal.mention} não está na lista de canais permitidos para este servidor.", ephemeral=True)
            return

        self.allowed_channel_ids[guild_id].remove(canal.id)
        self.save_allowed_channels()
        await interaction.response.send_message(f"O canal {canal.mention} foi removido da lista de canais permitidos para este servidor.", ephemeral=False)

    @channels_group.command(name="lista", description="Exibe a lista de canais permitidos para os comandos do bot.")
    async def list_channels(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id)
        
        
        guild_allowed_channels = self.allowed_channel_ids.get(guild_id, [])

        if not guild_allowed_channels:
            await interaction.response.send_message("Não há canais configurados na lista de canais permitidos para este servidor.", ephemeral=True)
            return

        channel_mentions = []
        for channel_id in guild_allowed_channels:
            channel = self.bot.get_channel(channel_id)
            if channel:
                channel_mentions.append(channel.mention)
            else:

                pass 

        if not channel_mentions:
            await interaction.response.send_message("Não consegui encontrar os canais configurados para este servidor. Eles podem ter sido excluídos.", ephemeral=True)
            return

        channels_text = "\n".join(channel_mentions)
        embed = discord.Embed(
            title="Canais Permitidos (Este Servidor)",
            description=f"Os comandos do bot só podem ser usados nos seguintes canais neste servidor:\n{channels_text}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AllowedChannels(bot))