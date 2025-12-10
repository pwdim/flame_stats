import discord
import requests
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('bot.log', encoding='utf-8')])

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Exibe o status atual do servidor.")
    async def status(self, interaction: discord.Interaction):
        should_be_ephemeral = False
        allowed_channels_cog = self.bot.get_cog("AllowedChannels")
        
        if allowed_channels_cog and interaction.guild: 
            guild_id_str = str(interaction.guild_id)
            
            if guild_id_str in allowed_channels_cog.allowed_channel_ids and \
               allowed_channels_cog.allowed_channel_ids[guild_id_str] and \
               interaction.channel_id not in allowed_channels_cog.allowed_channel_ids[guild_id_str]:
                
                should_be_ephemeral = True
        
        await interaction.response.defer(ephemeral=should_be_ephemeral)

        logging.info(f"Comando 'status' usado por {interaction.user.name} ({interaction.user.id}) no servidor {interaction.guild.name} ({interaction.guild.id}) no canal {interaction.channel.name} ({interaction.channel.id}).")

        api_url = "https://mcstatus.snowdev.com.br/api/query/v3/flamemc.com.br"
        
        try:
            response = requests.get(api_url)
            data = response.json()

            players_online = data.get("players_online")
            max_players = data.get("max_players")
            ping = data.get("ping")
            version = data.get("version")
            favicon = "https://mcstatus.snowdev.com.br/api/favicon/flamemc.com.br/favicon.png"

            if players_online is None or max_players is None or ping is None:
                embed_offline = discord.Embed(
                    title="❌ Erro ao pingar o servidor!",
                    description="O servidor pode estar offline no momento. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
                embed_offline.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")
                await interaction.followup.send(embed=embed_offline, ephemeral=should_be_ephemeral)
                return

            embed = discord.Embed(title="<:flame:1348790292408569876> Servidor Online!", color=discord.Color.green())
            embed.set_thumbnail(url=favicon)
            embed.add_field(name="Jogadores:", value=f"{players_online}/{max_players}", inline=True)
            embed.add_field(name="Ping:", value=f"{ping} ms", inline=True)
            embed.add_field(name="Versão:", value=version if version else "Indisponível", inline=True)
            embed.add_field(name="IPs: ", value="", inline=False)
            embed.add_field(name="", value="- flamemc.com.br", inline=False)
            embed.add_field(name="", value="- jogar.flamemc.com.br", inline=False)
            embed.add_field(name="", value="- pwdim.com", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")

            await interaction.followup.send(embed=embed, ephemeral=should_be_ephemeral)

        except requests.exceptions.RequestException as e:
            await interaction.followup.send(f"Erro ao consultar a API: {e}", ephemeral=True)
            logging.error(f"Erro ao consultar a API: {e}")
        except KeyError:
            await interaction.followup.send("Erro ao processar os dados da API.", ephemeral=True)
            logging.error("Erro ao processar os dados da API.")

async def setup(bot):
    await bot.add_cog(StatusCog(bot))