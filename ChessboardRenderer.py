from PIL import Image, ImageDraw, ImageFont
import chess

class ChessboardRenderer:
    def __init__(self):
        self.board_base = "images/chessboard_empty.png"  # Path to the base board
        self.piece_images = {
            'P': "images/white_pawn.png",
            'N': "images/white_knight.png",
            'B': "images/white_bishop.png",
            'R': "images/white_rook.png",
            'Q': "images/white_queen.png",
            'K': "images/white_king.png",
            'p': "images/black_pawn.png",
            'n': "images/black_knight.png",
            'b': "images/black_bishop.png",
            'r': "images/black_rook.png",
            'q': "images/black_queen.png",
            'k': "images/black_king.png",
        }
        self.square_size = 80  # Pixel size of each square (adjust as needed)
        self.padding = 50      # Add padding if the board image has margins
    
    def render(self, board: chess.Board):
        # Load the base board image
        base_image = Image.open(self.board_base)
        draw = ImageDraw.Draw(base_image)

        # Iterate through all squares on the board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_symbol = piece.symbol()
                piece_image_path = self.piece_images[piece_symbol]
                piece_image = Image.open(piece_image_path).resize(
                    (self.square_size, self.square_size)
                )
                
                # Calculate position on the board
                col = square % 8
                row = 7 - (square // 8)  # Flip row for chessboard representation
                
                # Adjust for padding/margin
                x = self.padding + col * self.square_size
                y = self.padding + row * self.square_size

                # Paste the piece image onto the board
                base_image.paste(piece_image, (x, y), piece_image)

        # Save the final board image
        base_image.save("images/chessboard.png")