import pygame
import math
import random
import seaborn
import matplotlib.pyplot as plt

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

    def collision_outcome(self, other, G, max_cone_angle, m_min, fragment_b, min_fragment_radius):
        (dvx, dvy, dvz) = self.get_relative_velocity(other)
        reduced_mass_KE = 0.5 * (self.mass * other.mass / (self.mass+other.mass)) * (dvx**2+dvy**2+dvz**2)
        binding_energy = G * self.mass**2 / self.radius + G * other.mass**2 / other.radius
        if reduced_mass_KE < binding_energy:
            return [self.merge(other)]
        else:
            return self.fragment(other, G, max_cone_angle, m_min, fragment_b, min_fragment_radius)

    def merge(self, other):
        new_mass = self.mass + other.mass
        new_velocity_x = (self.mass*self.velocity_x + other.mass*other.velocity_x) / new_mass
        new_velocity_y = (self.mass*self.velocity_y + other.mass*other.velocity_y) / new_mass
        new_velocity_z = (self.mass*self.velocity_z + other.mass*other.velocity_z) / new_mass

        new_x = (self.mass*self.x + other.mass*other.x) / (self.mass + other.mass)
        new_y = (self.mass*self.y + other.mass*other.y) / (self.mass + other.mass)
        new_z = (self.mass*self.z + other.mass*other.z) / (self.mass + other.mass)

        new_density = self.density*(self.mass/new_mass) + other.density*(other.mass/new_mass)
        new_volume = new_mass/new_density
        new_radius = (3*new_volume/(4*math.pi))**(1/3)

        return Body(new_x, new_y, new_z, new_velocity_x, new_velocity_y, new_velocity_z, new_radius, new_density, 0.8, [0,0,0])

    def fragment(self, other, G, max_cone_angle,m_min, fragment_b, min_fragment_radius):
        n_x, n_y, n_z = self.get_collision_normal(other)
        v_x, v_y, v_z = self.get_relative_velocity(other)
        v_length = math.sqrt(v_x**2 + v_y**2 + v_z**2)
        v_x = v_x/v_length
        v_y = v_y/v_length
        v_z = v_z/v_length

        dot = n_x*v_x + n_y*v_y + n_z*v_z           
        e1_x = n_x - dot*v_x
        e1_y = n_y - dot*v_y
        e1_z = n_z - dot*v_z    

        e1_length = math.sqrt(e1_x**2 + e1_y**2 + e1_z**2)
        if e1_length < 1e-9:
            if abs(v_x) < 0.9:
                e1_x, e1_y, e1_z = 0, v_z, -v_y
            else:
                e1_x, e1_y, e1_z = -v_z, 0, v_x
            e1_length = math.sqrt(e1_x**2 + e1_y**2 + e1_z**2)
        e1_x = e1_x/e1_length
        e1_y = e1_y/e1_length
        e1_z = e1_z/e1_length

        e2_x = v_y*e1_z - v_z*e1_y
        e2_y = v_z*e1_x - v_x*e1_z
        e2_z = v_x*e1_y - v_y*e1_x

        (dvx, dvy, dvz) = self.get_relative_velocity(other)
        reduced_mass_KE = 0.5 * (self.mass * other.mass / (self.mass+other.mass)) * (dvx**2+dvy**2+dvz**2)
        binding_energy = G * self.mass**2 / self.radius + G * other.mass**2 / other.radius
        energy_ratio = reduced_mass_KE / binding_energy
        cone_angle = max_cone_angle * (1 - 1/energy_ratio)

        total_mass = self.mass+other.mass
        fragment_masses = generate_fragment_masses(total_mass, m_min ,fragment_b)
        leftover_energy = reduced_mass_KE - binding_energy
        kick_speed = math.sqrt(2 * leftover_energy / total_mass)
        com_velocity_x = (self.mass*self.velocity_x + other.mass*other.velocity_x) / total_mass
        com_velocity_y = (self.mass*self.velocity_y + other.mass*other.velocity_y) / total_mass
        com_velocity_z = (self.mass*self.velocity_z + other.mass*other.velocity_z) / total_mass

        collision_x = (self.x + other.x) / 2
        collision_y = (self.y + other.y) / 2
        collision_z = (self.z + other.z) / 2

        fragment_density = self.density*(self.mass/total_mass) + other.density*(other.mass/total_mass)

        fragments = []

        for i in range(len(fragment_masses)):
            fragment_mass_i = fragment_masses[i]
            angle_around = 2 * math.pi * i / len(fragment_masses)

            dir_x = math.cos(cone_angle)*v_x + math.sin(cone_angle)*(math.cos(angle_around)*e1_x + math.sin(angle_around)*e2_x)
            dir_y = math.cos(cone_angle)*v_y + math.sin(cone_angle)*(math.cos(angle_around)*e1_y + math.sin(angle_around)*e2_y)
            dir_z = math.cos(cone_angle)*v_z + math.sin(cone_angle)*(math.cos(angle_around)*e1_z + math.sin(angle_around)*e2_z)

            fragment_velocity_x = com_velocity_x + kick_speed*dir_x
            fragment_velocity_y = com_velocity_y + kick_speed*dir_y
            fragment_velocity_z = com_velocity_z + kick_speed*dir_z

            fragment_volume_i = fragment_mass_i / fragment_density
            fragment_radius_i = (3*fragment_volume_i/(4*math.pi))**(1/3)

            distance_out = fragment_radius_i
            while True:
                fragment_x = collision_x + dir_x*distance_out
                fragment_y = collision_y + dir_y*distance_out
                fragment_z = collision_z + dir_z*distance_out

                overlapping = False
                for placed in fragments:
                    separation = math.sqrt((placed.x-fragment_x)**2 + (placed.y-fragment_y)**2 + (placed.z-fragment_z)**2)
                    if separation < placed.radius + fragment_radius_i:
                        overlapping = True
                        break

                if not overlapping:
                    break
                distance_out += fragment_radius_i

            fragments.append(Body(fragment_x, fragment_y, fragment_z, fragment_velocity_x, fragment_velocity_y, fragment_velocity_z, fragment_radius_i, fragment_density, 0.8, [0,0,0]))
        drift_x = sum(f.mass*(f.velocity_x - com_velocity_x) for f in fragments) / total_mass
        drift_y = sum(f.mass*(f.velocity_y - com_velocity_y) for f in fragments) / total_mass
        drift_z = sum(f.mass*(f.velocity_z - com_velocity_z) for f in fragments) / total_mass

        for f in fragments:
            f.velocity_x -= drift_x
            f.velocity_y -= drift_y
            f.velocity_z -= drift_z

        kick_energy = 0
        for f in fragments:
            kick_energy += 0.5*f.mass*((f.velocity_x-com_velocity_x)**2 + (f.velocity_y-com_velocity_y)**2 + (f.velocity_z-com_velocity_z)**2)

        if kick_energy > 0:
            scale = math.sqrt(leftover_energy / kick_energy)
            for f in fragments:
                f.velocity_x = com_velocity_x + (f.velocity_x - com_velocity_x)*scale
                f.velocity_y = com_velocity_y + (f.velocity_y - com_velocity_y)*scale
                f.velocity_z = com_velocity_z + (f.velocity_z - com_velocity_z)*scale

        return fragments


    def check_swept_collision(self, other, dt):
        px = other.x - self.x
        py = other.y - self.y
        pz = other.z - self.z
        vx, vy, vz = self.get_relative_velocity(other)

        sx = px - vx*dt
        sy = py - vy*dt
        sz = pz - vz*dt

        v_sq = vx**2 + vy**2 + vz**2
        if v_sq == 0:
            t = 0
        else:
            t = -(sx*vx + sy*vy + sz*vz) / v_sq
            t = max(0, min(dt, t))

        cx = sx + vx*t
        cy = sy + vy*t
        cz = sz + vz*t
        return math.sqrt(cx**2 + cy**2 + cz**2) <= self.radius + other.radius
    
