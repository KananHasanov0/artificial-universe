# artificial-universe
A computational ecosystem exploring the emergence of adaptive behavior.

# Results
8/20/2026 [2:46 AM UTC+4]
It is my first real observation since I started the project, as the project just begin to form. Right now, the observation is made around four bodies.

I should start by writing down their characteristics, i suppose. Starting with orbital_velocity, ball's and ball_2's orbital velocities are relative to each other. However, newly added other two's (body_3 and body_4) orbital velocities are only relative to ball_2, because formula used in orbital_velocity has no way to account for third body (it is derived for exactly two bodies). they all have various masses; therefore, different radiuses and densities. to make up your mind, i will give the order by which their masses decrease: the one with biggest mass is ball_2. following, ball, ball_3, respectively. ball_4 have the least mass.

The first observation was made while ball had located close to both ball_3 and ball_4 (can be observed in lasted commit Fix softening, restitution symmetry, and add 4th body). As a result, ball_3 and ball_4 ended up colliding with ball, which was something unexpected as they were suppose to orbit ball_2. It wasn't a complex problem to reason ,though. my first judgment was "ball's gravity isn't a part of velocity computation (as I mentioned before), and since ball's starting location is closer to smaller bodies than that of ball_2, its unmodeled pull dominates. proximity beats ball_2's larger mass, owing to gravity falling off with distance squared"

estimation wasn't enough, so I made my second observation with ball far apart from other two. This time, ball_3 and ball_4 didn't collide with ball as expected, but instead of setting orbit around ball_2, they became gravitationally bound to each other (since they started only 20 units apart, much closer to each other than to ball_2), collided, and the pair drifted away from ball_2's system together as a bound unit — a small-scale ejection.

Significance of this discovery:
Neither binary nor ejection was intentional. There is no coding saying "create binary and eject it". Everything was caused simply by combination of using formula suitable exclusively for calculation of orbital velocity of EXACTLY two bodies (orbital_velocity()), but applied to actual case containing FOUR bodies at once. That pattern repeated itself twice: initially, ball’s ignored gravitational attraction won over ball_2’s greater mass due to initial proximity between ball, ball_3, and ball_4; and again after displacement, ball_3 and ball_4 formed a binary system among themselves due to initial nearness (started from 20 units of separation), and got ejected together from ball_2’s system.

This phenomenon relates directly to known physics problem: there exists no analytical solution for n>2-body problem in contrast to two-body one (connection to Poincaré's theorem on non-integrability of system); furthermore, phenomena such as gravitational ejection of binaries are well recorded in nature, when stars get ejected from stellar cluster. So basically the process I described represents miniature analogy of real-world gravitational process emerging entirely due to application of fundamental physical formulas without any external manipulation or scripting.

just wanted to point out:

that particular result came from single trial of simulation with particular initial values I manually picked. I didn't test for consistency: for example, does small change of initial coordinates yield similar outcome? How dependent on precise initial separation distance this phenomenon is? Is it reproducible and meaningful pattern, or mere coincidence? This poses limitations rather than flaw of discovery itself.