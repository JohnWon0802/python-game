import pygame
import os
import sys
import random

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 640

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (20, 30, 90)
ORANGE = (250, 170, 70)
RED = (250, 0, 0)

FPS = 60

class Ball():
    def __init__(self, bounce_sound):
        self.rect = pygame.Rect(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2), 12, 12)
        self.bounce_sound = bounce_sound
        self.dx = 0
        self.dy = 7

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.left < 0:
            self.dx *= -1
            self.rect.left = 0
            self.bounce_sound.play()

        elif self.rect.right > SCREEN_WIDTH:
            self.dx *= -1
            self.rect.right = SCREEN_WIDTH
            self.bounce_sound.play()

    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.dx = random.randint(-3, 3)
        self.dy = 7

    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, self.rect)

class Player():
    def __init__(self, ping_sound):
        self.rect = pygame.Rect(0, 0, 50, 15)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - 40
        self.ping_sound = ping_sound
        self.dx = 0

    def update(self, ball):
        if self.rect.left <= 0 and self.dx < 0:
            self.dx = 0
        elif self.rect.right >= SCREEN_WIDTH and self.dx > 0:
            self.dx = 0

        if self.rect.colliderect(ball.rect):
            ball.dx = random.randint(-5, 5)
            ball.dy = -abs(ball.dy)  # 반사
            if abs(ball.dy) < 10:
                ball.dy *= 1.1
            ball.rect.bottom = self.rect.top
            self.ping_sound.play()

        self.rect.x += self.dx

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

class Enemy():
    def __init__(self, pong_sound):
        self.rect = pygame.Rect(0, 0, 50, 15)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = 25
        self.pong_sound = pong_sound

    def update(self, ball):
        if self.rect.centerx > ball.rect.centerx:
            diff = self.rect.centerx - ball.rect.centerx
            if diff <= 4:
                self.rect.centerx = ball.rect.centerx
            else:
                self.rect.x -= 4
        elif self.rect.centerx < ball.rect.centerx:
            diff = ball.rect.centerx - self.rect.centerx
            if diff <= 4:
                self.rect.centerx = ball.rect.centerx
            else:
                self.rect.x += 4

        if self.rect.colliderect(ball.rect):
            ball.dy = abs(ball.dy)  # 반사
            if abs(ball.dy) < 10:
                ball.dy *= 1.1
            ball.rect.top = self.rect.bottom
            self.pong_sound.play()

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)

class Game():
    def __init__(self):
        bounce_path = resource_path("assets/bounce.ogg")
        ping_path = resource_path("assets/ping.ogg")
        pong_path = resource_path("assets/pong.ogg")
        font_path = resource_path("assets/NanumGothicCoding-Bold.ttf")
        bounce_sound = pygame.mixer.Sound(bounce_path)
        ping_sound = pygame.mixer.Sound(ping_path)
        pong_sound = pygame.mixer.Sound(pong_path)
        self.font = pygame.font.Font(font_path, 50)
        self.ball = Ball(bounce_sound)
        self.player = Player(ping_sound)
        self.enemy = Enemy(pong_sound)
        self.player_score = 0
        self.enemy_score = 0
        self.screen = pygame.display.get_surface()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.dx -= 5
                elif event.key == pygame.K_RIGHT:
                    self.player.dx += 5
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.player.dx = 0
        return False

    def run_logic(self):
        self.ball.update()
        self.player.update(self.ball)
        self.enemy.update(self.ball)

        if self.ball.rect.y < 0:
            self.player_score += 1
            self.blink_score(self.screen)
            self.ball.reset(self.player.rect.centerx, self.player.rect.centery)

        elif self.ball.rect.y > SCREEN_HEIGHT:
            self.enemy_score += 1
            self.blink_score(self.screen)
            self.ball.reset(self.enemy.rect.centerx, self.enemy.rect.centery)

    def blink_score(self, screen):
        for _ in range(3):
            self.display_frame(screen, show_score=False)
            pygame.display.flip()
            pygame.time.delay(100)
            self.display_frame(screen, show_score=True)
            pygame.display.flip()
            pygame.time.delay(100)

    def display_message(self, screen, message, color):
        label = self.font.render(message, True, color)
        width = label.get_width()
        height = label.get_height()
        pos_x = int((SCREEN_WIDTH / 2) - (width / 2))
        pos_y = int((SCREEN_HEIGHT / 2) - (height / 2))
        screen.blit(label, (pos_x, pos_y))
        pygame.display.update()

    def display_frame(self, screen, show_score=True):
        screen.fill(BLUE)

        if self.player_score == 10:
            self.display_message(screen, "승리!", WHITE)
            self.player_score = 0
            self.enemy_score = 0
            pygame.time.wait(2000)

        elif self.enemy_score == 10:
            self.display_message(screen, "패배", WHITE)
            self.player_score = 0
            self.enemy_score = 0
            pygame.time.wait(2000)
        else:
            self.ball.draw(screen)
            self.player.draw(screen)
            self.enemy.draw(screen)

            for x in range(0, SCREEN_WIDTH, 24):
                pygame.draw.rect(screen, WHITE, [x, int(SCREEN_HEIGHT / 2), 10, 10])

            if show_score:
                enemy_score_label = self.font.render(str(self.enemy_score), True, WHITE)
                screen.blit(enemy_score_label, (10, 260))
                player_score_label = self.font.render(str(self.player_score), True, WHITE)
                screen.blit(player_score_label, (10, 340))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("pingpong game")
    clock = pygame.time.Clock()
    game = Game()

    done = False
    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()