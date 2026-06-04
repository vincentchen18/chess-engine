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

def castle(board, team, square, has_moved):
    moves = []
    row = int(3.5*team+3.5)
    if square != (row, 4): #not on correct starting square
        return []
    king_key = 'white_king' if team == 1 else 'black_king'
    if has_moved[king_key]:
        return []
    if is_check(board, team, square):
        return []

    # kingside castling
    rook_key = 'white_kingside_rook' if team == 1 else 'black_kingside_rook'
    if not has_moved[rook_key] and board[row][7] == team*4: #verify rook not moved and the rook is still there (not captured)
        if board[row][5] == 0 and board[row][6] == 0: # castling squares not blocked
            if not is_check(board, team, (row, 5)) and not is_check(board, team, (row, 6)): #make sure king doesnt castle into or thru check
                moves.append((row, 6))
    rook_key = 'white_queenside_rook' if team == 1 else 'black_queenside_rook'
    if not has_moved[rook_key] and board[row][0] == team*4:
        if board[row][1] == 0 and board[row][2] == 0 and board[row][3] == 0:
            if not is_check(board, team, (row, 3)) and not is_check(board, team, (row, 2)):
                moves.append((row, 2))
    return moves


def knight(board, team, square):
    legal_dirs = [(2,1), (-2,1), (1,2), (-1,2), (2,-1), (-2,-1),(1,-2),(-1,-2)]
    possibles = []
    for dir in legal_dirs:
        if check_valid(board, team, (square[0] + dir[0], square[1] + dir[1])):
            possibles.append((square[0] + dir[0], square[1] + dir[1]))
    return possibles

def pawn(board, team, square, en_passant_square=None):
    possibles = []
    if team == 1: #white, pawns move down indexes
        newsquare = (square[0]-1, square[1])
        if 0 <= newsquare[0] <= 7 and 0 <= newsquare[1] <= 7 and board[newsquare[0]][newsquare[1]] == 0: #can only move on to an empty square
            possibles.append(newsquare)
            newersquare = (newsquare[0]-1, newsquare[1]) #3 conditions: first pawn move, unblocked, front not blocked
            if 0 <= newersquare[0] <= 7 and 0 <= newersquare[1] <= 7 and board[newersquare[0]][newersquare[1]] == 0 and square[0] == 6:
                possibles.append(newersquare)
        # captures, only diagonal
        newsquare1, newsquare2 = (square[0]-1, square[1]+1), (square[0]-1, square[1]-1)
        if check_valid(board, team, newsquare1):
            if board[newsquare1[0]][newsquare1[1]] < 0:
                possibles.append(newsquare1)
        if check_valid(board, team, newsquare2):
            if board[newsquare2[0]][newsquare2[1]] < 0:
                possibles.append(newsquare2)
    elif team == -1:  # black, pawns move up indexes
        newsquare = (square[0]+1, square[1])
        if 0 <= newsquare[0] <= 7 and 0 <= newsquare[1] <= 7 and board[newsquare[0]][newsquare[1]] == 0:  # can only move on to an empty square
            possibles.append(newsquare)
            newersquare = (newsquare[0]+1, newsquare[1])  # 3 conditions: first pawn move, unblocked, front not blocked
            if 0 <= newersquare[0] <= 7 and 0 <= newersquare[1] <= 7 and board[newersquare[0]][newersquare[1]] == 0 and square[0] == 1:
                possibles.append(newersquare)
            # captures, only diagonal
        newsquare1, newsquare2 = (square[0]+1, square[1]+1), (square[0]+1, square[1]-1)
        if check_valid(board, team, newsquare1):
            if board[newsquare1[0]][newsquare1[1]] > 0:
                possibles.append(newsquare1)
        if check_valid(board, team, newsquare2):
            if board[newsquare2[0]][newsquare2[1]] > 0:
                possibles.append(newsquare2)
        #can only move on to an empty square
    if en_passant_target is not None: # en peasant
        if team == 1:  # white captures diagonally up
            for dcol in (-1, 1):
                ep_sq = (square[0] - 1, square[1] + dcol)
                if ep_sq == en_passant_target:
                    possibles.append(ep_sq)
        else:  # black captures diagonally down
            for dcol in (-1, 1):
                ep_sq = (square[0] + 1, square[1] + dcol)
                if ep_sq == en_passant_target:
                    possibles.append(ep_sq)

    return possibles


