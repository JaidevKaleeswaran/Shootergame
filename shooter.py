import pygame
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

moving_right = False
moving_left = False 
moving_right_a = False
moving_left_a = False 

shoot = False
shoot_a = False
grenade = False
grenade_a = False
grenade_thrown = False
grenade_thrown_a = False


GRAVITY = 0.75
TILE_SIZE = 40

#load images
bullet_png = pygame.image.load('Shooter/img/icons/bullet.png')
grenade_png = pygame.image.load('Shooter/img/icons/grenade.png')

#set background
BG = (141,201,120)
RED = (255,0,0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen,RED, (0,300), (SCREEN_WIDTH,300))

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
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * 0.6 * self.direction), self.rect.centery,self.direction)
            bullet_group.add(bullet)
            #shoot ammo
            self.ammo -= 1

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


enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()





#set framerate
clock = pygame.time.Clock()
FPS = 60

#define players
player = Soldier('player', 200, 200, 3, 5, 20, 2)
enemy = Soldier('enemy', 400, 200, 3, 5, 20, 2)
enemy2 = Soldier('enemy', 500, 200, 3, 5, 20, 2)
enemy_group.add(enemy2)
enemy_group.add(enemy)

run = True
while run:

    draw_bg()

    clock.tick(FPS)

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.update()
        enemy.draw()

    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)

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
    if enemy.alive:
        if shoot_a:
            enemy.shoot()
        elif grenade_a and grenade_thrown_a == False and enemy.grenades > 0:
            grenade_a = Grenade(enemy.rect.centerx + (0.5 * enemy.rect.size[0] * enemy.direction),
			 			enemy.rect.top, enemy.direction)
            grenade_group.add(grenade_a)
			#reduce grenades
            enemy.grenades -= 1
            grenade_thrown_a = True
        if enemy.in_air:
            enemy.update_action(2)
        elif moving_left_a or moving_right_a:
            enemy.update_action(1)
        else:
            enemy.update_action(0)
    player.move(moving_right, moving_left)
    enemy.move(moving_right_a, moving_left_a)


    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
    
        #set keybinds
        if event.type ==  pygame.KEYDOWN:
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
            if event.key == pygame.K_o:
                grenade_a = True
            if event.key == pygame.K_k:
                shoot_a = True
            if event.key == pygame.K_l:
                moving_left_a = True
            if event.key == pygame.K_j:
                moving_right_a = True
            if event.key == pygame.K_i:
                enemy.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False


        if event.type ==  pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_right = False
            if event.key == pygame.K_d:
                moving_left = False
            if event.key == pygame.K_l:
                moving_left_a = False
            if event.key == pygame.K_j:
                moving_right_a = False
            if event.key == pygame.K_s:
                shoot = False
            if event.key == pygame.K_k:
                shoot_a = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
            if event.key == pygame.K_o:
                grenade_a = False
                grenade_thrown_a = False
        


    pygame.display.update()

pygame.quit()            