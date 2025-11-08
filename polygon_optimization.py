import math
import polygon as poly


def exclude_next(polygon):
    pass


def convex_hull(points):
    """
    Using the Jarvis' Algorithm
    Find a convex polygon that includes all Included Points.

    :param points: A list of all excluded and included points
    :return:
    """

    included_points = [pt for pt in points if pt.state == poly.INCLUDED]
    if not included_points:
        return poly.Polygon()

    # Start with the point the most on the left
    start_point = min(included_points, key=lambda pt: pt.x)
    polygon_points = [start_point]

    current_point = start_point
    while True:
        min_angle = -1
        next_point = included_points[0]
        for pt in included_points[1:]:
            if pt == current_point:
                continue

            cross_product = cross(current_point, next_point, pt)
            # Choose the most counterclockwise point
            # If two points are at the same cross product, choose the farther one.
            if next_point == current_point or cross_product < 0 or (
                    cross_product == 0 and distance(current_point, pt) > distance(current_point, next_point)):
                next_point = pt

        if next_point == start_point:
            break

        polygon_points.append(next_point)
        current_point = next_point

    return poly.Polygon(polygon_points)


def cross(current_pt, next_pt, pt):
    v1 = [
        next_pt.x - current_pt.x,
        next_pt.y - current_pt.y
    ]

    v2 = [
        pt.x - current_pt.x,
        pt.y - current_pt.y
    ]

    return v1[0] * v2[1] - v1[1] * v2[0]


def distance(p1, p2):
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
