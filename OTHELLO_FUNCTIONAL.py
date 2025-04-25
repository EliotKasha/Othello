# To Do:
# Fallback to force evaluate terminal states

try:
    import pygame

except:
    import pip
    pip.main(["install", "pygame"])

    import pygame

import math

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

font = pygame.font.SysFont("comicsans", 40)
font_big = pygame.font.SysFont("comicsans", 120)

w = 1080
h = 800
window = pygame.display.set_mode((w, h))

sqsize = h / 8
move_dirs = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [-1, 1], [1, -1]]

heatmap = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, 3, 2, 2, 3, -2, 10],
    [5, -2, 2, 1, 1, 2, -2, 5],
    [5, -2, 2, 1, 1, 2, -2, 5],
    [10, -2, 3, 2, 2, 3, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100],
]

# Colors
felt = (79, 163, 113)
green_pale = (152, 255, 152)
green_paler = (195, 255, 195)
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
grey = (155, 155, 155)
target = (159, 159, 159)

# Settings
SHOW_RESULT = True  # Show what the move will do upon hover
DEPTH = 5  # Minimax depth

class Game:
    def __init__(self):
        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, -1, 1, 0, 0, 0],
            [0, 0, 0, 1, -1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]]

        self.prev = []

        self.turn = 1  # 1 = black / -1 = white
        self.human = 1  # 1 = black / -1 = white
        self.ai = self.human * -1

    # Returns the number of pieces for both players
    def score(self):
        b_score = 0
        w_score = 0

        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 1:
                    b_score += 1

                elif self.board[i][j] == -1:
                    w_score += 1

        return b_score, w_score

    # Returns a list of all legal moves, and what pieces they will flip
    def get_legal_moves(self):
        legal_moves = []
        flips = []

        for i in range(8):
            for j in range(8):
                if self.is_legal_square(i, j) != False:
                    legal_moves.append([i, j])
                    flips.append(self.is_legal_square(i, j))

        if not legal_moves:
            legal_moves.append("PASS")

        return legal_moves, flips

    # Check if a square is legal
    def is_legal_square(self, i, j):
        # Clean up later
        flipped = []
        legal = False

        if self.board[i][j] == 0:
            for move in move_dirs:
                current_flipped = []
                current = [i + move[0], j + move[1]]

                if self.is_square(current):
                    if self.board[current[0]][current[1]] == self.turn * -1:
                        current_flipped.append(current)

                        void = False
                        while self.is_square(current) and not void:

                            if self.board[current[0]][current[1]] == 0:
                                void = True

                            elif self.board[current[0]][current[1]] == self.turn:
                                void = True
                                legal = True
                                for flip in current_flipped:
                                    flipped.append(flip)

                            elif self.board[current[0]][current[1]] == self.turn * -1:
                                current_flipped.append(current)

                            current = [current[0] + move[0], current[1] + move[1]]

        if legal:
            return flipped

        else:
            return False

    # Checks if a square is within the board grid
    def is_square(self, square):
        if 0 <= square[0] < 8 and 0 <= square[1] < 8:
            return True

        return False

    # Check if no moves are available
    def is_terminal(self):
        legal_moves, _ = self.get_legal_moves()
        return legal_moves == []

    # Plays move at given square after validating move
    def move(self, pos):
        if pos == "PASS":
            # Save current position for undoing later
            _ = [row.copy() for row in self.board]
            self.prev.append(_)

            print("PASSED")

            # Swap turns
            self.turn *= -1
            return

        legal_moves, flips = self.get_legal_moves()

        for i in range(len(legal_moves)):
            if pos == legal_moves[i]:
                # Save current position for undoing later
                _ = [row.copy() for row in self.board]
                self.prev.append(_)

                self.board[pos[0]][pos[1]] = self.turn

                for flip in flips[i]:
                    self.board[flip[0]][flip[1]] = self.turn

                # Swap turns
                self.turn *= -1
                break  # Break after successful move

    # Undo last made move
    def undo(self):
        if self.prev:
            self.board = self.prev.pop()
            self.turn *= -1

    # Take user input
    def take_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if self.turn == self.human:
                # Place piece
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    int_pos = [math.floor(pos[1] / sqsize), math.floor(pos[0] / sqsize)]

                    self.move(int_pos)

                if event.type == pygame.KEYDOWN:

                    # Reset Game
                    if event.key == pygame.K_r:
                        self.__init__()

                    # Undo Move
                    if event.key == pygame.K_u:
                        self.undo()

                    if event.key == pygame.K_p:
                        legal_moves, _ = self.get_legal_moves()
                        if legal_moves == ["PASS"]:
                            self.move("PASS")

            else:
                self.move(self.best_move(DEPTH))

    # Draw to pygame window
    def render(self):
        window.fill(felt)

        # Grid
        for i in range(7):
            pygame.draw.rect(window, black, ((i + 1) * sqsize - 1, 0, 2, h))
            pygame.draw.rect(window, black, (0, (i + 1) * sqsize - 1, w, 2))

        # Legal moves
        moves, _ = self.get_legal_moves()

        for move in moves:
            if move != "PASS":
                pygame.draw.rect(window, green_pale,
                                 (move[1] * sqsize + 1, move[0] * sqsize + 1, sqsize - 2, sqsize - 2))

        # Pieces
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 1:
                    pygame.draw.circle(window, black, (j * sqsize + sqsize / 2, i * sqsize + sqsize / 2),
                                       sqsize / 2.5)
                elif self.board[i][j] == -1:
                    pygame.draw.circle(window, white, (j * sqsize + sqsize / 2, i * sqsize + sqsize / 2),
                                       sqsize / 2.5)

        # Hovered square
        int_pos = [math.floor(pygame.mouse.get_pos()[1] / sqsize), math.floor(pygame.mouse.get_pos()[0] / sqsize)]

        if int_pos[0] < 8 and int_pos[1] < 8 and int_pos in moves:
            pygame.draw.rect(window, green_paler,
                             (int_pos[1] * sqsize + 1, int_pos[0] * sqsize + 1, sqsize - 2, sqsize - 2))

            if SHOW_RESULT:
                pygame.draw.circle(window, self.turn, (int_pos[1] * sqsize + sqsize / 2, int_pos[0] * sqsize + sqsize / 2), sqsize / 2.5)

                for i in range(len(moves)):
                    if moves[i] == int_pos:
                        for flip in _[i]:
                            pygame.draw.circle(window, target,
                                               (flip[1] * sqsize + sqsize / 2, flip[0] * sqsize + sqsize / 2),
                                           sqsize / 2.5)
        '''
        # Game over
        if len(moves) == 0:
            label = font_big.render("Game over!", 1, red)
            window.blit(label, (h / 2 - label.get_width() / 2, h / 2 - label.get_height() / 2))
        '''

        # Sidebar
        pygame.draw.rect(window, grey, (h, 0, w - h, h))

        # Turn text
        if self.turn == 1:
            label = font.render("Black's turn", 1, black)

        else:
            label = font.render("White's turn", 1, white)

        window.blit(label, (h + ((w - h) / 2) - (label.get_width() / 2), 10))

        # Score text
        b_score, w_score = self.score()

        label = font.render(str(b_score), 1, black)
        window.blit(label, (h + 10, h - label.get_height() - 10))

        label = font.render(str(w_score), 1, white)
        window.blit(label, (w - label.get_width() - 10, h - label.get_height() - 10))

        label = font.render("vs", 1, red)
        window.blit(label, (h + (w - h) / 2 - (label.get_width() / 2), h - label.get_height() - 10))

        # Show fps
        clock.tick(60)
        pygame.display.set_caption("Othello / " + str(round(clock.get_fps(), 2)) + " fps")

        pygame.display.update()

    # Return best move
    def best_move(self, depth):
        best_move = []
        best_score = -math.inf

        alpha = -math.inf
        beta = math.inf

        legal_moves, _ = self.get_legal_moves()
        legal_moves.sort(key=lambda move: heatmap[move[0]][move[1]], reverse=True)

        for move in legal_moves:
            self.move(move)
            score = self.minimax(depth - 1, -math.inf, math.inf)
            self.undo()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move

    # Minimax recursion
    def minimax(self, depth, alpha, beta):
        if depth == 0:
            return self.eval()

        is_maximizing = (self.turn == self.ai)

        legal_moves, _ = self.get_legal_moves()
        legal_moves.sort(key=lambda move: heatmap[move[0]][move[1]], reverse=is_maximizing)

        if is_maximizing:
            best_score = -math.inf
            for move in legal_moves:
                self.move(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.undo()

                best_score = max(best_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break

        else:
            best_score = math.inf
            for move in legal_moves:
                self.move(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.undo()

                best_score = min(best_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break

        return best_score

    def eval(self):
        score = 0

        for i in range(8):
            for j in range(8):
                score += (self.board[i][j] * heatmap[i][j])

        return (score * self.ai)


def main():
    game = Game()

    while True:
        game.take_input()
        game.render()


if __name__ == "__main__":
    main()