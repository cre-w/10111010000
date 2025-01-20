import sqlite3
from random import randint

import pygame
import os
import sqlite3
from PIL import Image
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QPlainTextEdit, QWidget
from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QPixmap

pygame.init()


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


explosion_frames = [load_image("explosion_frame_1.png"),
                    load_image("explosion_frame_2.png"),
                    load_image("explosion_frame_3.png"),
                    load_image("explosion_frame_4.png"),
                    load_image("explosion_frame_5.png"),
                    load_image("explosion_frame_6.png")]
player_move = [load_image("player1.png"),
               load_image("player2.png"),
               load_image("player3.png"),
               load_image("player4.png")]
player_move_counter = 1


# noinspection PyUnboundLocalVariable
class Board(QMainWindow):
    def __init__(self, board_width, board_height):
        self.connection = sqlite3.connect("pg_game_db")
        self.current_player = 1
        self.width = board_width
        self.height = board_height
        self.board = [[0] * self.width for _ in range(self.height)]
        # 1 - player
        # 2 - wall
        # 3 - golden barrel (end)
        # 4 - range upgrade
        # 5 - timer upgrade
        self.board[4][0] = 2
        self.board[5][3] = 2
        self.board[1][0] = 2
        self.board[1][2] = 2
        self.board[1][3] = 2
        self.board[5][0] = 2
        self.board[5][4] = 2
        self.board[6][4] = 3
        self.wall_amount = 5
        self.bomb_board = [[0] * self.width for _ in range(self.height)]
        self.explode_board = [[0] * self.width for _ in range(self.height)]
        self.left = 10
        self.top = 10
        self.cell_size = 50
        self.x, self.y = 0, 0
        self.score = 0
        self.bomb_timer_fps, self.bomb_x, self.bomb_y = 0, 0, 0
        self.player = self.board[self.x][self.y] = 1
        self.bomb_placed = False
        self.bomb_range = 2
        self.bomb_ranges = self.bomb_range
        self.bomb_timer_length = 2
        self.can_place_bombs = True
        self.side_ranges = []
        self.explosion_frame_counter, self.explosions, self.explosion_counter = 0, 0, 0
        self.all_upgrades = ['range', 'timer']
        self.upgrades_left = self.all_upgrades.copy()

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def explosion_render(self):
        self.explosion_counter += 1
        if self.explosion_counter > self.explosions * 3:
            self.explosion_frame_counter += 1
            self.explosion_counter = 0
            if self.explosion_frame_counter > 5:
                self.explosion_frame_counter = 5
        return explosion_frames[self.explosion_frame_counter]

    def render(self, screen):
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.score), True, (100, 255, 100))
        screen.blit(text, (520, 0))
        for i in range(self.height):
            for j in range(self.width):
                if self.explode_board[i][j] == 1:
                    image = self.explosion_render()
                    screen.blit(image, (self.left + (j * self.cell_size) - 12, self.top + (i * self.cell_size) - 7))
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)
                if self.board[i][j] == 2:
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
                elif self.board[i][j] == 4:
                    pygame.draw.circle(screen, 'blue', (self.left + (j * self.cell_size) + self.cell_size // 2,
                                                        self.top + (i * self.cell_size) + self.cell_size // 2),
                                       self.cell_size // 2 - 2)
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)
                elif self.board[i][j] == 5:
                    pygame.draw.circle(screen, 'green', (self.left + (j * self.cell_size) + self.cell_size // 2,
                                                         self.top + (i * self.cell_size) + self.cell_size // 2),
                                       self.cell_size // 2 - 2)
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)
                else:
                    pygame.draw.rect(screen, "white", (
                        self.left + (j * self.cell_size), self.top + (i * self.cell_size), self.cell_size,
                        self.cell_size),
                                     width=1)

    def move_down(self):
        global player_move_counter
        if self.y + 1 < self.height and self.board[self.y + 1][self.x] not in [2, 3] and self.bomb_board[self.y + 1][
            self.x] != 1:
            self.board[self.y][self.x] = 0
            self.y += 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]
        player_move_counter = 1

    def move_up(self):
        global player_move_counter
        if self.y - 1 >= 0 and self.board[self.y - 1][self.x] not in [2, 3] and self.bomb_board[self.y - 1][
            self.x] != 1:
            self.board[self.y][self.x] = 0
            self.y -= 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]
        player_move_counter = 3

    def move_left(self):
        global player_move_counter
        if self.x - 1 >= 0 and self.board[self.y][self.x - 1] not in [2, 3] and self.bomb_board[self.y][
            self.x - 1] != 1:
            self.board[self.y][self.x] = 0
            self.x -= 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]
        player_move_counter = 2

    def move_right(self):
        global player_move_counter
        if self.x + 1 < self.width and self.board[self.y][self.x + 1] not in [2, 3] and self.bomb_board[self.y][
            self.x + 1] != 1:
            self.board[self.y][self.x] = 0
            self.x += 1
            self.board[self.y][self.x] = self.player
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]
        player_move_counter = 4

    def bomb_placement(self):
        if self.can_place_bombs:
            self.explosions = 0
            self.explosion_counter = 0
            self.explosion_frame_counter = 0
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
        else:
            y = 0
            x = step
        if self.board[self.bomb_y + y][self.bomb_x + x] == self.player or self.board[self.bomb_y][
            self.bomb_x] == self.player:
            exit()
        if self.board[self.bomb_y + y][self.bomb_x + x] == 3:
            self.score += 100
            cursor = self.connection.cursor()
            cursor.execute("UPDATE users SET user_xp = user_xp + 100 WHERE user_id = ?", (self.current_player,))
            self.connection.commit()
        upgrade_placed = False
        if self.board[self.bomb_y + y][self.bomb_x + x] == 2 and self.upgrades_left:
            rand_gen_numb_1 = 1
            """randint(1, self.wall_amount)"""
            self.wall_amount -= 1
            if rand_gen_numb_1 == 1:
                rand_gen_numb_2 = randint(1, len(self.upgrades_left))
                upgrade = self.upgrades_left[rand_gen_numb_2 - 1]
                if upgrade == 'range':
                    upgrade_number = 4
                    self.bomb_range += 1
                    self.bomb_ranges = self.bomb_range
                if upgrade == 'timer':
                    upgrade_number = 5
                    self.bomb_timer_length -= 0.5
                self.upgrades_left.pop(rand_gen_numb_2 - 1)
                self.board[self.bomb_y + y][self.bomb_x + x] = upgrade_number
                upgrade_placed = True
        if not upgrade_placed:
            self.board[self.bomb_y + y][self.bomb_x + x] = 0
        self.explode_board[self.bomb_y + y][self.bomb_x + x] = 1
        self.explosions += 1

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


