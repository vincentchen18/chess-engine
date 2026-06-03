def board():
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
        current = square
        while True:
            current[0] += dir[0]
            current[1] += dir[1]
            if current[0] < 0 or current[1] < 0 or current[0] >= len(board) or current[1] >= 8:
                break
            if board[current[0]][current[1]] / team > 0: #square occupied by teammate piece
                break
            if board[current[0]][current[1]] / team < 0: #enemy team
                possibles.append(current)
                break
            if board[current[0]][current[1]] == 0:
                possibles.append(current)
    return possibles

import pygame

pygame.init()
window = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

board_surface = pygame.Surface(window.get_size())
board_surface.fill((255, 255, 255))
size = (min(window.get_size()) - 20) // 8
start_x, start_y = (window.get_width() - size * 8) // 2, (window.get_height() - size * 8) // 2
board_rect = pygame.Rect(start_x, start_y, size * 8, size * 8)

for y in range(8):
    for x in range(8):
        color = (192, 192, 164) if (x + y) % 2 == 0 else (96, 64, 32)
        pygame.draw.rect(board_surface, color, (start_x + x * size, start_y + y * size, size, size))

unicode_map = {
    1: '♙', 2: '%s' % '♘', 3: '♗', 4: '♖', 5: '♕', 6: '♔',
    -1: '♟', -2: '♞', -3: '♝', -4: '♜', -5: '♛', -6: '♚'
}

seguisy = pygame.font.SysFont("segoeuisymbol", size - 4)
images = {}
for val, sym in unicode_map.items():
    color = (255, 255, 255) if val > 0 else (0, 0, 0)
    images[val] = seguisy.render(sym, True, color)


def get_grid_center(i, j):
    x = board_rect.left + board_rect.width // 8 * i + board_rect.width // 16
    y = board_rect.top + board_rect.height // 8 * (7 - j) + board_rect.height // 16
    return x, y


board = board()

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
            for piece in reversed(pieces):
                if piece['rect'].collidepoint(event.pos):
                    piece['dragging'] = True
                    piece['rel_pos'] = (event.pos[0] - piece['rect'].x, event.pos[1] - piece['rect'].y)

                    old_i = max(0, min(7, (piece['rect'].centerx - board_rect.left) // (board_rect.width // 8)))
                    old_j = 7 - max(0, min(7, (piece['rect'].centery - board_rect.top) // (board_rect.height // 8)))
                    piece['start_cell'] = (old_i, old_j)

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