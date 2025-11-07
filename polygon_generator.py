from opensimplex import OpenSimplex
import math
import polygon as poly


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
