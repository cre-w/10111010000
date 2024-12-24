import pygame


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
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
                if self.board[i][j] == 0:
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

    def down(self):
        self.board[self.x][self.y] = 0
        self.x += 1
        self.board[self.x][self.y] = self.player
        for i in range(len(self.board)):
            print(self.board[i])

    def up(self):
        self.board[self.x][self.y] = 0
        self.x -= 1
        self.board[self.x][self.y] = self.player
        for i in range(len(self.board)):
            print(self.board[i])

    def left(self):
        self.board[self.x][self.y] = 0
        self.y -= 1
        self.board[self.x][self.y] = self.player
        for i in range(len(self.board)):
            print(self.board[i])

    def right(self):
        self.board[self.x][self.y] = 0
        self.y += 1
        self.board[self.x][self.y] = self.player
        for i in range(len(self.board)):
            print(self.board[i])



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
                if event.key == pygame.K_DOWN:
                    board.down()
                    print(4)
                if event.key == pygame.K_UP:
                    board.up()
                    print(4)
                if event.key == pygame.K_LEFT:
                    board.left()
                    print(4)
                if event.key == pygame.K_RIGHT:
                    board.right()
                    print(4)
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()

