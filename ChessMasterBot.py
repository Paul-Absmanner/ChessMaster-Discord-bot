import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os
import json
import chess
from ChessboardRenderer import ChessboardRenderer

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

active_games = {}
renderer = ChessboardRenderer()

player_stats = {}
STATS_FILE = "stats.json"


def load_stats_from_json(filename: str):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        return {}


def save_stats_to_json(data: dict, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def init_player_in_stats(player_id: str):
    if str(player_id) not in player_stats:
        player_stats[str(player_id)] = {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0
        }

PIECE_TYPES = {
    "Pawn": chess.PAWN,
    "Bishop": chess.BISHOP,
    "Knight": chess.KNIGHT,
    "Rook": chess.ROOK,
    "Queen": chess.QUEEN,
    "King": chess.KING
}


@bot.tree.command(
    name="start_chess",
    description="Start a chess game with another player",
    guild=discord.Object(id=int(GUILD_ID))
)
async def start_chess(interaction: discord.Interaction, opponent: discord.Member):
    if interaction.user.id == opponent.id:
        await interaction.response.send_message("You cannot play against yourself!", ephemeral=True)
        return

    if interaction.user.id in active_games or opponent.id in active_games:
        await interaction.response.send_message("Either you or the opponent is already in a game!", ephemeral=True)
        return

    board = chess.Board()
    active_games[interaction.user.id] = {
        "board": board,
        "current_player": interaction.user.id,
        "players": {
            interaction.user.id: "white",
            opponent.id: "black"
        },
        "board_message": None
    }
    active_games[opponent.id] = active_games[interaction.user.id]

    renderer.render(board)
    await interaction.response.send_message(
        f"**Game Started!**\n:white_circle: {interaction.user.mention} is **White**\n:black_circle: {opponent.mention} is **Black**",
        file=discord.File("images/chessboard.png")
    )
    sent_msg = await interaction.original_response()
    active_games[interaction.user.id]["board_message"] = sent_msg

    await show_piece_selection(interaction, interaction.user.id)


async def show_piece_selection(interaction: discord.Interaction, player_id: int):
    if player_id not in active_games:
        return

    game_state = active_games[player_id]
    board = game_state["board"]
    current_player_id = game_state["current_player"]

    if current_player_id != player_id:
        return

    guild = interaction.guild
    player = guild.get_member(player_id) or await guild.fetch_member(player_id)

    view = View()

    for piece_name, piece_type in PIECE_TYPES.items():
        has_legal_moves = any(
            board.piece_at(move.from_square) is not None
            and board.piece_at(move.from_square).piece_type == piece_type
            for move in board.legal_moves
        )
        button = Button(
            label=piece_name,
            style=discord.ButtonStyle.primary,
            disabled=not has_legal_moves
        )

        async def piece_callback(i: discord.Interaction, piece_type=piece_type):
            if i.user.id != current_player_id:
                await i.response.send_message("It's not your turn!", ephemeral=True)
                return
            await i.response.defer()
            await show_move_options(i, player, piece_type)

        button.callback = piece_callback
        view.add_item(button)

    # Offer Draw (Remi)
    remi_button = Button(label="Remi (Offer Draw)", style=discord.ButtonStyle.secondary)
    remi_button.callback = lambda i: offer_draw(i, player_id)
    view.add_item(remi_button)

    # Surrender
    surrender_button = Button(label="Surrender", style=discord.ButtonStyle.danger)
    surrender_button.callback = lambda i: surrender(i, player_id)
    view.add_item(surrender_button)

    await interaction.edit_original_response(
        content=f"{player.mention}, select a piece type to move or offer Remi/Surrender:",
        view=view
    )


async def show_move_options(interaction, player, piece_type):
    if player.id not in active_games:
        return

    game_state = active_games[player.id]
    board = game_state["board"]
    current_player_id = game_state["current_player"]
    if current_player_id != player.id:
        return

    legal_moves = [
        m for m in board.legal_moves
        if board.piece_at(m.from_square) and board.piece_at(m.from_square).piece_type == piece_type
    ]

    if not legal_moves:
        await interaction.followup.send("No legal moves for this piece type!", ephemeral=True)
        return

    view = View()
    for move in legal_moves:
        button_label = f"{chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}"
        button = Button(label=button_label, style=discord.ButtonStyle.success)

        async def move_callback(i: discord.Interaction, m=move):
            if i.user.id != current_player_id:
                await i.response.send_message("It's not your turn!", ephemeral=True)
                return

            board.push(m)
            renderer.render(board)

            # Check if game is over
            if board.is_game_over():
                if board.is_checkmate():
                    winner_id = i.user.id
                    loser_id = next(x for x in game_state["players"] if x != winner_id)
                    await end_game_checkmate(winner_id, loser_id, i, m)
                else:
                    # stalemate => draw
                    w_id, b_id = list(game_state["players"].keys())
                    await end_game_draw(w_id, b_id, i, is_stalemate=True)
                return
            else:
                next_player_id = switch_player(player)
                await i.response.edit_message(
                    content=f"{player.mention} moved {chess.square_name(m.from_square)} -> {chess.square_name(m.to_square)}",
                    attachments=[discord.File("images/chessboard.png")],
                    view=None
                )
                if next_player_id in active_games:
                    await show_piece_selection(i, next_player_id)

        button.callback = move_callback
        view.add_item(button)

    await interaction.followup.edit_message(
        message_id=interaction.message.id,
        content="Select your move:",
        view=view
    )


# ---------------------
# Draw and Surrender
# ---------------------

async def offer_draw(interaction: discord.Interaction, player_id: int):
    if player_id not in active_games:
        return

    game_state = active_games[player_id]
    if interaction.user.id != game_state["current_player"]:
        await interaction.response.send_message("It's not your turn!", ephemeral=True)
        return

    await interaction.response.defer()
    opp_id = next(pid for pid in game_state["players"] if pid != player_id)
    opponent = interaction.guild.get_member(opp_id) or await interaction.guild.fetch_member(opp_id)
    player = interaction.guild.get_member(player_id) or await interaction.guild.fetch_member(player_id)

    view_remi = View()
    accept_btn = Button(label="Accept Draw", style=discord.ButtonStyle.success)
    deny_btn = Button(label="Deny Draw", style=discord.ButtonStyle.danger)

    async def accept_draw_callback(i: discord.Interaction):
        if i.user.id != opp_id:
            await i.response.send_message("Only the opponent can accept/deny!", ephemeral=True)
            return
        w_id, b_id = list(game_state["players"].keys())
        await end_game_draw(w_id, b_id, i, is_stalemate=False)

    async def deny_draw_callback(i: discord.Interaction):
        if i.user.id != opp_id:
            await i.response.send_message("Only the opponent can accept/deny!", ephemeral=True)
            return
        await i.response.edit_message(
            content=f"{opponent.mention} denied the draw. The game continues.",
            view=None
        )

    accept_btn.callback = accept_draw_callback
    deny_btn.callback = deny_draw_callback
    view_remi.add_item(accept_btn)
    view_remi.add_item(deny_btn)

    await interaction.followup.send(
        content=f"{player.mention} has offered a draw. {opponent.mention}, do you accept?",
        view=view_remi
    )


async def surrender(interaction: discord.Interaction, player_id: int):
    if player_id not in active_games:
        return

    game_state = active_games[player_id]
    if interaction.user.id != game_state["current_player"]:
        await interaction.response.send_message("It's not your turn!", ephemeral=True)
        return

    opp_id = next(pid for pid in game_state["players"] if pid != player_id)
    await end_game_surrender(loser_id=interaction.user.id, winner_id=opp_id, interaction=interaction)


# ---------------------
# Ending the Game
# ---------------------

async def end_game_checkmate(winner_id: int, loser_id: int, interaction: discord.Interaction, move: chess.Move):
    """Called when checkmate is detected. Show final board, stats, etc."""
    game_state = active_games.get(winner_id) or active_games.get(loser_id)
    board = game_state["board"]
    # Re-render final board
    renderer.render(board)

    winner = interaction.guild.get_member(winner_id)
    loser = interaction.guild.get_member(loser_id)

    # Edit the *interaction message* (the last move's message) to show final board
    await interaction.response.edit_message(
        content=f"Checkmate! {winner.mention} wins! ({chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)})",
        attachments=[discord.File("images/chessboard.png")],
        view=None
    )

    # Update stats
    init_player_in_stats(str(winner_id))
    init_player_in_stats(str(loser_id))
    player_stats[str(winner_id)]["wins"] += 1
    player_stats[str(loser_id)]["losses"] += 1
    player_stats[str(winner_id)]["games_played"] += 1
    player_stats[str(loser_id)]["games_played"] += 1
    save_stats_to_json(player_stats, STATS_FILE)

    # Disable the main board message with a final note
    await disable_game_view(game_state, content=f"Game ended. {winner.mention} is the winner!")

    # Remove from active_games
    for pid in list(game_state["players"].keys()):
        active_games.pop(pid, None)


async def end_game_draw(white_id: int, black_id: int, interaction: discord.Interaction, is_stalemate=False):
    game_state = active_games.get(white_id) or active_games.get(black_id)
    board = game_state["board"]
    renderer.render(board)

    white = interaction.guild.get_member(white_id)
    black = interaction.guild.get_member(black_id)

    if is_stalemate:
        content_text = f"Stalemate! {white.mention} and {black.mention} draw."
    else:
        content_text = f"{white.mention} and {black.mention} have agreed to a draw."

    await interaction.response.edit_message(
        content=content_text,
        attachments=[discord.File("images/chessboard.png")],
        view=None
    )

    # Update stats
    init_player_in_stats(str(white_id))
    init_player_in_stats(str(black_id))
    player_stats[str(white_id)]["draws"] += 1
    player_stats[str(black_id)]["draws"] += 1
    player_stats[str(white_id)]["games_played"] += 1
    player_stats[str(black_id)]["games_played"] += 1
    save_stats_to_json(player_stats, STATS_FILE)

    await disable_game_view(game_state, content="Game ended in a draw!")
    for pid in list(game_state["players"].keys()):
        active_games.pop(pid, None)


async def end_game_surrender(loser_id: int, winner_id: int, interaction: discord.Interaction):
    game_state = active_games.get(loser_id) or active_games.get(winner_id)
    board = game_state["board"]
    renderer.render(board)

    loser = interaction.guild.get_member(loser_id)
    winner = interaction.guild.get_member(winner_id)

    await interaction.response.edit_message(
        content=f"{loser.mention} has surrendered! {winner.mention} wins!",
        attachments=[discord.File("images/chessboard.png")],
        view=None
    )

    init_player_in_stats(str(loser_id))
    init_player_in_stats(str(winner_id))
    player_stats[str(loser_id)]["losses"] += 1
    player_stats[str(winner_id)]["wins"] += 1
    player_stats[str(loser_id)]["games_played"] += 1
    player_stats[str(winner_id)]["games_played"] += 1
    save_stats_to_json(player_stats, STATS_FILE)

    await disable_game_view(game_state, content=f"Game ended. {winner.mention} wins by surrender!")
    for pid in list(game_state["players"].keys()):
        active_games.pop(pid, None)


async def disable_game_view(game_state: dict, content: str = None):
    """
    Edits the main board message: sets a final 'Game ended' text
    and removes all buttons by setting view=None.
    Optionally includes the final board image if you want.
    """
    if not game_state:
        return
    msg = game_state.get("board_message")
    if not msg:
        return

    final_content = content if content else "Game ended."
    try:
       
        await msg.edit(
            content=final_content,
            view=None
        )
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        pass


def switch_player(current_player):
    game_state = active_games[current_player.id]
    other_player_id = next(pid for pid in game_state["players"] if pid != current_player.id)
    game_state["current_player"] = other_player_id
    return other_player_id


@bot.tree.command(name="stats", description="Show your or another player's chess stats.", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(user="The user you want to see stats for (optional).")
async def stats_command(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user

    uid = str(user.id)
    if uid not in player_stats:
        await interaction.response.send_message(
            f"{user.mention} has no recorded stats yet."
        )
        return

    s = player_stats[uid]
    await interaction.response.send_message(
        f"**{user.display_name}**'s stats:\n"
        f"- Games Played: {s['games_played']}\n"
        f"- Wins: {s['wins']}\n"
        f"- Losses: {s['losses']}\n"
        f"- Draws: {s['draws']}"
    )


@bot.event
async def on_ready():
    global player_stats
    player_stats = load_stats_from_json(STATS_FILE)
    print(f"Bot ready. Stats loaded from {STATS_FILE}.")

    try:
        guild = discord.Object(id=int(GUILD_ID))
        synced = await bot.tree.sync(guild=guild)
        print(f"Slash commands synced: {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")


bot.run(TOKEN)
