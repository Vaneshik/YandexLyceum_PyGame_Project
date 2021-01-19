import pygame
from random import randint
import sys
from itertools import chain
import numpy as np

# Небольшие настройки
FPS = 60
DIFFICULT = 'INTERMEDIATE'


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.status = 'playing'

        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.mines_quantity = 10
        self.first = 1
        self.mines = []
        self.board = []
        self.mines_on_brd = 0

        mine = pygame.image.load('data/mine.png')
        flag = pygame.image.load('data/flag.png')

        self.mine_img = pygame.transform.scale(mine, (self.cell_size - 5, self.cell_size - 5))
        self.flag_img = pygame.transform.scale(flag, (self.cell_size - 5, self.cell_size - 5))

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        y0 = self.top
        for i in range(self.height):
            x0 = self.left
            for j in range(self.width):
                pygame.draw.rect(screen, (255, 255, 255), (x0, y0, self.cell_size, self.cell_size), 1)
                if self.board[i][j][1] == 0:
                    pygame.draw.rect(screen, (170, 170, 170),
                                     (x0 + 1, y0 + 1, self.cell_size - 2, self.cell_size - 2))
                elif self.board[i][j][1] == 2:
                    pygame.draw.rect(screen, (190, 190, 190),
                                     (x0 + 1, y0 + 1, self.cell_size - 2, self.cell_size - 2))

                    screen.blit(self.flag_img, (x0 + 2, y0 + 2))
                else:
                    pygame.draw.rect(screen, (190, 190, 190),
                                     (x0 + 1, y0 + 1, self.cell_size - 2, self.cell_size - 2))
                    font = pygame.font.Font(None, 24)
                    if self.board[i][j][0]:
                        text = font.render(str(self.board[i][j][0]), True, (0, 0, 0))
                        text_x = x0 + self.cell_size // 2 - text.get_width() // 2
                        text_y = y0 + self.cell_size // 2 - text.get_height() // 2
                        screen.blit(text, (text_x, text_y))
                if self.status == 'lose':
                    if (j, i) in self.mines:
                        pygame.draw.rect(screen, (190, 190, 190),
                                         (x0 + 1, y0 + 1, self.cell_size - 2, self.cell_size - 2))
                        screen.blit(self.mine_img, (x0 + 2, y0 + 2))
                x0 += self.cell_size
            y0 += self.cell_size

    def get_cell(self, mouse_pos):
        pos = (mouse_pos[0] - self.left) // self.cell_size, (mouse_pos[1] - self.top) // self.cell_size
        if 0 <= pos[0] <= self.width - 1 and 0 <= pos[1] <= self.height - 1:
            return pos
        else:
            return None

    def on_click(self, cell_coords, button):
        if cell_coords:
            if button == 1 and self.board[cell_coords[1]][cell_coords[0]][1] != 2:
                if cell_coords not in self.mines:
                    self.board[cell_coords[1]][cell_coords[0]][1] = 1
                    if self.board[cell_coords[1]][cell_coords[0]][0] == 0:
                        self.open_empty_ceil(cell_coords)
                else:
                    if self.first:
                        while cell_coords in self.mines:
                            self.board = np.array([[[0, 0]] * self.width for _ in range(self.height)])
                            self.generate_brd(self.mines_quantity)
                        self.board[cell_coords[1]][cell_coords[0]][1] = 1
                        if self.board[cell_coords[1]][cell_coords[0]][0] == 0:
                            self.open_empty_ceil(cell_coords)
                        self.first = 0
                    else:
                        self.status = 'lose'
                if all(map(lambda x: x[1], filter(lambda x: x[0] != -1, chain.from_iterable(self.board)))):
                    self.status = 'win'
                    self.mines_on_brd = self.mines_quantity
                self.first = 0
            elif button == 3:
                if self.board[cell_coords[1]][cell_coords[0]][1] == 0 and self.mines_on_brd < self.mines_quantity:
                    self.board[cell_coords[1]][cell_coords[0]] = 2
                    self.mines_on_brd += 1
                elif self.board[cell_coords[1]][cell_coords[0]][1] == 2:
                    self.board[cell_coords[1]][cell_coords[0]] = 0
                    self.mines_on_brd -= 1

    def get_click(self, mouse_pos, button):
        if self.status == 'playing':
            cell = self.get_cell(mouse_pos)
            self.on_click(cell, button)

    def generate_brd(self, a):
        self.mines = []
        self.status = 'playing'

        while len(self.mines) < a:
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            if (y, x) not in self.mines:
                self.mines.append((x, y))
                self.board[y][x] = [-1, 0]
        # Генерация мин

        for i in range(self.height):
            for j in range(self.width):
                kek = 0
                for a, b in [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1), (i + 1, j - 1),
                             (i + 1, j), (i + 1, j + 1)]:
                    if a in range(self.height) and b in range(self.width):
                        if self.board[a][b][0] == -1:
                            kek += 1

                if self.board[i][j][0] != -1:
                    self.board[i][j][0] = kek
        # генерация поля взависимости от расположения мин

    def set_difficult(self):
        global DIFFICULT
        argv = sys.argv

        if len(argv) > 1:
            if '-d' in argv:
                DIFFICULT = argv[argv.index('-d') + 1].upper()
                if DIFFICULT not in ['BEGINNER', 'INTERMEDIATE', 'EXPERT']:
                    sys.exit('Difficult ERROR!')

        if DIFFICULT == 'INTERMEDIATE':
            self.width = self.height = 16
            self.mines_quantity = 40

        elif DIFFICULT == 'EXPERT':
            self.width = 30
            self.height = 16
            self.mines_quantity = 99

        self.board = np.array([[[0, 0]] * self.width for _ in range(self.height)])
        self.generate_brd(self.mines_quantity)
        # генерация доски

    def open_empty_ceil(self, pos):
        j, i = pos
        for a, b in [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1), (i + 1, j - 1),
                     (i + 1, j), (i + 1, j + 1)]:
            if a in range(self.height) and b in range(self.width):
                if list(self.board[a][b]) == [0, 0]:
                    self.board[a][b][1] = 1
                    self.open_empty_ceil((b, a))
                elif list(self.board[a][b]) != [-1, 0] and self.board[a][b][1] != 2:
                    self.board[a][b][1] = 1
        # Рекурсивно открываем пустые клеточки


