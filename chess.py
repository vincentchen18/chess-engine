def make_state():
    return {
        'board': init_board(),
        'turn': 1,
        'has_moved': {
            'white_king': False, 'white_kingside_rook': False, 'white_queenside_rook': False,
            'black_king': False, 'black_kingside_rook': False, 'black_queenside_rook': False,
        },
        'en_passant_target': None,
    }


def clone_state(state):
    return {
        'board': [row[:] for row in state['board']],
        'turn': state['turn'],
        'has_moved': dict(state['has_moved']),
        'en_passant_target': state['en_passant_target'],
    }

def position_hash(state):
    board_tuple = tuple(tuple(row) for row in state['board'])
    has_moved_tuple = tuple(sorted(state['has_moved'].items()))
    return (board_tuple, state['turn'], has_moved_tuple, state['en_passant_target']) #for 3fold repetition checking

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

def pawn(board, team, square, en_passant_target=None):
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

def get_legal_moves(state, square):
    board = state['board']
    piece = board[square[0]][square[1]]
    if piece == 0:
        return []  # empty square, no moves

    team = 1 if piece > 0 else -1
    piece_id = abs(piece)
    if piece_id == 1:
        moves = pawn(board, team, square, state['en_passant_target'])
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
        moves.extend(castle(board, team, square, state['has_moved']))
    legs = []
    for move in moves:
        shadow = [row[:] for row in board]
        shadow[move[0]][move[1]], shadow[square[0]][square[1]] = piece, 0
        if not is_check(shadow, team, [(r, c) for c in range(8) for r in range(8) if shadow[r][c] == team*6][0]):
            legs.append(move)
    return legs

def has_legal_moves(state, team):
    board = state['board']
    for r in range(8):
        for c in range(8):
            if board[r][c] * team > 0: #teammate piece
                if get_legal_moves(state, (r, c)):
                    return True
    return False

def get_all_moves(state):
    board = state['board']
    team = state['turn']
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c] * team > 0:
                for endsquare in get_legal_moves(state, (r,c)):
                    if abs(board[r][c]) == 1 and endsquare[0] in (0, 7):
                        for promote_to in (5, 4, 3, 2):  # each promotion is a different move.
                            moves.append(((r, c), endsquare, promote_to))
                    else:
                        moves.append(((r, c), endsquare, None))
    return moves

