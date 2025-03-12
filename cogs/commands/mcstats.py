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

def format_date_time(date_time):
    if not date_time:
        return "Indisponível"
    from datetime import datetime
    dt = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y %H:%M")

game_modes_config = {
    "arena": {
        "title": "🏟 Arena",
        "stats": {
            "pvp_arena_kills": "<a:abates:1348799859603406979> Abates na Arena",
            "pvp_arena_deaths": "<a:skull:1348799160979030096> Mortes na Arena",
            "pvp_arena_streak": "<a:streak:1348793266358714521> KillStreak na Arena",
            "pvp_arena_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak na Arena",
            "pvp_coins": "<a:coin:1348794160513024122> Coins no KitPvp",
            "pvp_exp": "<a:xp:1348792513300795504> XP no KitPvp",
        }
    },
    "fps": {
        "title": "🔫 FPS",
        "stats": {
            "pvp_fps_kills": "<a:abates:1348799859603406979> Abates em FPS",
            "pvp_fps_deaths": "<a:skull:1348799160979030096> Mortes em FPS",
            "pvp_fps_streak": "<a:streak:1348793266358714521> KillStreak em FPS",
            "pvp_fps_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em FPS",
            "pvp_coins": "<a:coin:1348794160513024122> Coins em KitPvp",
            "pvp_exp": "<a:xp:1348792513300795504> XP em KitPvp",
        }
    },
    "league": {
        "title": "🔥 FlameLeague",
        "stats": {
            "league_wins": "<a:wins:1348790119070564402> Vitórias em League",
            "league_kills": "<a:abates:1348799859603406979> Abates em League",
            "league_deaths": "<a:skull:1348799160979030096> Mortes em League",
            "league_coins": "<a:coin:1348794160513024122> Coins em League",
            "league_exp": "<a:xp:1348792513300795504> XP em League",
        }
    },
    "competitive": {
        "title": "🕹 CxC",
        "stats": {
            "competitive_wins": "<a:wins:1348790119070564402> Vitórias em Cxc",
            "competitive_defeats": "<a:skull:1348799160979030096> Derrotas em CxC",
            "competitive_kills": "<a:abates:1348799859603406979> Abates em CxC",
            "competitive_deaths": "<a:skull:1348799160979030096> Mortes em CxC",
            "competitive_coins": "<a:coin:1348794160513024122> Coins em CxC",
            "competitive_exp": "<a:xp:1348792513300795504> XP em CxC",
        }
    },
    "hg": {
        "title": "🏹 Hardcore Games",
        "stats": {
            "hg_wins": "<a:wins:1348790119070564402> Vitórias em HG",
            "hg_kills": "<a:abates:1348799859603406979> Abates em HG",
            "hg_deaths": "<a:skull:1348799160979030096> Mortes em HG",
            "hg_coins": "<a:coin:1348794160513024122> Coins em HG",
            "hg_exp": "<a:xp:1348792513300795504> XP em HG",
        }
    },
    "bedwars": {
        "title": "🛏 BedWars",
        "stats": {
            "bed_wars_total_games_played": "Partidas (Total)",
            "bed_wars_total_wins": "<a:wins:1348790119070564402> Vitórias em BedWars",
            "bed_wars_total_wins": "<a:wins:1348790119070564402> Derrotas em BedWars",
            "bed_wars_total_final_kills": "<a:abates:1348799859603406979> Abates Finais em BedWars",
            "bed_wars_total_deaths": "<a:skull:1348799160979030096> Mortes em BedWars",
            "bed_wars_experience": "<a:xp:1348792513300795504> XP em BedWars",
        }
    },
    "gladiator": {
        "title": "⛓️ Gladiator",
        "stats": {
            "duels_gladiator_wins": "<a:wins:1348790119070564402> Vitórias em Gladiator",
            "duels_gladiator_kills": "<a:abates:1348799859603406979> Abates em Gladiator",
            "duels_gladiator_defeats": "<a:skull:1348799160979030096> Mortes em Gladiator",
            "duels_gladiator_streak": "<a:streak:1348793266358714521> KillStreak em Gladiator",
            "duels_gladiator_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em Gladiator",
        }
    },
    "simulator": {
        "title": "⛰ Simulator",
        "stats": {
            "duels_simulator_wins": "<a:wins:1348790119070564402> Vitórias em Simulator",
            "duels_simulator_kills": "<a:abates:1348799859603406979> Abates em Simulator",
            "duels_simulator_defeats": "<a:skull:1348799160979030096> Mortes em Simulator",
            "duels_simulator_streak": "<a:streak:1348793266358714521> KillStreak em Simulator",
            "duels_simulator_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em Simulator",
        }
    },
    "sopa": {
        "title": "🥣 Sopa",
        "stats": {
            "duels_soup_wins": "<a:wins:1348790119070564402> Vitórias em Sopa",
            "duels_soup_kills": "<a:abates:1348799859603406979> Abates em Sopa",
            "duels_soup_defeats": "<a:skull:1348799160979030096> Mortes em Sopa",
            "duels_soup_streak": "<a:streak:1348793266358714521> KillStreak em Sopa",
            "duels_soup_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em Sopa",
        }
    },   
    "bridge": {
        "title": "🌉 The Bridge",
        "stats": {
            "duels_bridge_wins_solo": "<a:wins:1348790119070564402> Vitórias em The Bridge (Solo)",
            "duels_bridge_defeats_solo": "<a:skull:1348799160979030096> Derrotas emThe Bridge (Solo)",
            "duels_bridge_kills_solo": "<a:abates:1348799859603406979> Abates em The Bridge (Solo)",
            "duels_bridge_deaths_solo": "<a:skull:1348799160979030096> Mortes em The Bridge (Solo)",
            "duels_bridge_streak_solo": "<a:streak:1348793266358714521> KillStreak em The Bridge (Solo)",
            "duels_bridge_best_streak_solo": "<a:streak:1348793098175647764> Melhor KillStreak em The Bridge (Solo)",
            "duels_bridge_points_solo": "<a:xp:1348792513300795504> Pontos em The Bridge (Solo)",
        }
    },      
    
}

class McStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mcstats", description="Busca informações de um jogador no FlameMC.")
    @app_commands.describe(nick="Nome do jogador no Minecraft")
    async def mcstats(self, interaction: discord.Interaction, nick: str):
        await interaction.response.defer()

        logging.info(f"Comando '/mcstats {nick}' usado por {interaction.user.name} ({interaction.user.id}) no servidor {interaction.guild.name} ({interaction.guild.id}) no canal {interaction.channel.name} ({interaction.channel.id}). Nick pesquisado: {nick}")
        try:
            response = requests.get(f"https://api.flamemc.com.br/players/{nick}")
            response.raise_for_status()
            data = response.json()

            # Pegando as infos do player
            player_uuid = data.get("uuid", "Indisponível")
            player_rank = data["playerRanks"][0]["rankName"] if data.get("playerRanks") else "Membro"
            player_name = data.get("name", "Indisponível")
            player_first_login = format_date_time(data.get("firstLogin"))
            player_last_login = format_date_time(data.get("lastLogin"))
            player_clan = data.get("clan") 
            if player_clan == None:
                player_clan = "Sem clan"
            player_banned = "**<:barrier:1348790166344695841> **BANIDO** <:barrier:1348790166344695841>**" if data.get("banned", False) else ""
            player_premium = "<:premium:1348792849281318962> Original" if data.get("premium", False) else "<:offline:1348792969221640213> Pirata"
            avatar_url = f"https://mc-heads.net/avatar/{player_name}/256"

            if player_rank == "HEAD_ADMIN":
                player_rank = "ADMIN"
            

            
            # Cores por rank
            rank_colors = {
                "CEO": (170, 0, 0), "ADMIN": (170, 0, 0), "HEAD_ADMIN": (170, 0, 0),
                "MOD+": (146, 33, 145), "MOD": (146, 33, 145), "TRIAL": (146, 33, 145),
                "CREATOR+": (4, 156, 156), "CREATOR": (85, 255, 255), "STUDIO": (170, 0, 170),
                "LEGEND": (170, 0, 170), "BETA": (4, 4, 192), "FLAME": (255, 170, 0), "SPARK": (255, 255, 85)
            }
            embed_color = discord.Color.from_rgb(*rank_colors.get(player_rank, (218, 218, 218)))
            staff_ranks = ["STUDIO", "CREATOR+", "TRIAL", "MOD", "MOD+", "ADMIN", "HEAD_ADMIN", "CEO"]
            staff = "<a:staff:1348790083381362808>" if player_rank in staff_ranks else ""

                

            # Embed principal
            embed = discord.Embed(title=f"<a:minecraft:1347947160229904394> Perfil de {nick}", color=embed_color)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name=player_banned, value="", inline=False)
            embed.add_field(name="> <a:nick:1348794533617340416> Nick: ", value=player_name, inline=True)
            embed.add_field(name=f"> <:ranks:1348796107504750744> Rank: {staff}", value=player_rank, inline=True)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="> <:Clans:1348795465302282360> Clan: ", value=f"[{player_clan}]", inline=True)
            embed.add_field(name="> <:conta:1348794846336389232> Conta: ", value=player_premium, inline=True)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="> <a:clock:1348792701918642278> Último Login: ", value=player_last_login, inline=True)
            embed.add_field(name="> <a:first:1348794127482884238> Conta Criada: ", value=player_first_login, inline=True)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name=f"> <:mcname:1348801843014270976> Ver no NameMC: ", value=f"`•` [Clique aqui](https://pt.namemc.com/search?q={player_uuid})", inline=True)
            embed.add_field(name=f"> <:skin:1348796446031482943> Baixar Skin: ", value=f"`•`[Clique aqui](https://mc-heads.net/skin/{player_uuid})", inline=True)
            embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            # Embeds dos modos
            mode_embeds = {}
            for mode_key, mode_info in game_modes_config.items():
                mode_embed = discord.Embed(title=f"{mode_info['title']}", color=embed_color)
                mode_embed.set_thumbnail(url=avatar_url)
                for stat_key, custom_name in mode_info["stats"].items():
                    for stat in data.get("accountStats", []):
                        if stat["statsMap"]["name"] == stat_key:
                            mode_embed.add_field(name=f"> {custom_name}", value=f'  `•` {stat["value"]} ', inline=False)
                            mode_embed.add_field(name="", value="", inline=False)
                            mode_embed.add_field(name="", value="", inline=False)
                mode_embeds[mode_key] = mode_embed

            # Botões
            class StatsView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    self.add_item(MenuButton())
                    for mode_key, mode_info in game_modes_config.items():
                        self.add_item(GameModeButton(mode_key, mode_info['title']))

            class MenuButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="Menu Principal", style=discord.ButtonStyle.secondary)

                async def callback(self, interaction: discord.Interaction):
                    if interaction.user == interaction.message.interaction.user:
                        await interaction.response.edit_message(embed=embed, view=StatsView())
                    else:
                        await interaction.response.send_message("Use /mcstats <nick>.", ephemeral=True)

            class GameModeButton(discord.ui.Button):
                def __init__(self, mode_key, label):
                    super().__init__(label=label, style=discord.ButtonStyle.primary)
                    self.mode_key = mode_key

                async def callback(self, interaction: discord.Interaction):
                    if interaction.user == interaction.message.interaction.user:
                        await interaction.response.edit_message(embed=mode_embeds[self.mode_key], view=StatsView())
                    else:
                        await interaction.response.send_message("Use /mcstats <nick>.", ephemeral=True)

            await interaction.followup.send(embed=embed, view=StatsView())

        except requests.exceptions.RequestException:
            await interaction.followup.send("Erro ao buscar os dados.", ephemeral=True)
            logging.error(f"Erro ao buscar dados para {nick}: {requests.exceptions.RequestException}")
        except KeyError:
            await interaction.followup.send("Jogador não encontrado.", ephemeral=True)
            logging.warning(f"Jogador {nick} não encontrado.")


# ⚠️ Essa parte tem que ficar FORA da classe!
async def setup(bot):
    await bot.add_cog(McStats(bot))
