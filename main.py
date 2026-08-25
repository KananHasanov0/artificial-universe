import pygame
import math

class Body:
    def __init__(self,x,y,velocity_x,velocity_y,radius,density,restitution,total_acceleration):
        self.x = x
        self.y = y
        self.velocity_y = velocity_y
        self.velocity_x = velocity_x
        self.radius = radius
        self.density = density
        self.restitution = restitution
        self.total_acceleration = total_acceleration

        self.volume = 4/3 * math.pi * (self.radius**3)
        self.mass = self.volume * self.density

    def update(self, dt):
        
        velocity_change_x = self.total_acceleration[0] * dt   
        self.velocity_x += velocity_change_x

        velocity_change_y = self.total_acceleration[1] * dt
        self.velocity_y += velocity_change_y

        change_x = self.velocity_x * dt
        change_y = self.velocity_y * dt

        self.x += change_x
        self.y += change_y

    def gravitational_acceleration(self, other, G):
        dx = other.x - self.x
        dy = other.y - self.y
        eps = (self.radius + other.radius)*0.1
        r = math.sqrt((dx**2+dy**2+eps**2))

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

    def check_collision(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        r = math.sqrt((dx**2+dy**2))

        if r <= self.radius + other.radius:
            return True
        else:
            return False

    def get_collision_normal(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        r = math.sqrt((dx**2+dy**2))
        return dx/r, dy/r

    def get_relative_velocity(self, other):
        return other.velocity_x - self.velocity_x, other.velocity_y - self.velocity_y 

    def get_relative_normal_velocity(self, other):
        return self.get_collision_normal(other)[0]*self.get_relative_velocity(other)[0] + self.get_collision_normal(other)[1]*self.get_relative_velocity(other)[1]

    def is_approaching(self, other):
        if self.get_relative_normal_velocity(other) < 0:
            return True
        else:
            return False

    def calculate_collision_impulse(self, other):
        restitution = min(self.restitution, other.restitution)
        J = -((restitution+1)*self.get_relative_normal_velocity(other))/(1/self.mass+1/other.mass)
        return J*self.get_collision_normal(other)[0], J*self.get_collision_normal(other)[1]

    def apply_collision_impulse(self, other):
        impulse = self.calculate_collision_impulse(other)

        self.velocity_x -= impulse[0] / self.mass
        self.velocity_y -= impulse[1] / self.mass

        other.velocity_x += impulse[0] / other.mass
        other.velocity_y += impulse[1] / other.mass 

    def correct_position(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        r = math.sqrt((dx**2 + dy**2))

        penetration = (self.radius + other.radius) - r

        if penetration <= 0:
            return
        
        normal_x = self.get_collision_normal(other)[0]
        normal_y = self.get_collision_normal(other)[1]
        self_fraction = other.mass/(self.mass+other.mass)
        other_fraction = self.mass/(other.mass+self.mass)

        self_correction_x = penetration * self_fraction * normal_x
        self_correction_y = penetration * self_fraction * normal_y

        other_correction_x = penetration * other_fraction * normal_x
        other_correction_y = penetration * other_fraction * normal_y

        self.x -= self_correction_x
        self.y -= self_correction_y

        other.x += other_correction_x
        other.y += other_correction_y

pygame.init()
screen_x, screen_y = 800, 800
win = pygame.display.set_mode((screen_x, screen_y))
meter_to_pixel = 2
G = 1
fps = 240
physics_dt = 1 / 120

clock = pygame.time.Clock()

run = True
bodies = []
num_bodies = 6
central_radius = random.randint(10,30)
central_body = Body(200, 200,0, 0, 0, 0, central_radius, random.randint(5,7), 0.8, [0,0,0])

bodies.append(central_body)

for body in range(num_bodies):
    angle = random.uniform(0, 2*math.pi)
    distance = random.randint(central_radius+40, 150)
    x = central_body.x + distance * math.cos(angle)
    y = central_body.y + distance * math.sin(angle)
    radius = random.randint(1, 8)
    density = random.randint(1, 3)
    bodies.append(Body(x, y, 0, 0, 0, 0, radius, density, 0.8, [0,0,0]))

central_body.velocity_x = 0
central_body.velocity_y = 0

initialized = {0}
max_iterations = len(bodies)*2
iterations = 0

while len(initialized) < len(bodies) and iterations < max_iterations:
    iterations += 1

    for body in range(1, len(bodies)):
        if body in initialized:
            continue

        winner = None

        for other_body in range(len(bodies)):
            if other_body == body:
                continue

            if winner == None:
                winner = other_body
            else:
                if bodies[body].gravitational_acceleration(bodies[other_body], G)[4] > bodies[body].gravitational_acceleration(bodies[winner], G)[4]:
                    winner = other_body

        if winner in initialized:
            local_velocity_x, local_velocity_y, local_velocity_z = bodies[body].orbital_velocity(bodies[winner], G)

            bodies[body].velocity_x = local_velocity_x + bodies[winner].velocity_x
            bodies[body].velocity_y = local_velocity_y + bodies[winner].velocity_y
            bodies[body].velocity_z = local_velocity_z + bodies[winner].velocity_z

            initialized.add(body)

accumulator = 0

while run:
    dt = clock.tick(fps)
    accumulator += dt / 1000

    while accumulator >= physics_dt:

        for body in bodies:
            body.total_acceleration = [0,0]

            for other_body in bodies:
                if other_body == body:
                    continue

                body.total_acceleration[0] += body.gravitational_acceleration(other_body,1)[0]
                body.total_acceleration[1] += body.gravitational_acceleration(other_body,1)[1]

        for body in bodies:
            body.update(physics_dt)

        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                body = bodies[i]
                other_body = bodies[j]

                if body.check_collision(other_body):
                    if body.is_approaching(other_body):
                        body.apply_collision_impulse(other_body)
                    body.correct_position(other_body)

        accumulator -= physics_dt

    kinetic_energy = 0

    for body in bodies:
        kinetic_energy += (
            (1/2) * body.mass
            * (body.velocity_x**2 + body.velocity_y**2)
        )

    potential_energy = 0

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            body = bodies[i]
            other_body = bodies[j]

            distance = body.gravitational_acceleration(other_body, 1)[2]

            potential_energy += (-(1 * body.mass * other_body.mass)/distance)

    total_energy = kinetic_energy + potential_energy

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False

    win.fill((0,0,0))

    for body in bodies:
        pygame.draw.circle(
            surface=win,
            color=(255,0,0),
            center=(body.x*meter_to_pixel,screen_y-body.y*meter_to_pixel),
            radius=body.radius*meter_to_pixel
        )

    pygame.display.flip()