import matplotlib as mpl
import matplotlib.pyplot as plt
import polygon as poly
import polygon_optimization as poly_optim
import random
import time

mpl.rcParams.update({
    'figure.facecolor': '#121212',
    'axes.facecolor': '#121212',
    'axes.edgecolor': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'text.color': 'white',
    'grid.color': 'gray'
})


def on_mouse_move(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        point.set_data([x], [y])

        # Check if the point is in the polygon
        inside = polygon.point_in_polygon(poly.Point(x, y))
        color = "blue" if inside else "red"

        point.set_color(color)
        fig.canvas.draw_idle()


def on_key_press(pressed_key):
    if pressed_key.key == 'r':
        regenerate()
    elif pressed_key.key == 'o':
        optimize()


def optimize():
    print("Optimize")
    polygon.optimize(pts)
    update_lims(polygon)
    plt.draw()


def regenerate():
    global pts
    pts = []

    point.set_data([], [])

    # Generate random points
    included_pt_pos = [[], []]
    excluded_pt_pos = [[], []]

    seed = 300 #random.randint(1, 1_000_000_000_000)
    random.seed(seed)
    nb_included = 500
    nb_excluded = 500

    for i in range(nb_included + nb_excluded):
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        state = poly.INCLUDED if i < nb_included else poly.EXCLUDED
        pt = poly.Point(x, y, state)
        pts.append(pt)

        if state == poly.INCLUDED:
            included_pt_pos[0].append(x)
            included_pt_pos[1].append(y)
        else:
            excluded_pt_pos[0].append(x)
            excluded_pt_pos[1].append(y)

    polygon.convex_hull(pts)
    polygon.update_lines()

    random_included_points.set_data(included_pt_pos)
    random_excluded_points.set_data(excluded_pt_pos)

    #polygon.generate(new_seed=True, scale=1, smoothness=1)

    """
    print([str(l) for l in polygon.lines])
    print(f"Area: {polygon.get_area()} u^2")
    print()
    """

    update_lims(polygon)

    optim_time = 0
    step = 50
    i = 0
    while True:
        t = time.time()
        did_change = polygon.optimize(pts, update_bounds=False, update_patch=False)
        optim_time += time.time() - t

        if not did_change:
            break
        if i % step == 0:
            polygon.recalculate_bounds()
            polygon.update_patch_polygon()
            plt.draw()
            plt.pause(0.005)
        i += 1

    print(f"Seed: {seed}, Perimeter: {polygon.get_perimeter():.5f}, In {optim_time:.5f} secs")

    plt.draw()


def update_lims(ply):
    spacing_factor = 1.25
    offset = ply.bounds[0]
    size = max(ply.bounds[1]) / 2

    ax.set_xlim(
        -size * spacing_factor + offset[0],
        size * spacing_factor + offset[0]
    )
    ax.set_ylim(
        -size * spacing_factor + offset[1],
        size * spacing_factor + offset[1]
    )
    ax.set_aspect('equal')


fig = plt.figure(facecolor="#101010")
ax = fig.add_subplot(111, facecolor='#050505')

polygon = poly.Polygon()
pts = []

point, = ax.plot([], [], 'x', color='blue')
random_included_points, = ax.plot([], [], 'o', color='blue', markersize=1)
random_excluded_points, = ax.plot([], [], 'o', color='red', markersize=1)

ax.add_patch(polygon.polygon_patch)
regenerate()

fig.canvas.mpl_connect('key_press_event', on_key_press)
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

update_lims(polygon)

plt.style.use('dark_background')
plt.title("Original Polygon")
plt.show()
