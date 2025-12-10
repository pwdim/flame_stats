import discord
import requests
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message:s',
                    handlers=[logging.FileHandler('bot.log', encoding='utf-8')])

def format_date_time(date_time):
    if not date_time:
        return "Indisponível"
    dt = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y %H:%M")

def format_number_with_period(number):
    try:
        num_str = str(int(number))
        parts = []
        while num_str:
            parts.append(num_str[-3:])
            num_str = num_str[:-3]
        return ".".join(reversed(parts))
    except ValueError:
        return str(number)

game_modes_config = {
    "pvp": {
        "title": "⚔️ PvP",
        "type": "category",
        "sub_modes": {
            "arena": {
                "title": "🏟 Arena",
                "type": "game_mode",
                "stats": {
                    "pvp_arena_kills": "<a:abates:1348799859603406979> Abates em Arena",
                    "pvp_arena_deaths": "<a:skull:1348799160979030096> Mortes em Arena",
                    "pvp_arena_streak": "<a:streak:1348793266358714521> KillStreak em Arena",
                    "pvp_arena_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em Arena",
                    "pvp_coins": "<a:coin:1348794160513024122> Coins em KitPvp",
                    "pvp_exp": "<a:xp:1348792513300795504> XP em KitPvp",
                }
            },
            "fps": {
                "title": "🔫 FPS",
                "type": "game_mode",
                "stats": {
                    "pvp_fps_kills": "<a:abates:1348799859603406979> Abates em FPS",
                    "pvp_fps_deaths": "<a:skull:1348799160979030096> Mortes em FPS",
                    "pvp_fps_streak": "<a:streak:1348793266358714521> KillStreak em FPS",
                    "pvp_fps_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em FPS",
                    "pvp_coins": "<a:coin:1348794160513024122> Coins em KitPvp",
                    "pvp_exp": "<a:xp:1348792513300795504> XP em KitPvp",
                }
            }
        }
    },
    "hardcore_games_category": {
        "title": "🗡️ Hardcore Games",
        "type": "category",
        "sub_modes": {
            "hg": {
                "title": "🏹 Hunger Games",
                "type": "game_mode",
                "stats": {
                    "hg_wins": "<a:wins:1348790119070564402> Vitórias em HG",
                    "hg_kills": "<a:abates:1348799859603406979> Abates em HG",
                    "hg_deaths": "<a:skull:1348799160979030096> Mortes em HG",
                    "hg_coins": "<a:coin:1348794160513024122> Coins em HG",
                    "hg_exp": "<a:xp:1348792513300795504> XP em HG",
                }
            },
            "league": {
                "title": "🔥 FlameLeague",
                "type": "game_mode",
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
                "type": "game_mode",
                "stats": {
                    "competitive_wins": "<a:wins:1348790119070564402> Vitórias em Cxc",
                    "competitive_defeats": "<a:skull:1348799160979030096> Derrotas em CxC",
                    "competitive_kills": "<a:abates:1348799859603406979> Abates em CxC",
                    "competitive_deaths": "<a:skull:1348799160979030096> Mortes em CxC",
                    "competitive_exp": "<a:xp:1348792513300795504> XP em CxC",
                }
            },
        }
    },
    "academy_category": {
        "title": "📚 Academy",
        "type": "category",
        "sub_modes": {
            "fastrap": {
                "title": "💨 Fast Trap",
                "type": "game_mode",
                "stats": {
                    "academy_fast_trap_wins": "<a:wins:1348790119070564402> Vitórias em Fast Trap",
                    "academy_fast_trap_defeats": "<a:skull:1348799160979030096> Derrotas em Fast Trap",
                    "academy_fast_trap_streak": "<a:streak:1348793266358714521> KillStreak em Fast Trap",
                    "academy_fast_trap_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em Fast Trap",
                    "academy_exp": "<a:xp:1348792513300795504> Xp em Academy",
                }
            },
            "arena_flat": {
                "title": "🏗️ Arena Flat",
                "type": "game_mode",
                "stats": {
                    "academy_arena_flat_kills": "<a:abates:1348799859603406979> Abates em Arena Flat",
                    "academy_arena_flat_deaths": "<a:skull:1348799160979030096> Mortes em Arena Flat",
                    "academy_arena_flat_streak": "<a:streak:1348793266358714521> KillStreak em Arena Flat",
                    "academy_arena_flat_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak em Arena Flat",
                    "academy_exp": "<a:xp:1348792513300795504> Xp em Academy",
                }
            },
            "arena_cave": {
                "title": "🏞️ Arena Cave",
                "type": "game_mode",
                "stats": {
                    "academy_arena_cave_deaths": "<a:skull:1348799160979030096> Mortes em Arena Cave",
                    "academy_arena_cave_streak": "<a:streak:1348793266358714521> KillStreak em Arena Cave",
                    "academy_exp": "<a:xp:1348792513300795504> Xp em Academy",
                }
            },
            "digger_classic": {
                "title": "⛏️ Digger Classic",
                "type": "game_mode",
                "stats": {
                    "academy_digger_classic_wins": "<a:wins:1348790119070564402> Vitórias em Digger Classic",
                    "academy_digger_classic_streak": "<a:streak:1348793266358714521> KillStreak em Digger Classic",
                    "academy_digger_classic_defeats": "<a:skull:1348799160979030096> Derrotas em Digger Classic",
                    "academy_exp": "<a:xp:1348792513300795504> Xp em Academy",
                }
            },
            "digger_league": {
                "title": "🏆 Digger League",
                "type": "game_mode",
                "stats": {
                    "academy_digger_league_wins": "<a:wins:1348790119070564402> Vitórias em Digger League",
                    "academy_digger_league_streak": "<a:streak:1348793266358714521> KillStreak em Digger League",
                    "academy_digger_league_defeats": "<a:skull:1348799160979030096> Derrotas em Digger League",
                    "academy_exp": "<a:xp:1348792513300795504> Xp em Academy",
                }
            },
        }
    },
    "duels_category": {
        "title": "🗡 Duels",
        "type": "category",
        "sub_modes": {
            "gladiator": {
                "title": "⛓️ Gladiator",
                "type": "game_mode",
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
                "type": "game_mode",
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
                "type": "game_mode",
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
                "type": "game_mode",
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
    },
#    "bedwars": {
#        "title": "🛏 BedWars",
#        "type": "game_mode",
#        "stats": {
#            "bed_wars_total_games_played": "Partidas (Total)",
#            "bed_wars_total_wins": "<a:wins:1348790119070564402> Vitórias em BedWars",
#            "bed_wars_total_defeats": "<a:skull:1348799160979030096> Derrotas em BedWars",
#            "bed_wars_total_final_kills": "<a:abates:1348799859603406979> Abates Finais em BedWars",
#            "bed_wars_total_deaths": "<a:skull:1348799160979030096> Mortes em BedWars",
#            "bed_wars_experience": "<a:xp:1348792513300795504> XP em BedWars",
#        }
#    },
}

class InfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Acesse o menu de um jogador no FlameMC.")
    @app_commands.describe(nick="Nome do jogador no Minecraft")
    async def info(self, interaction: discord.Interaction, nick: str):
        should_be_ephemeral = False
        allowed_channels_cog = self.bot.get_cog("AllowedChannels")

        if allowed_channels_cog and interaction.guild:
            guild_id_str = str(interaction.guild_id)
            if guild_id_str in allowed_channels_cog.allowed_channel_ids and \
               allowed_channels_cog.allowed_channel_ids[guild_id_str] and \
               interaction.channel_id not in allowed_channels_cog.allowed_channel_ids[guild_id_str]:
                should_be_ephemeral = True

        await interaction.response.defer(ephemeral=should_be_ephemeral)

        log_channel_name = interaction.channel.name if interaction.channel else "DM"
        log_guild_name = interaction.guild.name if interaction.guild else "Mensagem Direta"
        logging.info(f"Comando '/info {nick}' usado por {interaction.user.name} ({interaction.user.id}) no servidor {log_guild_name} ({interaction.guild_id}), no canal {log_channel_name} ({interaction.channel_id}). Nick pesquisado: {nick}")

        try:
            response = requests.get(f"https://api.flamemc.com.br/players/{nick}")
            response.raise_for_status()
            data = response.json()

            player_uuid = data.get("uuid", "Indisponível")
            player_ranks_data = data.get("playerRanks", [])
            player_ranks = [rank["rankName"] for rank in player_ranks_data] if player_ranks_data else ["Membro"]

            player_name = data.get("name", "Indisponível")
            player_first_login = format_date_time(data.get("firstLogin"))
            player_last_login = format_date_time(data.get("lastLogin"))
            player_clan = data.get("clan")
            if player_clan is None:
                player_clan = "Sem clan"
            player_banned = "**<:barrier:1348790166344695841> **BANIDO** <:barrier:1348790166344695841>**" if data.get("banned", False) else ""
            player_premium = "<:premium:1348792849281318962> Original" if data.get("premium", False) else "<:offline:1348792969221640213> Pirata"
            avatar_url = f"https://mc-heads.net/avatar/{player_uuid}/256"

            rank_colors = {
                "CEO": (170, 0, 0), "ADMIN": (170, 0, 0), "HEAD_ADMIN": (170, 0, 0),
                "MOD+": (146, 33, 145), "MOD": (146, 33, 145), "TRIAL": (146, 33, 145),
                "CREATOR+": (4, 156, 156), "CREATOR": (85, 255, 255), "STUDIO": (170, 0, 170),
                "BUILDER": (0, 170, 0),
                "LEGEND": (170, 0, 170), "BETA": (4, 4, 192), "FLAME": (255, 170, 0), "SPARK": (255, 255, 85),
            }

            display_rank = player_ranks[0] if player_ranks else "Membro"
            embed_color = discord.Color.from_rgb(*rank_colors.get(display_rank, (218, 218, 218)))

            staff_ranks_set = {"STUDIO", "CREATOR+", "TRIAL", "MOD", "MOD+", "ADMIN", "HEAD_ADMIN", "CEO", "BUILDER", "Dono 2"}
            staff_indicator = "<a:staff:1348790083381362808>" if any(r in staff_ranks_set for r in player_ranks) else ""

            rank_display_names = {
                "CEO": "Administrador", "HEAD_ADMIN": "Administrador", "ADMIN": "Administrador",
                "MOD+": "Moderador Primário", "MOD": "Moderador Secundário", "TRIAL": "Trial Moderador",
                "BUILDER": "Builder", "STUDIO": "Studio", "CREATOR+": "Creator+", "CREATOR": "Creator",
                "BETA": "Beta", "LEGEND": "Legend", "FLAME": "Flame", "SPARK": "Spark",
                "Membro": "Membro"
            }

            formatted_player_ranks = ", ".join([rank_display_names.get(r, r) for r in player_ranks])

            special = ""
            if player_uuid == "4890f4c5-af0a-4cc7-b7a3-90f6b34a1348":
                special = " 🌹"
            if player_uuid == "fc883f59-f929-40b6-832c-95d1ee20e138":
                special = ", Top 1 brazuca"
                embed_color = discord.Color.from_rgb(96, 223, 255)

            embed = discord.Embed(title=f"<a:Minecraft:1376266806142046218> {player_name}{special} ", color=embed_color)
            embed.set_thumbnail(url=avatar_url)
            if player_banned:
                embed.add_field(name=player_banned, value="", inline=False)
            embed.add_field(name=f"> <:ranks:1348796107504750744> Rank: ", value=f"{staff_indicator} {formatted_player_ranks} ", inline=True)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="> <:Clans:1348795465302282360> Clan: ", value=f"{player_clan}", inline=True)
            embed.add_field(name="> <:conta:1348794846336389232> Conta: ", value=player_premium, inline=True)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="> <a:clock:1348792701918642278> Último Login: ", value=player_last_login, inline=True)
            embed.add_field(name="> <a:first:1348794127482884238> Conta Criada: ", value=player_first_login, inline=True)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name=f"> <:mcname:1348801843014270976> Ver no NameMC: ", value=f"`•` [Clique aqui](https://pt.namemc.com/search?q={player_uuid})", inline=True)
            embed.add_field(name=f"> <:skin:1348796446031482943> Baixar Skin: ", value=f"`•`[Clique aqui](https://mc-heads.net/skin/{player_uuid})", inline=True)
            embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

            def collect_game_mode_embeds(config_data, current_embeds, embed_color, avatar_url, player_data):
                for mode_key, mode_info in config_data.items():
                    if mode_info["type"] == "game_mode":
                        mode_embed = discord.Embed(title=f"{mode_info['title']}", color=embed_color)
                        mode_embed.set_thumbnail(url=avatar_url)

                        stats_found = False
                        for stat_key, custom_name in mode_info["stats"].items():
                            for stat in player_data.get("accountStats", []):
                                if stat.get("statsMap", {}).get("name") == stat_key:
                                    formatted_value = format_number_with_period(stat["value"])
                                    mode_embed.add_field(name=f"> {custom_name}", value=f'`•` {formatted_value}', inline=False)
                                    stats_found = True
                                    break
                        
                        if not stats_found:
                            mode_embed.add_field(name="Sem dados disponíveis", value="Nenhum dado encontrado para este modo de jogo.", inline=False)
                        
                        current_embeds[mode_key] = mode_embed
                    elif mode_info["type"] == "category":
                        collect_game_mode_embeds(mode_info["sub_modes"], current_embeds, embed_color, avatar_url, player_data)
                return current_embeds

            mode_embeds = collect_game_mode_embeds(game_modes_config, {}, embed_color, avatar_url, data)

            class StatsView(discord.ui.View):
                def __init__(self, main_embed, all_game_mode_embeds, original_interaction_user_id, is_ephemeral, current_level_modes_data: dict, parent_level_modes_data: dict = None):
                    super().__init__(timeout=None)
                    self.main_embed = main_embed
                    self.all_game_mode_embeds = all_game_mode_embeds
                    self.original_interaction_user_id = original_interaction_user_id
                    self.is_ephemeral = is_ephemeral
                    self.current_level_modes_data = current_level_modes_data
                    self.parent_level_modes_data = parent_level_modes_data

                    

                    if self.parent_level_modes_data is not None:
                        self.add_item(BackButton(self.main_embed, self.all_game_mode_embeds, self.original_interaction_user_id, self.is_ephemeral, self.parent_level_modes_data))

                    for mode_key, mode_info in self.current_level_modes_data.items():
                        if mode_info["type"] == "category":
                            self.add_item(CategoryButton(mode_key, mode_info, self.main_embed, self.all_game_mode_embeds, self.original_interaction_user_id, self.is_ephemeral, self.current_level_modes_data))
                        elif mode_info["type"] == "game_mode":
                            self.add_item(GameModeButton(mode_key, mode_info, self.all_game_mode_embeds, self.main_embed, self.original_interaction_user_id, self.is_ephemeral, self.current_level_modes_data, self.parent_level_modes_data))


            class BackButton(discord.ui.Button):
                def __init__(self, main_embed, all_game_mode_embeds, original_interaction_user_id, is_ephemeral, target_level_modes_data: dict):
                    super().__init__(label="Voltar", style=discord.ButtonStyle.red) # Grey
                    self.main_embed = main_embed
                    self.all_game_mode_embeds = all_game_mode_embeds
                    self.original_interaction_user_id = original_interaction_user_id
                    self.is_ephemeral = is_ephemeral
                    self.target_level_modes_data = target_level_modes_data

                async def callback(self, interaction: discord.Interaction):
                    if interaction.user.id == self.original_interaction_user_id:
                        def find_parent_of_data(root, target, parent=None):
                            for key, value in root.items():
                                if value is target:
                                    return parent
                                if isinstance(value, dict) and "sub_modes" in value and isinstance(value["sub_modes"], dict):
                                    found_parent = find_parent_of_data(value["sub_modes"], target, value)
                                    if found_parent:
                                        return found_parent
                            return None

                        if self.target_level_modes_data is game_modes_config:
                            new_parent_data = None
                        else:
                            new_parent_data = find_parent_of_data(game_modes_config, self.target_level_modes_data)

                        await interaction.response.edit_message(
                            embed=self.main_embed,
                            view=StatsView(self.main_embed, self.all_game_mode_embeds, self.original_interaction_user_id, self.is_ephemeral, self.target_level_modes_data, new_parent_data)
                        )
                    else:
                        await interaction.response.send_message("Use /info <nick> para interagir.", ephemeral=True)

            class CategoryButton(discord.ui.Button):
                def __init__(self, category_key: str, category_info: dict, main_embed: discord.Embed, all_game_mode_embeds: dict, original_interaction_user_id: int, is_ephemeral: bool, current_parent_level_modes_data: dict):
                    # Changed to red for distinct category color
                    super().__init__(label=category_info["title"], style=discord.ButtonStyle.green)
                    self.category_key = category_key
                    self.category_info = category_info
                    self.main_embed = main_embed
                    self.all_game_mode_embeds = all_game_mode_embeds
                    self.original_interaction_user_id = original_interaction_user_id
                    self.is_ephemeral = is_ephemeral
                    self.current_parent_level_modes_data = current_parent_level_modes_data

                async def callback(self, interaction: discord.Interaction):
                    if interaction.user.id == self.original_interaction_user_id:
                        await interaction.response.edit_message(
                            embed=self.main_embed,
                            view=StatsView(self.main_embed, self.all_game_mode_embeds, self.original_interaction_user_id, self.is_ephemeral, self.category_info["sub_modes"], self.current_parent_level_modes_data)
                        )
                    else:
                        await interaction.response.send_message("Use /info <nick> para interagir.", ephemeral=True)

            class GameModeButton(discord.ui.Button):
                def __init__(self, mode_key: str, mode_info: dict, all_game_mode_embeds: dict, main_embed: discord.Embed, original_interaction_user_id: int, is_ephemeral: bool, current_display_level_data: dict, parent_display_level_data: dict = None):
                    super().__init__(label=mode_info["title"], style=discord.ButtonStyle.green) 
                    self.mode_key = mode_key
                    self.mode_info = mode_info
                    self.all_game_mode_embeds = all_game_mode_embeds
                    self.main_embed = main_embed
                    self.original_interaction_user_id = original_interaction_user_id
                    self.is_ephemeral = is_ephemeral
                    self.current_display_level_data = current_display_level_data
                    self.parent_display_level_data = parent_display_level_data

                async def callback(self, interaction: discord.Interaction):
                    if interaction.user.id == self.original_interaction_user_id:
                        await interaction.response.edit_message(
                            embed=self.all_game_mode_embeds[self.mode_key],
                            view=StatsView(self.main_embed, self.all_game_mode_embeds, self.original_interaction_user_id, self.is_ephemeral, self.current_display_level_data, self.parent_display_level_data)
                        )
                    else:
                        await interaction.response.send_message("Use /info <nick> para interagir.", ephemeral=True)

            await interaction.followup.send(embed=embed, view=StatsView(embed, mode_embeds, interaction.user.id, should_be_ephemeral, game_modes_config, None), ephemeral=should_be_ephemeral)

        except requests.exceptions.RequestException as e:
            await interaction.followup.send("Erro ao buscar os dados. A API pode estar indisponível ou o jogador não existe.", ephemeral=True)
            logging.error(f"Erro ao buscar dados para {nick}: {e}")
        except KeyError:
            await interaction.followup.send("Jogador não encontrado ou dados inválidos recebidos.", ephemeral=True)
            logging.warning(f"Jogador {nick} não encontrado ou dados inválidos.")
        except Exception as e:
            await interaction.followup.send("Ocorreu um erro inesperado ao processar sua solicitação.", ephemeral=True)
            logging.error(f"Erro inesperado ao processar /info para {nick}: {e}", exc_info=True)


async def setup(bot):
    await bot.add_cog(InfoCommand(bot))