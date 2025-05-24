import matplotlib.pyplot as plt
import math


# plots data in polar coordinates
def rotary_plot_scan_results(data, ax=None, color='blue'):
    # Prepare polar coordinates
    angles = []
    distances = []

    for i, dist in enumerate(data):
        angle_rad = i*math.pi*2/len(data)   #np.deg2rad(i*(360/len(data)))
        if dist < 60000:  # Filter out invalid distances
            angles.append(angle_rad)
            distances.append(dist)

    # Plot
    plt.figure(figsize=(8, 8))
    if ax==None:
        ax = plt.subplot(111, polar=True)
    ax.scatter(angles, distances, s=10, c=color, alpha=0.7)

    ax.set_theta_zero_location("N")  # 0° at the top
    ax.set_theta_direction(-1)       # Clockwise

    plt.title("Polar Plot of Distance Measurements")
    plt.show()


#plots data in cartesian coordinates
def cartesian_plot_scan_results(x, y, rot, data, ax=None, color='blue'):
    # Convert polar scan data to Cartesian coordinates
    scan_points_x = []
    scan_points_y = []

    for i, dist in enumerate(data):
        if dist >= 60000:
            continue  # Ignore invalid distances

        angle_rel = i * 2 * math.pi / len(data)
        angle_global = rot + angle_rel  # Rotate scan to global frame

        px = x + dist * math.cos(angle_global)
        py = y + dist * math.sin(angle_global)

        scan_points_x.append(px)
        scan_points_y.append(py)

    # Plot
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(scan_points_x, scan_points_y, s=10, c=color, alpha=0.7, label='Scan Points')
    ax.plot(x, y, 'ro', label='Sensor Position')
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_title("Cartesian Plot of Scan Data")
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    return ax

# gets points to plot in cartesian coordinates for animation
def rotary_plot_scan_results(x, y, rot, data, ax):
    angles = []
    distances = []
    for i, dist in enumerate(data):
        if dist < 60000:
            angle = rot + i * 2 * math.pi / len(data)
            angles.append(angle)
            distances.append(dist)

    scan_x = [x + d * math.cos(a) for d, a in zip(distances, angles)]
    scan_y = [y + d * math.sin(a) for d, a in zip(distances, angles)]

    return scan_x, scan_y