import discord
import requests
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('bot.log', encoding='utf-8')])


class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Exibe o status atual do servidor.")
    async def status(self, interaction: discord.Interaction):
        # Log do comando
        logging.info(f"Comando 'status' usado por {interaction.user.name} ({interaction.user.id}) no servidor {interaction.guild.name} ({interaction.guild.id}) no canal {interaction.channel.name} ({interaction.channel.id}).")

        # Informa ao Discord que o bot está processando a interação
        await interaction.response.defer()

        # URL da API
        api_url = "https://mcstatus.snowdev.com.br/api/query/v3/flamemc.com.br"
        
        try:
            # Fazendo a requisição para a API
            response = requests.get(api_url)
            data = response.json()

            # Verificar se o servidor está online através dos dados essenciais
            players_online = data.get("players_online")
            max_players = data.get("max_players")
            ping = data.get("ping")
            version = data.get("version")
            favicon = "https://mcstatus.snowdev.com.br/api/favicon/flamemc.com.br/favicon.png"

            if players_online is None or max_players is None or ping is None:
                # Se algum dado importante estiver faltando, considera o servidor offline
                embed_offline = discord.Embed(
                    title="❌ Servidor Offline!",
                    description="O servidor está offline no momento. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
                embed_offline.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")
                await interaction.followup.send(embed=embed_offline)
                return  # Finaliza o comando

            # Se chegou aqui, o servidor está online
            embed = discord.Embed(title="<:flame:1348790292408569876> Servidor Online!", color=discord.Color.green())
            embed.set_thumbnail(url=favicon)
            embed.add_field(name="Jogadores:", value=f"{players_online}/{max_players}", inline=True)
            embed.add_field(name="Ping:", value=f"{ping} ms", inline=True)
            embed.add_field(name="Versão:", value=version if version else "Indisponível", inline=True)
            embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")

            # Envia a resposta final
            await interaction.followup.send(embed=embed)

        except requests.exceptions.RequestException as e:
            await interaction.followup.send(f"Erro ao consultar a API: {e}", ephemeral=True)
            logging.error(f"Erro ao consultar a API: {e}")
        except KeyError:
            await interaction.followup.send("Erro ao processar os dados da API.", ephemeral=True)
            logging.error("Erro ao processar os dados da API.")


async def setup(bot):
    await bot.add_cog(StatusCog(bot))
