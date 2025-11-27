import math
import polygon as poly
import polygon_utilities as poly_utils
from constants import *


def exclude_or_include_next(points, polygon, constraint=MINIMIZE_PERIMETER):
    """
    Main focus of our algorithm.
    The goal (to minimize the perimeter), is to take the
    point with the maximum perimeter modification in its side that
    modifies the least the perimeter.

    In a few words: take the point that will make the biggest
    change when included.

    Then, connect it to the polygon.

    :param points: Problematic points that needs inclusion/exclusion
    :param polygon: Current polygon
    :param constraint: Minimization parameter (perimeter or area)
    """

    if not points:
        return

    pt_line_excluded = []

    left_pts = points.copy()
    while True:
        longest_distance = None
        selected_point = None
        selected_line_index = None
        for point in left_pts:
            local_shortest = None
            local_selected_line_i = None
            for i, line in enumerate(polygon.lines):
                if [point, line] in pt_line_excluded:
                    continue

                #dist = polygon.point_to_line_distance(point, line)
                if constraint == MINIMIZE_PERIMETER:
                    l1 = poly.Line(line.point1, point)
                    l2 = poly.Line(point, line.point2)

                    start_dist = line.get_length()
                    new_dist = l1.get_length() + l2.get_length()
                    dist = new_dist - start_dist
                    dist = dist
                else:
                    # Form a triangle
                    l1 = poly.Line(line.point2, point)
                    l2 = poly.Line(point, line.point1)

                    dist = poly_utils.calculate_lines_area([line, l1, l2])
                    dist *= -1  # Find the biggest area

                if local_shortest is None or local_shortest >= dist:
                    local_shortest = dist
                    local_selected_line_i = i

            if longest_distance is None or longest_distance <= local_shortest:
                longest_distance = local_shortest
                selected_point = point
                selected_line_index = local_selected_line_i

        line = polygon.lines[selected_line_index]

        line1 = poly.Line(line.point1, selected_point)
        line2 = poly.Line(selected_point, line.point2)

        intersects = poly_utils.multiple_intersects_with_polygon([line1, line2], polygon)

        if not intersects:
            del polygon.lines[selected_line_index]
            polygon.lines.insert(selected_line_index, line2)
            polygon.lines.insert(selected_line_index, line1)
            idx = polygon.points.index(line.point2)
            polygon.points.insert(idx, selected_point)
            break
        else:
            pt_line_excluded.append([selected_point, line])


def convex_hull(points):
    """
    Using the Jarvis' Algorithm
    Find a convex polygon that includes all Included Points.

    :param points: A list of all excluded and included points
    :return:
    """

    included_points = [pt for pt in points if pt.state == poly.INCLUDED]
    if not included_points:
        return poly.Polygon(create_patch=False, update_bounds=False)

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

    return poly.Polygon(polygon_points, create_patch=False, update_bounds=False)


def cross(current_pt, next_pt, pt):
    """
    Find the determinant between:
        * The vector current -> next
        * The vector current -> point (another point)

    This function is used to compare vector angles.
    """

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
    # Distance between two points
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