def sample_fragment_mass(m_min, m_max, b):
    u = random.uniform(0, 1)
    m = (u * (m_max**(1-b) - m_min**(1-b)) + m_min**(1-b)) ** (1/(1-b))
    return m

def generate_fragment_masses(total_mass, m_min, b):
    m_max_initial = 0.5 * total_mass
    remaining_mass = total_mass
    fragment_masses = []

    while remaining_mass >= m_min:
        m_max = min(m_max_initial, remaining_mass)
        fragment_mass = sample_fragment_mass(m_min, m_max, b)

        fragment_masses.append(fragment_mass)
        remaining_mass -= fragment_mass

    if remaining_mass > 0 and len(fragment_masses) > 0:
        fragment_masses[-1] += remaining_mass

    return fragment_masses


pygame.init()
screen_x, screen_y = 800, 800
win = pygame.display.set_mode((screen_x, screen_y))
font = pygame.font.Font(None, 24)
meter_to_pixel = 800/5e11
radius_to_pixel = 3e-7
G = 6.674e-11
max_cone_angle = math.pi/2
fps = 240
physics_dt = 1 / 240
time_scale = 2e6
zoom = 0.6
fragment_b = 0.9
min_fragment_radius = 1e6
representative_density = 4250
m_min = (4/3 * math.pi * min_fragment_radius**3) * representative_density
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
num_bodies = 10
central_radius = random.uniform(5.9e8, 8.0e8)
central_body = Body(0, 0, 0, 0, 0, 0, central_radius, random.randint(1200, 1600), 0.8, [0,0,0])