def apply_move(state, start, end, promote_to=None):
    board = state['board']
    piece = board[start[0]][start[1]]

    # en passant capture detection
    is_ep = (abs(piece) == 1
             and state['en_passant_target'] == end
             and start[1] != end[1])

    # normal move
    board[end[0]][end[1]] = piece
    board[start[0]][start[1]] = 0

    # remove en passant captured pawn
    if is_ep:
        board[start[0]][end[1]] = 0

    # castling: move rook
    if abs(piece) == 6 and abs(end[1] - start[1]) == 2:
        row = end[0]
        if end[1] == 6:
            board[row][5] = board[row][7]
            board[row][7] = 0
        elif end[1] == 2:
            board[row][3] = board[row][0]
            board[row][0] = 0

    # castling bookeeping
    if piece == 6:
        state['has_moved']['white_king'] = True
    elif piece == -6:
        state['has_moved']['black_king'] = True
    elif piece == 4:
        if start == (7, 0):
            state['has_moved']['white_queenside_rook'] = True
        elif start == (7, 7):
            state['has_moved']['white_kingside_rook'] = True
    elif piece == -4:
        if start == (0, 0):
            state['has_moved']['black_queenside_rook'] = True
        elif start == (0, 7):
            state['has_moved']['black_kingside_rook'] = True

    # promotion
    if promote_to is not None:
        board[end[0]][end[1]] = promote_to * (1 if piece > 0 else -1)

    if abs(piece) == 1 and abs(end[0] - start[0]) == 2:
        state['en_passant_target'] = ((start[0] + end[0]) // 2, start[1])
    else:
        state['en_passant_target'] = None

    # flip turn
    state['turn'] = -state['turn']

def insufficient_material(state):
    board = state['board']
    white_pieces = []
    black_pieces = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece > 0 and piece != 6:  # white non-king
                white_pieces.append((piece, r, c))
            elif piece < 0 and piece != -6:  # black non-king
                black_pieces.append((piece, r, c))

    # any pawn, rook, queen so mate is possible so not over yet
    for p, _, _ in white_pieces + black_pieces:
        if abs(p) in (1, 4, 5):
            return False

    # only minor pieces (knights/bishops) and kings left
    # K vs K
    if len(white_pieces) == 0 and len(black_pieces) == 0:
        return True
    # K+minor vs K
    if len(white_pieces) == 1 and len(black_pieces) == 0:
        return True
    if len(white_pieces) == 0 and len(black_pieces) == 1:
        return True
    # K+B vs K+B with bishops on same color
    if len(white_pieces) == 1 and len(black_pieces) == 1:
        wp, wr, wc = white_pieces[0]
        bp, br, bc = black_pieces[0]
        if abs(wp) == 3 and abs(bp) == 3:  # both bishops
            if (wr + wc) % 2 == (br + bc) % 2:  # same color squares
                return True
    return False

# pst (piece square tables), make the pieces give less points if they're on bad squares and more points if good squares

pawn_pst = [
    [  0,   0,   0,   0,   0,   0,   0,   0],
    [ 110,  120,  120,  120,  120,  120,  120,  110],
    [ 30,  45,  55,  60,  60,  55,  45,  30],
    [ 10,  25,  35,  50,  50,  35,  25,  10],
    [  5,  10,  20,  40,  40,  20,  10,   5],
    [  0,   0,  10,  20,  20,  10,   0,   0],
    [  -5,  -5, -10,   0,   0,  5,  -5,   -5],
    [  0,   0,   0,   0,   0,   0,   0,   0],
]

knight_pst = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  20,  25,  25,  20,   0, -30],
    [-30,   5,  20,  25,  25,  20,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

bishop_pst = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

rook_pst = [
    [  0,   0,   0,   5,   5,   0,   0,   0],
    [ 10,  20,  20,  20,  20,  20,  20,  10],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [  0,   0,   0,   5,   5,   0,   0,   0],
]

queen_pst = [
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,   5,   5,   5,   0, -10],
    [ -5,   0,   5,   5,   5,   5,   0,  -5],
    [  0,   0,   5,   5,   5,   5,   0,  -5],
    [-10,   5,   5,   5,   5,   5,   0, -10],
    [-10,   0,   5,   0,   0,   0,   0, -10],
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
]

king_pst_opening = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [ 20,  20,   0,   0,   0,   0,  20,  20],
    [ 20,  30,  10,   0,   0,  10,  30,  20],
]

king_pst_endgame = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]

pst_tables = {
    1: pawn_pst,
    2: knight_pst,
    3: bishop_pst,
    4: rook_pst,
    5: queen_pst,
}

# ==== me make bot code here ===== #
piece_values = {1: 100, 2: 320, 3: 330, 4: 500, 5: 920, 6: 20000}

def evaluate(state):
    # eval>0 is good for white, eval<0 good for black
    # basic evaluation that only compares material, will add more stuff like king safety and mobility later
    score = 0
    board = state['board']
    material = 0
    for row in board:
        for piece in row:
            if piece != 0:
                material += piece_values[abs(piece)]
    material -= 40000
    is_endgame = material < 2400
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == 0:
                continue
            team = piece // abs(piece)
            piece_id = abs(piece)
            score += piece_values[piece_id] * team
            if piece_id == 6: #king use different pst for opening or endgame
                pst = king_pst_endgame if is_endgame else king_pst_opening
            else:
                pst = pst_tables[piece_id]
            pst_row = r if team == 1 else 7 - r
            score += pst[pst_row][c] * team
    return score
import math
def order_moves(state, moves):
    board = state['board']
    def score(move):
        start, end, _ = move
        captured = board[end[0]][end[1]]
        if captured != 0:
            attacker = board[start[0]][start[1]]
            return piece_values[abs(captured)] * 10 - piece_values[abs(attacker)]
        return 0
    return sorted(moves, key=score, reverse=True)

def quiescence(state, alpha, beta):
    curr_eval = evaluate(state)
    if state['turn'] == 1: # mini-minimax
        if curr_eval >= beta:
            return beta
        if curr_eval > alpha:
            alpha = curr_eval
    else:
        if curr_eval <= alpha:
            return alpha
        if curr_eval < beta:
            beta = curr_eval
    board = state['board']
    moves = get_all_moves(state)
    captures = [m for m in moves if board[m[1][0]][m[1][1]] != 0]
    captures = order_moves(state, captures)

    for move in captures:
        new_state = clone_state(state)
        apply_move(new_state, move[0], move[1], move[2])
        score = quiescence(new_state, alpha, beta)

        if state['turn'] == 1:
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        else:
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score

    return alpha if state['turn'] == 1 else beta

