import pygame
import math

class Body:
    def __init__(self,x,y,velocity_x,velocity_y,radius,density,restitution):
        self.x = x
        self.y = y
        self.velocity_y = velocity_y
        self.velocity_x = velocity_x
        self.radius = radius
        self.density = density
        self.restitution = restitution

        self.volume = 4/3 * math.pi * (self.radius**3)
        self.mass = self.volume * self.density

    def update(self, dt, acceleration_x, acceleration_y): #Accelerate, then change position.(Semi-implicit Euler)
        
        velocity_change_x = acceleration_x * dt   
        self.velocity_x += velocity_change_x

        velocity_change_y = acceleration_y * dt
        self.velocity_y += velocity_change_y

        change_x = self.velocity_x * dt
        change_y = self.velocity_y * dt


        self.x += change_x
        self.y += change_y

    def gravitational_acceleration(self, other, G):
        dx = other.x - self.x
        dy = other.y - self.y
        r = math.sqrt((dx**2+dy**2))

        a = G*other.mass/(r**2)

        direction_x=dx/r
        direction_y=dy/r

        ax = direction_x*a
        ay = direction_y*a

        return ax, ay, r

    def orbital_velocity(self, other, G):
        dx = other.x - self.x
        dy = other.y - self.y
        r = math.sqrt(dx**2 + dy**2)

        center_x = (self.mass*self.x + other.mass*other.x) / (self.mass + other.mass)
        center_y = (self.mass*self.y + other.mass*other.y) / (self.mass + other.mass)

        distance_x = self.x - center_x
        distance_y = self.y - center_y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        direction_x = -distance_y / distance
        direction_y = distance_x / distance

        speed = math.sqrt((G * other.mass / r**2) * distance)

        velocity_x = direction_x*speed
        velocity_y = direction_y*speed

        return velocity_x, velocity_y


pygame.init()
screen_x, screen_y = 400, 300
win = pygame.display.set_mode((screen_x, screen_y))
meter_to_pixel = 2

fps = 240
physics_dt = 1 / 120

clock = pygame.time.Clock()

run = True

ball = Body(150, 100, 0, 0, 10, 1, 0.8)
ball_2 = Body(110, 90, 0, 0, 3, 4, 0.8)

ball.velocity_x, ball.velocity_y = ball.orbital_velocity(ball_2, 1)
ball_2.velocity_x, ball_2.velocity_y = ball_2.orbital_velocity(ball, 1)

accumulator = 0

while run:
    dt = clock.tick(fps)
    accumulator += dt / 1000

    while accumulator >= physics_dt:

        acceleration_a = ball.gravitational_acceleration(ball_2, 1)
        acceleration_b = ball_2.gravitational_acceleration(ball, 1)

        ball.update(physics_dt, acceleration_a[0], acceleration_a[1])
        ball_2.update(physics_dt, acceleration_b[0], acceleration_b[1])

        accumulator -= physics_dt

    kinetic_energy = (
        (1/2) * ball.mass * (ball.velocity_x**2 + ball.velocity_y**2)
        + (1/2) * ball_2.mass * (ball_2.velocity_x**2 + ball_2.velocity_y**2)
    )

    potential_energy = (
        -(1 * ball.mass * ball_2.mass)
        / ball.gravitational_acceleration(ball_2, 1)[2]
    )

    total_energy = kinetic_energy + potential_energy
    print(total_energy)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False

    win.fill((0,0,0))

    pygame.draw.circle(
        surface=win,
        color=(255,0,0),
        center=(ball.x*meter_to_pixel, screen_y-ball.y*meter_to_pixel),
        radius=ball.radius*meter_to_pixel
    )

    pygame.draw.circle(
        surface=win,
        color=(255,0,0),
        center=(ball_2.x*meter_to_pixel, screen_y-ball_2.y*meter_to_pixel),
        radius=ball_2.radius*meter_to_pixel
    )

    pygame.display.flip()
