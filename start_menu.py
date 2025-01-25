import pygame
import os
import sys


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


pygame.init()
WIDTH, HEIGHT = 727, 400
MENU_LANGUAGE_RADIUS = 15
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
FLAGS = [load_image("ru.png"),
         load_image("en.png")]


class StartMenu:
    def __init__(self):
        self.R = MENU_LANGUAGE_RADIUS
        self.language = 0
        self.flag = FLAGS[self.language]

    def render(self, screen):
        name_font = pygame.font.Font(None, 45)
        font = pygame.font.Font(None, 30)
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
            description = font.render(game_description, True, 'green')
            screen.blit(description, (69, 75 + 25 * i))
        for i in range(len(instructions)):
            game_instruction = instructions[i]
            instruction = font.render(game_instruction, True, 'green')
            screen.blit(instruction, (69, 125 + 25 * i))
        for i in range(len(explanations)):
            game_explanation = explanations[i]
            explanation = font.render(game_explanation, True, 'green')
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

    def click_check(self, x, y):
        if x > WIDTH - self.R * 1.8 and y < self.R * 1.8:
            exit()
        elif x < self.R * 1.8 and y < self.R * 1.8:
            self.language = abs(self.language - 1)
        elif 695 > x > 545 and 325 < y < 375:
            running = False

    def update(self):
        self.flag = FLAGS[self.language]


if __name__ == '__main__':
    pygame.display.set_caption('menu')
    size = WIDTH, HEIGHT
    main_screen = pygame.display.set_mode(size)
    main_screen.fill('black')
    running = True
    menu = StartMenu()
    clock = pygame.time.Clock()
    FPS = 60
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                event_x, event_y = event.pos
                menu.click_check(event_x, event_y)
        clock.tick(FPS)
        menu.update()
        main_screen.fill('black')
        menu.render(main_screen)
        pygame.display.flip()
