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


def load_dataset(filepath):
    with open(filepath, "r+") as f:
        data_string = f.read()

    lines = data_string.split("\n")
    lines = [line for line in lines if line != ""]

    pts = []
    for line in lines:
        if line.count(" ") < 2:
            raise ValueError(f"Point '{line}' not Valid in File '{filepath}'.")
        color, x, y = line.split(" ")
        state = poly.EXCLUDED if color.upper() == "R" else poly.INCLUDED
        x = float(x)
        y = float(y)

        pt = poly.Point(x, y, state)
        pts.append(pt)

    return pts


def save_points(points, filepath):
    data_string = ""
    for pt in points:
        color = "B" if pt.state == poly.INCLUDED else "R"
        x = str(pt.x)
        y = str(pt.y)
        data_string += f"{color} {x} {y}\n"

    with open(filepath, "a+") as f:
        f.truncate(0)  # Empty the file
        f.write(data_string)
