import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

# Hole die Umgebungsvariablen
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Bot-Setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot ist bereit
@bot.event
async def on_ready():
    print(f"Bot ist bereit! Eingeloggt als {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=int(GUILD_ID)))
        print(f"Slash-Befehle synchronisiert: {len(synced)} Befehle")
    except Exception as e:
        print(f"Fehler beim Synchronisieren: {e}")


# Slash-Befehl: Ping
@bot.tree.command(name="ping", description="Testet die Verbindung", guild=discord.Object(id=int(GUILD_ID)))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# Bot starten
bot.run(TOKEN)
