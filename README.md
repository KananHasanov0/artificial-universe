# artificial-universe
A computational ecosystem exploring the emergence of adaptive behavior.

<img src="assets/simulation-demo.png" alt="Simulation screenshot showing selected body, orbit path, trail, and inspection panel" width="600">

## Overview

Beginning from scratch, this N-body physics simulation creates gravity, motion, and collision detection based upon fundamental principles instead of using a pre-existing physics library. The program models a small number of masses orbiting around a central body in three-dimensional space; a real time visualizer allows the user to see how the system evolves over time.

The question driving this project is whether a structured system like orbits will emerge from a few, basic physical principles without having the structure defined in the program. This is not about programming a simulated solar system but rather providing the program with an appropriate environment for gravity (force), mass and motion so that it may produce structures autonomously.

## How to Run

**Dependencies** — Libraries you need to install are pygame and matplotlib. This can be done with writing down these install commands in terminal:
```
pip install pygame
pip install matplotlib
```

**How to run** — In terminal write this command:
```
python main.py
```

**Controls:**
- **Left-click a body** to select it. This opens a panel showing that body's stats, highlights it with targeting brackets, shows its direction with an arrow, and draws a line to whatever it orbits.
- **Left-click the same body again** to deselect it.
- **Right-click anywhere** on the screen to close the panel.
- **Drag while holding left-click** on empty space to rotate the camera. Drag while your mouse is on the panel to move it.
- **Scroll wheel** to zoom in and out.
- **Space bar** to pause and unpause. Pausing opens the pause screen, where the energy plot and the list of found events are.
- **Left-click an event** in that list once to pick it, then click the same one again to actually open its replay.
- **Escape while a replay is playing** to stop it and go back to the pause screen.

## Physics Engine

Currently, this project has been verified as having included a verified 3-D physics engine which represents physics in three ways:

- Gravity
- Motion
- Collision Detection and Response

This engine was created using first principles of physics.

Everything runs on real units now. Masses are in kilograms, calculated from each body's radius and density, distances are in meters, and G is the actual constant, 6.674e-11. Before this the whole thing was toy-scale.

One thing about real units is that real orbital periods take months or years of real seconds, so if you just run it nothing looks like it is moving at all. I added a time_scale constant that multiplies the timestep, so simulated time can run faster than real time. Rendering has two separate scale constants too, one for position and one for radius, both kept apart from the physics. At real proportions one shared scale can't make distances and sizes both visible at the same time, i tried.