def main():
    pygame.init()

    board = Board(9, 9)
    board.set_difficult()

    pygame.display.set_caption('Minesweeper')
    pygame.display.set_icon(board.mine_img)

    width = board.width * board.cell_size + 100
    height = 80 + board.height * board.cell_size
    board.set_view(width // 2 - board.width * board.cell_size // 2, 70, board.cell_size)

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True

    button = pygame.Rect(width // 2 - 25, 10, 50, 50)
    restart = pygame.image.load('data/update-arrow.png')
    restart = pygame.transform.scale(restart, (45, 45))
    restart_x = button.left + 2
    restart_y = button.top + 2

    font = pygame.font.Font(None, 30)
    while running:
        color = (202, 202, 202)
        if board.status == 'lose':
            color = (255, 66, 82)
        elif board.status == 'win':
            color = (216, 252, 168)
        screen.fill(color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos, event.button)
                if button.collidepoint(event.pos):
                    board.first = 1
                    board.mines_on_brd = 0
                    board.board = np.array([[[0, 0]] * board.width for _ in range(board.height)])
                    board.generate_brd(board.mines_quantity)

        board.render(screen)
        text1 = font.render(f'Bombs: {board.mines_quantity - board.mines_on_brd}', True, (0, 0, 0))
        text2 = font.render(f'Status:{board.status}', True, (0, 0, 0))
        pygame.draw.rect(screen, [170, 170, 170], button)
        screen.blit(text1, (10, button.midleft[1] - text1.get_height() // 2))
        screen.blit(text2, (width - 10 - text2.get_width(), button.midleft[1] - text2.get_height() // 2))
        screen.blit(restart, (restart_x, restart_y))
        pygame.display.flip()
        clock.tick(FPS)
        # готовим кадр


if __name__ == '__main__':
    main()
