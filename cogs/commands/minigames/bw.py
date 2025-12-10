import discord
import requests
from discord.ext import commands
from discord import app_commands

BEDWARS_STATS = {
    "geral": {
        "bed_wars_total_games_played": "<a:wins:1348790119070564402> Partidas (Geral)",
        "bed_wars_total_beds_broken": "🛏 Camas Quebradas (Geral)",
        "bed_wars_total_beds_lost": "🛏 Camas Perdidas (Geral)",
        "bed_wars_total_wins": "<a:wins:1348790119070564402> Vitórias (Geral)",
        "bed_wars_total_losses": "<a:skull:1348799160979030096> Derrotas (Geral)",
        "bed_wars_total_deaths": "<a:skull:1348799160979030096> Mortes (Geral)",
        "bed_wars_total_kills": "<a:abates:1348799859603406979> Abates (Geral)", 
        "bed_wars_total_final_kills": "<a:abates:1348799859603406979> Abates Finais (Geral)",
        "bed_wars_total_winstreak": "<a:streak:1348793266358714521> WinStreak (Geral)",
        "bed_wars_experience": "<a:xp:1348792513300795504> XP em BedWars",
    },
    "solo": {
        "bed_wars_solo_games_played": "<a:wins:1348790119070564402> Partidas (Solo)",
        "bed_wars_solo_beds_broken": "🛏 Camas Quebradas (Solo)",
        "bed_wars_solo_beds_lost": "🛏 Camas Perdidas (Solo)",
        "bed_wars_solo_wins": "<a:wins:1348790119070564402> Vitórias (Solo)",
        "bed_wars_solo_losses": "<a:skull:1348799160979030096> Derrotas (Solo)",
        "bed_wars_solo_deaths": "<a:skull:1348799160979030096> Mortes (Solo)",
        "bed_wars_solo_kills": "<a:abates:1348799859603406979> Abates (Solo)", 
        "bed_wars_solo_final_kills": "<a:abates:1348799859603406979> Abates Finais (Solo)",
        "bed_wars_solo_winstreak": "<a:streak:1348793266358714521> WinStreak (Solo)",
    },
    "dupla": {
        "bed_wars_doubles_games_played": "<a:wins:1348790119070564402> Partidas (Dupla)",
        "bed_wars_doubles_beds_broken": "🛏 Camas Quebradas (Dupla)",
        "bed_wars_doubles_beds_lost": "🛏 Camas Perdidas (Dupla)",
        "bed_wars_doubles_wins": "<a:wins:1348790119070564402> Vitórias (Dupla)",
        "bed_wars_doubles_losses": "<a:skull:1348799160979030096> Derrotas (Dupla)",
        "bed_wars_doubles_deaths": "<a:skull:1348799160979030096> Mortes (Dupla)",
        "bed_wars_doubles_kills": "<a:abates:1348799859603406979> Abates (Dupla)", 
        "bed_wars_doubles_final_kills": "<a:abates:1348799859603406979> Abates Finais (Dupla)",
        "bed_wars_doubles_winstreak": "<a:streak:1348793266358714521> WinStreak (Dupla)",
        "bed_wars_experience": "<a:xp:1348792513300795504> XP em BedWars",
    },
    "trio": {
        "bed_wars_threesome_games_played": "<a:wins:1348790119070564402> Partidas (Trio)",
        "bed_wars_threesome_beds_broken": "🛏 Camas Quebradas (Trio)",
        "bed_wars_threesome_beds_lost": "🛏 Camas Perdidas (Trio)",
        "bed_wars_threesome_wins": "<a:wins:1348790119070564402> Vitórias (Trio)",
        "bed_wars_threesome_losses": "<a:skull:1348799160979030096> Derrotas (Trio)",
        "bed_wars_threesome_deaths": "<a:skull:1348799160979030096> Mortes (Trio)",
        "bed_wars_threesome_kills": "<a:abates:1348799859603406979> Abates (Trio)", 
        "bed_wars_threesome_final_kills": "<a:abates:1348799859603406979> Abates Finais (Trio)",
        "bed_wars_threesome_winstreak": "<a:streak:1348793266358714521> WinStreak (Trio)",
        "bed_wars_experience": "<a:xp:1348792513300795504> XP em BedWars",
    },
    "quarteto": {
        "bed_wars_group_games_played": "<a:wins:1348790119070564402> Partidas (Quarteto)",
        "bed_wars_group_beds_broken": "🛏 Camas Quebradas (Quarteto)",
        "bed_wars_group_beds_lost": "🛏 Camas Perdidas (Quarteto)",
        "bed_wars_group_wins": "<a:wins:1348790119070564402> Vitórias (Quarteto)",
        "bed_wars_group_losses": "<a:skull:1348799160979030096> Derrotas (Quarteto)",
        "bed_wars_group_deaths": "<a:skull:1348799160979030096> Mortes (Quarteto)",
        "bed_wars_group_kills": "<a:abates:1348799859603406979> Abates (Quarteto)", 
        "bed_wars_group_final_kills": "<a:abates:1348799859603406979> Abates Finais (Quarteto)",
        "bed_wars_group_winstreak": "<a:streak:1348793266358714521> WinStreak (Quarteto)",
        "bed_wars_experience": "<a:xp:1348792513300795504> XP em BedWars"
    }
}

class BedWars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bw", description="Veja estatísticas do BedWars.")
    @app_commands.describe(nick="Nome do jogador", modo="Modo de jogo")
    @app_commands.choices(modo=[
        app_commands.Choice(name="Total", value="geral"),
        app_commands.Choice(name="Solo", value="solo"),
        app_commands.Choice(name="Dupla", value="dupla"),
        app_commands.Choice(name="Trio", value="trio"),
        app_commands.Choice(name="Quarteto", value="quarteto"),
    ])
    async def bedwars(self, interaction: discord.Interaction, nick: str, modo: str):
        await interaction.response.defer()

        try:
            response = requests.get(f"https://api.flamemc.com.br/players/{nick}")
            response.raise_for_status()
            data = response.json()
            stats = data.get("accountStats", [])

            player_name = data.get("name", "Indisponível")
            avatar_url = f"https://mc-heads.net/avatar/{player_name}/256"

            embed = discord.Embed(
                title=f"🛏 BedWars ({modo.capitalize()}) - {player_name}",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=avatar_url)

            stat_keys = BEDWARS_STATS.get(modo, {})

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


async def setup(bot):
    await bot.add_cog(BedWars(bot))