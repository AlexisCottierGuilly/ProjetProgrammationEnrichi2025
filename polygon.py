import math
import random
from matplotlib.patches import Polygon as PatchPolygon

import polygon_utilities as poly_utls
import polygon_generator as poly_gen

INCLUDED = 0
EXCLUDED = 1
IGNORE = 2


class Polygon:
    def __init__(self, points=None, lines=None, seed=None):
        self.points = points or []
        self.lines = lines or []
        self.seed = seed or self.get_random_seed()

        self.polygon_patch = PatchPolygon([(0, 0)], closed=True)

        self.bounds = [(0, 0), (0, 0)]  # [center, scale]

        if self.points != [] and self.lines == []:
            self.update_lines()

        self.recalculate_bounds()
        self.update_patch_polygon()

    def get_random_seed(self):
        return random.randint(1, 1_000_000_000_000)

    def generate(self, center=None, scale=1, smoothness=1, new_seed=False):
        if new_seed:
            self.seed = self.get_random_seed()

        center = center or [0, 0]
        self.points = poly_gen.generate_polygon_points(
            self.seed, center, scale, smoothness
        )
        self.update_lines()
        self.recalculate_bounds()
        self.update_patch_polygon()

    def update_lines(self):
        self.lines = []

        if len(self.points) < 2:
            return

        last_point = None
        for pt in self.points:
            if last_point is not None:
                ln = Line(last_point, pt)
                self.lines.append(ln)
            last_point = pt

        if len(self.points) >= 2:
            self.lines.append(
                Line(self.points[-1], self.points[0])
            )

    def get_area(self):
        return poly_utls.calculate_area(self)

    def point_in_polygon(self, point):
        return poly_utls.point_in_polygon(point, self)

    def recalculate_bounds(self):
        self.bounds = poly_utls.calculate_bounds(self)

    def update_patch_polygon(self):
        vertices = []
        for pt in self.points:
            vertices.append((pt.x, pt.y))

        if not vertices:
            vertices = [(0, 0)]

        self.polygon_patch.set_xy(vertices)


class Point:
    def __init__(self, x, y, state=INCLUDED):
        self.x = x
        self.y = y
        self.state = state

    def __str__(self):
        return f"({self.x}, {self.y})"

class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def get_dx(self): return self.point1.x - self.point2.x
    def get_dy(self): return self.point1.y - self.point2.y

    def get_length(self):
        return math.sqrt(self.get_dx() ** 2 + self.get_dy() ** 2)

    def get_direction(self):
        normalization = 1 / self.get_length()
        dir_x = normalization * self.get_dx()
        dir_y = normalization * self.get_dy()
        return [dir_x, dir_y]

    def __str__(self):
        return f"({self.point1} -> {self.point2})"