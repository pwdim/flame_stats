import discord
import requests
from discord.ext import commands
from discord import app_commands

SOUP_STATS = {
    "duels_soup_wins": "<a:wins:1348790119070564402> Vitórias em Sopa",
    "duels_soup_kills": "<a:abates:1348799859603406979> Abates em Sopa",
    "duels_soup_defeats": "<a:skull:1348799160979030096> Mortes em Sopa",
    "duels_soup_streak": "<a:streak:1348793266358714521> KillStreak em Sopa",
    "duels_soup_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em Sopa",
}

class Soup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sopa", description="Veja suas estatísticas do modo Sopa.")
    @app_commands.describe(nick="Nome do jogador")
    async def sopa(self, interaction: discord.Interaction, nick: str):
        await interaction.response.defer()

        try:
            response = requests.get(f"https://api.flamemc.com.br/players/{nick}")
            response.raise_for_status()
            data = response.json()
            stats = data.get("accountStats", [])

            player_name = data.get("name", "Indisponível")
            avatar_url = f"https://mc-heads.net/avatar/{player_name}/256"

            embed = discord.Embed(
                title=f"🥣 Sopa - {player_name}",
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url=avatar_url)

            for stat_name, label in SOUP_STATS.items():
                value = "0"
                for stat in stats:
                    if stat["statsMap"]["name"] == stat_name:
                        value = stat["value"]
                        break
                embed.add_field(name=label, value=f"`\u2022` {value}", inline=False)

            embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")
            await interaction.followup.send(embed=embed)

        except requests.exceptions.RequestException:
            await interaction.followup.send("Erro ao buscar os dados.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Soup(bot))