def minimax(state, depth, alpha, beta, counts): #alpha beta prune (like the connect4 engine)
    if depth == 0:
        return quiescence(state, alpha, beta), None
    if counts.get(position_hash(state), 0) >= 3:
        return 0, None
    moves = order_moves(state, get_all_moves(state))
    if not moves:
        king_pos = [(r, c) for r in range(8) for c in range(8) if state['board'][r][c] == state['turn']*6][0]
        if is_check(state['board'], state['turn'], king_pos):
            return (-100000 - depth) * state['turn'], None # checkmate, subtract depth so bot prefers faster mates
        else:
            return 0, None
    if insufficient_material(state):
        return 0, None

    best_move = None
    if state['turn'] == 1: #white, play move that maximises eval
        max_eval = float('-inf')
        for move in moves:
            newstate = clone_state(state)
            apply_move(newstate, move[0], move[1], move[2])
            new_counts = dict(counts)
            new_key = position_hash(newstate)
            new_counts[new_key] = new_counts.get(new_key, 0) + 1
            eval_score, useless_variable = minimax(newstate, depth - 1, alpha, beta, new_counts)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else: #black, play move that minimises eval
        min_eval = math.inf
        for move in moves:
            newstate = clone_state(state)
            apply_move(newstate, move[0], move[1], move[2])
            new_counts = dict(counts)
            new_key = position_hash(newstate)
            new_counts[new_key] = new_counts.get(new_key, 0) + 1
            eval_score, useless_variable = minimax(newstate, depth - 1, alpha, beta, new_counts)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, min_eval)
            if beta <= alpha:
                break
        return min_eval, best_move


