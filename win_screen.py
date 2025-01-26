import pygame

pygame.init()
WIDTH, HEIGHT = 727, 400
LANGUAGES = ['EN', 'RU']
FONT = pygame.font.Font(None, 30)
language = 0


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
        screen.blit(quit_surface, (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + quit_coef * len(quit_text), HEIGHT * 0.4727 + 22))
        pygame.draw.rect(screen, 'white',
                         (WIDTH // 12 * 3.4, HEIGHT * 0.5727 + 15, WIDTH // 9 * 4, HEIGHT // 10 - 4), width=2)
        exit_surface = FONT.render(exit_text, True, 'white')
        screen.blit(exit_surface,
                    (WIDTH // 12 * 3.5 + WIDTH // 8 + 25 + exit_coef * len(exit_text), HEIGHT * 0.5727 + 22))

    def click_check(self, x, y):
        global running
        if (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
                HEIGHT * 0.3727 + 15 < y < HEIGHT * 0.3727 + 15 + HEIGHT // 10 - 4):
            # continue
            pass
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.4727 + 15 < y < HEIGHT * 0.4727 + 15 + HEIGHT // 10 - 4):
            # quit to menu
            pass
        elif (WIDTH // 12 * 3.5 < x < WIDTH // 12 * 3.5 + WIDTH // 9 * 4 and
              HEIGHT * 0.5727 + 15 < y < HEIGHT * 0.5727 + 15 + HEIGHT // 10 - 4):
            running = False


if __name__ == '__main__':
    pygame.display.set_caption('win')
    size = WIDTH, HEIGHT
    main_screen = pygame.display.set_mode(size)
    main_screen.fill('black')
    running = True
    clock = pygame.time.Clock()
    FPS = 60
    menu = WinScreen()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                event_x, event_y = event.pos
                menu.click_check(event_x, event_y)
        clock.tick(FPS)
        main_screen.fill('black')
        menu.render(main_screen)
        pygame.display.flip()