def is_check(board, team, square):
    attack = rook(board, team, square) # check if attacked by rook or queen
    for coord in attack:
        if board[coord[0]][coord[1]] == -4*team or board[coord[0]][coord[1]] == -5*team:
            return True
    attack = bishop(board, team, square) # check if attacked by bishop or queen
    for coord in attack:
        if board[coord[0]][coord[1]] == -3*team or board[coord[0]][coord[1]] == -5*team:
            return True
    attack = knight(board, team, square) # check if attacked by knight
    for coord in attack:
        if board[coord[0]][coord[1]] == -2*team:
            return True
    attack = pawn(board, team, square)
    for coord in attack:
        if coord[1] != square[1] and board[coord[0]][coord[1]] == -team: # if pawn is on the same column it isn't attacking
            return True
    attack = king(board, team, square)
    for coord in attack:
        if board[coord[0]][coord[1]] == -6*team: #enemy king
            return True
    return False

def get_legal_moves(board, square):
    piece = board[square[0]][square[1]]
    if piece == 0:
        return []  # empty square, no moves

    team = 1 if piece > 0 else -1
    piece_id = abs(piece)
    if piece_id == 1:
        moves = pawn(board, team, square, en_passant_target)
    elif piece_id == 2:  # knight
        moves = knight(board, team, square)
    elif piece_id == 3:  # bishop
        moves = bishop(board, team, square)
    elif piece_id == 4:  # rook
        moves = rook(board, team, square)
    elif piece_id == 5:  # queen
        moves = queen(board, team, square)
    elif piece_id == 6:  # king
        moves = king(board, team, square)
        moves.extend(castle(board, team, square, has_moved))
    legs = []
    for move in moves:
        shadow = [row[:] for row in board]
        shadow[move[0]][move[1]], shadow[square[0]][square[1]] = piece, 0
        if not is_check(shadow, team, [(r, c) for c in range(8) for r in range(8) if shadow[r][c] == team*6][0]):
            legs.append(move)
    return legs

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
current_turn = 1
promoting = None

pieces = []
for row_idx, row in enumerate(board):
    for col_idx, val in enumerate(row):
        if val != 0:
            j = 7 - row_idx
            img = images[val]
            rect = img.get_rect(center=get_grid_center(col_idx, j))
            pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})
