import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Active games and invitations
active_invitations = {}

# Slash command to invite a player
@bot.tree.command(name="invite", description="Invite another player to a chess game", guild=discord.Object(id=int(GUILD_ID)))
async def invite(interaction: discord.Interaction, player: discord.Member):
    # Check if the inviter already has an active game or invitation
    if interaction.user.id in active_invitations:
        await interaction.response.send_message("You already have an active invitation or game!", ephemeral=True)
        return

    # Create the invitation
    active_invitations[interaction.user.id] = {"inviter": interaction.user, "invitee": player}
    
    # Create Accept and Decline buttons
    accept_button = Button(label="Accept", style=discord.ButtonStyle.success)
    decline_button = Button(label="Decline", style=discord.ButtonStyle.danger)

    async def accept_callback(interaction_button: discord.Interaction):
        # Check if the correct player is responding
        if player.id != interaction_button.user.id:
            await interaction_button.response.send_message("You are not the invited player!", ephemeral=True)
            return

        # Handle game acceptance
        if interaction.user.id in active_invitations:
            del active_invitations[interaction.user.id]  # Remove the invitation
            # Disable buttons
            for item in view.children:
                item.disabled = True
            await interaction.edit_original_response(content=f"{player.mention} accepted the invitation! The game can now begin!", view=view)
        else:
            await interaction_button.response.send_message("This invitation is no longer valid.", ephemeral=True)

    async def decline_callback(interaction_button: discord.Interaction):
        # Check if the correct player is responding
        if player.id != interaction_button.user.id:
            await interaction_button.response.send_message("You are not the invited player!", ephemeral=True)
            return

        # Handle game decline
        if interaction.user.id in active_invitations:
            del active_invitations[interaction.user.id]  # Remove the invitation
            # Disable buttons
            for item in view.children:
                item.disabled = True
            await interaction.edit_original_response(content=f"{player.mention} declined the invitation.", view=view)
        else:
            await interaction_button.response.send_message("This invitation is no longer valid.", ephemeral=True)

    # Set callbacks for buttons
    accept_button.callback = accept_callback
    decline_button.callback = decline_callback

    # Create the view and add buttons
    view = View()
    view.add_item(accept_button)
    view.add_item(decline_button)

    # Send the invitation message
    await interaction.response.send_message(
        f"{player.mention}, {interaction.user.mention} has invited you to a game of chess!",
        view=view
    )

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    try:
        guild = discord.Object(id=int(GUILD_ID))
        synced = await bot.tree.sync(guild=guild)
        print(f"Slash commands synced: {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Start the bot
bot.run(TOKEN)
