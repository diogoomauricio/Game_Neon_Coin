import pygame
import math
import random
import sys

#Configurações
RESOLUTIONS = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
FPS = 120

#Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (45, 45, 45)
BLUE = (70, 110, 200)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 80, 80)
GREEN = (80, 200, 120)

#Estados
MENU = "menu"
SETTINGS = "settings"
VIDEO = "video"
AUDIO = "audio"
COUNTDOWN = "countdown"
PLAYING = "playing"
GAME_OVER = "game_over"
WIN = "win"

#Classes do jogo

class Player:
    def __init__(self, w, h):
        self.size = 40
        self.pos = pygame.Vector2(w // 2, h // 2)
        self.speed = 7
        self.angle = 0
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, BLUE, (0, 0, self.size, self.size), border_radius=6)

    def move(self, walls, w, h):
        keys = pygame.key.get_pressed()
        old = self.pos.copy()

        if keys[pygame.K_a]: self.pos.x -= self.speed
        if keys[pygame.K_d]: self.pos.x += self.speed
        if keys[pygame.K_w]: self.pos.y -= self.speed
        if keys[pygame.K_s]: self.pos.y += self.speed

        self.pos.x = max(20, min(w - 20, self.pos.x))
        self.pos.y = max(20, min(h - 20, self.pos.y))

        for wall in walls:
            if wall.rect.collidepoint(int(self.pos.x), int(self.pos.y)):
                self.pos = old

        mx, my = pygame.mouse.get_pos()
        self.angle = math.degrees(math.atan2(-(my - self.pos.y), mx - self.pos.x))

    def draw(self, screen):
        rot = pygame.transform.rotate(self.surface, self.angle)
        screen.blit(rot, rot.get_rect(center=self.pos))

class Enemy:
    def __init__(self, w, h, player_pos=None):
        # Garantir que os inimigos não aparecem perto do jogador
        while True:
            self.pos = pygame.Vector2(random.randint(100, w - 100), random.randint(100, h - 100))
            if player_pos is None or self.pos.distance_to(player_pos) > 250:
                break
        self.speed = random.uniform(0.8, 1.5)
        self.radius = 15

    def update(self, player, walls):
        direction = player.pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()

        old = self.pos.copy()
        self.pos += direction * self.speed

        for wall in walls:
            if wall.rect.collidepoint(int(self.pos.x), int(self.pos.y)):
                self.pos = old

    def draw(self, screen):
        pygame.draw.circle(screen, RED, self.pos, self.radius)

class Collectible:
    def __init__(self, w, h):
        self.pos = pygame.Vector2(random.randint(50, w - 50), random.randint(50, h - 50))
        self.radius = 12

    def draw(self, screen):
        # Desenhar moeda como círculo amarelo com borda
        pygame.draw.circle(screen, YELLOW, self.pos, self.radius)
        pygame.draw.circle(screen, (200, 180, 0), self.pos, self.radius, 3)
        
        pygame.draw.circle(screen, (200, 180, 0), self.pos, self.radius // 2, 1)

class Wall:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(int(x), int(y), int(w), int(h))

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)



