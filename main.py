import pygame
import math
import random

class Body:
    def __init__(self,x,y,z,velocity_x,velocity_y,velocity_z,radius,density,restitution,total_acceleration):
        self.x = x
        self.y = y
        self.z = z
        self.velocity_y = velocity_y
        self.velocity_x = velocity_x
        self.velocity_z = velocity_z
        self.radius = radius
        self.density = density
        self.restitution = restitution
        self.total_acceleration = total_acceleration
        self.orbiting = None
        self.trail = []
        

        self.volume = 4/3 * math.pi * (self.radius**3)
        self.mass = self.volume * self.density

    def update(self, dt):
        
        velocity_change_x = self.total_acceleration[0] * dt   
        self.velocity_x += velocity_change_x

        velocity_change_y = self.total_acceleration[1] * dt
        self.velocity_y += velocity_change_y

        velocity_change_z = self.total_acceleration[2] * dt
        self.velocity_z += velocity_change_z

        change_x = self.velocity_x * dt
        change_y = self.velocity_y * dt
        change_z = self.velocity_z * dt

        self.x += change_x
        self.y += change_y
        self.z += change_z

    def gravitational_acceleration(self, other, G):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        eps = (self.radius + other.radius)*0.1
        r = math.sqrt((dx**2+dy**2+dz**2+eps**2))

        a = G*other.mass/(r**2)

        direction_x=dx/r
        direction_y=dy/r
        direction_z=dz/r

        ax = direction_x*a
        ay = direction_y*a
        az = direction_z*a

        return ax, ay, az, r, a

    def orbital_velocity(self, other, G):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        r = math.sqrt(dx**2 + dy**2 + dz**2)

        center_x = (self.mass*self.x + other.mass*other.x) / (self.mass + other.mass)
        center_y = (self.mass*self.y + other.mass*other.y) / (self.mass + other.mass)
        center_z = (self.mass*self.z + other.mass*other.z) / (self.mass + other.mass)

        distance_x = self.x - center_x
        distance_y = self.y - center_y
        distance_z = self.z - center_z

        distance = math.sqrt(distance_x**2 + distance_y**2 + distance_z**2)

        raw_length = math.sqrt(distance_x**2+distance_y**2+0**2)

        if raw_length == 0:
            return 0, 0, 0

        direction_x = distance_y / raw_length
        direction_y = -distance_x / raw_length
        direction_z = 0 / raw_length

        speed = math.sqrt((G * other.mass / r**2) * distance)

        velocity_x = direction_x*speed
        velocity_y = direction_y*speed
        velocity_z = direction_z*speed

        return velocity_x, velocity_y, velocity_z

    def check_collision(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        r = math.sqrt((dx**2+dy**2+dz**2))

        if r <= self.radius + other.radius:
            return True
        else:
            return False

    def get_collision_normal(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        r = math.sqrt((dx**2+dy**2+dz**2))
        return dx/r, dy/r, dz/r

    def get_relative_velocity(self, other):
        return other.velocity_x - self.velocity_x, other.velocity_y - self.velocity_y, other.velocity_z - self.velocity_z

    def get_relative_normal_velocity(self, other):
        return self.get_collision_normal(other)[0]*self.get_relative_velocity(other)[0] + self.get_collision_normal(other)[1]*self.get_relative_velocity(other)[1] + self.get_collision_normal(other)[2]*self.get_relative_velocity(other)[2]

    def is_approaching(self, other):
        if self.get_relative_normal_velocity(other) < 0:
            return True
        else:
            return False

    def calculate_collision_impulse(self, other):
        restitution = min(self.restitution, other.restitution)
        J = -((restitution+1)*self.get_relative_normal_velocity(other))/(1/self.mass+1/other.mass)
        return J*self.get_collision_normal(other)[0], J*self.get_collision_normal(other)[1], J*self.get_collision_normal(other)[2]

    def apply_collision_impulse(self, other):
        impulse = self.calculate_collision_impulse(other)

        self.velocity_x -= impulse[0] / self.mass
        self.velocity_y -= impulse[1] / self.mass
        self.velocity_z -= impulse[2] / self.mass

        other.velocity_x += impulse[0] / other.mass
        other.velocity_y += impulse[1] / other.mass
        other.velocity_z += impulse[2] / other.mass 

    def correct_position(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        r = math.sqrt((dx**2 + dy**2 + dz**2))

        penetration = (self.radius + other.radius) - r

        if penetration <= 0:
            return

        correction_percent = 1.0
        normal_x = self.get_collision_normal(other)[0]
        normal_y = self.get_collision_normal(other)[1]
        normal_z = self.get_collision_normal(other)[2]
        self_fraction = other.mass/(self.mass+other.mass)
        other_fraction = self.mass/(other.mass+self.mass)

        self_correction_x = penetration * self_fraction * normal_x * correction_percent
        self_correction_y = penetration * self_fraction * normal_y * correction_percent
        self_correction_z = penetration * self_fraction * normal_z * correction_percent

        other_correction_x = penetration * other_fraction * normal_x * correction_percent
        other_correction_y = penetration * other_fraction * normal_y * correction_percent
        other_correction_z = penetration * other_fraction *normal_z * correction_percent

        self.x -= self_correction_x
        self.y -= self_correction_y
        self.z -= self_correction_z

        other.x += other_correction_x
        other.y += other_correction_y
        other.z += other_correction_z

pygame.init()
screen_x, screen_y = 800, 800
win = pygame.display.set_mode((screen_x, screen_y))
font = pygame.font.Font(None, 24)
meter_to_pixel = 2
G = 1
fps = 240
physics_dt = 1 / 240

min_brightness = 100
max_brightness = 255

panel_x = 10
panel_y = 10
panel_width = 200
panel_height = 210
panel_dragging = False
panel_drag_offset_x, panel_drag_offset_y = 0, 0

clock = pygame.time.Clock()

run = True
bodies = []
num_bodies = 6
central_radius = random.randint(17,30)
central_body = Body(200, 200,0, 0, 0, 0, central_radius, random.randint(5,7), 0.8, [0,0,0])

bodies.append(central_body)

for body in range(num_bodies):
    angle = random.uniform(0, 2*math.pi)
    distance = random.randint(central_radius+40, 150)
    x = central_body.x + distance * math.cos(angle)
    y = central_body.y + distance * math.sin(angle)
    z = random.randint(-30, 30)
    radius = random.randint(3, 10)
    density = random.randint(1, 3)
    bodies.append(Body(x, y, z, 0, 0, 0, radius, density, 0.8, [0,0,0]))

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
            bodies[body].orbiting = bodies[winner]
            bodies[body].velocity_x = local_velocity_x + bodies[winner].velocity_x
            bodies[body].velocity_y = local_velocity_y + bodies[winner].velocity_y
            bodies[body].velocity_z = local_velocity_z + bodies[winner].velocity_z

            initialized.add(body)

accumulator = 0
selected_body = None
camera_angle = 0
dragging = False

while run:
    dt = clock.tick(fps)
    accumulator += dt / 1000

    while accumulator >= physics_dt:

        for body in bodies:
            body.total_acceleration = [0,0,0]

            for other_body in bodies:
                if other_body == body:
                    continue

                body.total_acceleration[0] += body.gravitational_acceleration(other_body,G)[0]
                body.total_acceleration[1] += body.gravitational_acceleration(other_body,G)[1]
                body.total_acceleration[2] += body.gravitational_acceleration(other_body,G)[2]

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
            * (body.velocity_x**2 + body.velocity_y**2 + body.velocity_z**2)
        )

    potential_energy = 0

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            body = bodies[i]
            other_body = bodies[j]

            distance = body.gravitational_acceleration(other_body, G)[3]

            potential_energy += (-(1 * body.mass * other_body.mass)/distance)

    total_energy = kinetic_energy + potential_energy



    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.MOUSEBUTTONUP:
            dragging = False
            panel_dragging = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 3:
                selected_body = None
                print(selected_body)
                continue

            

            clicked_body = None
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if selected_body:
                if panel_x < mouse_x < panel_x +panel_width and panel_y < mouse_y < panel_y + panel_height:
                    panel_drag_offset_x = mouse_x - panel_x
                    panel_drag_offset_y = mouse_y - panel_y 
                    panel_dragging = True
                    print(panel_dragging)
                    continue
            for body in bodies:
                relative_x = body.x - central_body.x
                relative_z = body.z - central_body.z

                rotated_x = relative_x*math.cos(camera_angle) + relative_z*math.sin(camera_angle)

                screen_body_x = screen_x/2 + rotated_x*meter_to_pixel
                screen_body_y = screen_y/2 - (body.y-central_body.y)*meter_to_pixel

                if math.sqrt((mouse_x-screen_body_x)**2 + (mouse_y-screen_body_y)**2) <= body.radius*meter_to_pixel:
                    clicked_body = body
            
            if clicked_body == None:
                dragging = True
            elif clicked_body == selected_body:
                selected_body = None
            else:
                selected_body = clicked_body


            print(selected_body)


    dx, dy = pygame.mouse.get_rel()

    if dragging == True:
        camera_angle += dx * 0.003
                


    win.fill((0,0,0))

    bodies_with_depth = []

    min_z = None
    max_z = None

    for body in bodies:
        relative_x = body.x - central_body.x
        relative_z = body.z - central_body.z

        rotated_z = -relative_x*math.sin(camera_angle) + relative_z*math.cos(camera_angle)

        bodies_with_depth.append((body, rotated_z))

        if min_z == None:
            min_z = rotated_z
            max_z = rotated_z
        else:
            if rotated_z < min_z:
                min_z = rotated_z
            if rotated_z > max_z:
                max_z = rotated_z

    bodies_with_depth.sort(key=lambda pair: pair[1])


    for body, rotated_z in bodies_with_depth:
        relative_x = body.x - central_body.x
        relative_z = body.z - central_body.z

        rotated_x = relative_x*math.cos(camera_angle) + relative_z*math.sin(camera_angle)

        screen_body_x = screen_x/2 + rotated_x*meter_to_pixel
        screen_body_y = screen_y/2 - (body.y-central_body.y)*meter_to_pixel

        if max_z != min_z:
            depth_fraction = (rotated_z - min_z) / (max_z - min_z)
        else:
            depth_fraction = 1

        brightness = min_brightness + depth_fraction * (max_brightness - min_brightness)

        pygame.draw.circle(
            surface=win,
            color=(brightness, 0, 0),
            center=(screen_body_x, screen_body_y),
            radius=body.radius*meter_to_pixel
        )


        if body == selected_body:
            if len(body.trail) >= 150:
                body.trail.pop(0)
            body.trail.append((screen_body_x,screen_body_y))
            trail_surface = pygame.Surface((screen_x, screen_y), pygame.SRCALPHA)

            for index, point in enumerate(selected_body.trail):
                if index == len(selected_body.trail) - 1:
                    continue

                fraction = index / len(selected_body.trail)
                opacity = int(fraction * 200)

                pygame.draw.line(trail_surface, (0, 255, 0, opacity), selected_body.trail[index], selected_body.trail[index + 1], 3)
            win.blit(trail_surface, (0, 0))


            gap = body.radius * meter_to_pixel + 10
            bracket_len = 10

            top_left = (screen_body_x - gap, screen_body_y - gap)
            top_right = (screen_body_x + gap, screen_body_y - gap)
            bottom_left = (screen_body_x - gap, screen_body_y + gap)
            bottom_right = (screen_body_x + gap, screen_body_y + gap)

            pygame.draw.line(win, (255, 255, 255), top_left, (top_left[0] + bracket_len, top_left[1]), 2)
            pygame.draw.line(win, (255, 255, 255), top_left, (top_left[0], top_left[1] + bracket_len), 2)

            pygame.draw.line(win, (255, 255, 255), top_right, (top_right[0] - bracket_len, top_right[1]), 2)
            pygame.draw.line(win, (255, 255, 255), top_right, (top_right[0], top_right[1] + bracket_len), 2)

            pygame.draw.line(win, (255, 255, 255), bottom_left, (bottom_left[0] + bracket_len, bottom_left[1]), 2)
            pygame.draw.line(win, (255, 255, 255), bottom_left, (bottom_left[0], bottom_left[1] - bracket_len), 2)

            pygame.draw.line(win, (255, 255, 255), bottom_right, (bottom_right[0] - bracket_len, bottom_right[1]), 2)
            pygame.draw.line(win, (255, 255, 255), bottom_right, (bottom_right[0], bottom_right[1] - bracket_len), 2)


            speed = math.sqrt(body.velocity_x**2 + body.velocity_y**2 + body.velocity_z**2)
            if speed != 0:
                direction_x = body.velocity_x / speed
                direction_y = body.velocity_y / speed
                direction_z = body.velocity_z / speed

                arrow_length = min(speed*2, 80)

                rotated_dir_x = direction_x*math.cos(camera_angle) + direction_z*math.sin(camera_angle)
                rotated_dir_y = -direction_y

                arrow_end_x = screen_body_x + rotated_dir_x * arrow_length
                arrow_end_y = screen_body_y + rotated_dir_y * arrow_length

                reverse_x = -rotated_dir_x
                reverse_y = -rotated_dir_y

                angle = math.radians(35)

                wing1_x = reverse_x*math.cos(angle) - reverse_y*math.sin(angle)
                wing1_y = reverse_x*math.sin(angle) + reverse_y*math.cos(angle)

                wing1_end_x = arrow_end_x + wing1_x * 10
                wing1_end_y = arrow_end_y + wing1_y * 10

                wing2_x = reverse_x*math.cos(-angle) - reverse_y*math.sin(-angle)
                wing2_y = reverse_x*math.sin(-angle) + reverse_y*math.cos(-angle)

                wing2_end_x = arrow_end_x + wing2_x * 10
                wing2_end_y = arrow_end_y + wing2_y * 10

                


                pygame.draw.line(win, (0, 255, 0), (screen_body_x, screen_body_y), (arrow_end_x, arrow_end_y), 4)
                pygame.draw.line(win, (0, 255, 0), (arrow_end_x, arrow_end_y), (wing1_end_x, wing1_end_y), 3)
                pygame.draw.line(win, (0, 255, 0), (arrow_end_x, arrow_end_y), (wing2_end_x, wing2_end_y), 3)


            if selected_body.orbiting != None:
                relative_x = selected_body.orbiting.x - central_body.x
                relative_z = selected_body.orbiting.z - central_body.z

                rotated_x = relative_x*math.cos(camera_angle) + relative_z*math.sin(camera_angle)

                orbited_screen_x = screen_x/2 + rotated_x*meter_to_pixel
                orbited_screen_y = screen_y/2 - (selected_body.orbiting.y - central_body.y)*meter_to_pixel

                line_surface = pygame.Surface((screen_x, screen_y), pygame.SRCALPHA)
                pygame.draw.line(line_surface, (255,255,255, 150), (screen_body_x, screen_body_y), (orbited_screen_x, orbited_screen_y), 3)
                win.blit(line_surface, (0,0))


    if panel_dragging == True:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        panel_x = mouse_x - panel_drag_offset_x
        panel_y = mouse_y - panel_drag_offset_y
    
    if selected_body != None:
        speed = math.sqrt(selected_body.velocity_x**2 + selected_body.velocity_y**2 + selected_body.velocity_z**2)
        stats = [('Mass', selected_body.mass), ('X', selected_body.x), ('Y', selected_body.y), ('Z', selected_body.z), ('Radius', selected_body.radius),('Velocity X', selected_body.velocity_x), ('Velocity Y', selected_body.velocity_y), ('Velocity Z', selected_body.velocity_z), ('Speed', speed)]
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 150), (0,0,panel_width, panel_height), border_radius=10)
        win.blit(panel_surface, (panel_x, panel_y))
        pygame.draw.rect(win, (90,90,90), (panel_x,panel_y,panel_width,panel_height), width=3, border_radius=10)

        for index, (label, value) in enumerate(stats):
            line_text = f"{label}: {round(value, 2)}"
            line_surface = font.render(line_text, True, (0, 0, 0))
            win.blit(line_surface, (panel_x + 10, panel_y + 10 + index*20))

        exit_info = font.render("Right-click to close", True, (30, 30, 30))
        win.blit(exit_info, (panel_x +20, panel_y + panel_height - 22))

    

    pygame.display.flip()