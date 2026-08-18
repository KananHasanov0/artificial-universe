import pygame
import math

class Body:
    def __init__(self,x,y,velocity_x,velocity_y,radius,mass,restitution):
        self.x = x
        self.y = y
        self.velocity_y = velocity_y
        self.velocity_x = velocity_x
        self.radius = radius
        self.mass = mass
        self.restitution = restitution

    def update(self, dt, acceleration):
        change_x = self.velocity_x*dt/1000
        change_y = self.velocity_y*dt/1000

        self.x += change_x
        self.y += change_y

        velocity_change = acceleration*dt/1000
        self.velocity_y+= velocity_change


    def collide_with_ground(self):
        if self.y - self.radius <=0 and self.velocity_y < 0:
            self.y = self.radius
            self.velocity_y = -self.velocity_y*self.restitution

        




pygame.init()
screen_x, screen_y = 400, 300
win = pygame.display.set_mode((screen_x, screen_y)) # pixels
meter_to_pixel = 2 # 1 metre = 2 pixels

fps = 60 # frame per second

gravity = -9.8 # m/s**2
radius = 2 # metre
density = 7850 # kg/m**3 and steel
volume = 4/3 * math.pi * (radius**3)

acceleration = gravity
clock = pygame.time.Clock()

run = True
ball = Body(10, 70, 0, 0, 2, volume*density, 0.8)
while run:
    dt = clock.tick(fps)

    ball.update(dt,acceleration)
    ball.collide_with_ground()


    

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
    win.fill((0,0,0))

    pygame.draw.circle(surface=win,
                       color=(255,0,0),
                       center=(ball.x*meter_to_pixel,screen_y-ball.y*meter_to_pixel),
                       radius=ball.radius*meter_to_pixel)
    
    pygame.display.flip()



        


     
    
