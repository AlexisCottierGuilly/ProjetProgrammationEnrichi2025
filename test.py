import matplotlib as mpl
import matplotlib.pyplot as plt
import polygon as poly

mpl.rcParams.update({
    'figure.facecolor': 'black',
    'axes.facecolor': 'black',
    'axes.edgecolor': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'text.color': 'white',
    'grid.color': 'gray'
})


def on_key_press(pressed_key):
    if pressed_key.key == 'r':
        regenerate()


def regenerate():
    polygon.generate(new_seed=True, scale=1)
    update_lims(polygon)
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


fig = plt.figure(facecolor="black")
ax = fig.add_subplot(111, facecolor='black')

polygon = poly.Polygon()
regenerate()

ax.add_patch(polygon.polygon_patch)
fig.canvas.mpl_connect('key_press_event', on_key_press)

update_lims(polygon)

plt.style.use('dark_background')
plt.title("Original Polygon")
plt.show()
