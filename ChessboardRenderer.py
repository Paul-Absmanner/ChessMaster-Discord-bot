from PIL import Image, ImageDraw, ImageFont
import chess


class ChessboardRenderer:
    def __init__(self):
        self.square_size = 80
        self.board_size = self.square_size * 8
        self.border_size = 50
        self.total_size = self.board_size + 2 * self.border_size

    def render(self, board):
        # Create the image with a dark background for the border
        img = Image.new("RGB", (self.total_size, self.total_size), "#b58863")  # Dark color for the border background
        draw = ImageDraw.Draw(img)

        # Colors for the squares
        light_color = "#f0d9b5"
        dark_color = "#b58863"

        # Draw the outer black border around the chessboard
        black_border_thickness = 5
        chessboard_start = self.border_size - black_border_thickness
        chessboard_end = self.board_size + self.border_size + black_border_thickness
        draw.rectangle(
            [chessboard_start, chessboard_start, chessboard_end, chessboard_end],
            fill=None,
            outline="black",
            width=black_border_thickness,
        )

        # Draw the chessboard squares
        for rank in range(8):
            for file in range(8):
                x0 = file * self.square_size + self.border_size
                y0 = rank * self.square_size + self.border_size
                x1 = x0 + self.square_size
                y1 = y0 + self.square_size
                color = light_color if (rank + file) % 2 == 0 else dark_color
                draw.rectangle([x0, y0, x1, y1], fill=color)

        # Load font for the pieces and labels
        try:
            piece_font = ImageFont.truetype("arial.ttf", 48)
            label_font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            piece_font = ImageFont.load_default()
            label_font = ImageFont.load_default()

        # Parse the FEN and draw pieces
        rows = board.board_fen().split("/")
        for rank, row in enumerate(rows):
            file = 0
            for char in row:
                if char.isdigit():
                    # Empty squares
                    file += int(char)
                else:
                    # Chess piece
                    x = file * self.square_size + self.border_size + self.square_size // 4
                    y = rank * self.square_size + self.border_size + self.square_size // 4
                    draw.text((x, y), char, fill="black", font=piece_font)
                    file += 1

        # Draw the rank numbers (1-8) on the left and right borders
        for rank in range(8):
            y = rank * self.square_size + self.border_size + self.square_size // 2
            rank_label = str(8 - rank)  # Ranks are in reverse order (8 at top, 1 at bottom)
            # Left side
            draw.text((self.border_size // 4, y - 12), rank_label, fill="white", font=label_font)  # White for contrast
            # Right side
            draw.text((self.total_size - self.border_size + self.border_size // 3, y - 12), rank_label, fill="white", font=label_font)  # White for contrast

        # Draw the file letters (a-h) on the top and bottom borders
        for file in range(8):
            x = file * self.square_size + self.border_size + self.square_size // 2
            file_label = chr(ord('a') + file)  # Files are 'a' to 'h'
            draw.text((x - 10, self.border_size // 4), file_label, fill="white", font=label_font)  # White for contrast
            draw.text((x - 10, self.total_size - self.border_size + self.border_size // 8), file_label, fill="white", font=label_font)  # White for contrast


        # Save the image
        img.save("chessboard.png")