class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.res_index = 0
        self.fullscreen = False
        self.width, self.height = RESOLUTIONS[self.res_index]
        self.apply_video()

        pygame.display.set_caption("NEON COIN")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 32)

        # ÁUDIO ESTADO
        self.menu_music_on = True
        self.game_music_on = True
        self.load_audio()

        # ESTADOS / MENUS
        self.state = MENU
        self.menu_sel = 0
        self.set_sel = 0
        self.video_sel = 0
        self.audio_sel = 0
        self.game_over_sel = 0
        self.win_sel = 0
        self.countdown_start = 0

        #Níveis
        self.level = 1

        #Iluminação
        self.light_surface = pygame.Surface((self.width, self.height))
        self.light_radius = 260

        self.reset_game()
        self.play_menu_music()

    def apply_video(self):
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.mouse.set_visible(True)

    def load_audio(self):
        #Ficheiros
        self.menu_music_file = "menu_bg.mp3"
        self.game_music_file = "game_bg.mp3"
        
        
        try:
            self.snd_collect = pygame.mixer.Sound("collect.wav")
            self.snd_lose = pygame.mixer.Sound("lose.wav")
        except:
            self.snd_collect = None
            self.snd_lose = None

    def play_menu_music(self):
        if self.menu_music_on:
            try:
                pygame.mixer.music.load(self.menu_music_file)
                pygame.mixer.music.play(-1)
            except:
                pass 

    def play_game_music(self):
        if self.game_music_on:
            try:
                pygame.mixer.music.load(self.game_music_file)
                pygame.mixer.music.play(-1)
            except:
                pass

    def reset_game(self):
        self.player = Player(self.width, self.height)
        self.collectible = Collectible(self.width, self.height)
        self.difficulty = 1.0  
        self.score = 0
        self.target_score = 5

        if self.level == 1:
            self.enemies = [Enemy(self.width, self.height, self.player.pos) for _ in range(3)]
            self.walls = [
                Wall(self.width * 0.15, self.height * 0.25, 300, 30),
                Wall(self.width * 0.5, self.height * 0.4, 30, 250),
                Wall(self.width * 0.3, self.height * 0.7, 400, 30),
                Wall(self.width * 0.75, self.height * 0.2, 30, 300)
            ]
            self.bg_color = GRAY
        elif self.level == 2:
            self.enemies = [Enemy(self.width, self.height, self.player.pos) for _ in range(4)]
            self.walls = [
                Wall(self.width * 0.1, self.height * 0.2, 250, 40),
                Wall(self.width * 0.4, self.height * 0.35, 40, 200),
                Wall(self.width * 0.6, self.height * 0.5, 300, 40),
                Wall(self.width * 0.25, self.height * 0.75, 40, 150),
                Wall(self.width * 0.8, self.height * 0.3, 40, 250)
            ]
            self.bg_color = (30, 30, 60)  
        elif self.level == 3:
            self.enemies = [Enemy(self.width, self.height, self.player.pos) for _ in range(5)]
            self.walls = [
                Wall(self.width * 0.05, self.height * 0.15, 200, 50),
                Wall(self.width * 0.3, self.height * 0.25, 50, 180),
                Wall(self.width * 0.5, self.height * 0.4, 250, 50),
                Wall(self.width * 0.75, self.height * 0.55, 50, 200),
                Wall(self.width * 0.2, self.height * 0.7, 300, 50),
                Wall(self.width * 0.6, self.height * 0.8, 50, 100)
            ]
            self.bg_color = (60, 30, 30) 

    def draw_lighting(self):
        self.light_surface.fill((10, 10, 10))
       
        for r in range(self.light_radius, 0, -30):
            alpha = max(0, 255 - (r * 0.8))
            pygame.draw.circle(
                self.light_surface,
                (alpha, alpha, alpha),
                (int(self.player.pos.x), int(self.player.pos.y)),
                r
            )
        self.screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_MULT)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    # Lógica de Menus
                    if self.state == MENU:
                        if event.key == pygame.K_UP: self.menu_sel = (self.menu_sel - 1) % 3
                        if event.key == pygame.K_DOWN: self.menu_sel = (self.menu_sel + 1) % 3
                        if event.key == pygame.K_RETURN:
                            if self.menu_sel == 0:
                                self.state = COUNTDOWN
                                self.countdown_start = pygame.time.get_ticks()
                                self.reset_game()
                                pygame.mixer.music.stop()
                            elif self.menu_sel == 1: self.state = SETTINGS
                            elif self.menu_sel == 2: running = False

                    elif self.state == SETTINGS:
                        if event.key == pygame.K_UP: self.set_sel = (self.set_sel - 1) % 3
                        if event.key == pygame.K_DOWN: self.set_sel = (self.set_sel + 1) % 3
                        if event.key == pygame.K_RETURN:
                            if self.set_sel == 0: self.state = VIDEO
                            elif self.set_sel == 1: self.state = AUDIO
                            elif self.set_sel == 2: self.state = MENU

                    elif self.state == VIDEO:
                        if event.key == pygame.K_UP: self.video_sel = (self.video_sel - 1) % 3
                        if event.key == pygame.K_DOWN: self.video_sel = (self.video_sel + 1) % 3
                        if event.key == pygame.K_RETURN:
                            if self.video_sel == 0:
                                self.res_index = (self.res_index + 1) % len(RESOLUTIONS)
                                self.width, self.height = RESOLUTIONS[self.res_index]
                                self.apply_video()
                                self.light_surface = pygame.Surface((self.width, self.height))
                                self.reset_game()
                            elif self.video_sel == 1:
                                self.fullscreen = not self.fullscreen
                                self.apply_video()
                            elif self.video_sel == 2: self.state = SETTINGS

                    elif self.state == AUDIO:
                        if event.key == pygame.K_UP: self.audio_sel = (self.audio_sel - 1) % 3
                        if event.key == pygame.K_DOWN: self.audio_sel = (self.audio_sel + 1) % 3
                        if event.key == pygame.K_RETURN:
                            if self.audio_sel == 0:
                                self.menu_music_on = not self.menu_music_on
                                if not self.menu_music_on: pygame.mixer.music.stop()
                                else: self.play_menu_music()
                            elif self.audio_sel == 1:
                                self.game_music_on = not self.game_music_on
                            elif self.audio_sel == 2: self.state = SETTINGS

                    elif self.state == GAME_OVER:
                        if event.key == pygame.K_UP: self.game_over_sel = (self.game_over_sel - 1) % 2
                        if event.key == pygame.K_DOWN: self.game_over_sel = (self.game_over_sel + 1) % 2
                        if event.key == pygame.K_RETURN:
                            if self.game_over_sel == 0:
                                self.state = COUNTDOWN
                                self.countdown_start = pygame.time.get_ticks()
                                self.reset_game()
                                pygame.mixer.music.stop()
                            elif self.game_over_sel == 1:
                                self.state = MENU
                                self.menu_sel = 0
                                self.reset_game()
                                self.play_menu_music()

                    elif self.state == WIN:
                        if event.key == pygame.K_UP: self.win_sel = (self.win_sel - 1) % 2
                        if event.key == pygame.K_DOWN: self.win_sel = (self.win_sel + 1) % 2
                        if event.key == pygame.K_RETURN:
                            if self.win_sel == 0:
                                self.state = COUNTDOWN
                                self.countdown_start = pygame.time.get_ticks()
                                self.reset_game()
                                pygame.mixer.music.stop()
                            elif self.win_sel == 1:
                                self.state = MENU
                                self.menu_sel = 0
                                self.reset_game()
                                self.play_menu_music()

           #Lógica do jogo 
            if self.state == COUNTDOWN:
                elapsed = (pygame.time.get_ticks() - self.countdown_start) // 1000
                if elapsed >= 3:
                    self.state = PLAYING
                    self.play_game_music()

            elif self.state == PLAYING:
                self.player.move(self.walls, self.width, self.height)
                for enemy in self.enemies:
                    # Aumentar velocidade do inimigo baseado na dificuldade
                    original_speed = enemy.speed / self.difficulty
                    enemy.speed = original_speed * self.difficulty
                    enemy.update(self.player, self.walls)
                    if enemy.pos.distance_to(self.player.pos) < 25:
                        if self.snd_lose: self.snd_lose.play()
                        self.state = GAME_OVER
                        self.game_over_sel = 0

                if self.collectible.pos.distance_to(self.player.pos) < 30:
                    if self.snd_collect: self.snd_collect.play()
                    self.score += 1
                    self.collectible = Collectible(self.width, self.height)
                    
                    # Aumentar dificuldade a cada nível: a cada bola, aumenta 15%
                    self.difficulty = 1.0 + (self.score * 0.15)
                    
                    if self.score >= self.target_score:
                        if self.level < 3:
                            self.level += 1
                            self.reset_game()
                        else:
                            self.state = WIN
                            self.win_time = pygame.time.get_ticks()

          
            self.screen.fill(BLACK)

            if self.state == MENU:
                self.draw_center("NEON COIN", 120, CYAN)
                self.draw_list(["INICIAR JOGO", "DEFINIÇÕES", "SAIR"], self.menu_sel)

            elif self.state == SETTINGS:
                self.draw_center("DEFINIÇÕES", 120, YELLOW)
                self.draw_list(["VÍDEO", "ÁUDIO", "VOLTAR"], self.set_sel)

            elif self.state == VIDEO:
                self.draw_center("VÍDEO", 120, YELLOW)
                self.draw_list([f"Res: {self.width}x{self.height}", f"Tela Cheia: {self.fullscreen}", "VOLTAR"], self.video_sel)

            elif self.state == AUDIO:
                self.draw_center("ÁUDIO", 120, YELLOW)
                menu_text = f"Música - Menu: {'Sim' if self.menu_music_on else 'Não'}"
                game_text = f"Música - Jogo: {'Sim' if self.game_music_on else 'Não'}"
                self.draw_list([menu_text, game_text, "VOLTAR"], self.audio_sel)

            elif self.state == COUNTDOWN:
                rem = 3 - ((pygame.time.get_ticks() - self.countdown_start) // 1000)
                self.draw_center(str(max(1, rem)), self.height // 2 - 50, YELLOW)

            elif self.state == PLAYING:
                self.screen.fill(self.bg_color)
                for w in self.walls: w.draw(self.screen)
                self.collectible.draw(self.screen)
                self.player.draw(self.screen)
                for e in self.enemies: e.draw(self.screen)
                self.draw_lighting()
                score_txt = self.font_med.render(f"Nível {self.level} - Moedas: {self.score}/{self.target_score}", True, WHITE)
                self.screen.blit(score_txt, (20, 20))

            elif self.state == WIN:
                self.draw_center("PARABÉNS!", self.height // 2 - 150, GREEN)
                self.draw_center("GANHASTE O JOGO!", self.height // 2 - 70, CYAN)
                
           
                for i, item in enumerate(["TENTAR NOVAMENTE", "VOLTAR AO MENU"]):
                    col = YELLOW if i == self.win_sel else WHITE
                    txt = self.font_med.render(item, True, col)
                    y_pos = self.height // 2 + 60 + i * 80
                    self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, y_pos))

            elif self.state == GAME_OVER:
                self.draw_center("PERDESTE!", self.height // 2 - 150, RED)
                self.draw_center(f"Pontuação: {self.score}/{self.target_score}", self.height // 2 - 50, YELLOW)
                
               
                for i, item in enumerate(["TENTAR NOVAMENTE", "VOLTAR AO MENU"]):
                    col = YELLOW if i == self.game_over_sel else WHITE
                    txt = self.font_med.render(item, True, col)
                    y_pos = self.height // 2 + 50 + i * 80
                    self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, y_pos))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def draw_center(self, text, y, color):
        txt = self.font_big.render(text, True, color)
        self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, y))

    def draw_list(self, items, sel):
        for i, it in enumerate(items):
            col = YELLOW if i == sel else WHITE
            txt = self.font_med.render(it, True, col)
            self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, 300 + i * 60))

if __name__ == "__main__":
    Game().run()







