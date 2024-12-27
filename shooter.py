import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

moving_right = False
moving_left = False 
moving_right_a = False
moving_left_a = False 

x = 200
y = 200

#set background
BG = (141,201,120)

def draw_bg():
    screen.fill(BG)

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(f'Shooter/{self.char_type}.png')
        self.image = pygame.transform.scale(img,(int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()   
        self.rect.center = (x,y)

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
    
    def move(self, moving_left_a,moving_right_a):
        #reset movement variable
        dx = 0
        dy = 0

        #assign movement variable if moving left or right
        if moving_left_a:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right_a:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #update rectable position
        self.rect.y += dy
        self.rect.x += dx

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


#set framerate
clock = pygame.time.Clock()
FPS = 60

#define players
player = Soldier('player', 200,200, 3, 5)
enemy = Soldier('enemy', 400, 200, 3, 5)


run = True
while run:

    draw_bg()

    clock.tick(FPS)

    player.draw()
    enemy.draw()


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
            if event.key == pygame.K_l:
                moving_left_a = True
            if event.key == pygame.K_j:
                moving_right_a = True
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
        


    pygame.display.update()

pygame.quit()            