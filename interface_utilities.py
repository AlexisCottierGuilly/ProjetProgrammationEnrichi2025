import math
import polygon as poly


def customize_button(button, rc_params):
    button.ax.set_facecolor(rc_params["axes.facecolor"])
    button.color = "0"
    button.hovercolor = "0.1"


def get_pressed_point(points, point_radius, mouse_pos):
    for point in points:
        if get_distance(point, mouse_pos) < point_radius:
            return point

    return None


def get_point_index(point, plot):
    x_data, y_data = plot.get_data()
    for i in range(len(x_data)):
        if point.x == x_data[i] and point.y == y_data[i]:
            return i
    return -1


def modify_point(pos, point, index, plot):
    point.x, point.y = pos[0], pos[1]
    x_data, y_data = plot.get_data()
    x_data[index] = pos[0]
    y_data[index] = pos[1]

    plot.set_data([x_data, y_data])


def get_distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