has_moved = {
    'white_king':False,
    'white_kingside_rook':False,
    'white_queenside_rook':False,
    'black_king':False,
    'black_kingside_rook':False,
    'black_queenside_rook':False,
}
run = True
en_passant_target = None
while run:
    clock.tick(60)
    event_list = pygame.event.get()

    for event in event_list:
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if promoting is not None and event.button == 1:
                square = promoting['square']
                team = promoting['team']
                options_center = get_grid_center(square[1], 7-square[0])
                options_x, options_y = options_center[0]-size//2, options_center[1]-size//2
                #select q, n, r, or b
                choices = [5,2,4,3]
                direction = 1 if team == 1 else -1
                for index, piece_id in enumerate(choices):
                    option_rectangle = pygame.Rect(options_x, options_y + index * size * direction, size, size)
                    if option_rectangle.collidepoint(event.pos):
                        #selected
                        board[square[0]][square[1]] = piece_id * team
                        promoting = None
                        pieces = []
                        for r_idx, row in enumerate(board):
                            for c_idx, val in enumerate(row):
                                if val != 0:
                                    current_j = 7 - r_idx
                                    img = images[val]
                                    rect = img.get_rect(center=get_grid_center(c_idx, current_j))
                                    pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})
                        current_turn = -current_turn  # change turn
                        break
                continue

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
                        piece_team = 1 if piece['value'] > 0 else -1
                        if piece_team != current_turn: # not your turn! so im not going to let you move the piece.
                            break
                        piece['dragging'] = True
                        piece['rel_pos'] = (event.pos[0] - piece['rect'].x, event.pos[1] - piece['rect'].y)

                        old_i = max(0, min(7, (piece['rect'].centerx - board_rect.left) // (board_rect.width // 8)))
                        old_j = 7 - max(0, min(7, (piece['rect'].centery - board_rect.top) // (board_rect.height // 8)))
                        piece['start_cell'] = (old_i, old_j)
                        piece['start_center'] = piece['rect'].center
                        start_square = (7 - old_j, old_i)
                        piece['legal_moves'] = get_legal_moves(board, start_square)
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
                    start_center = piece.pop('start_center', None)

                    start_square = (7 - start_j, start_i)
                    end_square = (7 - new_j, new_i)

                    legal = get_legal_moves(board, start_square)

                    if end_square in legal and end_square != start_square:
                        moved_piece = piece['value']
                        is_en_passant = abs(moved_piece) == 1 and en_passant_target is not None and end_square == en_passant_target and start_square[1] != end_square[1]
                        # legal move, apply it
                        board[start_square[0]][start_square[1]] = 0
                        board[end_square[0]][end_square[1]] = piece['value']

                        if is_en_passant: # delete the enpassanted pawn
                            captured_pawn_row = start_square[0]
                            captured_pawn_col = end_square[1]
                            board[captured_pawn_row][captured_pawn_col] = 0
                        if abs(moved_piece) == 6 and abs(end_square[1] - start_square[1]) == 2:
                            row = end_square[0]
                            if end_square[1] == 6:  # kingside castle
                                board[row][5] = board[row][7]  # rook from h-file to f-file
                                board[row][7] = 0
                            elif end_square[1] == 2:  # queenside castle
                                board[row][3] = board[row][0]  # rook from a-file to d-file
                                board[row][0] = 0
                        # en peasant logic
                        if abs(moved_piece) == 1 and abs(end_square[0] - start_square[0]) == 2:
                            # pawn moved 2 squares, skip square is captuable
                            en_passant_target = ((start_square[0] + end_square[0]) // 2, start_square[1])
                        else:
                            en_passant_target = None

                        if abs(moved_piece) == 1 and end_square[0] in [0, 7]: #promotion
                            promoting = {'square': end_square, 'team':moved_piece//abs(moved_piece)}
                        # CASTLING VARIABLES
                        if moved_piece == 6:  # white king
                            has_moved['white_king'] = True
                        elif moved_piece == -6:  # black king
                            has_moved['black_king'] = True
                        elif moved_piece == 4:  # white rook
                            if start_square == (7, 0):  # a1
                                has_moved['white_rook_queenside'] = True
                            elif start_square == (7, 7):  # h1
                                has_moved['white_rook_kingside'] = True
                        elif moved_piece == -4:  # black rook
                            if start_square == (0, 0):  # a8
                                has_moved['black_rook_queenside'] = True
                            elif start_square == (0, 7):  # h8
                                has_moved['black_rook_kingside'] = True

                        # finish castling chekcs

                        pieces = []
                        for r_idx, row in enumerate(board):
                            for c_idx, val in enumerate(row):
                                if val != 0:
                                    current_j = 7 - r_idx
                                    img = images[val]
                                    rect = img.get_rect(center=get_grid_center(c_idx, current_j))
                                    pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})
                        if promoting is None:
                            current_turn = -current_turn
                    else:
                        # illegal return to position
                        if start_center is not None:
                            piece['rect'].center = start_center
                    break

        elif event.type == pygame.MOUSEMOTION:
            for piece in pieces:
                if piece['dragging']:
                    piece['rect'].x = event.pos[0] - piece['rel_pos'][0]
                    piece['rect'].y = event.pos[1] - piece['rel_pos'][1]

    window.blit(board_surface, (0, 0))
    for piece in pieces:
        if piece['dragging'] and 'legal_moves' in piece:
            for sq in piece['legal_moves']:
                row, col = sq
                i = col
                j = 7 - row
                center = get_grid_center(i, j)

                # if the destination has an enemy piece, draw a ring instead of a dot
                if board[row][col] == 6 or board[row][col] == -6:
                    pygame.draw.circle(window, (200, 0, 0, 120), center, size // 2 - 4)
                elif board[row][col] != 0:
                    pygame.draw.circle(window, (0, 0, 0, 120), center, size // 2 - 4, 5)
                else:
                    pygame.draw.circle(window, (0, 0, 0, 120), center, size // 6.5)
    for piece in pieces:
        window.blit(images[piece['value']], piece['rect'])
    if promoting is not None:
        square = promoting['square']
        team = promoting['team']
        options_center = get_grid_center(square[1], 7 - square[0])
        options_x, options_y = options_center[0] - size // 2, options_center[1] - size // 2
        choices = [5, 2, 4, 3]
        direction = 1 if team == 1 else -1
        for index, piece_id in enumerate(choices):
            option_rectangle = pygame.Rect(options_x, options_y + index * size * direction, size, size)
            pygame.draw.rect(window, (250, 250, 250), option_rectangle)
            pygame.draw.rect(window, (50, 50, 50), option_rectangle, 2)
            img = images[piece_id * team]
            window.blit(img, img.get_rect(center=option_rectangle.center))
    pygame.display.flip()

pygame.quit()
exit()