bodies.append(central_body)

for body in range(num_bodies):
    angle = random.uniform(0, 2*math.pi)
    distance = random.uniform(6e10, 5e11)
    x = central_body.x + distance * math.cos(angle)
    y = central_body.y + distance * math.sin(angle)
    z = random.uniform(-1e10, 1e10)
    radius = random.uniform(10e6,10e7)
    density = random.randint(3000,5500)
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
simulated_time = 0
E0 = None
previously_touching = set()

listed_energy = []
deviation_list = []
abnormal_events = []
replay_buffer = []
baseline = None
was_abnormal = False
paused = False
last_abnormal_event = None
clicked_event = None
selected_event = None
event_replays = []
recording_after = False
after_frames_remaining = 0
current_event_snapshot = None

while run:
    
    dt = clock.tick(fps)
    
    if paused == False:
        accumulator += dt / 1000
        accumulator = min(accumulator, physics_dt * 20)
        while accumulator >= physics_dt:

            for body in bodies:
                body.total_acceleration = [0,0,0]

                for other_body in bodies:
                    if other_body == body:
                        continue
                    acceleration = body.gravitational_acceleration(other_body,G)
                    body.total_acceleration[0] += acceleration[0]
                    body.total_acceleration[1] += acceleration[1]
                    body.total_acceleration[2] += acceleration[2]

            for body in bodies:
                body.update(physics_dt*time_scale)

            pending_collisions = []
            currently_touching = set()

            for i in range(len(bodies)):
                for j in range(i + 1, len(bodies)):
                    body = bodies[i]
                    other_body = bodies[j]

                    if body.check_swept_collision(other_body, physics_dt*time_scale):
                        pair = (body, other_body)
                        currently_touching.add(pair)
                        if pair not in previously_touching:
                            pending_collisions.append(pair)
                        body.correct_position(other_body)

            previously_touching = currently_touching

            destroyed = set()
            new_bodies = []

            for body, other_body in pending_collisions:
                if body in destroyed or other_body in destroyed:
                    continue

                result = body.collision_outcome(other_body, G, max_cone_angle, m_min, fragment_b, min_fragment_radius)

                destroyed.add(body)
                destroyed.add(other_body)
                new_bodies.extend(result)

                for first in range(len(result)):
                    for second in range(first + 1, len(result)):
                        previously_touching.add((result[first], result[second]))

            bodies = [b for b in bodies if b not in destroyed]
            bodies.extend(new_bodies)

            accumulator -= physics_dt

            simulated_time+=physics_dt*time_scale

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

                potential_energy += (-(G * body.mass * other_body.mass)/distance)

        total_energy = kinetic_energy + potential_energy
        if E0 == None:
            E0 = total_energy



        normalized_deviation = (total_energy-E0)/abs(E0)

        listed_energy.append([simulated_time/86400,normalized_deviation])
        if len(deviation_list) < 15:
            deviation_list.append(normalized_deviation)
        else:
            baseline = sum(deviation_list) / len(deviation_list)
            if abs(normalized_deviation - baseline) > 0.001:

                if was_abnormal == False:
                    last_abnormal_event = simulated_time
                    if len(abnormal_events) > 0:
                        if last_abnormal_event - abnormal_events[-1] > 3600:
                            abnormal_events.append(last_abnormal_event)
                            current_event_snapshot = list(replay_buffer)
                            recording_after = True
                            after_frames_remaining = 3600
                    else:
                        abnormal_events.append(last_abnormal_event)
                        current_event_snapshot = list(replay_buffer)
                        recording_after = True
                        after_frames_remaining = 3600
                    
                was_abnormal = True
                deviation_list = []

            else:
                was_abnormal = False
                
                deviation_list.pop(0)
                deviation_list.append(normalized_deviation)
        if after_frames_remaining == 0 and recording_after == True:
            recording_after = False
            event_replays.append(current_event_snapshot)
        if len(replay_buffer) < 3600:
            all_bodies_coordinates = []
            for body in bodies:
                all_bodies_coordinates.append((body.x,body.y,body.z))

            replay_buffer.append(all_bodies_coordinates)
            if recording_after == True:
                current_event_snapshot.append(all_bodies_coordinates)
                after_frames_remaining -= 1
        else:
            all_bodies_coordinates = []
            replay_buffer.pop(0)
            for body in bodies:
                all_bodies_coordinates.append((body.x,body.y,body.z))
            replay_buffer.append(all_bodies_coordinates)

            if recording_after == True:
                current_event_snapshot.append(all_bodies_coordinates)
                after_frames_remaining -= 1

        
            
                



        



    
    for e in pygame.event.get():
        
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.KEYDOWN:

            if e.key == pygame.K_SPACE:
                if paused == True:
                    paused = False
                else:
                    paused = True

                    time = []
                    energy = []
                    for i in listed_energy:
                        time.append(i[0])
                        energy.append(i[1])

                    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
                    ax.plot(time, energy)
                    fig.canvas.draw()
                    plot_width, plot_height = fig.canvas.get_width_height()
                    raw_data = fig.canvas.buffer_rgba()
                    plot_surface = pygame.image.frombuffer(raw_data, (plot_width, plot_height), "RGBA")
                    plt.close(fig)


        if e.type == pygame.MOUSEWHEEL:
            zoom += e.y * 0.1
            zoom = max(zoom, 0.1)

        if e.type == pygame.MOUSEBUTTONUP:
            dragging = False
            panel_dragging = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            
            if paused == True:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if clicked_event != None:
                    for i, v in enumerate(abnormal_events):
                
                        event_x = 110
                        event_y = 450 + i*20
                        if event_x < mouse_x < event_x + 200 and event_y < mouse_y < event_y + 16:
                            if clicked_event == i:
                                selected_event = i
                            else:
                                clicked_event = i

                else:
                    for i, v in enumerate(abnormal_events):
                        
                        event_x = 110
                        event_y = 450 + i*20
                        if event_x < mouse_x < event_x + 200 and event_y < mouse_y < event_y + 16:
                            clicked_event = i
                if selected_event != None:
                    cancel_replay = False
                    if selected_event < len(event_replays):
                        saved_positions = []
                        for body in bodies:
                            saved_positions.append((body.x, body.y, body.z))
                        replay_data = event_replays[selected_event]
                        
                        for frame_index, frame in enumerate(replay_data):
                            replay_dt = clock.tick(fps)
                            for i, body in enumerate(bodies):
                                body.x, body.y, body.z = frame[i]

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
                                screen_body_x = screen_x/2 + rotated_x*meter_to_pixel*zoom
                                screen_body_y = screen_y/2 - (body.y-central_body.y)*meter_to_pixel*zoom

                                if max_z != min_z:
                                    depth_fraction = (rotated_z - min_z) / (max_z - min_z)
                                else:
                                    depth_fraction = 1

                                brightness = min_brightness + depth_fraction * (max_brightness - min_brightness)

                                pygame.draw.circle(
                                    surface=win,
                                    color=(brightness, 0, 0),
                                    center=(screen_body_x, screen_body_y),
                                    radius=body.radius*radius_to_pixel*zoom
                                )


                            seconds_offset = frame_index - 3600
                            replay_label_text = f"REPLAY  t = {seconds_offset:+d}s"
                            replay_label_surface = font.render(replay_label_text, True, (255, 255, 255))
                            win.blit(replay_label_surface, (10, 10))

                            pygame.display.flip()
                            for replay_e in pygame.event.get():
                                if replay_e.type == pygame.QUIT:
                                    run = False
                                if replay_e.type == pygame.MOUSEWHEEL:
                                    zoom += replay_e.y * 0.1
                                    zoom = max(zoom, 0.1)
                                if replay_e.type == pygame.KEYDOWN:
                                    if replay_e.key == pygame.K_ESCAPE:
                                        cancel_replay = True
                            if run == False or cancel_replay == True:
                                break       

                        for i, body in enumerate(bodies):
                            body.x, body.y, body.z = saved_positions[i]
                    else:
                        print("Replay still recording, not ready yet")

                            


            if e.button == 3:
                selected_body = None
                
                continue
 
            

            clicked_body = None
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if selected_body:
                if panel_x < mouse_x < panel_x +panel_width and panel_y < mouse_y < panel_y + panel_height:
                    panel_drag_offset_x = mouse_x - panel_x
                    panel_drag_offset_y = mouse_y - panel_y 
                    panel_dragging = True
                    
                    continue
            for body in bodies:
                relative_x = body.x - central_body.x
                relative_z = body.z - central_body.z

                rotated_x = relative_x*math.cos(camera_angle) + relative_z*math.sin(camera_angle)

                screen_body_x = screen_x/2 + rotated_x*meter_to_pixel*zoom
                screen_body_y = screen_y/2 - (body.y-central_body.y)*meter_to_pixel*zoom

                if e.button == 1 and math.sqrt((mouse_x-screen_body_x)**2 + (mouse_y-screen_body_y)**2) <= body.radius*radius_to_pixel*zoom:
                    clicked_body = body
            
            if clicked_body == None:
                dragging = True
            elif clicked_body == selected_body:
                selected_body = None
            else:
                selected_body = clicked_body




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

        screen_body_x = screen_x/2 + rotated_x*meter_to_pixel*zoom
        screen_body_y = screen_y/2 - (body.y-central_body.y)*meter_to_pixel*zoom

        if max_z != min_z:
            depth_fraction = (rotated_z - min_z) / (max_z - min_z)
        else:
            depth_fraction = 1

        brightness = min_brightness + depth_fraction * (max_brightness - min_brightness)

        pygame.draw.circle(
            surface=win,
            color=(brightness, 0, 0),
            center=(screen_body_x, screen_body_y),
            radius=body.radius*radius_to_pixel*zoom
        )


        if body == selected_body:
            if len(body.trail) >= 250:
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


            gap = body.radius * radius_to_pixel*zoom + 10
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

                arrow_length = min(speed*2/1000, 80)

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

                orbited_screen_x = screen_x/2 + rotated_x*meter_to_pixel*zoom
                orbited_screen_y = screen_y/2 - (selected_body.orbiting.y - central_body.y)*meter_to_pixel*zoom

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

    if paused == True:
        paused_screen = pygame.Surface((screen_x, screen_y), pygame.SRCALPHA)
        paused_screen.fill((150, 150, 150, 150))
        win.blit(paused_screen, (0, 0))
        win.blit(plot_surface, (100, 20))
        text_x, text_y = 100, 440
        for index, value in enumerate(abnormal_events):
            event_text = f"Event {index+1}: {value/86400:.1f} days"
            if index == clicked_event:
                if index == selected_event:
                    line_surface = font.render(event_text, True, (255, 0, 0))
                else:
                    line_surface = font.render(event_text, True, (0, 0, 255))
            else:
                line_surface = font.render(event_text, True, (0, 0, 0))

            win.blit(line_surface, (text_x + 10, text_y + 10 + index*20))

    

    pygame.display.flip()



