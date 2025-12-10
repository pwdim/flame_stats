import discord
import requests
from discord.ext import commands
from discord import app_commands

class HG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_leaderboard(self):
        url = "https://api.flamemc.com.br/leaderboards?statId=3&size=200"
        try:
            response = requests.get(url)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar leaderboard de HG: {e}")
            return None

    def get_player_position(self, player_name):
        leaderboard = self.get_leaderboard()
        if leaderboard:
            for player in leaderboard:
                if player["name"].lower() == player_name.lower():
                    return player['position']
        return None

    def get_rank(self, exp, position):
        if position is not None:
            if 1 <= position <= 3:
                return "<:Master:1352502537730916352> Master"
            elif 4 <= position <= 10:
                return "<:Amethyst:1352502566214176768> Amethyst"
            elif 11 <= position <= 30:
                return "<:Ruby:1352502577757032458> Ruby"
        
        ranks = [
            (6000, "Sapphire", "<:Sapphire:1352502587169181777>"),
            (4755, "Emerald", "<:Emerald:1352502596715413544>"),
            (3000, "Diamond", "<:Diamond:1352502605011615854>"),
            (1815, "Platinum", "<:Platinum:1352502612452184084>"),
            (580, "Gold", "<:Gold:1348794160513024122>"),
            (70, "Silver", "<:Silver:1352502628852043847>"),
            (0, "Bronze", "<:Bronze:1352502636762497065>")
        ]
        
        for threshold, rank_name, emoji in ranks:
            if exp >= threshold:
                return f"{emoji} {rank_name}"
        return "Desconhecido"

    hg_rank_colors = {
        "Bronze": discord.Colour(0xffff55),
        "Silver": discord.Colour(0xaaaaaa),
        "Gold": discord.Colour(0xffaa00),
        "Platinum": discord.Colour(0xff55ff),
        "Diamond": discord.Colour(0x55ffff),
        "Emerald": discord.Colour(0x00aa00),
        "Sapphire": discord.Colour(0x0000aa),
        "Ruby": discord.Colour(0xff5555),
        "Amethyst": discord.Colour(0xaa00aa),
        "Master": discord.Colour(0xaa0000),
    }

    @app_commands.command(name="arena", description="Veja suas estatísticas da Arena-PvP")
    @app_commands.describe(nick="Nome do jogador")
    async def hg(self, interaction: discord.Interaction, nick: str):
        
        should_be_ephemeral = False
        allowed_channels_cog = self.bot.get_cog("AllowedChannels")
        
        if allowed_channels_cog and hasattr(allowed_channels_cog, 'allowed_channel_ids') and allowed_channels_cog.allowed_channel_ids:
        
            if not interaction.user.guild_permissions.administrator and \
               interaction.channel_id not in allowed_channels_cog.allowed_channel_ids:
                should_be_ephemeral = True
        
        await interaction.response.defer(ephemeral=should_be_ephemeral)

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
                "pvp_arena_kills": "<a:abates:1348799859603406979> Abates na Arena",
                "pvp_arena_deaths": "<a:skull:1348799160979030096> Mortes na Arena",
                "pvp_arena_streak": "<a:streak:1348793266358714521> KillStreak na Arena",
                "pvp_arena_best_streak": "<a:streak:1348793098175647764> Melhor KillStreak na Arena",
                "pvp_coins": "<a:coin:1348794160513024122> Coins no KitPvp",
                "pvp_exp": "<a:xp:1348792513300795504> XP no KitPvp",
            }

            exp = 0
            for stat in stats:
                if stat["statsMap"]["name"] == "pvp_exp":
                    exp = stat["value"]
                    break

            position = self.get_player_position(nick)
            rank = self.get_rank(exp, position)

            for stat_name, label in stat_keys.items():
                value = "0"
                for stat in stats:
                    if stat["statsMap"]["name"] == stat_name:
                        value = stat["value"]
                        break
                embed.add_field(name=label, value=f"• {value}", inline=False)

          
            rank_name_for_color = rank.split(" ")[1] if " " in rank and " " in rank else rank
           
            if "<" in rank_name_for_color and ">" in rank_name_for_color:
                rank_name_for_color = rank_name_for_color.split(" ")[1]

            embed_color = self.hg_rank_colors.get(rank_name_for_color, discord.Colour.gold())
            embed.color = embed_color

            embed.add_field(name="<:rank:1352527135109283871> Rank", value=rank, inline=False)
            embed.add_field(name="<:podium:1352528120762204190> Colocação", value=f"#{position}" if position else "Não classificado", inline=False)

            embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")
            await interaction.followup.send(embed=embed, ephemeral=should_be_ephemeral)

        except requests.exceptions.RequestException:
            await interaction.followup.send("Erro ao buscar os dados do jogador. Certifique-se de que o nick está correto ou tente novamente mais tarde.", ephemeral=True)
        except Exception as e:
            print(f"Ocorreu um erro inesperado no comando /arena: {e}")
            await interaction.followup.send("Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(HG(bot))