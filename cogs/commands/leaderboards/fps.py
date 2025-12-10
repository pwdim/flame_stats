import discord
import requests
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

# Configuração de logging para registrar eventos do bot
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('bot.log', encoding='utf-8')])

def format_date_time(date_time):
    """Formata uma string de data/hora ISO 8601 para um formato legível brasileiro."""
    if not date_time:
        return "Indisponível"
    # Substitui 'Z' por '+00:00' para compatibilidade com fromisoformat
    dt = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y %H:%M")

def format_number_with_period(number):
    """Formata um número inteiro para ter pontos como separadores de milhares."""
    try:
        num_str = str(int(number))
        parts = []
        while num_str:
            parts.append(num_str[-3:])
            num_str = num_str[:-3]
        return ".".join(reversed(parts))
    except ValueError:
        return str(number)

class FPSLeaderboards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.leaderboard_data = {}
        self.page_size = 10
        self.max_position = 100
        self.current_page_start_index = 0
        self.original_interaction_user_id = None
        self.original_interaction_for_edit = None # Adicionado para persistir a interação original para edições
        self.current_stat_id = "3"
        self.current_period = "total"

        self.stat_info = {
            "total": {
                "7": {"name": "Abates", "stat_key": "pvp_fps_kills", "emoji": "<a:abates:1348799859603406979>", "endpoint_suffix": "", "data_key": "accountStats"},
                "8": {"name": "Mortes", "stat_key": "pvp_fps_deaths", "emoji": "<a:skull:1348799160979030096>", "endpoint_suffix": "", "data_key": "accountStats"},
                "3": {"name": "XP", "stat_key": "pvp_exp", "emoji": "<a:xp:1348792513300795504>", "endpoint_suffix": "", "data_key": "accountStats"},
                "10": {"name": "Melhor Streak", "stat_key": "pvp_fps_best_streak", "emoji": "<a:best_streak:1348793098175647764>", "endpoint_suffix": "", "data_key": "accountStats"},
            },
            "weekly": {
                "7": {"name": "Abates", "stat_key": "pvp_fps_kills", "emoji": "<a:abates:1348799859603406979>", "endpoint_suffix": "/weekly", "data_key": "accountStatsWeekly"},
                "8": {"name": "Mortes", "stat_key": "pvp_fps_deaths", "emoji": "<a:skull:1348799160979030096>", "endpoint_suffix": "/weekly", "data_key": "accountStatsWeekly"},
                "3": {"name": "XP", "stat_key": "pvp_exp", "emoji": "<a:xp:1348792513300795504>", "endpoint_suffix": "/weekly", "data_key": "accountStatsWeekly"},
                "10": {"name": "Melhor Streak", "stat_key": "pvp_fps_best_streak", "emoji": "<a:best_streak:1348793098175647764>", "endpoint_suffix": "/weekly", "data_key": "accountStatsWeekly"},
            },
            "monthly": {
                "7": {"name": "Abates", "stat_key": "pvp_fps_kills", "emoji": "<a:abates:1348799859603406979>", "endpoint_suffix": "/monthly", "data_key": "accountStatsMonthly"},
                "8": {"name": "Mortes", "stat_key": "pvp_fps_deaths", "emoji": "<a:skull:1348799160979030096>", "endpoint_suffix": "/monthly", "data_key": "accountStatsMonthly"},
                "3": {"name": "XP", "stat_key": "pvp_exp", "emoji": "<a:xp:1348792513300795504>", "endpoint_suffix": "/monthly", "data_key": "accountStatsMonthly"},
                "10": {"name": "Melhor Streak", "stat_key": "pvp_fps_best_streak", "emoji": "<a:best_streak:1348793098175647764>", "endpoint_suffix": "/monthly", "data_key": "accountStatsMonthly"},
            },
        }

    fps = app_commands.Group(name="fps", description="Exibe as classificações do FPS do FlameMC.")

    async def fetch_leaderboard(self, stat_id: str, period: str):
        """Busca os dados do placar da API do FlameMC para a estatística e período especificados."""
        selected_stat_info = self.stat_info.get(period, {}).get(stat_id)
        if not selected_stat_info:
            logging.error(f"Erro: Nenhuma informação de estatística encontrada para o período '{period}' e statId '{stat_id}'")
            self.leaderboard_data[period] = None
            return

        suffix = selected_stat_info["endpoint_suffix"]
        url = f"https://api.flamemc.com.br/leaderboards{suffix}?statId={stat_id}&size=200"
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.leaderboard_data[period] = response.json()
            self.current_stat_id = stat_id
            self.current_period = period
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao buscar a classificação de FPS {period} para statId {stat_id}: {e}")
            self.leaderboard_data[period] = None

    async def create_leaderboard_page(self, start_index: int, is_ephemeral: bool):
        """Cria um embed e uma view para exibir uma página do placar."""
        leaderboard_data_for_period = self.leaderboard_data.get(self.current_period)

        if leaderboard_data_for_period is None:
            embed = discord.Embed(
                title="Erro na Classificação do FPS",
                description="Dados do placar do FPS não estão disponíveis ou houve um erro na comunicação com a API. Por favor, tente novamente mais tarde.",
                color=discord.Color.red(),
            )
            return embed, discord.ui.View()

        if not leaderboard_data_for_period:
            current_period_stats = self.stat_info.get(self.current_period, {})
            current_stat_name = current_period_stats.get(self.current_stat_id, {}).get("name", "N/A")

            period_text = {"total": "Total", "monthly": "Mensal", "weekly": "Semanal"}.get(self.current_period, "")
            embed = discord.Embed(
                title=f"Classificação do FPS ({period_text}) - {current_stat_name}",
                description=f"Não há dados disponíveis para a classificação de {current_stat_name} no período {period_text} no momento. Tente novamente mais tarde!",
                color=discord.Color.orange(),
            )
            embed.set_footer(
                text="• Desenvolvido por pwdim",
                icon_url="https://mc-heads.net/avatar/pwdim/64",
            )
            return embed, discord.ui.View()

        end_index = min(
            start_index + self.page_size, len(leaderboard_data_for_period), self.max_position
        )
        page_data = leaderboard_data_for_period[start_index:end_index]

        current_period_stats = self.stat_info.get(self.current_period, {})
        current_stat_name = current_period_stats.get(self.current_stat_id, {}).get("name", "N/A")
        period_text = {"total": "Total", "monthly": "Mensal", "weekly": "Semanal"}.get(self.current_period, "")
        embed = discord.Embed(
            title=f"Classificação do FPS ({period_text}) - {current_stat_name}",
            color=discord.Color.blue(),
        )

        if page_data:
            first_player_name = page_data[0]["name"]
            avatar_url = f"https://mc-heads.net/avatar/{first_player_name}/256"
            embed.set_thumbnail(url=avatar_url)
        else:
            embed.description = "Não há jogadores nesta página ou no placar do FPS."

        stat_key_to_display = current_period_stats.get(self.current_stat_id, {}).get("stat_key")
        stat_emoji_to_display = current_period_stats.get(self.current_stat_id, {}).get("emoji")
        data_key = current_period_stats.get(self.current_stat_id, {}).get("data_key")

        for player in page_data:
            position = player["position"]
            name = player["name"]
            clan = player.get("clan")
            clan_text = f"[{clan}]" if clan else ""

            banned = any(
                rank.get("rank") == "BANIDO" for rank in player.get("playerRanks", [])
            )
            banned_text = (
                "<:barrier:1348790166344695841> BANIDO <:barrier:1348790166344695841>"
                if banned
                else ""
            )

            stat_value = 0
            if data_key:
                for stat in player.get(data_key, []): 
                    if stat.get("statsMap", {}).get("name") == stat_key_to_display:
                        stat_value = stat["value"]
                        break

            formatted_stat_value = format_number_with_period(stat_value)

            embed.add_field(
                name=f"#{position} - {name} {clan_text}\n {banned_text}",
                value=f"{stat_emoji_to_display} {current_stat_name}: {formatted_stat_value}",
                inline=False,
            )

        embed.set_footer(
            text="• Desenvolvido por pwdim",
            icon_url="https://mc-heads.net/avatar/pwdim/64",
        )

        total_players = min(
            len(leaderboard_data_for_period), self.max_position
        )
        total_pages = (total_players + self.page_size - 1) // self.page_size
        current_page_number = (start_index // self.page_size) + 1
        embed.set_author(name=f"Página {current_page_number}/{total_pages}")

        class LeaderboardView(discord.ui.View):
            def __init__(self, parent_cog, initial_start_index, original_user_id, is_ephemeral_view):
                super().__init__(timeout=300)
                self.parent_cog = parent_cog
                self.current_start_index = initial_start_index
                self.original_user_id = original_user_id
                self.is_ephemeral_view = is_ephemeral_view

                # Adiciona botões para cada estatística
                current_period_stats = self.parent_cog.stat_info.get(self.parent_cog.current_period, {})
                for stat_id, info in current_period_stats.items():
                    self.add_item(
                        StatButton(
                            parent_cog=self.parent_cog,
                            stat_id=stat_id,
                            label=info["name"],
                            emoji=info["emoji"],
                            original_user_id=self.original_user_id,
                            is_ephemeral_button=self.is_ephemeral_view,
                        )
                    )

                self.add_item(self.create_page_select())
                self.add_item(
                    SearchPlayerButton(self.parent_cog, self.original_user_id, self.is_ephemeral_view)
                )

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                """Verifica se a interação foi feita pelo usuário original do comando."""
                if interaction.user and interaction.user.id == self.original_user_id:
                    return True
                else:
                    await interaction.response.send_message(
                        "Apenas quem invocou o comando pode interagir com ele.",
                        ephemeral=True,
                    )
                    return False

            def create_page_select(self):
                """Cria o menu suspenso para seleção de páginas."""
                leaderboard_data_for_period = self.parent_cog.leaderboard_data.get(self.parent_cog.current_period)
                if leaderboard_data_for_period is None or not leaderboard_data_for_period:
                    return discord.ui.Select(placeholder="Nenhuma página disponível", options=[discord.SelectOption(label="N/A", value="0")], disabled=True)

                options = []
                total_players = min(
                    len(leaderboard_data_for_period), self.parent_cog.max_position
                )
                total_pages = (
                    total_players + self.parent_cog.page_size - 1
                ) // self.parent_cog.page_size

                for i in range(total_pages):
                    start_pos = i * self.parent_cog.page_size + 1
                    end_pos = min((i + 1) * self.parent_cog.page_size, total_players)
                    options.append(
                        discord.SelectOption(
                            label=f"Página {i + 1} ({start_pos}-{end_pos})",
                            value=str(i * self.parent_cog.page_size),
                        )
                    )

                if not options:
                    options.append(
                        discord.SelectOption(
                            label="Nenhuma página disponível",
                            value="0",
                            default=True,
                        )
                    )

                select = discord.ui.Select(
                    placeholder="Ir para página...",
                    options=options,
                    custom_id="page_select_fps", # ID customizado para este select
                    disabled=not options or total_pages <= 1, # Desabilita se houver apenas 1 página ou nenhuma
                )
                select.callback = self.page_select_callback
                return select

            async def page_select_callback(self, interaction: discord.Interaction):
                """Callback para a seleção de páginas."""
                new_start_index = int(interaction.data["values"][0])
                await interaction.response.defer()

                self.parent_cog.current_page_start_index = new_start_index
                embed, view = await self.parent_cog.create_leaderboard_page(
                    new_start_index, self.is_ephemeral_view
                )
                await interaction.edit_original_response(embed=embed, view=view)

        class StatButton(discord.ui.Button):
            def __init__(self, parent_cog, stat_id: str, label: str, emoji: str, original_user_id: int, is_ephemeral_button: bool):
                super().__init__(
                    label=label,
                    style=discord.ButtonStyle.secondary, # Estilo padrão, pois cores personalizadas não são suportadas
                    emoji=emoji,
                    custom_id=f"stat_button_fps_{stat_id}", # ID customizado único para cada botão de estatística
                )
                self.parent_cog = parent_cog
                self.stat_id = stat_id
                self.original_user_id = original_user_id
                self.is_ephemeral_button = is_ephemeral_button

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != self.original_user_id:
                    await interaction.response.send_message(
                        "Apenas quem invocou o comando pode interagir com ele.",
                        ephemeral=True,
                    )
                    return

                await interaction.response.defer()

                self.parent_cog.current_stat_id = self.stat_id
                await self.parent_cog.fetch_leaderboard(self.parent_cog.current_stat_id, self.parent_cog.current_period)
                self.parent_cog.current_page_start_index = 0

                embed, view = await self.parent_cog.create_leaderboard_page(
                    self.parent_cog.current_page_start_index, self.is_ephemeral_button
                )
                await interaction.edit_original_response(embed=embed, view=view)

        class SearchPlayerButton(discord.ui.Button):
            def __init__(self, parent_cog, original_user_id, is_ephemeral_button):
                super().__init__(
                    label="Pesquisar Jogador",
                    style=discord.ButtonStyle.secondary,
                    custom_id="search_player_fps", # ID customizado para este botão
                )
                self.parent_cog = parent_cog
                self.original_user_id = original_user_id
                self.is_ephemeral_button = is_ephemeral_button

            async def callback(self, interaction: discord.Interaction):
                """Callback para o botão de pesquisa de jogador, que abre um modal."""
                if interaction.user.id != self.original_user_id:
                    await interaction.response.send_message(
                        "Apenas quem invocou o comando pode interagir com ele.",
                        ephemeral=True,
                    )
                    return

                class NickSearchModal(discord.ui.Modal, title="Pesquisar Jogador do FPS"):
                    def __init__(self, parent_cog, is_ephemeral_modal, original_interaction_for_edit):
                        super().__init__()
                        self.parent_cog = parent_cog
                        self.is_ephemeral_modal = is_ephemeral_modal
                        self.original_interaction_for_edit = original_interaction_for_edit
                        self.nick_input = discord.ui.TextInput(
                            label="Nick do Jogador",
                            placeholder="Digite o nick do jogador...",
                            max_length=16,
                            min_length=3,
                            required=True,
                        )
                        self.add_item(self.nick_input)

                    async def on_submit(self, interaction: discord.Interaction):
                        """Lida com a submissão do modal de pesquisa de nick."""
                        await interaction.response.defer(ephemeral=True)
                        leaderboard_data_for_period = self.parent_cog.leaderboard_data.get(self.parent_cog.current_period)
                        search_nick = self.nick_input.value.strip()

                        if not leaderboard_data_for_period:
                            await interaction.followup.send(
                                "Os dados da leaderboard não estão disponíveis.",
                                ephemeral=True,
                            )
                            return

                        found_player = None
                        for player in leaderboard_data_for_period:
                            if player["name"].lower() == search_nick.lower():
                                found_player = player
                                break

                        if found_player:
                            position = found_player["position"]
                            target_page_start_index = ((position - 1) // self.parent_cog.page_size) * self.parent_cog.page_size
                            self.parent_cog.current_page_start_index = target_page_start_index
                            
                            embed, view = await self.parent_cog.create_leaderboard_page(
                                self.parent_cog.current_page_start_index, self.is_ephemeral_modal
                            )
                            # Usa a interação original para editar a mensagem que contém o leaderboard
                            await self.original_interaction_for_edit.edit_original_response(embed=embed, view=view)
                            await interaction.followup.send(
                                f"Encontrado **{search_nick}** na posição **#{position}**. A leaderboard foi atualizada para mostrar a página.",
                                ephemeral=True,
                            )
                        else:
                            await interaction.followup.send(
                                f"Jogador '**{search_nick}**' não encontrado na leaderboard atual (Top {self.parent_cog.max_position}).",
                                ephemeral=True,
                            )

                modal = NickSearchModal(self.parent_cog, self.is_ephemeral_button, self.original_interaction_for_edit)
                await interaction.response.send_modal(modal)

        view = LeaderboardView(self, start_index, self.original_interaction_user_id, is_ephemeral)
        return embed, view

    @fps.command(name="total", description="Exibe a classificação total do FPS.")
    async def total(self, interaction: discord.Interaction):
        """Comando para exibir o placar total do FPS."""
        should_be_ephemeral = False
        allowed_channels_cog = self.bot.get_cog("AllowedChannels")
        
        if allowed_channels_cog and interaction.guild: 
            guild_id_str = str(interaction.guild_id)
            
            if guild_id_str in allowed_channels_cog.allowed_channel_ids and \
               allowed_channels_cog.allowed_channel_ids[guild_id_str] and \
               interaction.channel_id not in allowed_channels_cog.allowed_channel_ids[guild_id_str]:
                
                should_be_ephemeral = True
        
        await interaction.response.defer(ephemeral=should_be_ephemeral)
        self.original_interaction_user_id = interaction.user.id
        self.original_interaction_for_edit = interaction # Armazena a interação original para edições futuras
        self.current_period = "total"
        self.current_stat_id = "3"

        await self.fetch_leaderboard(self.current_stat_id, self.current_period)

        if self.leaderboard_data.get(self.current_period) is None:
            await interaction.followup.send(
                "Erro ao buscar a classificação total do FPS. Tente novamente mais tarde.",
                ephemeral=True,
            )
            return

        self.current_page_start_index = 0
        embed, view = await self.create_leaderboard_page(self.current_page_start_index, should_be_ephemeral)
        await interaction.followup.send(
            embed=embed, view=view, ephemeral=should_be_ephemeral
        )

    @fps.command(name="mensal", description="Exibe a classificação mensal do FPS.")
    async def mensal(self, interaction: discord.Interaction):
        """Comando para exibir o placar mensal do FPS."""
        should_be_ephemeral = False
        allowed_channels_cog = self.bot.get_cog("AllowedChannels")
        
        if allowed_channels_cog and interaction.guild: 
            guild_id_str = str(interaction.guild_id)
            
            if guild_id_str in allowed_channels_cog.allowed_channel_ids and \
               allowed_channels_cog.allowed_channel_ids[guild_id_str] and \
               interaction.channel_id not in allowed_channels_cog.allowed_channel_ids[guild_id_str]:
                
                should_be_ephemeral = True
        
        await interaction.response.defer(ephemeral=should_be_ephemeral)

        self.original_interaction_user_id = interaction.user.id
        self.original_interaction_for_edit = interaction # Armazena a interação original para edições futuras
        self.current_period = "monthly"
        self.current_stat_id = "3"

        await self.fetch_leaderboard(self.current_stat_id, self.current_period)

        if self.leaderboard_data.get(self.current_period) is None:
            await interaction.followup.send(
                "Erro ao buscar a classificação mensal do FPS. Tente novamente mais tarde.",
                ephemeral=True,
            )
            return

        self.current_page_start_index = 0
        embed, view = await self.create_leaderboard_page(self.current_page_start_index, should_be_ephemeral)
        await interaction.followup.send(
            embed=embed, view=view, ephemeral=should_be_ephemeral
        )

    @fps.command(name="semanal", description="Exibe a classificação semanal do FPS.")
    async def semanal(self, interaction: discord.Interaction):
        """Comando para exibir o placar semanal do FPS."""
        should_be_ephemeral = False
        allowed_channels_cog = self.bot.get_cog("AllowedChannels")
        
        if allowed_channels_cog and interaction.guild: 
            guild_id_str = str(interaction.guild_id)
            
            if guild_id_str in allowed_channels_cog.allowed_channel_ids and \
               allowed_channels_cog.allowed_channel_ids[guild_id_str] and \
               interaction.channel_id not in allowed_channels_cog.allowed_channel_ids[guild_id_str]:
                
                should_be_ephemeral = True
        
        await interaction.response.defer(ephemeral=should_be_ephemeral)

        self.original_interaction_user_id = interaction.user.id
        self.original_interaction_for_edit = interaction # Armazena a interação original para edições futuras
        self.current_period = "weekly"
        self.current_stat_id = "3"

        await self.fetch_leaderboard(self.current_stat_id, self.current_period)

        if self.leaderboard_data.get(self.current_period) is None:
            await interaction.followup.send(
                "Erro ao buscar a classificação semanal do FPS. Tente novamente mais tarde.",
                ephemeral=True,
            )
            return

        self.current_page_start_index = 0
        embed, view = await self.create_leaderboard_page(self.current_page_start_index, should_be_ephemeral)
        await interaction.followup.send(
            embed=embed, view=view, ephemeral=should_be_ephemeral
        )

async def setup(bot):
    """Função de setup para adicionar o cog ao bot."""
    await bot.add_cog(FPSLeaderboards(bot))