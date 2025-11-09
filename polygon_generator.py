from opensimplex import OpenSimplex
import math
import polygon as poly
import random


def generate_polygon_points(seed, center, scale, smoothness=1):
    points = []
    noise = OpenSimplex(seed)

    num_points = math.ceil(scale * 10)
    base_radius = scale
    frequency = scale

    angle = 0
    for n in range(num_points):
        noise_value = noise.noise2(
            math.cos(angle) * frequency,
            math.sin(angle) * frequency
        )

        radius = base_radius + (1 / smoothness) * noise_value
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        point = poly.Point(x, y, poly.INCLUDED)
        points.append(point)

        angle += 2 * math.pi / num_points

    return points


def get_random_points(included_pts=10, excluded_pts=10, x_range=None, y_range=None):
    x_range = x_range or [0, 1]
    y_range = y_range or [0, 1]

    pts = []
    for i in range(included_pts + excluded_pts):
        state = poly.INCLUDED if i < included_pts else poly.EXCLUDED
        x = random.uniform(*x_range)
        y = random.uniform(*y_range)
        pt = poly.Point(x, y, state)
        pts.append(pt)

    return pts
