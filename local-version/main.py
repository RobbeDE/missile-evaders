import pygame
import random
from pygame.locals import (
    RLEACCEL,
    K_SPACE,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_RETURN,
    K_BACKSPACE,
    KEYDOWN,
    QUIT,
)
import asyncio

#constants for screen height and width
HEIGHT = 800
WIDTH = 1200

screen = pygame.display.set_mode((WIDTH,HEIGHT))

# Initialize Pygame and Pygame Font Module
pygame.init()

#defining classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player,self).__init__()
        self.surf = pygame.image.load("assets/sprites/jet.png").convert()
        self.surf.set_colorkey((255,255,255),RLEACCEL)
        self.rect = self.surf.get_rect()
        self.speed = 10
    def update(self, pressed_keys):
        if pressed_keys[K_UP] == True:
            self.rect.move_ip(0,-self.speed)
        if pressed_keys[K_DOWN] == True:
            self.rect.move_ip(0,self.speed)
        if pressed_keys[K_LEFT] == True:
            self.rect.move_ip(-self.speed,0)
        if pressed_keys[K_RIGHT] == True:
            self.rect.move_ip(self.speed,0)
        if self.rect.top<=0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.left<=0:
            self.rect.left = 0
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy,self).__init__()
        self.surf = pygame.image.load("assets/sprites/missile.png").convert()
        self.surf.set_colorkey((255,255,255),RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                WIDTH,random.randint(0,HEIGHT)
                )
            )
        self.speed = random.randint(4,10)
    def update(self):
        self.rect.move_ip(-self.speed,0)
        if self.rect.left <= 0:
            self.kill()
            
class Clouds(pygame.sprite.Sprite):
    def __init__(self):
        super(Clouds,self).__init__()
        self.surf = pygame.image.load("assets/sprites/cloud.png").convert()
        self.surf.set_colorkey((0,0,0),RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                WIDTH,random.randint(0,HEIGHT)
                )
            )
        self.speed = 6
    def update(self):
        self.rect.move_ip(-self.speed,0)
        if self.rect.left < 0:
            self.kill()
class Text:
    def __init__(self,text,font,coX,coY,color):   
        Font = pygame.font.Font("freesansbold.ttf",font)
        self.surf = Font.render(text,True,color)
        self.rect = self.surf.get_rect()
        self.text = text
        self.rect.center = (coX,coY)
    def update(self):
        screen.blit(self.surf, self.rect)
        
class Shape:
    def __init__(self,width,height, color, coX, coY):
        self.surf = pygame.Surface((width,height))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(
            center = (coX,coY)
            )
    def update(self):
        screen.blit(self.surf,self.rect)

ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY,100)
ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD,200)

pygame.mixer.init()

#initiate pygame
pygame.init()

#assign objects to classes
player = Player()

#create groups and assign sprites
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
clouds = pygame.sprite.Group()
all_sprites.add(player)

clock = pygame.time.Clock()

pygame.display.set_caption("Missile Evaders")

async def main():
    running = True

    click = pygame.mixer.Sound("assets/soundtracks/click.wav")
    start = pygame.mixer.Sound("assets/soundtracks/start.wav")
    pygame.mixer.music.load("assets/soundtracks/main2.mp3")
    pygame.mixer.music.play(loops=-1)

    playername = ""
    input_active = True
    input_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 32, 200, 64)
    color_active = pygame.Color('lightskyblue3')
    color_passive = pygame.Color('gray15')
    color = color_passive
    font = pygame.font.Font(None, 64)

    while input_active:
        screen.fill((135, 206, 235))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    start.play()
                    input_active = False
                elif event.key == K_BACKSPACE:
                    playername = playername[:-1]
                else:
                    playername += event.unicode
            if event.type == ADDCLOUD:
                new_cloud = Clouds()
                all_sprites.add(new_cloud)
                clouds.add(new_cloud)
        
        clouds.update()
        for entity in clouds:
            screen.blit(entity.surf, entity.rect)

        header = Text("Give in a username, press space to proceed",44,WIDTH//2,HEIGHT//4,(0,0,0))
        header.update()

        # Render the current playername
        txt_surface = font.render(playername, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_rect.w = width
        screen.blit(txt_surface, (input_rect.x + 5, input_rect.y + 5))
        pygame.draw.rect(screen, color, input_rect, 2)

        pygame.display.flip()
        clock.tick(30)

        await asyncio.sleep(0)

    explosion = pygame.mixer.Sound("assets/soundtracks/Explosion+3.wav")
    running = True

    score_int = 0

    while running:
        score_int +=1
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == QUIT:
                running = False
            elif event.type == ADDENEMY:
                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)
            if event.type == ADDCLOUD:
                new_cloud = Clouds()
                all_sprites.add(new_cloud)
                clouds.add(new_cloud)
                
        #capturing player and enemy movements
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)
        enemies.update()
        clouds.update()
        
        #screen background 
        screen.fill((135,206,235))
        
        #plotting all sprites
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        if pygame.sprite.spritecollideany(player,enemies):
            explosion.play()
            player.kill()
            running = False
        
        #tracking score
        score_string2 = str(score_int)
        score_string1 = "score: "
        score_string = score_string1 + score_string2
        score_text = Text(score_string, 35, 1080, 25,(0,0,0))
        score_text.update()
        
        #refresh display
        pygame.display.flip()
        clock.tick(60)

        await asyncio.sleep(0)


    all_scores = open("data/Missile Evaders all scores.txt","a")
    score_log = playername + ": " + score_string +"\n"
    all_scores.write(score_log)
    all_scores.close()
    high_scores = open("data/Missile Evaders highscores.txt", "r")
    high_score_list = []
    teller = 0
    for x in high_scores:
        sep_line = x.split(": ")
        sep_line[1] = sep_line[1].strip("\n")
        high_score_list.append(dict(profile = sep_line[0], score = int(sep_line[1]))) 
    high_score_list.append(dict(profile = playername, score = score_int))
    sort_list = []
    for x in range(6):
        sort_list.append(high_score_list[x].get("score"))
    sort_list.sort()
    sort_list.pop(0)
    sort_list.reverse()
    high_score_list_new = []
    high_score_list_new_strings = []
    for x in range(5):
        for y in range(6):      
            if sort_list[x] == high_score_list[y].get("score"):
                high_score_list_new.append(high_score_list[y])
                high_score_list_new_strings.append(high_score_list_new[x].get("profile") + ": " + str(high_score_list_new[x].get("score")) + "\n")
                break
    high_scores.close()
    high_scores = open("data/Missile Evaders highscores.txt", "w")
    for x in high_score_list_new_strings:
        high_scores.write(x)
    high_scores.close()


    running = True

    while running:
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                elif event.key == K_SPACE:
                    running = False
        game_over = Text("GAME OVER", 120, WIDTH//2, 150, (255,255,255))
        game_over.update()

        high_scores_display = Text("HIGHSCORES",50,WIDTH//2,300,(255,255,255))
        high_scores_display.update()
        for x in range(5):
            high_score_string_stripped = high_score_list_new_strings[x].strip("\n")
            high_score_string_display = Text(high_score_string_stripped,40,WIDTH//2,400 + 70*x, (255,255,255))
            high_score_string_display.update()
        
        pygame.display.flip()


        await asyncio.sleep(0)

# This is the program entry point
asyncio.run(main())

pygame.quit()
    
