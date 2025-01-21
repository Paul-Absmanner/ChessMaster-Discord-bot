import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os
import chess
from ChessboardRenderer import ChessboardRenderer

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Bot setup
intents = discord.Intents.default()
intents.members = True  # Enable members intent
bot = commands.Bot(command_prefix="!", intents=intents)

# Active games
active_games = {}
renderer = ChessboardRenderer()

# Chess piece categories
PIECE_TYPES = {
    "Pawn": chess.PAWN,
    "Bishop": chess.BISHOP,
    "Knight": chess.KNIGHT,
    "Rook": chess.ROOK,
    "Queen": chess.QUEEN,
    "King": chess.KING
}

# Slash command to start a chess game
@bot.tree.command(name="start_chess", description="Start a chess game with another player", guild=discord.Object(id=int(GUILD_ID)))
async def start_chess(interaction: discord.Interaction, opponent: discord.Member):
    # -- existing checks --

    # Initialize the board, store in active_games, etc.
    board = chess.Board()
    active_games[interaction.user.id] = {
        "board": board,
        "current_player": interaction.user.id,
        "players": {interaction.user.id: "white", opponent.id: "black"}
    }
    active_games[opponent.id] = active_games[interaction.user.id]

    # Render and send the initial board
    renderer.render(board)
    await interaction.response.send_message(
        f"**Game Started!**\n:white_circle: {interaction.user.mention} is **White**\n:black_circle: {opponent.mention} is **Black**",
        file=discord.File("images/chessboard.png")
    )

    # Now that we have responded, we can show piece selection
    await show_piece_selection(interaction, interaction.user.id)


async def show_piece_selection(interaction: discord.Interaction, player_id: int):
    """Show piece selection for the given player."""
    guild = interaction.guild
    # Retrieve or fetch the player
    player = guild.get_member(player_id) or await guild.fetch_member(player_id)

    view = View()
    for piece_name in PIECE_TYPES:
        button = Button(label=piece_name, style=discord.ButtonStyle.primary)

        async def piece_callback(interaction_button: discord.Interaction, piece_name=piece_name):
            # Defer to avoid "This interaction failed" if the logic takes time
            await interaction_button.response.defer()
            await show_move_options(interaction_button, player, PIECE_TYPES[piece_name])

        button.callback = piece_callback
        view.add_item(button)

    # Instead of editing by message ID, edit the "original response"
    await interaction.edit_original_response(
        content=f"{player.mention}, select a piece type to move:",
        view=view
    )



# Function to show move options for a selected piece type
async def show_move_options(interaction, player, piece_type):
    game_state = active_games[player.id]
    board = game_state["board"]
    legal_moves = [move for move in board.legal_moves if board.piece_at(move.from_square).piece_type == piece_type]

    if not legal_moves:
        await interaction.followup.send("No legal moves for this piece type!", ephemeral=True)
        return

    view = View()

    for move in legal_moves:
        button_label = f"{chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}"
        button = Button(label=button_label, style=discord.ButtonStyle.success)

        async def move_callback(interaction_button: discord.Interaction, move=move):
            board.push(move)
            renderer.render(board)
            
            next_player_id = switch_player(player)

            # Instead of using followup.edit_message, just edit the "active" message
            await interaction_button.response.edit_message(
                content=f"{player.mention} moved {chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}",
                attachments=[discord.File("images/chessboard.png")],
                view=None
            )

            # Show piece selection for the next player, etc...
            await show_piece_selection(interaction_button, next_player_id)



        button.callback = move_callback
        view.add_item(button)

    # Edit the original message using follow-up to update buttons
    await interaction.followup.edit_message(
        message_id=interaction.message.id,
        content="Select your move:",
        view=view
    )


# Function to switch the current player
def switch_player(current_player):
    game_state = active_games[current_player.id]
    other_player_id = next(player for player in game_state["players"] if player != current_player.id)
    game_state["current_player"] = other_player_id
    return other_player_id  # Return the new current player ID


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