class Bomb(pygame.sprite.Sprite):
    image = load_image("bomb_3.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Bomb.image
        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    image = load_image('player1.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Player.image
        self.rect = self.image.get_rect()

    def update(self):
        self.image = player_move[player_move_counter - 1]
        self.rect.x = board.x * board.cell_size + board.left + 5
        self.rect.y = board.y * board.cell_size + board.top


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 450, 300)
        self.setWindowTitle('Bomber')

        self.new_txt_button = QPushButton("Играть", self)
        self.new_txt_button.move(75, 70)
        self.new_txt_button.resize(300, 50)
        self.new_txt_button.clicked.connect(self.game)

        self.new_txt_button = QPushButton("Выйти", self)
        self.new_txt_button.move(75, 170)
        self.new_txt_button.resize(300, 50)
        self.new_txt_button.clicked.connect(self.exit1)

    def exit1(self):
        exit()
    def game(self):
        pygame.display.set_caption('bomber')
        size = width, height = 600, 400
        main_screen = pygame.display.set_mode(size)
        main_screen.fill('black')
        board = Board(10, 7)
        running = True
        clock = pygame.time.Clock()
        fps = 60
        bomb_group = pygame.sprite.Group()
        bomb = Bomb()
        bomb_group.add(bomb)
        player_group = pygame.sprite.Group()
        player = Player()
        player_group.add(player)
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
            main_screen.fill('black')
            player_group.update()
            player_group.draw(main_screen)
            board.render(main_screen)
            clock.tick(fps)
            if board.bomb_placed:
                board.bomb_timer_fps += 1
                bomb_group.draw(main_screen)
                if board.bomb_timer_fps == fps * board.bomb_timer_length:
                    board.explode_check()
                    board.bomb_placed = False
                    board.can_place_bombs = True
            else:
                board.bomb_timer_fps += 1
                if board.bomb_timer_fps == fps * (board.bomb_timer_length + 0.25):
                    board.explode_clear()
            pygame.display.flip()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())

