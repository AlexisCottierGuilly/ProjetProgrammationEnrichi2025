import math
import numpy as np
import polygon as poly
import polygon_optimization as poly_optim


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


def calculate_perimeter(polygon):
    perimeter = 0
    for line in polygon.lines:
        perimeter += line.get_length()

    return perimeter


def point_to_line_distance(point, line):
    x1, y1 = line.point1.x, line.point1.y
    x2, y2 = line.point2.x, line.point2.y

    line_v = [x2 - x1, y2 - y1]
    pt_to_line_v = [point.x - x1, point.y - y1]

    # Orthogonal projection of pt_to_line on line_v. t is a multiple of line_v
    t = (line_v[0] * pt_to_line_v[0] + line_v[1] * pt_to_line_v[1]) / (line_v[0] ** 2 + line_v[1] ** 2)

    # We want the shortest distance between point and line, so clamp t to be on the line
    projected_point = None
    if t < 0:
        projected_point = [x1, y1]
    elif t > 1:
        projected_point = [x2, y2]
    else:
        projected_point = [x1 + line_v[0] * t, y1 + line_v[1] * t]

    return math.sqrt((point.x - projected_point[0]) ** 2 + (point.y - projected_point[1]) ** 2)


def get_included_excluded(points, polygon):
    # Returns a list of all excluded points that are still in the polygon
    included_excluded_points = []

    for point in points:
        if point.state == poly.EXCLUDED and point not in polygon.points:
            inside = polygon.point_in_polygon(point)
            if inside:
                included_excluded_points.append(point)

    return included_excluded_points


def get_excluded_included(points, polygon):
    # Returns a list of all included points that are still outside the polygon
    excluded_included_points = []

    for point in points:
        if point.state == poly.INCLUDED and point not in polygon.points:
            outside = not polygon.point_in_polygon(point)
            if outside:
                excluded_included_points.append(point)

    return excluded_included_points


def intersects_with_line(line1, line2):
    o1 = poly_optim.cross(line1.point1, line1.point2, line2.point1)
    o2 = poly_optim.cross(line1.point1, line1.point2, line2.point2)
    o3 = poly_optim.cross(line2.point1, line2.point2, line1.point1)
    o4 = poly_optim.cross(line2.point1, line2.point2, line1.point2)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True

    if o1 == 0 and on_segment(line1.point1, line1.point2, line2.point1):
        return True
    if o2 == 0 and on_segment(line1.point1, line1.point2, line2.point2):
        return True
    if o3 == 0 and on_segment(line2.point1, line2.point2, line1.point1):
        return True
    if o4 == 0 and on_segment(line2.point1, line2.point2, line1.point2):
        return True

    return False


def on_segment(p1, p2, p):
    if min(p1.x, p2.x) < p.x < max(p1.x, p2.x) and min(p1.y, p2.y) < p.y < max(p1.y, p2.y):
        return True
    return False


def intersects_with_polygon(line, polygon):
    return any([intersects_with_line(line, l) for l in polygon.lines])