The semi-implicit method used for integration was tested against a previously identified failure mode (energy drift caused by explicit Euler's method), and it passed. Total energy stays bounded rather than increasing without bound.

That test was from back when everything was toy-scale though, so i re-did it with real units over a 13,000 simulated-day run, and it looked like energy stayed in one band for around 7,800 days and then shifted into another. That result was wrong. The energy calculation was still using G = 1 from the toy-scale version, so potential energy came out around 10^10 times too big and kinetic energy basically didn't count. The force calculation always used the real G, so the simulation itself was fine, only the energy check was off.

With the fix i redid it, 5 runs of about 13,500 simulated days each. Between steps energy barely changes. In 3 of the 5 runs it stayed within 0.5% the whole time. The other two jumped, by up to 4.7% and 11%. The 11% one ended 8.8% off, so it was a one-time jump and not slow drift, and the 4.7% one also had a merge in it, which takes energy out on purpose. The runs with the closest passes had the biggest jumps, which fits one 8,333 second step being too coarse to follow a close encounter. So energy stays bounded without steady drift, except for jumps during close passes.

Close encounters have also been addressed by applying a softening term to prevent singularities at close encounter points.

Collisions used to be a bounce with a restitution value, which isn't what planets actually do. Now when two bodies touch, the energy of the impact (reduced mass kinetic energy) is compared to how strongly both bodies hold themselves together (binding energy, G·m²/r for each, added up). If the impact is weaker, they merge into one body, with mass, momentum and position combined. If it's stronger, they break into fragments.

Fragment sizes follow a power law, many small pieces and a few big ones, like real collision debris. The directions aren't random, they come from the impact itself: fragments fly out in a cone around the direction of the hit, and the cone gets wider the more the impact energy goes past the binding energy. Their speed comes from whatever energy is left after the binding energy. Total mass and momentum stay exactly the same as the two bodies had before.

Collision detection checks the whole path a body moved during a step, not just where it ended up. One step covers 8,333 simulated seconds and planets move further than their own size in that time, so checking only end positions let them pass straight through each other.

In practice real collisions are rare. Close passes happen much more often, and since the planets are heavy they usually slingshot each other instead of hitting.

## Orbit Assignment

Each body will automatically be placed into orbit about another body by identifying its "parent". Its "parent" is defined as the body which causes it to be accelerated or decelerated the greatest amount, not necessarily the largest mass.

Once its "parent" has been determined, the child will inherit all aspects of its parent's motion. Thus, a moon may orbit around a planet whose orbit is being influenced by the central body.

## Visualization

This system is user interactable via an exploratory 3-dimensional view:

- Camera rotation
- Zoom
- Depth sorted rendering
- Distance based shading
- A separate panel to display physical data of each object, including their orbital target and velocity vector
- A pause screen, which stops the simulation without closing it

Pause screen has the energy plot for the run so far, and under it a list of found events. Event here means a moment where total energy went further from its own recent rolling average than a set threshold. Picking one from the list plays back the recorded positions from a window before and after that moment, in the same view, and you can zoom during it or press escape to stop.

Replay itself works from a rolling buffer of recent positions that gets copied when an event is found, then keeps recording for a while after. One known problem: replay assumes the number of bodies stays the same, so an event that includes a merge or fragmentation won't play back correctly yet.

Bodies are drawn much bigger than their real size compared to the distances between them, otherwise every planet would be smaller than a pixel. Because of that, two planets can overlap on screen while being far apart in the simulation, so an overlap on screen doesn't mean they collided.

---

# Results

## 8/20/2026 — [2:46 AM UTC+4]

It is my first real observation since I started the project, as the project just begin to form. Right now, the observation is made around four bodies.

I should start by writing down their characteristics, i suppose. Starting with orbital_velocity, ball's and ball_2's orbital velocities are relative to each other. However, newly added other two's (body_3 and body_4) orbital velocities are only relative to ball_2, because formula used in orbital_velocity has no way to account for third body (it is derived for exactly two bodies). they all have various masses; therefore, different radiuses and densities. to make up your mind, i will give the order by which their masses decrease: the one with biggest mass is ball_2. following, ball, ball_3, respectively. ball_4 have the least mass.

The first observation was made while ball had located close to both ball_3 and ball_4 (can be observed in lasted commit Fix softening, restitution symmetry, and add 4th body). As a result, ball_3 and ball_4 ended up colliding with ball, which was something unexpected as they were suppose to orbit ball_2. It wasn't a complex problem to reason ,though. my first judgment was "ball's gravity isn't a part of velocity computation (as I mentioned before), and since ball's starting location is closer to smaller bodies than that of ball_2, its unmodeled pull dominates. proximity beats ball_2's larger mass, owing to gravity falling off with distance squared"

estimation wasn't enough, so I made my second observation with ball far apart from other two. This time, ball_3 and ball_4 didn't collide with ball as expected, but instead of setting orbit around ball_2, they became gravitationally bound to each other (since they started only 20 units apart, much closer to each other than to ball_2), collided, and the pair drifted away from ball_2's system together as a bound unit — a small-scale ejection.

**Significance of this discovery:**

Neither binary nor ejection was intentional. There is no coding saying "create binary and eject it". Everything was caused simply by combination of using formula suitable exclusively for calculation of orbital velocity of EXACTLY two bodies (orbital_velocity()), but applied to actual case containing FOUR bodies at once. That pattern repeated itself twice: initially, ball's ignored gravitational attraction won over ball_2's greater mass due to initial proximity between ball, ball_3, and ball_4; and again after displacement, ball_3 and ball_4 formed a binary system among themselves due to initial nearness (started from 20 units of separation), and got ejected together from ball_2's system.

This phenomenon relates directly to known physics problem: there exists no analytical solution for n>2-body problem in contrast to two-body one (connection to Poincaré's theorem on non-integrability of system); furthermore, phenomena such as gravitational ejection of binaries are well recorded in nature, when stars get ejected from stellar cluster. So basically the process I described represents miniature analogy of real-world gravitational process emerging entirely due to application of fundamental physical formulas without any external manipulation or scripting.

**Just wanted to point out:**

That particular result came from single trial of simulation with particular initial values I manually picked. I didn't test for consistency: for example, does small change of initial coordinates yield similar outcome? How dependent on precise initial separation distance this phenomenon is? Is it reproducible and meaningful pattern, or mere coincidence? This poses limitations rather than flaw of discovery itself.


## 9/24/2026 — [12:43 PM UTC+4]

This is written after the "add collision merging and fragmentation" commit and will include results I observed while coding it. In test simulations, for the most part, planets kept looking like they bounced, and made me believe something is broken with the current code. My first hypothesis was maybe they weren't even touching. To check if they were really touching, i thought about how the code handles a collision. Any real contact destroys both bodies, since they either merge into one or break into fragments, there is no bouncing anymore. Both bodies were still there after "bouncing", so they couldn't have touched. What looked like a bounce was actually gravity bending their paths while they passed close to each other.

To get actual numbers i ran the same physics in a separate script without the window, 5 simulations of about 13,500 simulated days each. Two planets overlapped on screen 117 times, and only 1 of those was a real collision (a merge). In the other 116 they never touched. The closest they got was 3 times their combined radii, and usually it was more like 125 times. Their paths bent about 46 degrees in a typical pass and up to 177 degrees, and 29 of them turned more than 90 degrees, which is the kind that looks like a bounce.

The reason it looked like contact is how bodies are drawn. Position and radius have two different scale constants, meter_to_pixel is 1.6e-9 and radius_to_pixel is 3e-7, and 3e-7 / 1.6e-9 comes out around 190. So every body is drawn about 190 times bigger compared to the distances between them. I did that on purpose, at true scale every planet would be smaller than a pixel, but it means two circles can overlap on screen while the bodies are still far apart.

The bend was that strong because the planets are heavy. Escape velocity is v = √(2GM/R). For the biggest planet the code can make (radius 1e8 m, density 5500) i got a mass of about 2.3e28 kg and an escape velocity of around 175 km/s, while planets orbit at about 16 to 47 km/s. When escape velocity is that much bigger than how fast they move past each other, gravity turns them away before they can actually hit.

Giving big planets gas giant density later should make them lighter and the slingshots weaker, so it'd be interesting to see if collisions become more common after that.

**Just wanted to point out:**

These numbers come from 5 runs, counted with the default camera angle and zoom, so a different view would give a different number of overlaps. My planets are also heavier than real ones, since big radii still get rocky density. The heaviest in these runs were 6.5 to 10.5 times Jupiter's mass, which makes the slingshots stronger than they would be in a real system. And one physics step is 8,333 simulated seconds, which is coarse for a close pass, so the bend angles aren't exact either.

---

# Design notes 

## 8/21/2026 — [4:14 AM UTC+4]

Hello there. I decided that I should write about why and how the code and engine are changed overtime when I face a problem. I am writing it while having a break from coding part, and as the part I am working on right now isn't ready, I haven't committed it. For situational awareness, I will be giving some information about the thing, I am working on right now: 2.5D environment is the main focus of the project right now. the physics engine itself is genuinely 3D (real gravity, real motion, real collisions in three dimensions). "2.5D" refers specifically to the rendering approach still to come, where 3D positions will be projected onto a flat 2D screen rather than rendered with a true 3D camera.

The hardest part until now was adapting orbital_velocity() method; therefore, i will be talking about it after now. Previously, orbital_velocity() was finding a perpendicular direction with a pragmatic solution: swap the two components of the center-to-body vector and flip the sign of one. visually (-distance_y, distance_x). It is obvious that switching to 3D simulation broke this, since "perpendicular to a vector" isn't a single direction in 3D. It's basically a whole plane of possible directions, because there are infinitely many vectors that can be perpendicular to a given vector in 3D.

*(Leaving this as a work in progress for tonight. I need to get some sleep and will finish it up tomorrow.)*

## 8/25/2026 — [2:00 AM UTC+4]

After a long break, I am back. it is the contination of my first design note:

With all this information considered, only two options came to my mind: giving each body's orbital plane a small random tilt, or using a fixed reference axis for every body. First option would give more visual variety, I admit, but the tilt itself would be arbitrary, not caused by anything the simulation actually did, just injected in from outside. And that goes against the same principle I've been following since the observations entry (same reasoning as with the binary/ejection case): there is no coding saying "tilt this randomly", so i shouldn't add one. Therefore, second option: one shared, fixed reference axis for every body. Gives a flat orbital disk instead of tilted ones, but nothing arbitrary gets added on top of what the physics already gives.

Mechanism itself is a cross product. By crossing the body's position vector (relative to the barycenter) with the fixed reference axis, (0,0,1), you get a new vector that is guaranteed perpendicular to both of the originals, which puts it exactly where it needs to be, somewhere in the plane perpendicular to "up".

I worked through the general cross product formula by hand, substituted this specific reference axis in, and simplified it down. Small thing fell out of it that i wasn't expecting but was happy about: resulting z-component of the new vector came out to exactly zero. This works as a nice built-in check, because it means, if a body is already lying in the shared flat plane, the formula correctly gives it a direction that also stays in that plane, consistent with the flat-disk design, and not just something that happened to look right by luck. Let me also write it down:

**General 3D cross product** of `a = (a1,a2,a3)` and `b = (b1,b2,b3)` is:

```
a × b = (a2*b3 − a3*b2,  a3*b1 − a1*b3,  a1*b2 − a2*b1)
```

If we consider `a = (distance_x, distance_y, distance_z)` and fixed axis as `b = (0,0,1)`, every component will be like this:

| Component | Calculation | Result |
|---|---|---|
| x | distance_y × 1 − distance_z × 0 | distance_y |
| y | distance_z × 0 − distance_x × 1 | −distance_x |
| z | distance_x × 0 − distance_y × 0 | 0 |

So the raw direction vector is `(distance_y, -distance_x, 0)`. Of course, it still needs to be divided by its own length before it is a usable unit direction.

*These all still haven't coded, but in theory, should work.*
