import sqlite3
from random import randint
import pygame
import os
import sys

pygame.init()
pygame.mixer.init()


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


BG_MUSIC = pygame.mixer.music
BG_MUSIC.load("sanctuary.mp3")
BG_MUSIC.set_volume(0.34)
BG_MUSIC.play(loops=True)
EXPLOSION_SFX = pygame.mixer.Sound("explosion.mp3")


def explosion_sound():
    pygame.mixer.Channel(0).play(EXPLOSION_SFX)


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
TIMER_UPGRADE_IMAGE = load_image("pocket_watch.png")
RANGE_UPGRADE_IMAGE = load_image("blast.png")
BOMB_AMOUNT_UPGRADE_IMAGE = load_image("bomb_1.png")
WIDTH, HEIGHT = 727, 400
BOARD_WIDTH, BOARD_HEIGHT = 10, 7
DESCRIPTIONS_EN = ["In this game you need to blow up the golden block", "to proceed to the next stage."]
INSTRUCTIONS_EN = ["To move use the arrow keys and", "spacebar to place down a bomb."]
EXPLANATIONS_EN = ["Brown blocks are walls, gray blocks are invulnerable",
                   "to explosions. The pocket watch is a timer upgrade,",
                   "reducing the time the bomb needs to explode by 0.5 seconds.",
                   "The bomb (not the one you place) adds 3 more bombs.",
                   "And the plus sign adds range to your bomb",
                   "(exploding 2 blocks in each row, rather than 1)."]
DESCRIPTIONS_RU = ["В этой игре вам нужно подорвать золотой блок", "чтобы пройти на следующий уровень."]
INSTRUCTIONS_RU = ["Чтобы двигаться используйте стрелки и", "пробел, чтобы положить бомбу."]
EXPLANATIONS_RU = ["Коричневые блоки - стены, серые блоки - невосприимчивы",
                   "к взрывам. Карманные часы - улучшение времени,",
                   "снижающее время взрыва бомбы на 0.5 секунд.",
                   "Бомба (не та, которую вы ставите) дает 3 доп. бомбы.",
                   "И плюсовой бонус увеличивает радиус взрыва бомбы",
                   "(подрывается 2 блока в каждую сторону, вместо 1)."]
LANGUAGES = ['EN', 'RU']
language = 0
FLAGS = [load_image("ru.png"),
         load_image("en.png")]
player_move_counter = 1
FONT = pygame.font.Font(None, 30)


