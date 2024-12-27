import pygame
import os
import sys

pygame.init()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Bomb(pygame.sprite.Sprite):
    image = load_image("bomb_3.png")
    def __init__(self, *group):
        super().__init__(*group)
        self.image = Bomb.image
        self.rect = self.image.get_rect()

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.board[4][0] = 2
        self.board[5][3] = 2
        self.board[1][0] = 2
        self.board[5][0] = 2
        self.board[5][4] = 2
        self.board[6][4] = 3
        self.score = 0
        self.bomb_board = [[0] * width for _ in range(height)]
        self.explode_board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 50
        self.x = 0
        self.y = 0
        self.player = self.board[self.x][self.y] = 1
        self.bomb_placed = False
        self.bomb_timer_fps = 0
        self.bomb_x = 0
        self.bomb_y = 0
        self.bomb_range = 1
        self.bomb_ranges = self.bomb_range
        self.bomb_timer_length = 2
        self.side_ranges = []
        self.can_place_bombs = True

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.score), True, (100, 255, 100))
        screen.blit(text, (520, 0))
        for i in range(self.height):
            for j in range(self.width):
                if self.explode_board[i][j] == 1:
                    pygame.draw.rect(screen, "blue", (
                        self.left + (j * self.cell_size) + 5, self.top + (i * self.cell_size) + 5,
                        self.cell_size - 10,
                        self.cell_size - 10))
                if self.board[i][j] == 1:
                    pygame.draw.circle(screen, "red", ((self.left + (j * self.cell_size)) + self.cell_size / 2,
                                                       (self.top + (i * self.cell_size)) + self.cell_size / 2),
                                       self.cell_size / 2 - 2,
                                       width=2)
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)
                elif self.board[i][j] == 2:
                    pygame.draw.rect(screen, "brown", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size))
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)
                elif self.board[i][j] == 3:
                    pygame.draw.rect(screen, "yellow", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size))
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)
                elif self.board[i][j] == 0:
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)

    def move_down(self):
        if self.y + 1 < self.height and self.board[self.y + 1][self.x] not in [2, 3] and self.bomb_board[self.y + 1][
            self.x] != 1:
            self.board[self.y][self.x] = 0
            self.y += 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def move_up(self):
        if self.y - 1 >= 0 and self.board[self.y - 1][self.x] not in [2, 3] and self.bomb_board[self.y - 1][
            self.x] != 1:
            self.board[self.y][self.x] = 0
            self.y -= 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def move_left(self):
        if self.x - 1 >= 0 and self.board[self.y][self.x - 1] not in [2, 3] and self.bomb_board[self.y][
            self.x - 1] != 1:
            self.board[self.y][self.x] = 0
            self.x -= 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def move_right(self):
        if self.x + 1 < self.width and self.board[self.y][self.x + 1] not in [2, 3] and self.bomb_board[self.y][
            self.x + 1] != 1:
            self.board[self.y][self.x] = 0
            self.x += 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def bomb_placement(self):
        if self.can_place_bombs:
            self.bomb_board[self.y][self.x] = 1
            self.bomb_x = self.x
            self.bomb_y = self.y
            bomb.rect.x = self.bomb_x * self.cell_size + self.left + 5
            bomb.rect.y = self.bomb_y * self.cell_size + self.top + 5
            self.bomb_timer_fps = 0
            self.bomb_placed = True
            self.can_place_bombs = False

    def actual_explosion(self, side, br):
        step = br + 1
        if side == 0:
            y = -step
            x = 0
        elif side == 1:
            y = 0
            x = -step
        elif side == 2:
            y = step
            x = 0
        elif side == 3:
            y = 0
            x = step
        if self.board[self.bomb_y + y][self.bomb_x + x] == self.player or self.board[self.bomb_y][
            self.bomb_x] == self.player:
            exit()
        if self.board[self.bomb_y + y][self.bomb_x + x] == 3:
            self.score += 100
        self.board[self.bomb_y + y][self.bomb_x + x] = 0
        self.explode_board[self.bomb_y + y][self.bomb_x + x] = 1

    def explode_clear(self):
        self.explode_board = [[0] * width for _ in range(height)]

    def explode(self):
        all_sides_list = list(reversed(self.side_ranges))
        for bomb_range, sides_list in enumerate(all_sides_list):
            if not any(sides_list):
                continue
            for i, side in enumerate(sides_list):
                if not side:
                    continue
                self.actual_explosion(i, bomb_range)
        self.side_ranges = []
        self.bomb_board = [[0] * self.width for _ in range(self.height)]

    def explode_check(self):
        top, left, bottom, right = False, False, False, False
        if self.bomb_y - self.bomb_ranges >= 0:
            top = True
        if self.bomb_x - self.bomb_ranges >= 0:
            left = True
        if self.bomb_y + self.bomb_ranges < self.height:
            bottom = True
        if self.bomb_x + self.bomb_ranges < self.width:
            right = True
        self.side_ranges.append([top, left, bottom, right])
        if self.bomb_ranges - 1:
            self.bomb_ranges -= 1
            self.explode_check()
        else:
            self.bomb_ranges = self.bomb_range
        self.explode()


if __name__ == '__main__':
    pygame.display.set_caption('bomber')
    size = width, height = 600, 400
    screen = pygame.display.set_mode(size)
    screen.fill('black')
    board = Board(10, 7)
    running = True
    clock = pygame.time.Clock()
    fps = 60
    bomb_group = pygame.sprite.Group()
    bomb = Bomb()
    bomb_group.add(bomb)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.bomb_placement()
                if event.key == pygame.K_DOWN:
                    board.move_down()
                if event.key == pygame.K_UP:
                    board.move_up()
                if event.key == pygame.K_LEFT:
                    board.move_left()
                if event.key == pygame.K_RIGHT:
                    board.move_right()
        screen.fill((0, 0, 0))
        board.render(screen)
        clock.tick(fps)
        if board.bomb_placed:
            board.bomb_timer_fps += 1
            bomb_group.draw(screen)
            if board.bomb_timer_fps == fps * board.bomb_timer_length:
                board.explode_check()
                board.bomb_placed = False
                board.can_place_bombs = True
        else:
            board.bomb_timer_fps += 1
            if board.bomb_timer_fps == fps * (board.bomb_timer_length + 0.25):
                board.explode_clear()
        pygame.display.flip()
