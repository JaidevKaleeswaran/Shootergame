import pygame
import os
import random
import button
import csv

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN,SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Shooter')

moving_right = False
moving_left = False 
moving_right_a = False
moving_left_a = False 

scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

shoot = False
shoot_a = False
grenade = False
grenade_a = False
grenade_thrown = False
grenade_thrown_a = False


GRAVITY = 0.75
ROWS = 16
COLUMNS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 1
current_tile = 0


#load images
bullet_png = pygame.image.load('Shooter/img/icons/bullet.png').convert_alpha()
grenade_png = pygame.image.load('Shooter/img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('Shooter/img/icons/health_box.png').convert_alpha()
ammo_img = pygame.image.load('Shooter/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('Shooter/img/icons/grenade_box.png').convert_alpha()
pine1_img = pygame.image.load('Shooter/img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('Shooter/img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('Shooter/img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('Shooter/img/Background/sky_cloud.png').convert_alpha()

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Shooter/img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

item_boxes = {
    'Health'    : health_box_img,
    'Ammo'      : ammo_box_img,
    'Grenade'   : grenade_box_img
}

save_img = pygame.image.load(f'Shooter/img/save_btn.png').convert_alpha()
load_img = pygame.image.load(f'Shooter/img/load_btn.png').convert_alpha()

# create buttons
save_button = button.Button(SCREEN_HEIGHT // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_HEIGHT // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
# make a button list
button_list = []
button_col = 0
button_row = 0
for x in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[x], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col ==3:
        button_row += 1
        button_col = 0

#set background
BG = (141,201,120)
GREEN = (0,255,0)
BLACK = (0,0,0)
RED = (255,0,0)
WHITE = (255,255,255)

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(4):
        screen.blit(sky_img, ((x*width) -scroll * 0.5 ,0))
        screen.blit(mountain_img, ((x*width)-scroll*0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x*width)-scroll*0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x*width)-scroll*0.8, SCREEN_HEIGHT - pine2_img.get_height()))

#set text attributes
font = pygame.font.SysFont('Futura', 20)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def draw_grid():
    #vertical lines
    for c in range(COLUMNS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    # horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE),( SCREEN_WIDTH, c * TILE_SIZE))

#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLUMNS
    world_data.append(r)

#create ground
for tile in range(0, COLUMNS):
    world_data[ROWS - 1][tile] = 0
print(world_data)    

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,150,20)
        self.idling = False
        self.idling_counter = 0

        #load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
			#reset temporary list of images
            temp_list = []
			#count number of files in the folder
            num_of_frames = len(os.listdir(f'Shooter/img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Shooter/img/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)



        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    #move for player
    def move(self, moving_left,moving_right):
        #reset movement variable
        dx = 0
        dy = 0

        #assign movement variable if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #update rectable position
        self.rect.y += dy
        self.rect.x += dx


    #move for enemy
    def move(self, moving_left, moving_right):
		#reset movement variables
        dx = 0
        dy = 0

		#assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

		#jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

		#apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

		#check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

		#update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * 0.75 * self.direction), self.rect.centery,self.direction)
            bullet_group.add(bullet)
            #shoot ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,200) == 1:
                self.update_action(0) #idle
                self.idling = True
                self.idling_counter = 50
            #check if ai is near player
            if self.vision.colliderect(player.rect):
                self.update_action(0) # idle
                self.shoot()
            if self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                else :
                    ai_moving_right = False
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left, ai_moving_right)
                self.update_action(1) # run
                self.move_counter += 1
                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                if self.move_counter > TILE_SIZE:
                    self.direction *= -1
                    self.move_counter *= -1    
            else:
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False            

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    #no overlapping animations
    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if animation has run out thn reset to start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animations settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen , RED, self.rect, 1)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
                print('player', player.health)
            if self.item_type == 'Ammo':
                player.ammo += 15
                print('player', player.ammo)
            if self.item_type == 'Grenade':
                player.grenades += 3
                print('player', player.grenades)
            self.kill()
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health

        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20)) 
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))    
        

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_png
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet went off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check for collision
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 20
                print("player", player.health)
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 20
                    print("enemy", enemy.health)
                    self.kill()
            
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_png
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0

        #check collision with walls
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed
        
        #update grenade pos
        self.rect.x += dx
        self.rect.y += dy

        #countdown timera
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 3)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
                print('player', player.health)    

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                    print('enemy', enemy.health)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'Shooter/img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        #update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if animation is done, delete explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

        

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

#temp
item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 260)
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 500, 260)
item_box_group.add(item_box)



#set framerate
clock = pygame.time.Clock()
FPS = 60

#define players
player = Soldier('player', 200, 200, 1.65, 3, 20, 2)
health_bar = HealthBar(10,10, player.health, player.health)

enemy = Soldier('enemy', 400, 200, 1.65, 3, 20, 2)
enemy2 = Soldier('enemy', 300, 200, 1.65, 3, 20, 2)
enemy_group.add(enemy2)
enemy_group.add(enemy)

run = True
while run:
    #set background
    draw_bg()
    draw_grid()
    draw_world()
    
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    #save and load data
    save_button.draw(screen)
    load_button.draw(screen)

    #highlight selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    #add new tiles to screen
    #get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    #check if within the screen
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        #update tile value
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile 
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    #healthbar
    health_bar.draw(player.health)

    #show ammo
    draw_text(f'AMMO: ', font, WHITE, 10, 35)
    for x in range(player.ammo):
        screen.blit(bullet_png, (90 + (x * 10), 45))
    draw_text(f'GRENADES: ', font, WHITE, 10, 60)
    for x in range(player.grenades):
        screen.blit(grenade_png, (135 + (x * 20), 65))

    clock.tick(FPS)

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)

    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True:
        scroll += 5 * scroll_speed

    if player.alive:
    #update player moving action
        if shoot:
            player.shoot()
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
			 			player.rect.top, player.direction)
            grenade_group.add(grenade)
			#reduce grenades
            player.grenades -= 1
            grenade_thrown = True
        if player.in_air:
            player.update_action(2) # jump
        elif moving_left or moving_right:
            player.update_action(1) #idle
        else:
            player.update_action(0) #run
    player.move(moving_right, moving_left)


    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
    
        #set keybinds
        if event.type ==  pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_left = True    
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5    
            if event.key == pygame.K_a:
                moving_right = True
            if event.key == pygame.K_d:
                moving_left = True
            if event.key == pygame.K_w:
                player.jump = True
            if event.key == pygame.K_s:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_ESCAPE:
                run = False


        if event.type ==  pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_right = False
            if event.key == pygame.K_d:
                moving_left = False
            if event.key == pygame.K_s:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
            if event.key == pygame.K_LEFT:
                scroll_left = False    
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1 


    pygame.display.update()

pygame.quit()            