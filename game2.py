import pygame


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.board[4][0] = 2
        self.board[5][3] = 2
        self.bomboard = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.x = 0
        self.y = 0
        self.player = self.board[self.x][self.y] = 1

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                if self.bomboard[i][j] == 3:
                    pygame.draw.rect(screen, "green", (
                        self.left + (j * self.cell_size) + 5, self.top + (i * self.cell_size) + 5, self.cell_size - 10,
                        self.cell_size - 10))
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)

                elif self.board[i][j] == 1:
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
        if self.x + 1 != self.height and self.board[self.x + 1][self.y] != 2:
            self.board[self.x][self.y] = 0
            self.x += 1
            self.board[self.x][self.y] = self.player
            for i in range(len(self.bomboard)):
                print(self.bomboard[i])
        else:
            self.board[self.x][self.y] = self.board[self.x][self.y]

    def up(self):
        if self.x - 1 != -1 and self.board[self.x - 1][self.y] != 2:
            self.board[self.x][self.y] = 0
            self.x -= 1
            self.board[self.x][self.y] = self.player
        else:
            self.board[self.x][self.y] = self.board[self.x][self.y]

    def left1(self):
        if self.y - 1 != -1 and self.board[self.x][self.y - 1] != 2:
            self.board[self.x][self.y] = 0
            self.y -= 1
            self.board[self.x][self.y] = self.player
        else:
            self.board[self.x][self.y] = self.board[self.x][self.y]

    def right(self):
        if self.y + 1 != self.width and self.board[self.x][self.y + 1] != 2:
            self.board[self.x][self.y] = 0
            self.y += 1
            self.board[self.x][self.y] = self.player
        else:
            self.board[self.x][self.y] = self.board[self.x][self.y]

    def bomb1(self):
        self.bomboard[self.x][self.y] = 3
        for i in range(len(self.bomboard)):
            print(self.bomboard[i])


if __name__ == '__main__':
    pygame.display.set_caption('Чёрное в белое и наоборот')
    size = width, height = 400, 400
    screen = pygame.display.set_mode(size)
    screen.fill('black')
    board = Board(5, 7)
    running = True
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
        pygame.display.flip()
