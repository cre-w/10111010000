import pygame
from random import randint


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[-1] * width for _ in range(height)]
        self.left = 20
        self.top = 20
        self.cell_size = 45

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, "white", (
                    self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                    self.cell_size), width=1)


class Minesweeper(Board):
    def __init__(self, width=10, height=15):
        super().__init__(width, height)
        self.mine_amount = 10
        for _ in range(self.mine_amount):
            rand_x = randint(0, width - 1)
            rand_y = randint(0, height - 1)
            while self.board[rand_y][rand_x] != -1:
                rand_x = randint(0, width - 1)
                rand_y = randint(0, height - 1)
            self.board[rand_y][rand_x] = 10

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == 10:
                    pygame.draw.rect(screen, "red", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size))
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size), width=1)
                elif self.board[i][j] == -1:
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size), width=1)
                else:
                    font = pygame.font.Font(None, 25)
                    text = font.render(str(self.board[i][j]), True, "green")
                    text_x = self.left + (j * self.cell_size) + 2
                    text_y = self.top + (i * self.cell_size) + 2
                    screen.blit(text, (text_x, text_y))
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size), width=1)

    def get_cell(self, x, y):
        if x > self.left + (self.cell_size * self.width) or x < self.left:
            return None
        elif y > self.top + (self.cell_size * self.height) or y < self.top:
            return None
        else:
            return (x - self.left) // self.cell_size, (y - self.top) // self.cell_size

    def open_cell(self, coordinates):
        if self.board[coordinates[1]][coordinates[0]] == 10:
            return
        mine_count = 0
        top, right, bottom, left = False, False, False, False
        if coordinates[1] - 1 >= 0:
            top = True
        if coordinates[1] + 1 < self.height:
            bottom = True
        if coordinates[0] - 1 >= 0:
            left = True
        if coordinates[0] + 1 < self.width:
            right = True
        if right:
            mine_count += self.board[coordinates[1]][coordinates[0] + 1] == 10
        if left:
            mine_count += self.board[coordinates[1]][coordinates[0] - 1] == 10
        if top:
            mine_count += self.board[coordinates[1] - 1][coordinates[0]] == 10
            if left:
                mine_count += self.board[coordinates[1] - 1][coordinates[0] - 1] == 10
            if right:
                mine_count += self.board[coordinates[1] - 1][coordinates[0] + 1] == 10
        if bottom:
            mine_count += self.board[coordinates[1] + 1][coordinates[0]] == 10
            if left:
                mine_count += self.board[coordinates[1] + 1][coordinates[0] - 1] == 10
            if right:
                mine_count += self.board[coordinates[1] + 1][coordinates[0] + 1] == 10
        self.board[coordinates[1]][coordinates[0]] = mine_count

    def m1_click(self, x, y):
        coordinates = self.get_cell(x, y)
        if coordinates is not None:
            self.open_cell(coordinates)
            self.render(screen)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Дедушка сапёра')
    size = width, height = 727, 727
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))
    board = Minesweeper(10, 15)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                board.m1_click(x, y)
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()
