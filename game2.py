import pygame


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
        self.board[6][4] = 2
        self.bomb_board = [[0] * width for _ in range(height)]
        self.explode_board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
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
        for i in range(self.height):
            for j in range(self.width):
                if self.explode_board[i][j] == 1:
                    pygame.draw.rect(screen, "blue", (
                        self.left + (j * self.cell_size) + 5, self.top + (i * self.cell_size) + 5,
                        self.cell_size - 10,
                        self.cell_size - 10))
                elif self.bomb_board[i][j] == 1:
                    pygame.draw.rect(screen, "green", (
                        self.left + (j * self.cell_size) + 5, self.top + (i * self.cell_size) + 5,
                        self.cell_size - 10,
                        self.cell_size - 10))
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)
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
                elif self.board[i][j] == 0:
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)

    def down(self):
        if self.y + 1 < self.height and self.board[self.y + 1][self.x] != 2 and self.bomb_board[self.y + 1][
            self.x] != 1:
            self.board[self.y][self.x] = 0
            self.y += 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def up(self):
        if self.y - 1 >= 0 and self.board[self.y - 1][self.x] != 2 and self.bomb_board[self.y - 1][self.x] != 1:
            self.board[self.y][self.x] = 0
            self.y -= 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def left1(self):
        if self.x - 1 >= 0 and self.board[self.y][self.x - 1] != 2 and self.bomb_board[self.y][self.x - 1] != 1:
            self.board[self.y][self.x] = 0
            self.x -= 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def right(self):
        if self.x + 1 < self.width and self.board[self.y][self.x + 1] != 2 and self.bomb_board[self.y][self.x + 1] != 1:
            self.board[self.y][self.x] = 0
            self.x += 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def bomb1(self):
        if self.can_place_bombs:
            self.bomb_board[self.y][self.x] = 1
            self.bomb_x = self.x
            self.bomb_y = self.y
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
        if self.board[self.bomb_y + y][self.bomb_x + x] == self.player:
            print("гойда")
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
    pygame.display.set_caption('Чёрное в белое и наоборот')
    size = width, height = 400, 400
    screen = pygame.display.set_mode(size)
    screen.fill('black')
    board = Board(5, 7)
    running = True
    clock = pygame.time.Clock()
    fps = 60
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.bomb1()
                if event.key == pygame.K_DOWN:
                    board.down()
                if event.key == pygame.K_UP:
                    board.up()
                if event.key == pygame.K_LEFT:
                    board.left1()
                if event.key == pygame.K_RIGHT:
                    board.right()
        screen.fill((0, 0, 0))
        board.render(screen)
        clock.tick(fps)
        if board.bomb_placed:
            board.bomb_timer_fps += 1
            if board.bomb_timer_fps == fps * board.bomb_timer_length:
                board.explode_check()
                board.bomb_placed = False
                board.can_place_bombs = True
        else:
            board.bomb_timer_fps += 1
            if board.bomb_timer_fps == fps * (board.bomb_timer_length + 0.25):
                board.explode_clear()
        pygame.display.flip()
