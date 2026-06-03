def init_board():
    return [
        [-4, -2, -3, -5, -6, -3, -2, -4],
        [-1, -1, -1, -1, -1, -1, -1, -1],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 1,  1,  1,  1,  1,  1,  1,  1],
        [ 4,  2,  3,  5,  6,  3,  2,  4],
    ]

def go(board, dirs, team, square): #dir is list of direction tuples, team is 1 or -1, square is tuple of 2 ints
    possibles = []
    for dir in dirs:
        cy, cx = square[0], square[1]
        while True:
            cy += dir[0]
            cx += dir[1]
            if cy < 0 or cx < 0 or cy >= len(board) or cx >= 8:
                break
            if board[cy][cx] * team > 0: #square occupied by teammate piece
                break
            if board[cy][cx] * team < 0: #enemy team
                possibles.append((cy, cx))
                break
            if board[cy][cx] == 0:
                possibles.append((cy, cx))
    return possibles

def rook(board, team, square):
    return go(board, [(1, 0), (-1, 0), (0, 1), (0, -1)], team, square)

def bishop(board, team, square):
    return go(board, [(1,1),(1,-1),(-1,1),(-1,-1)], team, square)

def queen(board, team, square):
    return rook(board, team, square) + bishop(board, team, square)
import pygame

def check_valid(board, team, square):
    if 0 <= square[0] <= 7 and 0 <= square[1] <= 7 and board[square[0]][square[1]] * team <= 0:
        return True
    return False

def king(board, team, square):
    legal_dirs = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,1),(-1,0),(-1,-1)]
    possibles = []
    for dir in legal_dirs:
        if check_valid(board, team, (square[0] + dir[0], square[1] + dir[1])):
            possibles.append((square[0] + dir[0], square[1] + dir[1]))
    return possibles

def knight(board, team, square):
    legal_dirs = [(2,1), (-2,1), (1,2), (-1,2), (2,-1), (-2,-1),(1,-2),(-1,-2)]
    possibles = []
    for dir in legal_dirs:
        if check_valid(board, team, (square[0] + dir[0], square[1] + dir[1])):
            possibles.append((square[0] + dir[0], square[1] + dir[1]))
    return possibles

def pawn(board, team, square):
    return (min(square[0]+1, 7), square[1]) #fix this later

def get_legal_moves(board, square):
    piece = board[square[0]][square[1]]
    if piece == 0:
        return []  # empty square, no moves

    team = 1 if piece > 0 else -1
    piece_id = abs(piece)

    if piece_id == 1:
        return pawn(board, team, square)
    elif piece_id == 2:  # knight
        return knight(board, team, square)
    elif piece_id == 3:  # bishop
        return bishop(board, team, square)
    elif piece_id == 4:  # rook
        return rook(board, team, square)
    elif piece_id == 5:  # queen
        return queen(board, team, square)
    elif piece_id == 6:  # king
        return king(board, team, square)
    return []

pygame.init()
window = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
pygame.display.set_caption("Chessboard")
board_surface = pygame.Surface(window.get_size())
board_surface.fill((255, 255, 255))
size = (min(window.get_size()) - 20) // 8
start_x, start_y = (window.get_width() - size * 8) // 2, (window.get_height() - size * 8) // 2
board_rect = pygame.Rect(start_x, start_y, size * 8, size * 8)

for y in range(8):
    for x in range(8):
        color = (240, 217, 181) if (x + y) % 2 == 0 else (181, 136, 99)
        pygame.draw.rect(board_surface, color, (start_x + x * size, start_y + y * size, size, size))

import sys
import os
def resource_path(relative):
    if hasattr(sys, '_MEIPASS'): # this is so when we use pyinstaller to pack there are no errors
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath('.'), relative)
piece_files = {
     1: 'white_pawn.png',   2: 'white_knight.png', 3: 'white_bishop.png',
     4: 'white_rook.png',   5: 'white_queen.png',  6: 'white_king.png',
    -1: 'black_pawn.png',  -2: 'black_knight.png', -3: 'black_bishop.png',
    -4: 'black_rook.png',  -5: 'black_queen.png',  -6: 'black_king.png',
}

images = {}
for val, filename in piece_files.items():
    path = resource_path(os.path.join('pieces', filename))
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.smoothscale(img, (size - 4, size - 4))
    images[val] = img


def get_grid_center(i, j):
    x = board_rect.left + board_rect.width // 8 * i + board_rect.width // 16
    y = board_rect.top + board_rect.height // 8 * (7 - j) + board_rect.height // 16
    return x, y


board = init_board()

pieces = []
for row_idx, row in enumerate(board):
    for col_idx, val in enumerate(row):
        if val != 0:
            j = 7 - row_idx
            img = images[val]
            rect = img.get_rect(center=get_grid_center(col_idx, j))
            pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})

run = True
while run:
    clock.tick(60)
    event_list = pygame.event.get()

    for event in event_list:
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 3: #right click to drop piece
                for piece in pieces:
                    if piece['dragging']:
                        piece['dragging'] = False
                        piece['rect'].center = piece['start_center']
                        piece.pop('start_cell', None)
                        piece.pop('start_center', None)
                        break
            elif event.button == 1:
                for piece in reversed(pieces):
                    if piece['rect'].collidepoint(event.pos):
                        piece['dragging'] = True
                        piece['rel_pos'] = (event.pos[0] - piece['rect'].x, event.pos[1] - piece['rect'].y)

                        old_i = max(0, min(7, (piece['rect'].centerx - board_rect.left) // (board_rect.width // 8)))
                        old_j = 7 - max(0, min(7, (piece['rect'].centery - board_rect.top) // (board_rect.height // 8)))
                        piece['start_cell'] = (old_i, old_j)
                        piece['start_center'] = piece['rect'].center
                        pieces.remove(piece)
                        pieces.append(piece)
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            for piece in pieces:
                if piece['dragging']:
                    piece['dragging'] = False

                    new_i = max(0, min(7, (piece['rect'].centerx - board_rect.left) // (board_rect.width // 8)))
                    new_j = 7 - max(0, min(7, (piece['rect'].centery - board_rect.top) // (board_rect.height // 8)))

                    start_i, start_j = piece.pop('start_cell')

                    board[7 - start_j][start_i] = 0
                    board[7 - new_j][new_i] = piece['value']

                    pieces = []
                    for r_idx, row in enumerate(board):
                        for c_idx, val in enumerate(row):
                            if val != 0:
                                current_j = 7 - r_idx
                                img = images[val]
                                rect = img.get_rect(center=get_grid_center(c_idx, current_j))
                                pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})
                    break

        elif event.type == pygame.MOUSEMOTION:
            for piece in pieces:
                if piece['dragging']:
                    piece['rect'].x = event.pos[0] - piece['rel_pos'][0]
                    piece['rect'].y = event.pos[1] - piece['rel_pos'][1]

    window.blit(board_surface, (0, 0))
    for piece in pieces:
        window.blit(images[piece['value']], piece['rect'])

    pygame.display.flip()

pygame.quit()
exit()