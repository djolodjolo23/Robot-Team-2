import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import localization.plot as plot
from localization.monte_carlo import OccupationMap, MonteCarloLocalization

import localization.monte_carlo
from pathfinding import Map, Obstacle
num_particles = 100


scan = [656, 660, 660, 659, 659, 659, 661, 661, 660, 660, 660, 657, 657, 653, 653, 647, 647, 647, 643, 643, 639, 639, 639, 636, 636, 636, 636, 636, 635, 635, 636, 636, 636, 641, 641, 646, 646, 646, 650, 650, 660, 660, 660, 669, 669, 680, 680, 680, 694, 694, 714, 714, 714, 744, 744, 771, 771, 795, 795, 795, 805, 805, 814, 814, 814, 815, 815, 817, 817, 817, 818, 818, 823, 823, 823, 831, 831, 840, 840, 840, 853, 853, 868, 868, 890, 890, 890, 918, 918, 942, 942, 942, 974, 974, 981, 981, 975, 975, 975, 956, 956, 935, 935, 935, 919, 919, 904, 904, 904, 892, 892, 883, 883, 883, 878, 878, 875, 875, 876, 876, 876, 875, 875, 878, 878, 879, 879, 879, 880, 880, 873, 873, 862, 862, 862, 862, 862, 835, 835, 825, 825, 825, 825, 825, 813, 813, 813, 812, 812, 810, 810, 810, 806, 806, 811, 811, 813, 813, 813, 821, 821, 821, 821, 821, 827, 827, 841, 841, 853, 853, 853, 864, 864, 866, 866, 868, 868, 868, 868, 868, 870, 870, 870, 865, 865, 862, 862, 856, 856, 856, 828, 828, 769, 769, 769, 665, 665, 617, 617, 617, 583, 583, 582, 582, 582, 599, 599, 580, 580, 594, 594, 594, 617, 617, 610, 610, 610, 634, 634, 633, 633, 681, 681, 681, 699, 699, 734, 734, 734, 944, 944, 1173, 1173, 1324, 1324, 1422, 1422, 1422, 1480, 1480, 1530, 1530, 1593, 1593, 1593, 1658, 1658, 1684, 1684, 1684, 1724, 1724, 1724, 1703, 1703, 1707, 1707, 1707, 1673, 1673, 1673, 1673, 1673, 1673, 1673, 1626, 1626, 1626, 1626, 1588, 1588, 1588, 1572, 1572, 1561, 1561, 1561, 1542, 1542, 1536, 1536, 1536, 1523, 1523, 1520, 1520, 1517, 1517, 1517, 1507, 1507, 1511, 1511, 1508, 1508, 1508, 1509, 1509, 1507, 1507, 1506, 1506, 1506, 1519, 1519, 1516, 1516, 1516, 1517, 1517, 1533, 1533, 1539, 1539, 1539, 1549, 1549, 1568, 1568, 1568, 1578, 1578, 1578, 1578, 1578, 1569, 1569, 1560, 1560, 1560, 1512, 1512, 1404, 1404, 1364, 1364, 1364, 1365, 1365, 1353, 1353, 1345, 1345, 1345, 1299, 1299, 1176, 1176, 1241, 1241, 1241, 1034, 1034, 989, 989, 989, 1013, 1013, 983, 983, 901, 901, 901, 812, 812, 799, 799, 811, 811, 811, 777, 777, 759, 759, 759, 755, 755, 689, 689, 645, 645, 645, 601, 601, 550, 550, 550, 522, 522, 516, 516, 516, 508, 508, 505, 505, 505, 500, 500, 490, 490, 482, 482, 482, 474, 474, 466, 466, 459, 459, 459, 454, 454, 450, 450, 450, 444, 444, 443, 443, 443, 438, 438, 434, 434, 434, 434, 434, 431, 431, 430, 430, 430, 430, 430, 430, 427, 427, 427, 427, 423, 423, 423, 425, 427, 427, 427, 427, 427, 430, 430, 433, 433, 433, 435, 435, 438, 438, 438, 441, 441, 441, 441, 441, 445, 445, 450, 450, 455, 455, 455, 460, 460, 460, 467, 467, 474, 474, 477, 477, 477, 484, 484, 496, 496, 496, 503, 503, 511, 511, 511, 522, 522, 534, 534, 545, 545, 545, 559, 559, 571, 571, 571, 584, 584, 608, 608, 608, 626, 626, 640, 640, 664, 664, 664, 686, 686, 700, 700, 700, 700, 700, 744, 744, 744, 748, 748, 737, 737, 737, 716, 716, 690, 690, 670, 670, 670, 649, 649, 649, 628, 628, 628, 628, 599, 599, 587, 587, 587, 577, 577, 577, 569, 569, 563, 563, 559, 559, 555, 555, 555, 553, 553, 552, 552, 552, 552, 552, 551, 551, 551, 555, 555, 557, 557, 560, 560, 558, 558, 558, 555, 555, 546, 546, 546, 545, 545, 544, 544, 544, 543, 543, 544, 544, 541, 541, 541, 543, 543, 543, 543, 542, 542, 542]
scan = [x/100 for x in scan]  # Convert to meters
scan= [scan[i] for i in range(0,len(scan), 30)]
scan= scan[::-1]
# print(len(scan))
o1 = Obstacle(10, 0, 4, 4)
map = Map(22, 14, [o1], [])


occ= localization.monte_carlo.OccupationMap.from_Map(map)
localization = MonteCarloLocalization(occ, num_particles=num_particles)
# Setup plot
fig, ax = plt.subplots(figsize=(6, 6))
plot.cartesian_plot_scan_results(10, 10, 0, scan, ax=ax, color='green')
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
# ax = plot.cartesian_plot_scan_results(50, 50, 0, scan, ax=ax, color='red')

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
        scan_x_i, scan_y_i = plot.rotary_plot_scan_results(p0.x, p0.y, 0, occ.get_particle_distance_scan(p0,len(scan)), ax)
        scan_x+=scan_x_i
        scan_y+=scan_y_i
    scan_plot.set_offsets(np.c_[scan_x, scan_y])

    return (quiver,scan_plot)

# Create animation
ani = animation.FuncAnimation(fig, update, frames=200, init_func=init,
                              blit=True, repeat=False, interval=10)

plt.show()
