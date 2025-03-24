import discord
import requests
from discord.ext import commands
from discord import app_commands

class LeagueLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.leaderboard_data = None
        self.page_size = 10
        self.max_position = 100

    async def fetch_leaderboard(self):
        url = "https://api.flamemc.com.br/leaderboards?statId=25&size=200"  # Assuming statId 25 is correct for League
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.leaderboard_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar a classificação: {e}")
            self.leaderboard_data = None

    async def get_player_data(self, nick):
        try:
            response = requests.get(f"https://api.flamemc.com.br/players/{nick}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados do jogador {nick}: {e}")
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
            (580, "Gold", "<:Gold:1352502620144537692>"),
            (70, "Silver", "<:Silver:1352502628852043847>"),
            (0, "Bronze", "<:Bronze:1352502636762497065>")
        ]

        for threshold, rank_name, emoji in ranks:
            if exp >= threshold:
                return f"{emoji} {rank_name}"
        return "Desconhecido"

    league_rank_colors = {  # Changed to league_rank_colors
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

    @app_commands.command(name="leader_fl", description="Exibe a classificação do League.")
    async def league_leaderboard(self, interaction: discord.Interaction): # changed command name and function name
        await interaction.response.defer()
        await self.fetch_leaderboard()

        if self.leaderboard_data is None:
            await interaction.followup.send("Erro ao buscar a classificação.", ephemeral=True)
            return

        embed, view = await self.create_leaderboard_page(0)
        await interaction.followup.send(embed=embed, view=view)
        interaction.message = await interaction.original_response() # store the original message

    async def create_leaderboard_page(self, start_index: int):
        end_index = min(start_index + self.page_size, len(self.leaderboard_data), self.max_position)
        page_data = self.leaderboard_data[start_index:end_index]

        embed = discord.Embed(title=" Classificação League", color=discord.Color.dark_green()) # changed embed title

        if page_data:
            first_player_name = page_data[0]["name"]
            avatar_url = f"https://mc-heads.net/avatar/{first_player_name}/256"
            embed.set_thumbnail(url=avatar_url)

        for player in page_data:
            position = player["position"]
            name = player["name"]
            player_data = await self.get_player_data(name)
            exp = 0  # Initialize exp to 0
            if player_data and player_data.get("accountStats"):
                for stat in player_data["accountStats"]:
                    if stat["statsMap"]["name"] == "league_exp": #assuming hg_exp is still the correct stat, check for the correct stat name for league.
                        exp = stat["value"]
                        break
            banned = player_data.get("banned", False) if player_data else False
            rank = self.get_rank(exp, position)
            rank_name = rank.split(" ")[1] if " " in rank else rank
            embed_color = self.league_rank_colors.get(rank_name, discord.Colour.gold()) # changed rank colors
            embed.color = embed_color
            banned_text = "<:barrier:1348790166344695841> BANIDO <:barrier:1348790166344695841>" if banned else ""
            formatted_exp = "{:,}".format(exp).replace(",", ".")
            cdata = player["clan"]
            if cdata == None:
                clan = ""
            else:
                clan = f"[{cdata}]" 
            embed.add_field(name=f"#{position} - {name} {clan}\n {banned_text}", value=f"{rank}\n<a:xp:1348792513300795504> XP: {formatted_exp}", inline=False)

        embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")

        prev_button = discord.ui.Button(style=discord.ButtonStyle.primary, label="Anterior", custom_id="prev")
        next_button = discord.ui.Button(style=discord.ButtonStyle.primary, label="Próximo", custom_id="next")

        if start_index == 0:
            prev_button.disabled = True
        if end_index >= min(len(self.leaderboard_data), self.max_position):
            next_button.disabled = True

        view = discord.ui.View()
        view.add_item(prev_button)
        view.add_item(next_button)

        async def prev_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            embed, view = await self.create_leaderboard_page(start_index - self.page_size)
            await interaction.message.edit(embed=embed, view=view)

        async def next_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            embed, view = await self.create_leaderboard_page(start_index + self.page_size)
            await interaction.message.edit(embed=embed, view=view)

        prev_button.callback = prev_callback
        next_button.callback = next_callback

        return embed, view

async def setup(bot):
    await bot.add_cog(LeagueLeaderboard(bot)) # changed cog name