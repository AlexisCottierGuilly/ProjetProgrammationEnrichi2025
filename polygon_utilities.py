import math
import numpy as np


def calculate_bounds(polygon):
    if len(polygon.points) == 0:
        return [(0, 0), (0, 0)]

    x_bounds = None
    y_bounds = None

    for point in polygon.points:
        if x_bounds is None:
            x_bounds = [point.x, point.x]
        if y_bounds is None:
            y_bounds = [point.y, point.y]

        x_bounds = [
            min(x_bounds[0], point.x),
            max(x_bounds[1], point.x)
        ]

        y_bounds = [
            min(y_bounds[0], point.y),
            max(y_bounds[1], point.y)
        ]

    x_size = x_bounds[1] - x_bounds[0]
    y_size = y_bounds[1] - y_bounds[0]
    bounds = [
        (x_bounds[0] + x_size / 2, y_bounds[0] + y_size / 2),
        (x_size, y_size)
    ]

    return bounds


def point_in_polygon(point, polygon):
    '''
    Using a Ray-Casting Algorithm (Crossing Number Algorithm)
    If a ray incoming from infinity to our point crosses
    an odd number of times the polygon's borders, the point
    is inside the polygon (the opposite is also true).

    Steps:
    1 - Cast a ray to thr right of the point
    2 - Calculate the number of intersections with
        the border.
    '''

    lines_crossed = 0
    for line in polygon.lines:
        x1, y1 = line.point1.x, line.point1.y
        x2, y2 = line.point2.x, line.point2.y

        if (y1 <= point.y < y2) or (y2 <= point.y < y1):
            # The line is at the right height
            # Now, check the x position
            edge_x = x1 + (point.y - y1) * (x2 - x1) / (y2 - y1)

            if edge_x >= point.x:
                lines_crossed += 1

    return lines_crossed % 2 == 1


def calculate_area(polygon):
    # Shoelace Formula

    total_area = 0
    for line in polygon.lines:
        x1, y1 = line.point1.x, line.point1.y
        x2, y2 = line.point2.x, line.point2.y
        total_area += x1 * y2 - x2 * y1

    return abs(total_area) / 2


def point_to_line_distance(point, line):
    x1, y1 = line.point1.x, line.point1.y
    x2, y2 = line.point2.x, line.point2.y

    line_v = [x2 - x1, y2 - y1]
    pt_to_line_v = [point.x - x1, point.y - y1]

    # Orthogonal projection of pt_to_line on line_v. t is a multiple of line_v
    t = (line_v[0] * pt_to_line_v[0] + line_v[1] * pt_to_line_v[1]) / (line_v[0] ** 2 + line_v[1] ** 2)

    # We want the shortest distance between point and line, so clamb t to be on the line
    projected_point = None
    if t < 0:
        projected_point = [x1, y1]
    elif t > 1:
        projected_point = [x2, y2]
    else:
        projected_point = [x1 + line_v[0] * t, y1 + line_v[1] * t]

    return math.sqrt((point.x - projected_point[0]) ** 2 + (point.y - projected_point[1]) ** 2)
