import discord
import requests
from discord.ext import commands
from discord import app_commands

class HG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hg", description="Veja suas estatísticas de HG.")
    @app_commands.describe(nick="Nome do jogador")
    async def hg(self, interaction: discord.Interaction, nick: str):
        await interaction.response.defer()

        try:
            response = requests.get(f"https://api.flamemc.com.br/players/{nick}")
            response.raise_for_status()
            data = response.json()
            stats = data.get("accountStats", [])

            player_name = data.get("name", "Indisponível")
            avatar_url = f"https://mc-heads.net/avatar/{player_name}/256"

            embed = discord.Embed(
                title=f"🏹 HG - {player_name}",
                color=discord.Color.dark_green()
            )
            embed.set_thumbnail(url=avatar_url)

            stat_keys = {
                "hg_wins": "<a:wins:1348790119070564402> Vitórias ",
                "hg_kills": "<a:abates:1348799859603406979> Abates ",
                "hg_deaths": "<a:skull:1348799160979030096> Mortes ",
                "hg_coins": "<a:coin:1348794160513024122> Coins ",
                "hg_exp": "<a:xp:1348792513300795504> XP ",
            }

            for stat_name, label in stat_keys.items():
                value = "0"
                for stat in stats:
                    if stat["statsMap"]["name"] == stat_name:
                        value = stat["value"]
                        break
                embed.add_field(name=label, value=f"`•` {value}", inline=False)

            embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")
            await interaction.followup.send(embed=embed)

        except requests.exceptions.RequestException:
            await interaction.followup.send("Erro ao buscar os dados.", ephemeral=True)

# ⚠️ Fora da classe
async def setup(bot):
    await bot.add_cog(HG(bot))
