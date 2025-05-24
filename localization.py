import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from shapely.geometry import LineString, Polygon, Point
import localization.plot as plot
from localization.monte_carlo import Particle, OccupationMap, MonteCarloLocalization

num_particles = 50
num_scan_points = 30
        
# Instantiate Localization
obstacles = [
    [(0, 0), (10, 0), (10, 10), (0, 10)],  # Obstacle 1
    [(20, 20), (30, 20), (30, 30), (20, 30)],  # Obstacle 2
    [(60, 60), (70, 60), (70, 70), (60, 70)],  # Obstacle 4
    [(80, 80), (90, 80), (90, 90), (80, 90)]]   # Obstacle 5

occ=OccupationMap([(0, 0), (100, 0), (100, 100), (0, 100)], obstacles)
localization = MonteCarloLocalization(occ, num_particles=num_particles)
scan = occ.get_dummy_scan(50,50,0, num_points=num_scan_points)  # Dummy scan input

# Setup plot
fig, ax = plt.subplots(figsize=(6, 6))
plot.cartesian_plot_scan_results(50, 50, 0, scan, ax=ax, color='green')
occ.plot(ax)
# Create initial dummy data for the quiver plot
initial_x = np.zeros(localization.num_particles)
initial_y = np.zeros(localization.num_particles)
initial_u = np.zeros(localization.num_particles)
initial_v = np.zeros(localization.num_particles)
initial_c = np.zeros(localization.num_particles)
initial_c[0]=1

# Quiver object: store this globally to update later
quiver = ax.quiver(initial_x, initial_y, initial_u, initial_v, initial_c,
                   cmap='viridis', scale=1, angles='xy', scale_units='xy')

# Axis settings
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Particle Filter Animation')
ax.grid(True)
p0=localization.particles[0]
# plot.rotary_plot_scan_results(scan, ax=ax)
ax = plot.cartesian_plot_scan_results(50, 50, 0, scan, ax=ax, color='red')

scan_plot = ax.scatter([], [], s=5, c='blue')


# Initialization function
def init():
    quiver.set_offsets(np.c_[initial_x, initial_y])
    quiver.set_UVC(initial_u, initial_v, initial_c)
    return (quiver,)

# Update function for each frame
def update(frame):
    dx = 0.0
    dy = 0
    drot = 0
    localization.update_step(dx, dy, drot, scan)
    particles = localization.particles
    x = [p.x for p in particles]
    y = [p.y for p in particles]
    u = [np.cos(p.rotation) for p in particles]
    v = [np.sin(p.rotation) for p in particles]
    prob = [p.probability for p in particles]
    # Normalize and scale arrow lengths
    max_prob = max(prob)
    if max_prob == 0:
        max_prob = 1e-6
    arrow_lengths = [5 + 20 * p/max_prob for p in prob]
    u = [u[i] * arrow_lengths[i] for i in range(len(u))]
    v = [v[i] * arrow_lengths[i] for i in range(len(v))]
    # Update quiver
    
    quiver.set_offsets(np.c_[x, y])
    quiver.set_UVC(u, v, prob)
    global scan_plot
    # p0=localization.particles[0]
    # print(p0.rotation)
    scan_x, scan_y=[],[]
    for p0 in localization.particles:
        scan_x_i, scan_y_i = plot.rotary_plot_scan_results(p0.x, p0.y, 0, occ.get_particle_distance_scan(p0,num_scan_points), ax)
        scan_x+=scan_x_i
        scan_y+=scan_y_i
    scan_plot.set_offsets(np.c_[scan_x, scan_y])

    return (quiver,scan_plot)

# Create animation
ani = animation.FuncAnimation(fig, update, frames=200, init_func=init,
                              blit=True, repeat=False, interval=10)

plt.show()
