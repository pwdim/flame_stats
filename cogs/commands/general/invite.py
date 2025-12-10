import discord
from discord.ext import commands
from discord import app_commands
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('bot.log', encoding='utf-8')])

class InviteOnlyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="convite", description="Convide o bot para o seu servidor.")
    async def invite(self, interaction: discord.Interaction):
        should_be_ephemeral = False
        
  
        allowed_channels_cog = self.bot.get_cog("AllowedChannels")
        if allowed_channels_cog and interaction.guild:
            guild_id_str = str(interaction.guild_id)
            if guild_id_str in allowed_channels_cog.allowed_channel_ids and \
               allowed_channels_cog.allowed_channel_ids[guild_id_str] and \
               interaction.channel_id not in allowed_channels_cog.allowed_channel_ids[guild_id_str]:
                should_be_ephemeral = True

        await interaction.response.defer(ephemeral=should_be_ephemeral)

        logging.info(f"Comando 'convite' usado por {interaction.user.name} ({interaction.user.id}) no servidor {interaction.guild.name} ({interaction.guild.id}) no canal {interaction.channel.name} ({interaction.channel.id}).")

        if not self.bot.application_id:
            logging.error("Client ID do bot não encontrado. Não é possível gerar o link de convite.")
            await interaction.followup.send("Não foi possível gerar o link de convite do bot. Verifique a configuração.", ephemeral=True)
            return

   
        invite_link = "https://discord.com/oauth2/authorize?client_id=1347224237143756841"

        embed = discord.Embed(
            title="<:link:1348790292408569876> Convidar o Bot", 
            description=f"Clique [aqui]({invite_link}) para me adicionar ao seu servidor!",
            color=discord.Color.blue()
        )
        embed.set_footer(text="• Desenvolvido por pwdim", icon_url="https://mc-heads.net/avatar/pwdim/64")

        await interaction.followup.send(embed=embed, ephemeral=should_be_ephemeral)

async def setup(bot):
    await bot.add_cog(InviteOnlyCog(bot))