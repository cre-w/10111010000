import sqlite3
from random import randint
import pygame
import os
import sys

pygame.init()


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


EXPLOSION_FRAMES = [load_image("explosion_frame_1.png"),
                    load_image("explosion_frame_2.png"),
                    load_image("explosion_frame_3.png"),
                    load_image("explosion_frame_4.png"),
                    load_image("explosion_frame_5.png"),
                    load_image("explosion_frame_6.png")]
PLAYER_MOVE = [load_image("player1.png"),
               load_image("player2.png"),
               load_image("player3.png"),
               load_image("player4.png")]
player_move_counter = 1
WIDTH, HEIGHT = 600, 400
BOARD_WIDTH, BOARD_HEIGHT = 10, 7


class Board:
    def __init__(self, board_width, board_height):
        self.CONNECTION = sqlite3.connect("pg_game_db")
        self.WIDTH = board_width
        self.HEIGHT = board_height
        self.board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]
        self.PLAYER = 9
        self.WALL = 1
        self.GOLDEN_BARREL = 2  # (the end goal)
        # self.BLAST_RESISTANT_WALL = 3 # (can't blow them up)
        self.RANGE_UPGRADE = 4
        self.TIMER_UPGRADE = 5
        self.BOMB_AMOUNT_UPGRADE = 6
        self.wall_amount = 0
        cursor = self.CONNECTION.cursor()
        saved_game_check = list(cursor.execute("SELECT saved FROM saved_on_quitting_info"))[0][0]
        self.explosion_frame_counter, self.explosions, self.explosion_counter = 0, 0, 0
        self.can_place_bombs = True
        self.side_ranges = []
        self.bomb_board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]
        self.explode_board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]
        self.LEFT = 40
        self.TOP = 40
        self.CELL_SIZE = 50
        self.bomb_timer_fps, self.bomb_x, self.bomb_y = 0, 0, 0
        self.ALL_UPGRADES = ['range', 'timer', 'bomb']
        self.bomb_placed = False
        if saved_game_check == 1:
            self.board_txt = list(cursor.execute("SELECT saved_board FROM saved_on_quitting_info"))[0][0]
            self.board_id = list(cursor.execute("SELECT saved_board_id FROM saved_on_quitting_info"))[0][0]
            self.bomb_amount = list(cursor.execute("SELECT bombs_left FROM saved_on_quitting_info"))[0][0]
            self.bomb_range = list(cursor.execute("SELECT bomb_range FROM saved_on_quitting_info"))[0][0]
            self.bomb_timer_length = list(cursor.execute("SELECT bomb_timer FROM saved_on_quitting_info"))[0][0]
            self.score = list(cursor.execute("SELECT current_board_score FROM saved_on_quitting_info"))[0][0]
            self.upgrades_left = list(cursor.execute("SELECT upgrades_left FROM saved_on_quitting_info"))[0][0].split()
        else:
            cursor.execute("UPDATE saved_on_quitting_info SET win = 0")
            self.previous_board = list(cursor.execute("SELECT previously_played_board_id FROM user_data"))[0][0]
            self.board_id = randint(1, list(cursor.execute("SELECT COUNT(*) FROM bomber_fields"))[0][0])
            while self.board_id == self.previous_board:
                self.board_id = randint(1, list(cursor.execute("SELECT COUNT(*) FROM bomber_fields"))[0][0])
            self.board_txt = list(cursor.execute("SELECT field_composition FROM bomber_fields WHERE field_id = ?", (self.board_id,)))[0][0]
            self.score = 0
            self.bomb_range = 1
            self.bomb_timer_length = 2
            self.bomb_amount = \
                list(cursor.execute("SELECT bomb_amount FROM bomber_fields WHERE field_id = ?",
                                    (self.board_id,)))[0][0]
            self.upgrades_left = self.ALL_UPGRADES.copy()
        self.board_splitted = self.board_txt.split()
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                if self.board_splitted[i][j] == ".":
                    tile = 0
                elif self.board_splitted[i][j] == "#":
                    tile = self.WALL
                    self.wall_amount += 1
                #elif self.board_splitted[i][j] == #E:
                    #tile = self.BLAST_RESISTANT_WALL"""
                elif self.board_splitted[i][j] == "P":
                    tile = self.PLAYER
                    self.x = j
                    self.y = i
                else:
                    tile = 2
                self.board[i][j] = tile
        self.bomb_ranges = self.bomb_range
        cursor.close()

    def explosion_render(self):
        self.explosion_counter += 1
        if self.explosion_counter > self.explosions * 3:
            self.explosion_frame_counter += 1
            self.explosion_counter = 0
            if self.explosion_frame_counter > 5:
                self.explosion_frame_counter = 5
        return EXPLOSION_FRAMES[self.explosion_frame_counter]

    def render(self, screen):
        font = pygame.font.Font(None, 30)
        score_string = "Score: " + str(self.score)
        score = font.render(score_string, True, (100, 255, 100))
        bomb_counter = "Bombs left: " + str(self.bomb_amount)
        bomb_count = font.render(bomb_counter, True, (100, 255, 100))
        screen.blit(score, (WIDTH - 11 * len(score_string), self.TOP // 5))
        screen.blit(bomb_count, (WIDTH - 11 * len(bomb_counter) - 11 * len(score_string), self.TOP // 5))
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                if self.explode_board[i][j] == 1:
                    image = self.explosion_render()
                    screen.blit(image, (self.LEFT + (j * self.CELL_SIZE) - 12, self.TOP + (i * self.CELL_SIZE) - 7))
                    pygame.draw.rect(screen, "white", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                if self.board[i][j] == self.WALL:
                    pygame.draw.rect(screen, "brown", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE))
                    pygame.draw.rect(screen, "white", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.GOLDEN_BARREL:
                    pygame.draw.rect(screen, "yellow", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE))
                    pygame.draw.rect(screen, "white", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.RANGE_UPGRADE:
                    pygame.draw.circle(screen, 'blue', (self.LEFT + (j * self.CELL_SIZE) + self.CELL_SIZE // 2,
                                                        self.TOP + (i * self.CELL_SIZE) + self.CELL_SIZE // 2),
                                       self.CELL_SIZE // 2 - 2)
                    pygame.draw.rect(screen, "white", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.TIMER_UPGRADE:
                    pygame.draw.circle(screen, 'green', (self.LEFT + (j * self.CELL_SIZE) + self.CELL_SIZE // 2,
                                                         self.TOP + (i * self.CELL_SIZE) + self.CELL_SIZE // 2),
                                       self.CELL_SIZE // 2 - 2)
                    pygame.draw.rect(screen, "white", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.BOMB_AMOUNT_UPGRADE:
                    pygame.draw.circle(screen, 'red', (self.LEFT + (j * self.CELL_SIZE) + self.CELL_SIZE // 2,
                                                       self.TOP + (i * self.CELL_SIZE) + self.CELL_SIZE // 2),
                                       self.CELL_SIZE // 2 - 2)
                    pygame.draw.rect(screen, "white", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                else:
                    pygame.draw.rect(screen, "white", (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)

    def upgrade_checker(self, y_move, x_move):
        if self.board[self.y + y_move][self.x + x_move] == self.RANGE_UPGRADE:
            self.bomb_range += 1
            self.bomb_ranges = self.bomb_range
        elif self.board[self.y + y_move][self.x + x_move] == self.TIMER_UPGRADE:
            self.bomb_timer_length -= 0.5
        elif self.board[self.y + y_move][self.x + x_move] == self.BOMB_AMOUNT_UPGRADE:
            self.bomb_amount += 3
        else:
            return
        self.score += 200
        cursor = self.CONNECTION.cursor()
        cursor.execute("UPDATE user_data SET user_score = user_score + 50")
        cursor.close()

    def move_down(self):
        if self.y + 1 < self.HEIGHT and self.board[self.y + 1][self.x] not in [1, 2] and self.bomb_board[self.y + 1][
            self.x] != 1:
            self.upgrade_checker(1, 0)
            self.board[self.y][self.x] = 0
            self.y += 1
            self.board[self.y][self.x] = self.PLAYER
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def move_up(self):
        if self.y - 1 >= 0 and self.board[self.y - 1][self.x] not in [1, 2] and self.bomb_board[self.y - 1][
            self.x] != 1:
            self.upgrade_checker(-1, 0)
            self.board[self.y][self.x] = 0
            self.y -= 1
            self.board[self.y][self.x] = self.PLAYER
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def move_left(self):
        if self.x - 1 >= 0 and self.board[self.y][self.x - 1] not in [1, 2] and self.bomb_board[self.y][
            self.x - 1] != 1:
            self.upgrade_checker(0, -1)
            self.board[self.y][self.x] = 0
            self.x -= 1
            self.board[self.y][self.x] = self.PLAYER
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def move_right(self):
        if self.x + 1 < self.WIDTH and self.board[self.y][self.x + 1] not in [1, 2] and self.bomb_board[self.y][
            self.x + 1] != 1:
            self.upgrade_checker(0, 1)
            self.board[self.y][self.x] = 0
            self.x += 1
            self.board[self.y][self.x] = self.PLAYER
        else:
            self.board[self.y][self.x] = self.board[self.y][self.x]

    def bomb_placement(self):
        if self.can_place_bombs:
            self.explosions = 0
            self.explosion_counter = 0
            self.explosion_frame_counter = 0
            self.bomb_board[self.y][self.x] = 1
            self.bomb_x = self.x
            self.bomb_y = self.y
            bomb.rect.x = self.bomb_x * self.CELL_SIZE + self.LEFT + 5
            bomb.rect.y = self.bomb_y * self.CELL_SIZE + self.TOP + 5
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
        if self.board[self.bomb_y + y][self.bomb_x + x] == self.PLAYER or self.board[self.bomb_y][
            self.bomb_x] == self.PLAYER:
            exit()
        if self.board[self.bomb_y + y][self.bomb_x + x] == self.GOLDEN_BARREL:
            self.score += 1000
            cursor = self.CONNECTION.cursor()
            cursor.execute("UPDATE user_data SET user_score = user_score + 200")
            cursor.execute("UPDATE user_data SET user_wins = user_wins + 1")
            cursor.execute("UPDATE user_data SET previously_played_board_id = ?", (self.board_id,))
            cursor.execute("UPDATE saved_on_quitting_info SET win = 1")
            self.CONNECTION.commit()
            cursor.close()
        upgrade_placed = False
        if self.board[self.bomb_y + y][self.bomb_x + x] == self.WALL and self.upgrades_left:
            rand_gen_numb_1 = randint(1, self.wall_amount)
            self.wall_amount -= 1
            if rand_gen_numb_1 in [1, 2, 3]:
                rand_gen_numb_2 = randint(1, len(self.upgrades_left))
                upgrade = self.upgrades_left[rand_gen_numb_2 - 1]
                if upgrade == 'range':
                    upgrade_number = self.RANGE_UPGRADE
                elif upgrade == 'timer':
                    upgrade_number = self.TIMER_UPGRADE
                else:
                    upgrade_number = self.BOMB_AMOUNT_UPGRADE
                self.upgrades_left.pop(rand_gen_numb_2 - 1)
                self.board[self.bomb_y + y][self.bomb_x + x] = upgrade_number
                upgrade_placed = True
        if not upgrade_placed:
            self.board[self.bomb_y + y][self.bomb_x + x] = 0
        self.explode_board[self.bomb_y + y][self.bomb_x + x] = 1
        self.explosions += 1

    def explode_clear(self):
        self.explode_board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]

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
        self.bomb_board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]

    def explode_check(self):
        top, left, bottom, right = False, False, False, False
        if self.bomb_y - self.bomb_ranges >= 0:
            top = True
        if self.bomb_x - self.bomb_ranges >= 0:
            left = True
        if self.bomb_y + self.bomb_ranges < self.HEIGHT:
            bottom = True
        if self.bomb_x + self.bomb_ranges < self.WIDTH:
            right = True
        self.side_ranges.append([top, left, bottom, right])
        if self.bomb_ranges - 1:
            self.bomb_ranges -= 1
            self.explode_check()
        else:
            self.bomb_ranges = self.bomb_range
        "self.explosion_sound()"
        self.explode()

    def save_data_on_quit(self):
        txt_board = ""
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                if self.board[i][j] == self.GOLDEN_BARREL:
                    tile = "$"
                elif self.board[i][j] == self.WALL:
                    tile = "#"
                elif self.board[i][j] == self.PLAYER:
                    tile = "P"
                else:
                    tile = "."
                txt_board += tile
            txt_board += "\n"
        txt_upgrades = " ".join(self.upgrades_left)
        cursor = self.CONNECTION.cursor()
        end_check = abs(list(cursor.execute("SELECT win FROM saved_on_quitting_info"))[0][0] - 1)
        print(end_check)
        cursor.execute("UPDATE saved_on_quitting_info SET "
                       "bombs_left = ?,"
                       "saved_board = ?,"
                       "upgrades_left = ?,"
                       "bomb_range = ?,"
                       "bomb_timer = ?,"
                       "current_board_score = ?,"
                       "saved_board_id = ?,"
                       "saved = ?",
                       (self.bomb_amount, txt_board, txt_upgrades,
                        self.bomb_range, self.bomb_timer_length, self.score, self.board_id, end_check))
        self.CONNECTION.commit()
        cursor.close()


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
        self.image = PLAYER_MOVE[player_move_counter - 1]
        self.rect.x = board.x * board.CELL_SIZE + board.LEFT + 5
        self.rect.y = board.y * board.CELL_SIZE + board.TOP


if __name__ == '__main__':
    pygame.display.set_caption('bomber')
    size = WIDTH, HEIGHT
    main_screen = pygame.display.set_mode(size)
    main_screen.fill('black')
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    running = True
    clock = pygame.time.Clock()
    FPS = 60
    bomb_group = pygame.sprite.Group()
    bomb = Bomb()
    bomb_group.add(bomb)
    player_group = pygame.sprite.Group()
    player = Player()
    player_group.add(player)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                board.save_data_on_quit()
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.bomb_placement()
                if event.key == pygame.K_DOWN:
                    board.move_down()
                    player_move_counter = 1
                if event.key == pygame.K_UP:
                    board.move_up()
                    player_move_counter = 3
                if event.key == pygame.K_LEFT:
                    board.move_left()
                    player_move_counter = 2
                if event.key == pygame.K_RIGHT:
                    board.move_right()
                    player_move_counter = 4
        main_screen.fill('black')
        player_group.update()
        player_group.draw(main_screen)
        board.render(main_screen)
        clock.tick(FPS)
        if board.bomb_placed:
            board.bomb_timer_fps += 1
            bomb_group.draw(main_screen)
            if board.bomb_timer_fps == FPS * board.bomb_timer_length:
                board.explode_check()
                board.bomb_placed = False
                board.can_place_bombs = True
                board.bomb_amount -= 1
        else:
            board.bomb_timer_fps += 1
            if board.bomb_timer_fps == FPS * (board.bomb_timer_length + 0.25):
                board.explode_clear()
        pygame.display.flip()