def show_menu():
    font = pygame.font.SysFont(None, 40)
    small_font = pygame.font.SysFont(None, 28)

    white_choice = 'human'
    black_choice = 'bot'

    # button rects
    white_human = pygame.Rect(80, 150, 150, 50)
    white_bot = pygame.Rect(270, 150, 150, 50)
    black_human = pygame.Rect(80, 250, 150, 50)
    black_bot = pygame.Rect(270, 250, 150, 50)
    start_btn = pygame.Rect(175, 380, 150, 60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if white_human.collidepoint(event.pos):
                    white_choice = 'human'
                elif white_bot.collidepoint(event.pos):
                    white_choice = 'bot'
                elif black_human.collidepoint(event.pos):
                    black_choice = 'human'
                elif black_bot.collidepoint(event.pos):
                    black_choice = 'bot'
                elif start_btn.collidepoint(event.pos):
                    return white_choice, black_choice

        window.fill((40, 40, 60))

        # title
        title = font.render("Chess Engine", True, (240, 240, 240))
        window.blit(title, title.get_rect(center=(250, 60)))

        # white row
        label = small_font.render("White:", True, (240, 240, 240))
        window.blit(label, (20, 165))

        for rect, label, val in [(white_human, "Human", 'human'), (white_bot, "Bot", 'bot')]:
            color = (100, 180, 100) if white_choice == val else (80, 80, 100)
            pygame.draw.rect(window, color, rect, border_radius=8)
            text = small_font.render(label, True, (255, 255, 255))
            window.blit(text, text.get_rect(center=rect.center))

        # black row
        label = small_font.render("Black:", True, (240, 240, 240))
        window.blit(label, (20, 265))

        for rect, label, val in [(black_human, "Human", 'human'), (black_bot, "Bot", 'bot')]:
            color = (100, 180, 100) if black_choice == val else (80, 80, 100)
            pygame.draw.rect(window, color, rect, border_radius=8)
            text = small_font.render(label, True, (255, 255, 255))
            window.blit(text, text.get_rect(center=rect.center))

        # start button
        pygame.draw.rect(window, (180, 140, 60), start_btn, border_radius=8)
        text = font.render("Start", True, (255, 255, 255))
        window.blit(text, text.get_rect(center=start_btn.center))

        pygame.display.flip()



def make_red_glow(s): #make a special ring for the loser king
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    center = (s // 2, s // 2)
    max_radius = s // 2

    # draw rings from outside in, each one more opaque
    steps = 20
    for i in range(steps):
        radius = max_radius * (steps - i) // steps
        alpha = int(180 * (i / steps) ** 2)  # quadratic falloff = smoother gradient
        pygame.draw.circle(surf, (255, 50, 50, alpha), center, radius)

    return surf

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
 # import assets from pieces/
images = {}
for val, filename in piece_files.items():
    path = resource_path(os.path.join('pieces', filename))
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.smoothscale(img, (size - 4, size - 4))
    images[val] = img
icon_files = {
    'crown': 'crown.png',
    'half':  'half.png',
    'hash':  'hash.png',
}
icons = {}
for name, filename in icon_files.items():
    path = resource_path(os.path.join('pieces', filename))
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.smoothscale(img, (size // 3, size // 3))
    icons[name] = img


def get_grid_center(i, j):
    x = board_rect.left + board_rect.width // 8 * i + board_rect.width // 16
    y = board_rect.top + board_rect.height // 8 * (7 - j) + board_rect.height // 16
    return x, y

import threading # vinniebot thinks too slow >:((((((
state = make_state()
white_player,black_player = show_menu()
promoting = None
game_over = None
loser_team = None
vinniebot_thread = None
vinniebot_result = None
run = True
position_counts = {}
position_counts[position_hash(state)] = 1
def vinniebot_think(state_copy):
    global vinniebot_result
    counts_copy = dict(position_counts)
    useless_variable, move = minimax(state_copy, 4, -math.inf, math.inf, counts_copy)
    vinniebot_result = move

pieces = []
for row_idx, row in enumerate(state['board']):
    for col_idx, val in enumerate(row):
        if val != 0:
            j = 7 - row_idx
            img = images[val]
            rect = img.get_rect(center=get_grid_center(col_idx, j))
            pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})

while run:
    clock.tick(60)
    event_list = pygame.event.get()

    for event in event_list:
        if event.type == pygame.QUIT:
            run = False
        if vinniebot_thread is not None:
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                continue

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
                        state['board'][square[0]][square[1]] = piece_id * team
                        promoting = None
                        pieces = []
                        for r_idx, row in enumerate(state['board']):
                            for c_idx, val in enumerate(row):
                                if val != 0:
                                    current_j = 7 - r_idx
                                    img = images[val]
                                    rect = img.get_rect(center=get_grid_center(c_idx, current_j))
                                    pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})
                        state['turn'] = -state['turn']  # change turn
                        key = position_hash(state)
                        position_counts[key] = position_counts.get(key, 0) + 1
                        current_player = white_player if state['turn'] == 1 else black_player
                        # check check/stale mate
                        if position_counts.get(position_hash(state), 0) >= 3:
                            game_over = 'stalemate'
                        elif not has_legal_moves(state, state['turn']):
                            king_pos = [(r, c) for r in range(8) for c in range(8) if state['board'][r][c] == state['turn'] * 6][0]
                            if is_check(state['board'], state['turn'], king_pos):
                                game_over = 'checkmate'
                                loser_team = state['turn']  # they can't move AND are in check
                            else:
                                game_over = 'stalemate'  # can't move but not in check
                        current_player = white_player if state['turn'] == 1 else black_player
                        if game_over is None and current_player == 'bot': #vinniebot's turn
                            if vinniebot_thread is None:
                                vinniebot_result = None
                                state_copy = clone_state(state)
                                vinniebot_thread = threading.Thread(target=vinniebot_think, args=(state_copy,))
                                vinniebot_thread.start()
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
                current_player = white_player if state['turn'] == 1 else black_player
                if current_player == 'bot':
                    break
                for piece in reversed(pieces):
                    if piece['rect'].collidepoint(event.pos):
                        piece_team = 1 if piece['value'] > 0 else -1
                        if piece_team != state['turn']: # not your turn! so im not going to let you move the piece.
                            break
                        piece['dragging'] = True
                        piece['rel_pos'] = (event.pos[0] - piece['rect'].x, event.pos[1] - piece['rect'].y)

                        old_i = max(0, min(7, (piece['rect'].centerx - board_rect.left) // (board_rect.width // 8)))
                        old_j = 7 - max(0, min(7, (piece['rect'].centery - board_rect.top) // (board_rect.height // 8)))
                        piece['start_cell'] = (old_i, old_j)
                        piece['start_center'] = piece['rect'].center
                        start_square = (7 - old_j, old_i)
                        piece['legal_moves'] = get_legal_moves(state, start_square)
                        pieces.remove(piece)
                        pieces.append(piece)
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if game_over:
                continue
            for piece in pieces:
                if piece['dragging']:
                    piece['dragging'] = False

                    new_i = max(0, min(7, (piece['rect'].centerx - board_rect.left) // (board_rect.width // 8)))
                    new_j = 7 - max(0, min(7, (piece['rect'].centery - board_rect.top) // (board_rect.height // 8)))

                    start_i, start_j = piece.pop('start_cell')
                    start_center = piece.pop('start_center', None)

                    start_square = (7 - start_j, start_i)
                    end_square = (7 - new_j, new_i)

                    legal = get_legal_moves(state, start_square)

                    if end_square in legal and end_square != start_square:
                        moved_piece = piece['value']
                        is_en_passant = abs(moved_piece) == 1 and state['en_passant_target'] is not None and end_square == state['en_passant_target'] and start_square[1] != end_square[1]
                        # legal move, apply it
                        state['board'][start_square[0]][start_square[1]] = 0
                        state['board'][end_square[0]][end_square[1]] = piece['value']

                        if is_en_passant: # delete the enpassanted pawn
                            captured_pawn_row = start_square[0]
                            captured_pawn_col = end_square[1]
                            state['board'][captured_pawn_row][captured_pawn_col] = 0
                        if abs(moved_piece) == 6 and abs(end_square[1] - start_square[1]) == 2:
                            row = end_square[0]
                            if end_square[1] == 6:  # kingside castle
                                state['board'][row][5] = state['board'][row][7]  # rook from h-file to f-file
                                state['board'][row][7] = 0
                            elif end_square[1] == 2:  # queenside castle
                                state['board'][row][3] = state['board'][row][0]  # rook from a-file to d-file
                                state['board'][row][0] = 0
                        # en peasant logic
                        if abs(moved_piece) == 1 and abs(end_square[0] - start_square[0]) == 2:
                            # pawn moved 2 squares, skip square is captuable
                            state['en_passant_target'] = ((start_square[0] + end_square[0]) // 2, start_square[1])
                        else:
                            state['en_passant_target'] = None

                        if abs(moved_piece) == 1 and end_square[0] in [0, 7]: #promotion
                            promoting = {'square': end_square, 'team':moved_piece//abs(moved_piece)}
                        # CASTLING VARIABLES
                        if moved_piece == 6:  # white king
                            state['has_moved']['white_king'] = True
                        elif moved_piece == -6:  # black king
                            state['has_moved']['black_king'] = True
                        elif moved_piece == 4:  # white rook
                            if start_square == (7, 0):  # a1
                                state['has_moved']['white_queenside_rook'] = True
                            elif start_square == (7, 7):  # h1
                                state['has_moved']['white_kingside_rook'] = True
                        elif moved_piece == -4:  # black rook
                            if start_square == (0, 0):  # a8
                                state['has_moved']['black_queenside_rook'] = True
                            elif start_square == (0, 7):  # h8
                                state['has_moved']['black_kingside_rook'] = True

                        # finish castling chekcs

                        pieces = []
                        for r_idx, row in enumerate(state['board']):
                            for c_idx, val in enumerate(row):
                                if val != 0:
                                    current_j = 7 - r_idx
                                    img = images[val]
                                    rect = img.get_rect(center=get_grid_center(c_idx, current_j))
                                    pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})
                        if promoting is None:
                            state['turn'] = -state['turn']

                            key = position_hash(state) #3fold checks
                            position_counts[key] = position_counts.get(key, 0) + 1

                            # check check/stale mate
                            if position_counts.get(position_hash(state), 0) >= 3:
                                game_over = 'stalemate'
                            elif not has_legal_moves(state, state['turn']):
                                king_pos = [(r, c) for r in range(8) for c in range(8) if state['board'][r][c] == state['turn'] * 6][0]
                                if is_check(state['board'], state['turn'], king_pos):
                                    game_over = 'checkmate'
                                    loser_team = state['turn']  # they can't move and are in check
                                else:
                                    game_over = 'stalemate' # can't move but not in check
                            current_player = white_player if state['turn'] == 1 else black_player
                            if game_over is None and current_player == 'bot':
                                if vinniebot_thread is None:
                                    vinniebot_result = None
                                    state_copy = clone_state(state)
                                    vinniebot_thread = threading.Thread(target=vinniebot_think, args=(state_copy,))
                                    vinniebot_thread.start()
                    else:
                        # illegal return to position
                        if start_center is not None:
                            piece['rect'].center = start_center
                    break

        elif event.type == pygame.MOUSEMOTION:
            if game_over:
                continue
            for piece in pieces:
                if piece['dragging']:
                    piece['rect'].x = event.pos[0] - piece['rel_pos'][0]
                    piece['rect'].y = event.pos[1] - piece['rel_pos'][1]
    if vinniebot_thread is not None and not vinniebot_thread.is_alive():
        if vinniebot_result is not None:
            apply_move(state, vinniebot_result[0], vinniebot_result[1], vinniebot_result[2])
            # rebuild pieces
            key = position_hash(state)
            position_counts[key] = position_counts.get(key, 0) + 1
            pieces = []
            for r_idx, row in enumerate(state['board']):
                for c_idx, val in enumerate(row):
                    if val != 0:
                        current_j = 7 - r_idx
                        img = images[val]
                        rect = img.get_rect(center=get_grid_center(c_idx, current_j))
                        pieces.append({'value': val, 'rect': rect, 'dragging': False, 'rel_pos': (0, 0)})
            # game-over check
            if position_counts.get(position_hash(state), 0) >= 3:
                game_over = 'stalemate'
            elif not has_legal_moves(state, state['turn']):
                king_pos = [(r, c) for r in range(8) for c in range(8) if state['board'][r][c] == state['turn'] * 6][0]
                if is_check(state['board'], state['turn'], king_pos):
                    game_over = 'checkmate'
                    loser_team = state['turn']
                else:
                    game_over = 'stalemate'
        vinniebot_thread = None
        vinniebot_result = None
    if (game_over is None and promoting is None and vinniebot_thread is None):
        current_player = white_player if state['turn'] == 1 else black_player
        if current_player == 'bot':
            vinniebot_result = None
            state_copy = clone_state(state)
            vinniebot_thread = threading.Thread(target=vinniebot_think, args=(state_copy,))
            vinniebot_thread.start()

    window.blit(board_surface, (0, 0))
    for piece in pieces:
        if piece['dragging'] and 'legal_moves' in piece:
            for sq in piece['legal_moves']:
                row, col = sq
                i = col
                j = 7 - row
                center = get_grid_center(i, j)

                # if the destination has an enemy piece, draw a ring instead of a dot
                if state['board'][row][col] == 6 or state['board'][row][col] == -6:
                    pygame.draw.circle(window, (200, 0, 0, 120), center, size // 2 - 4)
                elif state['board'][row][col] != 0:
                    pygame.draw.circle(window, (0, 0, 0, 120), center, size // 2 - 4, 5)
                else:
                    pygame.draw.circle(window, (0, 0, 0, 120), center, size // 6.5)
    if game_over == 'checkmate':
        for piece in pieces:
            if piece['value'] == loser_team * 6:  # the losing king
                glow_size = int(size * 1.8)  # slightly bigger than a square
                if 'red_glow' not in icons:  # build once, save/cache
                    icons['red_glow'] = make_red_glow(glow_size)
                glow = icons['red_glow']
                glow_rect = glow.get_rect(center=piece['rect'].center)
                window.blit(glow, glow_rect)
    for piece in pieces:
        if abs(piece['value']) == 6 and is_check(state['board'], piece['value']//abs(piece['value']), [(r,c) for r in range(8) for c in range(8) if state['board'][r][c] == piece['value']][0]):  # the losing king
            glow_size = int(size * 1.6)  # slightly bigger than a square
            if 'red_glow' not in icons:  # build once, save/cache
                icons['red_glow'] = make_red_glow(glow_size)
            glow = icons['red_glow']
            glow_rect = glow.get_rect(center=piece['rect'].center)
            window.blit(glow, glow_rect)

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
    if game_over:
        icon_size = size // 3
        for piece in pieces:
            if abs(piece['value']) == 6:  # find each king
                corner_x = piece['rect'].right - icon_size
                corner_y = piece['rect'].top

                if game_over == 'stalemate':
                    window.blit(icons['half'], (corner_x, corner_y))
                elif game_over == 'checkmate':
                    if piece['value'] == loser_team * 6:
                        window.blit(icons['hash'], (corner_x, corner_y))
                    else:
                        window.blit(icons['crown'], (corner_x, corner_y))

    pygame.display.flip()
    pygame.display.flip()

pygame.quit()
exit()