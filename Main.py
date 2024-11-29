import pygame
import sys
import csv
import os
import button
import Zombie_game.Zombie_game as Z
import random
import time
pygame.init()

screen_width = 1400
screen_height = 780

# Global variables
sokill=0
run = True
level = 1
start_game = False
is_win = False
restart = False
paused= False
ROWS = 16
COLS = 29
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 21
scroll = 200
screen_scroll = 0
bg_scroll = 0
isdie = True
record = 0
count = 0
is_muted = False
#Display and asset info

bg_musicHome = pygame.mixer.Sound('Sound/cottagecore-17463.mp3')
hit_sound = pygame.mixer.Sound('Sound/sound bắn trúg zombie.mp3')
bg_music = pygame.mixer.Sound('Sound/nền.mp3')
shot_music = pygame.mixer.Sound('Sound/tiếng súng .mp3')
start_music = pygame.mixer.Sound('Sound/fight khi start game.mp3')
died_music = pygame.mixer.Sound('Sound/Mình chết.mp3')

bg_music.set_volume(0.1)
bg_musicHome.set_volume(0.4)
shot_music.set_volume(0.2)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ngôi trường xác sống")
clock = pygame.time.Clock()


#Load images

#Button images
start_img = pygame.transform.scale(pygame.image.load('asset2/start.png').convert_alpha(), (200, 111))
exit_img = pygame.transform.scale(pygame.image.load('asset2/exit.png'), (200, 111))
resume_img = pygame.transform.scale(pygame.image.load('asset2/resume.png'), (200, 111))
restart_img = pygame.transform.scale(pygame.image.load('asset2/restart.png'), (200, 111))
board_img = pygame.transform.scale(pygame.image.load('asset2/board.png'), (1200, 635))
menu_img = pygame.transform.scale(pygame.image.load('asset2/menu.png'), (200, 111))
mute_img = pygame.transform.scale(pygame.image.load('asset2/mute.png'), (46, 46))
unmute_img = pygame.transform.scale(pygame.image.load('asset2/unmute.png'), (50, 50))


#Background images
bg_surface = pygame.transform.scale(pygame.image.load('asset2/background13.png'), (1400, 787))
portal_suface = pygame.transform.scale(pygame.image.load('asset2/portal.png').convert_alpha(), (120, 120))
portal_rect = portal_suface.get_rect(center = (1328, 608))
bg_img = pygame.transform.scale(pygame.image.load('asset2/background11.png'), (1400, 787))
red_heart = pygame.transform.scale(pygame.image.load('asset2/red-heart.png'), (30, 30))
black_heart = pygame.transform.scale(pygame.image.load('asset2/black-heart.png'), (30, 30))
heart_rect = red_heart.get_rect(center = (25, 30))

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'asset2/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
    
# #define fonts
# font = pygame.font.SysFont('arialblack', 40)
# def draw_text(text, font, text_col, x, y):
#     img = font.render(text, True, text_col)
#     screen.blit(img, (x, y))
custom_font_48 = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", 48)
custom_font_24 = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", 24)

win_text = custom_font_48.render('YOU WIN!', False, 'White').convert_alpha()
win_rect = win_text.get_rect(center=(screen_width*0.5, screen_height*0.2))
#define player action variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False
attacking = False

def draw_bg():
    screen.fill('#89A477')
    screen.blit(bg_surface, (0, 0))
    # Hiển thị 10 trái tim đỏ
    for i in range(10):
        x_position = 25 + i * (27 + 10)  # 20 là cách lề trái, 27 là chiều rộng ảnh, 10 là khoảng cách giữa ảnh
        screen.blit(red_heart, (x_position, 25)) # 25 là vị trí y để căn giữa ảnh theo chiều cao
    if is_win:
        screen.blit(portal_suface, portal_rect)
def reset_level():
    data = []
    for row in range(ROWS + 1):
        r = [-1] * COLS
        data.append(r)
    return data

def displayScore():
    score_surface = custom_font_48.render(f'KILLS: {count}', False, "White")
    score_rect = score_surface.get_rect(topright=(screen_width - 30, 10))
    screen.blit(score_surface, score_rect)

