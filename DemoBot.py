import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import chess
from PIL import Image, ImageDraw, ImageFont

#load env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")


#bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


#chessboard rendering
def render_chessboard(board):
    square_size = 80
    board_size = square_size * 8
    img = Image.new("RGB", (board_size, board_size), "white")
    draw = ImageDraw.Draw(img)

    #colour for the squares of the board
    light_color = "#f0d9b5"
    dark_color = "#b58863"

    #draw squares
    for rank in range(8):
        for file in range(8):
            x0 = file * square_size
            y0 = rank * square_size
            x1 = x0 + square_size
            y1 = y0 + square_size
            color = light_color if (rank + file) % 2 == 0 else dark_color
            draw.rectangle([x0, y0, x1, y1], fill=color)


    #load font(unicode chess font)
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except IOError:
        font = ImageFont.load_default()

    #parse the FEN (information to construct game position)
    rows = board.board_fen().split("/")
    for rank, row in enumerate(rows):
        file = 0
        for char in row:
            if char.isdigit():
                #empty the squares
                file += int(char)
            else:
                #chess piece
                x = file * square_size + square_size // 4
                y = rank * square_size + square_size // 4
                draw.text((x, y), char, fill="black", font=font)
                file += 1

    #save the image of the chessboard
    img.save("chessboard.png")

#with /board it shows the chessboard
@bot.tree.command(name="board", description="Zeigt das Schachbrett", guild=discord.Object(id=int(GUILD_ID)))
async def board(interaction: discord.Interaction):
    #creation of a new chess board
    chess_board = chess.Board()
    render_chessboard(chess_board)

    #send the rendert image to discord
    await interaction.response.send_message(file=discord.File("chessboard.png"))

#event: (bot is ready!)
@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    try:
        guild = discord.Object(id=int(GUILD_ID))
        synced = await bot.tree.sync(guild=guild)
        print(f"Slash commands synced: {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")



'''# Event: Bot ist bereit
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
    await interaction.response.send_message("Pong!")'''

# Bot starten
bot.run(TOKEN)