class StartMenu:
    def __init__(self):
        global language
        self.R = 15
        self.connection = sqlite3.connect('pg_game_db')
        cursor = self.connection.cursor()
        self.language = list(cursor.execute("SELECT user_chosen_language FROM user_data"))[0][0]
        cursor.close()
        language = self.language
        self.flag = FLAGS[self.language]

    def restart(self):
        self.__init__()

    def render(self, screen):
        name_font = pygame.font.Font(None, 45)
        if LANGUAGES[self.language] == 'EN':
            game_name = "Bomber"
            descriptions = DESCRIPTIONS_EN
            instructions = INSTRUCTIONS_EN
            explanations = EXPLANATIONS_EN
        else:
            game_name = "Бомбер"
            descriptions = DESCRIPTIONS_RU
            instructions = INSTRUCTIONS_RU
            explanations = EXPLANATIONS_RU
        name = name_font.render(game_name, True, 'green')
        screen.blit(name, (69, 30))
        for i in range(len(descriptions)):
            game_description = descriptions[i]
            description = FONT.render(game_description, True, 'green')
            screen.blit(description, (69, 75 + 25 * i))
        for i in range(len(instructions)):
            game_instruction = instructions[i]
            instruction = FONT.render(game_instruction, True, 'green')
            screen.blit(instruction, (69, 125 + 25 * i))
        for i in range(len(explanations)):
            game_explanation = explanations[i]
            explanation = FONT.render(game_explanation, True, 'green')
            screen.blit(explanation, (69, 175 + 25 * i))
        pygame.draw.circle(screen, 'white', (self.R, self.R), self.R, width=1)
        pygame.draw.rect(screen, 'white', (545, 325, 150, 50), width=2)
        start = name_font.render("Start", True, 'white')
        screen.blit(start, (585, 335.5))
        screen.blit(self.flag, (self.R * 0.3, self.R * 2 / 3 - 2))
        pygame.draw.circle(screen, 'white', (WIDTH - self.R, self.R), self.R, width=1)
        pygame.draw.line(screen, "white", (WIDTH - self.R * 1.5, self.R // 2),
                         (WIDTH - self.R // 2 - 1, self.R * 1.5),
                         width=2)
        pygame.draw.line(screen, "white", (WIDTH - self.R * 1.5, self.R * 1.5),
                         (WIDTH - self.R // 2 - 1, self.R // 2),
                         width=2)

    def save_on_quit(self):
        global language
        language = self.language
        cursor = self.connection.cursor()
        cursor.execute("UPDATE user_data SET user_chosen_language = ?", (self.language,))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def click_check(self, x, y):
        global game_running, menu_running, running, board
        if x > WIDTH - self.R * 1.8 and y < self.R * 1.8:
            self.save_on_quit()
            menu_running = False
            running = False
        elif x < self.R * 1.8 and y < self.R * 1.8:
            self.language = abs(self.language - 1)
        elif 695 > x > 545 and 325 < y < 375:
            self.save_on_quit()
            board = Board(BOARD_WIDTH, BOARD_HEIGHT)
            game_running = True
            menu_running = False

    def update(self):
        self.flag = FLAGS[self.language]


class PauseMenu:
    def __init__(self):
        global language
        self.language = language

    def render(self, screen):
        pygame.draw.rect(screen, 'black', (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2))
        pygame.draw.rect(screen, 'white', (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2), width=3)
        if LANGUAGES[self.language] == 'EN':
            pause_text = "Paused"
            quit_text = "Quit to menu"
            restart_text = "Restart"
            resume_text = "Resume"
            quit_coef = -1.342
            resume_coef = 0.5
        else:
            pause_text = "Пауза"
            quit_text = "Выйти в меню"
            restart_text = "Заново"
            resume_text = "Продолжить"
            quit_coef = -2.34
            resume_coef = -2
        pause = FONT.render(pause_text, True, 'white')
        screen.blit(pause, (WIDTH // 11 * 5, WIDTH // 6 + 5))
        pygame.draw.rect(screen, 'white', (WIDTH // 12 * 3.4, HEIGHT * 0.3727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4),
                         width=2)
        resume = FONT.render(resume_text, True, 'white')
        screen.blit(resume,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + resume_coef * len(resume_text), HEIGHT * 0.3727 + 22))
        pygame.draw.rect(screen, 'white',
                         (WIDTH // 12 * 3.4, HEIGHT * 0.4727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4), width=2)
        restart = FONT.render(restart_text, True, 'white')
        screen.blit(restart, (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + len(restart_text), HEIGHT * 0.4727 + 22))
        pygame.draw.rect(screen, 'white',
                         (WIDTH // 12 * 3.4, HEIGHT * 0.5727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4), width=2)
        quit_surface = FONT.render(quit_text, True, 'white')
        screen.blit(quit_surface,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + quit_coef * len(quit_text), HEIGHT * 0.5727 + 22))

    def click_check(self, x, y):
        global menu_running, paused, game_running
        if (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
                HEIGHT * 0.3727 + 15 < y < HEIGHT * 0.3727 + 15 + HEIGHT // 10 - 4):
            paused = False
            game_running = True
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.4727 + 15 < y < HEIGHT * 0.4727 + 15 + HEIGHT // 10 - 4):
            paused = False
            game_running = True
            board.continue_playing()
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.5727 + 15 < y < HEIGHT * 0.5727 + 15 + HEIGHT // 10 - 4):
            paused = False
            board.save_data_on_quit()
            menu.restart()
            menu_running = True


class WinScreen:
    def __init__(self):
        global language
        self.language = language

    def render(self, screen):
        pygame.draw.rect(screen, 'black', (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2))
        pygame.draw.rect(screen, 'white', (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2), width=3)
        if LANGUAGES[self.language] == 'EN':
            win_text = "You won!"
            continue_text = "Continue"
            quit_text = "Quit to menu"
            exit_text = "Exit"
            win_coef = 0.69
            continue_coef = 0
            quit_coef = -1.5
            exit_coef = 5
        else:
            win_text = "Вы победили!"
            continue_text = "Продолжить"
            quit_text = "Выйти в меню"
            exit_text = "Выйти из игры"
            win_coef = -1.634
            continue_coef = -2
            quit_coef = -2.5
            exit_coef = -2.34727
        death = FONT.render(win_text, True, 'white')
        screen.blit(death, (WIDTH // 66 * 29 + win_coef * (len(win_text)), WIDTH // 6 + 5))
        pygame.draw.rect(screen, 'white', (WIDTH // 12 * 3.4, HEIGHT * 0.3727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4),
                         width=2)
        restart = FONT.render(continue_text, True, 'white')
        screen.blit(restart,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + continue_coef * len(continue_text), HEIGHT * 0.3727 + 22))
        pygame.draw.rect(screen, 'white',
                         (WIDTH // 12 * 3.4, HEIGHT * 0.4727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4), width=2)
        quit_surface = FONT.render(quit_text, True, 'white')
        screen.blit(quit_surface,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + quit_coef * len(quit_text), HEIGHT * 0.4727 + 22))
        pygame.draw.rect(screen, 'white',
                         (WIDTH // 12 * 3.4, HEIGHT * 0.5727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4), width=2)
        exit_surface = FONT.render(exit_text, True, 'white')
        screen.blit(exit_surface,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + exit_coef * len(exit_text), HEIGHT * 0.5727 + 22))

    def click_check(self, x, y):
        global running, won, menu_running, game_running
        if (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
                HEIGHT * 0.3727 + 15 < y < HEIGHT * 0.3727 + 15 + HEIGHT // 10 - 4):
            won = False
            game_running = True
            board.continue_playing()
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.4727 + 15 < y < HEIGHT * 0.4727 + 15 + HEIGHT // 10 - 4):
            won = False
            menu_running = True
            menu.restart()
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.5727 + 15 < y < HEIGHT * 0.5727 + 15 + HEIGHT // 10 - 4):
            won = False
            running = False


class DeathScreen:
    def __init__(self):
        global language
        self.language = language

    def render(self, screen):
        pygame.draw.rect(screen, 'black', (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2))
        pygame.draw.rect(screen, 'white', (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2), width=3)
        if LANGUAGES[self.language] == 'EN':
            death_text = "You died!"
            restart_text = "Restart"
            quit_text = "Quit to menu"
            exit_text = "Exit"
            death_coef = 0
            restart_coef = 0.5
            quit_coef = -1.5
            exit_coef = 5
        else:
            death_text = "Вы погибли!"
            restart_text = "Заново"
            quit_text = "Выйти в меню"
            exit_text = "Выйти из игры"
            death_coef = -1.2
            restart_coef = 0.5
            quit_coef = -2.5
            exit_coef = -2.34727
        death = FONT.render(death_text, True, 'white')
        screen.blit(death, (WIDTH // 66 * 29 + death_coef * (len(death_text)), WIDTH // 6 + 5))
        pygame.draw.rect(screen, 'white', (WIDTH // 12 * 3.4, HEIGHT * 0.3727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4),
                         width=2)
        restart = FONT.render(restart_text, True, 'white')
        screen.blit(restart,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + restart_coef * len(restart_text), HEIGHT * 0.3727 + 22))
        pygame.draw.rect(screen, 'white',
                         (WIDTH // 12 * 3.4, HEIGHT * 0.4727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4), width=2)
        quit_surface = FONT.render(quit_text, True, 'white')
        screen.blit(quit_surface,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + quit_coef * len(quit_text), HEIGHT * 0.4727 + 22))
        pygame.draw.rect(screen, 'white',
                         (WIDTH // 12 * 3.4, HEIGHT * 0.5727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4), width=2)
        exit_surface = FONT.render(exit_text, True, 'white')
        screen.blit(exit_surface,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + exit_coef * len(exit_text), HEIGHT * 0.5727 + 22))

    def click_check(self, x, y):
        global running, dead, menu_running, game_running
        if (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
                HEIGHT * 0.3727 + 15 < y < HEIGHT * 0.3727 + 15 + HEIGHT // 10 - 4):
            dead = False
            game_running = True
            board.restart()
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.4727 + 15 < y < HEIGHT * 0.4727 + 15 + HEIGHT // 10 - 4):
            dead = False
            menu_running = True
            menu.restart()
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.5727 + 15 < y < HEIGHT * 0.5727 + 15 + HEIGHT // 10 - 4):
            dead = False
            running = False


class Board:
    def __init__(self, board_width, board_height):
        global player_move_counter
        player_move_counter = 1
        self.CONNECTION = sqlite3.connect('pg_game_db')
        self.WIDTH = board_width
        self.HEIGHT = board_height
        self.PLAYER = 9
        self.WALL = 1
        self.GOLDEN_BARREL = 2  # (the end goal)
        self.BLAST_RESISTANT_WALL = 3  # (can't blow them up)
        self.RANGE_UPGRADE = 4
        self.TIMER_UPGRADE = 5
        self.BOMB_AMOUNT_UPGRADE = 6
        self.LEFT = 40
        self.TOP = 40
        self.CELL_SIZE = 50
        self.R = 15
        self.ALL_UPGRADES = ['range', 'timer', 'bomb']
        self.board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]
        self.wall_amount = 0
        self.language = language
        cursor = self.CONNECTION.cursor()
        saved_game_check = list(cursor.execute("SELECT saved FROM saved_on_quitting_info"))[0][0]
        self.explosion_frame_counter, self.explosions, self.explosion_counter = 0, 0, 0
        self.can_place_bombs = True
        self.side_ranges = []
        self.bomb_board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]
        self.explode_board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]
        self.bomb_timer_fps, self.bomb_x, self.bomb_y, self.upgrade_text_timer = 0, 0, 0, 0
        self.picked_up_upgrade = ""
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
            self.board_txt = \
                list(
                    cursor.execute("SELECT field_composition FROM bomber_fields WHERE field_id = ?", (self.board_id,)))[
                    0][0]
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
                if self.board_splitted[i][j] == '.':
                    tile = 0
                elif self.board_splitted[i][j] == '#':
                    tile = self.WALL
                    self.wall_amount += 1
                elif self.board_splitted[i][j] == 'E':
                    tile = self.BLAST_RESISTANT_WALL
                elif self.board_splitted[i][j] == 'P':
                    tile = self.PLAYER
                    self.x = j
                    self.y = i
                else:
                    tile = 2
                self.board[i][j] = tile
        self.bomb_ranges = self.bomb_range
        cursor.close()

    def continue_playing(self):
        self.CONNECTION.close()
        self.__init__(BOARD_WIDTH, BOARD_HEIGHT)

    def restart(self):
        cursor = self.CONNECTION.cursor()
        cursor.execute("UPDATE saved_on_quitting_info SET saved = 0")
        self.CONNECTION.commit()
        cursor.close()
        self.CONNECTION.close()
        self.__init__(BOARD_WIDTH, BOARD_HEIGHT)

    def explosion_render(self):
        self.explosion_counter += 1
        if self.explosion_counter > self.explosions * 3:
            self.explosion_frame_counter += 1
            self.explosion_counter = 0
            if self.explosion_frame_counter > 5:
                self.explosion_frame_counter = 5
        return EXPLOSION_FRAMES[self.explosion_frame_counter]

    def render(self, screen):
        if LANGUAGES[self.language] == 'EN':
            score_string = "Score: " + str(self.score)
            bomb_counter = "Bombs left: " + str(self.bomb_amount)
        else:
            score_string = "Очки: " + str(self.score)
            bomb_counter = "Бомб осталось: " + str(self.bomb_amount)
        score = FONT.render(score_string, True, 'green')
        bomb_count = FONT.render(bomb_counter, True, 'green')
        screen.blit(score, (WIDTH - 11 * len(score_string), self.TOP // 5))
        screen.blit(bomb_count, (WIDTH - 11 * len(bomb_counter) - 11 * len(score_string), self.TOP // 5))
        upgrade = FONT.render(self.picked_up_upgrade, True, 'green')
        screen.blit(upgrade, (WIDTH // 5, self.TOP // 5))
        pygame.draw.circle(screen, 'white', (self.R, self.R), self.R, width=1)
        pygame.draw.line(screen, 'white', (self.R // 3 * 2, self.R // 2), (self.R // 3 * 2, self.R * 1.5), width=4)
        pygame.draw.line(screen, 'white', (self.R // 7 * 9, self.R // 2), (self.R // 7 * 9, self.R * 1.5), width=4)
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                if self.explode_board[i][j] == 1:
                    image = self.explosion_render()
                    screen.blit(image, (self.LEFT + (j * self.CELL_SIZE) - 12, self.TOP + (i * self.CELL_SIZE) - 7))
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                if self.board[i][j] == self.WALL:
                    pygame.draw.rect(screen, 'brown', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE))
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.GOLDEN_BARREL:
                    pygame.draw.rect(screen, 'yellow', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE))
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.BLAST_RESISTANT_WALL:
                    pygame.draw.rect(screen, 'gray', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE))
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.RANGE_UPGRADE:
                    screen.blit(RANGE_UPGRADE_IMAGE, (self.LEFT + (j * self.CELL_SIZE) + self.CELL_SIZE * 0.2,
                                                      self.TOP + (i * self.CELL_SIZE) + self.CELL_SIZE * 0.2))
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.TIMER_UPGRADE:
                    screen.blit(TIMER_UPGRADE_IMAGE, (self.LEFT + (j * self.CELL_SIZE) + self.CELL_SIZE * 0.2,
                                                      self.TOP + (i * self.CELL_SIZE) + self.CELL_SIZE * 0.2))
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                elif self.board[i][j] == self.BOMB_AMOUNT_UPGRADE:
                    screen.blit(BOMB_AMOUNT_UPGRADE_IMAGE, (self.LEFT + (j * self.CELL_SIZE) + self.CELL_SIZE * 0.2,
                                                            self.TOP + (i * self.CELL_SIZE) + self.CELL_SIZE * 0.2))
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)
                else:
                    pygame.draw.rect(screen, 'white', (
                        self.LEFT + (j * self.CELL_SIZE), self.TOP + (i * self.CELL_SIZE), self.CELL_SIZE,
                        self.CELL_SIZE),
                                     width=1)

    def upgrade_checker(self, y_move, x_move):
        global upgrade_text_check
        if self.board[self.y + y_move][self.x + x_move] == self.RANGE_UPGRADE:
            if LANGUAGES[self.language] == 'EN':
                self.picked_up_upgrade = "Range upgraded!"
            else:
                self.picked_up_upgrade = "Радиус увеличен!"
            self.bomb_range += 1
            self.bomb_ranges = self.bomb_range
        elif self.board[self.y + y_move][self.x + x_move] == self.TIMER_UPGRADE:
            if LANGUAGES[self.language] == 'EN':
                self.picked_up_upgrade = "Timer upgraded!"
            else:
                self.picked_up_upgrade = "Время взрыва уменьшено!"
            self.bomb_timer_length -= 0.5
        elif self.board[self.y + y_move][self.x + x_move] == self.BOMB_AMOUNT_UPGRADE:
            if LANGUAGES[self.language] == 'EN':
                self.picked_up_upgrade = "More bombs are available!"
            else:
                self.picked_up_upgrade = "Доступно больше бомб!"
            self.bomb_amount += 3
        else:
            return
        upgrade_text_check = True
        self.upgrade_text_timer = 0
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
        global dead, game_running, won, running
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
            dead = True
            game_running = False
        if self.board[self.bomb_y + y][self.bomb_x + x] == self.GOLDEN_BARREL:
            self.score += 1000
            cursor = self.CONNECTION.cursor()
            cursor.execute("UPDATE user_data SET user_score = user_score + ?", (self.score,))
            cursor.execute("UPDATE user_data SET user_wins = user_wins + 1")
            cursor.execute("UPDATE user_data SET previously_played_board_id = ?", (self.board_id,))
            cursor.execute("UPDATE saved_on_quitting_info SET win = 1")
            self.CONNECTION.commit()
            cursor.close()
            won = True
            self.save_data_on_quit()
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
        if not upgrade_placed and self.board[self.bomb_y + y][self.bomb_x + x] != self.BLAST_RESISTANT_WALL:
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
        explosion_sound()
        self.explode()

    def click_check(self, x, y):
        global paused, game_running
        if x < self.R * 1.8 and y < self.R * 1.8:
            game_running = False
            paused = True

    def save_data_on_quit(self):
        txt_board = ""
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                if self.board[i][j] == self.GOLDEN_BARREL:
                    tile = '$'
                elif self.board[i][j] == self.WALL:
                    tile = '#'
                elif self.board[i][j] == self.PLAYER:
                    tile = 'P'
                elif self.board[i][j] == self.BLAST_RESISTANT_WALL:
                    tile = 'E'
                else:
                    tile = '.'
                txt_board += tile
            txt_board += '\n'
        txt_upgrades = " ".join(self.upgrades_left)
        cursor = self.CONNECTION.cursor()
        end_check = abs(list(cursor.execute("SELECT win FROM saved_on_quitting_info"))[0][0] - 1)
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
    image = load_image("bomb.png")

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
    running = True
    menu_running = True
    game_running = False
    dead = False
    paused = False
    won = False
    upgrade_text_check = False
    menu = StartMenu()
    pause_menu = PauseMenu()
    death_screen = DeathScreen()
    win_screen = WinScreen()
    clock = pygame.time.Clock()
    FPS = 60
    bomb_group = pygame.sprite.Group()
    bomb = Bomb()
    bomb_group.add(bomb)
    player_group = pygame.sprite.Group()
    player = Player()
    player_group.add(player)
    while running:
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu.save_on_quit()
                    menu_running = False
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    event_x, event_y = event.pos
                    menu.click_check(event_x, event_y)
            clock.tick(FPS)
            menu.update()
            main_screen.fill('black')
            menu.render(main_screen)
            pygame.display.flip()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    paused = False
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    event_x, event_y = event.pos
                    pause_menu.click_check(event_x, event_y)
            clock.tick(FPS)
            pause_menu.render(main_screen)
            pygame.display.flip()
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    board.save_data_on_quit()
                    game_running = False
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    event_x, event_y = event.pos
                    board.click_check(event_x, event_y)
            main_screen.fill('black')
            player_group.update()
            player_group.draw(main_screen)
            board.language = language
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
                    if won:
                        game_running = False
            if upgrade_text_check:
                board.upgrade_text_timer += 1
                if board.upgrade_text_timer >= 90:
                    board.picked_up_upgrade = ""
                    upgrade_text_check = False
            pygame.display.flip()
        while dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    dead = False
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    event_x, event_y = event.pos
                    death_screen.click_check(event_x, event_y)
            clock.tick(FPS)
            death_screen.render(main_screen)
            pygame.display.flip()
        while won:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    won = False
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    event_x, event_y = event.pos
                    win_screen.click_check(event_x, event_y)
            clock.tick(FPS)
            win_screen.render(main_screen)
            pygame.display.flip()