class Character(pygame.sprite.Sprite):
    def __init__(self, char, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.awin = False
        self.char = char
        self.scale = scale
        self.speed = speed
        self.direction = 1 
        self.flip = False
        self.frame_index = 0
        self.animation_list = []
        self.action = 0
        self.health = 100
        self.max_health = self.health
        self.update_time = pygame.time.get_ticks()
        #load all images for the player
        animation_types = ['left', 'right', 'up', 'down']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'player_{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'player_{animation}/{animation}_{i + 1}.png').convert_alpha()
                img = pygame.transform.scale(img, (40, 80))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.imgage = self.animation_list[self.action][self.frame_index]
        self.rect = self.imgage.get_rect(center = (x, y))
        self.x = x
        self.y = y
        self.width = self.imgage.get_width()
        self.height = self.imgage.get_height()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.imgage = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
    
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def update(self):
        self.update_animation()
        self.check_alive()
    
    def draw(self):
        if self.action != -1: screen.blit(self.imgage ,self.rect)
        else: 
            screen.blit(pygame.transform.scale(pygame.image.load('player_down/down_2.png').convert_alpha(), (40, 80)), self.rect)
    def move(self, moving_left, moving_right, moving_up, moving_down):
        screen_scroll = 0
        dx = 0
        dy = 0
        if moving_left:
            dx -= self.speed
            self.direction = -1
        if moving_right:
            dx += self.speed
            self.direction = 1 
        if moving_up:
            dy -= self.speed
            self.direction = -1
        if moving_down:
            dy += self.speed
            self.direction = 1  
        #check for collision
        for tile in world.obstancle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                dy = 0
        self.rect.x += dx
        self.rect.y += dy 
        self.x += dx
        self.y += dy
        if (self.rect.right > screen_width - scroll and bg_scroll < (world.level_length * TILE_SIZE - 300) - screen_width) or (self.rect.right < scroll and (self.direction == -1 or moving_down or moving_up) and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx
        return screen_scroll
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            
            
class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health       
        
#Creat map     
class World():
    def __init__(self):
        self.obstancle_list = []
        self.tile_list = []
    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                img = img_list[tile]
                img_rect = img.get_rect()
                img_rect.x = x * TILE_SIZE
                img_rect.y = y * TILE_SIZE
                tile_data = (img, img_rect)
                if tile == 16:
                    self.obstancle_list.append(tile_data)
                elif tile == 15:
                    player = Character('player_img', 80, 680, 1, 5)  
                else:
                    self.tile_list.append(tile_data)
        return player
    def draw(self):
        for tile in self.obstancle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
        for tile in self.tile_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
                       
#get data from excel
world_data = []
for row in range(ROWS + 1):
	r = [-1] * COLS
	world_data.append(r)
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
            
#creat buttons
start_button = button.Button(screen_width // 2 - 100, screen_height // 2 - 300, start_img, 1)
exit_button = button.Button(screen_width // 2 - 100, screen_height // 2 - 150, exit_img, 1)
restart_button = button.Button(screen_width // 2 - 100, screen_height // 2 - 150, restart_img, 1)
menu_button = button.Button(screen_width // 2 - 100, screen_height // 2 - 300, menu_img, 1)
resume_button = button.Button(screen_width // 2 - 100, screen_height // 2 - 300, resume_img , 1)
mute_button = button.Button(screen_width - 60, 10, mute_img , 1)
unmute_button = button.Button(screen_width - 60, 10, unmute_img , 1)
#Create objects
world = World()
player = world.process_data(world_data)
# enemy1 = Z.Enemy(161, 173, 75, 75, 'Zombies/Baby Zombie.png', 3, 5)
# enemy2 = Z.Enemy(1292, 121, 75, 75, 'Zombies/Boy Zombie.png', 3, 5)
# enemy3 = Z.Enemy(1306, 611, 75, 75, 'Zombies/Baby Zombie.png', 3, 5)
times=0
delay = 10000
enemy=Z.Enemy(161,173,75,75,f'Zombies/{random.randint(1,4)}_Zombie.png',4,5)
enemy=Z.Enemy(1292, 121, 80, 80, f'Zombies/{random.randint(1,4)}_Zombie.png', 3, 4)    
enemy=Z.Enemy(1306, 611, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 2) 
start_ticks=pygame.time.get_ticks()
    
target=Z.Object(0,0,50,50,pygame.image.load("player_bullet/tam.png"))


bullets = []

def shoot():
    
    player_center =player.rect.center
    r1=sokill //10
    if r1==0:
        bullet=Z.Object(player_center[0]-15,player_center[1]-17,30,34,pygame.image.load("player_bullet/bullet_D.png"))
    elif r1==1:
        bullet=Z.Object(player_center[0]-15,player_center[1]-17,30,34,pygame.image.load("player_bullet/bullet_C.png"))
    elif r1==2:
        bullet=Z.Object(player_center[0]-15,player_center[1]-17,30,34,pygame.image.load("player_bullet/bullet_B.png"))
    else:
        bullet=Z.Object(player_center[0]-15,player_center[1]-17,30,34,pygame.image.load("player_bullet/bullet_red.png"))

    target_center=target.get_center()
    bullet.velocity=pygame.math.Vector2(target_center[0]-player_center[0],target_center[1]-player_center[1])
    bullet.velocity.normalize_ip()
    bullet.velocity*=6
    bullets.append(bullet)


#added by bao
def reset_game():
    # Reset các biến toàn cục
    global times, start_ticks, player, world, count, target, sokill
    
    # Xóa các đối tượng
    Z.enemies.clear()
    Z.objects.clear()
    Z.particles.clear()
    Z.health_items.clear()
    
    
    # Reset biến đếm và thời gian
    times = 0
    count = 0
    sokill =0
    start_ticks = pygame.time.get_ticks()
    #thêm lại các enemy ban đầu 
    enemy=Z.Enemy(161, 173, 75, 75,f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 5)
    enemy=Z.Enemy(1292, 121, 80, 80, f'Zombies/{random.randint(1,4)}_Zombie.png', 3, 4)    
    enemy=Z.Enemy(1306, 611, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 2)     
    # Reset player và world
    world_data = reset_level()
    with open(f'level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
    world = World()
    player = world.process_data(world_data)
    player.alive = True
    player.health = 100
    
    # Reset target (chuột)
    target = Z.Object(0, 0, 50, 50, pygame.image.load("player_bullet/tam.png"))
while run:
    clock.tick(60)
    current_ticks = pygame.time.get_ticks()
    if current_ticks-start_ticks>=delay and times < 5:
        enemy=Z.Enemy(161,173,75,75,f'Zombies/{random.randint(1,4)}_Zombie.png',4,5)
        enemy=Z.Enemy(1292, 121, 80, 80, f'Zombies/{random.randint(1,4)}_Zombie.png', 3, 4)    
        enemy=Z.Enemy(1306, 611, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 4) 
        enemy=Z.Enemy(75, 611, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 3, 4) 

        times+=1
        start_ticks=current_ticks
    elif current_ticks-start_ticks>=delay and times < 8:
        enemy=Z.Enemy(161,173,75,75,f'Zombies/{random.randint(1,4)}_Zombie.png',4,5)
        enemy=Z.Enemy(1292, 121, 80, 80, f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 4)    
        enemy=Z.Enemy(1306, 611, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 3, 4) 
        enemy=Z.Enemy(75, 611, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 4) 
        enemy=Z.Enemy(780, 693, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 4)
        times+=1
        start_ticks=current_ticks
    elif current_ticks-start_ticks>=delay and times == 8:
        enemy=Z.Enemy(161,173,100,100,f'Zombies/5_Zombie.png', 2, 25)
        enemy=Z.Enemy(1306,611,120,120,f'Zombies/6_Zombie.png',2, 30)
        enemy=Z.Enemy(1292, 121, 80, 80, f'Zombies/{random.randint(1,4)}_Zombie.png', 4, 4)    
        enemy=Z.Enemy(75, 611, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 3, 2) 
        enemy=Z.Enemy(780, 693, 60, 60, f'Zombies/{random.randint(1,4)}_Zombie.png', 3, 2) 
        times += 1
    if len(Z.enemies)==0 and times == 9:
        is_win = True
    if start_game == False:
        pygame.mouse.set_visible(True)
        bg_music.stop()
        bg_musicHome.play(loops = -1, fade_ms = 5)
        screen.blit(bg_img, (0, 0))
        if start_button.draw(screen):
            bg_musicHome.stop()
            start_music.play()
            start_game = True
            is_muted = False
        if exit_button.draw(screen):
            run = False
        if not is_muted:
            if unmute_button.draw(screen):
                start_music.set_volume(0)
                hit_sound.set_volume(0)
                bg_music.set_volume(0)
                shot_music.set_volume(0)
                died_music.set_volume(0)
                bg_musicHome.set_volume(0)
                is_muted = True
        else:
            if mute_button.draw(screen):
                start_music.play()
                hit_sound.play()
                bg_music.set_volume(0.1)
                shot_music.set_volume(0.2)
                died_music.play()
                bg_musicHome.set_volume(0.4)
                is_muted = False
        pygame.display.flip()
            
    elif is_win and player.rect.colliderect(portal_rect):
            screen.fill('Black')
            screen.blit(win_text, win_rect)
            if restart:
                #added by bao
                reset_game()

                player.alive = True
                player.health = 100
                world_data = reset_level()
                player.health = 100
                #restart map
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_data(world_data)
                start_game = False
                is_win = False
                count = 0
                times = 0
                len(Z.enemies)==0 
    elif paused == True:
        pygame.mouse.set_visible(True)
        bg_music.stop()
        bg_musicHome.play(loops = -1, fade_ms = 5)
        screen.blit(bg_img, (0, 0))
        if resume_button.draw(screen):
            paused= False
        if exit_button.draw(screen):
            run = False
    else:
        
        if player.alive:
            pygame.mouse.set_visible(False)
              
        bg_music.play(loops = -1, fade_ms = 3)  
        world.draw()
        draw_bg()
        player.update()
        player.draw()
        displayScore()
        for obj in Z.objects:
            if (type(obj)==Z.Enemy):
                obj.update(player)
            elif (type(obj)==Z.HealthItem ):
                obj.update(player, Z.health_items)
            else:
                obj.update()
            # - red heart; + black heart
            if player.health >= 90 and player.health < 100:
                screen.blit(black_heart, (25 + 9 * (27 + 10), 25))
            if player.health >= 80 and player.health < 90:
                for i in range(8, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health >= 70 and player.health < 80:
                for i in range(7, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health >= 60 and player.health < 70:
                for i in range(6, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health >= 50 and player.health < 60:
                for i in range(5, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health >= 40 and player.health < 50:
                for i in range(4, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health >= 30 and player.health < 40:
                for i in range(3, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health >= 20 and player.health < 30:
                for i in range(2, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health >= 10 and player.health < 20:
                for i in range(1, 10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 25))
            if player.health == 0:
                for i in range(10):
                    screen.blit(black_heart, (25 + i * (27 + 10), 26))
        for e in Z.enemies:
            if pygame.Rect.colliderect(e.image_rect,player.rect)==True:
                player.health-=0.5
                if player.health<=0:
                    player.alive=False
                continue      
            for b in bullets:
               if pygame.Rect.colliderect(e.image_rect,b.image_rect)==True:
                    if(e.take_damage(1)):
                        count += 1
                        sokill += 1
                    if b in bullets:
                        bullets.remove(b)
                    if b in Z.objects:  
                        Z.objects.remove(b)
        for item in Z.health_items[:]:
            item.draw()
        for p in Z.particles:
            p.image.set_alpha(p.image.get_alpha()-1)
            if p.image.get_alpha()==0:
                Z.objects.remove(p)
                Z.particles.remove(p)
                continue
            Z.objects.remove(p)
            Z.objects.insert(0,p)
        
              
        if player.alive:
            isdie = True
            bg_musicHome.stop()
            if moving_up:
                player.update_action(2)
            elif moving_down:
                player.update_action(3)
            elif moving_left:
                player.update_action(0) 
            elif moving_right:
                player.update_action(1) 
            else: player.action = -1
            screen_scroll = player.move(moving_left, moving_right, moving_up, moving_down)
            bg_scroll -= screen_scroll
        else:
            # pygame.mouse.set_visible(True)
            bg_music.stop()
            if isdie:
                died_music.play()
                isdie = False
            bg_musicHome.play(loops = -1, fade_ms = 5)
            screen.blit(bg_img, (0, 0))
            screen_scroll = 0
            #button restart
            if restart_button.draw(screen):
                #added by bao
                reset_game()

                player.alive = True
                player.health = 100
                world_data = reset_level()
                player.health = 100
                #restart map
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_data(world_data)
                times = 0
                count = 0
                
            #button menu
            if menu_button.draw(screen):
                #added by bao
                reset_game()
                player.alive = True
                player.health = 100
                world_data = reset_level()
                player.health = 100
                #restart map
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_data(world_data)
                start_game = False  #Go to menu
                count = times = 0
                
        mousePos=pygame.mouse.get_pos()
        target.x=mousePos[0]-target.width//2
        target.y=mousePos[1]-target.height//2
        if player.alive == False:
            pygame.mouse.set_visible(True)
            pygame.display.update()
    #Even game            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if player.alive:
            if event.type == pygame.MOUSEBUTTONDOWN:            
                bg_music.stop()
                shot_music.play()
                bg_music.play(loops = -1, fade_ms = 5)
                shoot()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_SPACE:
                paused = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False
            if event.key == pygame.K_ESCAPE:
                run = False
    #draw_text('Press SPACE to pause', font, 'White', 100, 250)
    pygame.display.update()
    
pygame.quit()
sys.exit()