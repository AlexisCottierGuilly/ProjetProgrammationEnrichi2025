import math
import random
from matplotlib.patches import Polygon as PatchPolygon

import polygon_utilities as poly_utls
import polygon_generator as poly_gen
import polygon_optimization as poly_optim

from constants import *

INCLUDED = 0
EXCLUDED = 1
IGNORE = 2


class Polygon:
    def __init__(self, points=None, lines=None, seed=None, create_patch=True, update_bounds=True):
        self.points = points or []
        self.lines = lines or []
        self.seed = seed or self.get_random_seed()

        if create_patch:
            self.polygon_patch = PatchPolygon([(0, 0)], closed=True, fill=True, facecolor="#101010", edgecolor='white', linewidth=2)
        else:
            self.polygon_patch = None

        self.bounds = [(0, 0), (0, 0)]  # [center, scale]

        if self.points != [] and self.lines == []:
            self.update_lines()

        if update_bounds:
            self.recalculate_bounds()

        if create_patch:
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

    def convex_hull(self, points):
        self.set_points(poly_optim.convex_hull(points).points)

    def max_optimize(self, points, update_patch=True, update_bounds=True, constraint=MINIMIZE_PERIMETER):
        while True:
            did_change = self.optimize(points, update_patch=False, update_bounds=False, constraint=constraint)
            if not did_change:
                break

        if update_bounds:
            self.recalculate_bounds()
        if update_patch:
            self.update_patch_polygon()

    def optimize(self, points, update_patch=True, update_bounds=True, constraint=MINIMIZE_PERIMETER):
        did_change = False
        included_excluded = poly_utls.get_included_excluded(points, self)
        excluded_included = poly_utls.get_excluded_included(points, self, constraint)

        problematic_points = included_excluded + excluded_included

        if problematic_points:
            poly_optim.exclude_or_include_next(problematic_points, self, constraint=constraint)
            did_change = True

        if update_bounds:
            self.recalculate_bounds()
        if update_patch:
            self.update_patch_polygon()

        return did_change

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

    def update_points(self):
        self.points = []
        for line in self.lines:
            self.points.append(line.point1)

    def get_area(self):
        return poly_utls.calculate_area(self)

    def get_perimeter(self):
        return poly_utls.calculate_perimeter(self)

    def point_in_polygon(self, point):
        return poly_utls.point_in_polygon(point, self)

    def point_to_line_distance(self, point, line):
        return poly_utls.point_to_line_distance(point, line)

    def recalculate_bounds(self):
        self.bounds = poly_utls.calculate_bounds(self)

    def update_patch_polygon(self):
        if self.polygon_patch is None:
            self.polygon_patch = PatchPolygon([(0, 0)], closed=True, fill=True, facecolor="#101010", edgecolor='white', linewidth=2)

        vertices = []
        for pt in self.points:
            vertices.append((pt.x, pt.y))

        if not vertices:
            vertices = [(0, 0)]

        self.polygon_patch.set_xy(vertices)

    def set_points(self, points):
        self.points = points
        self.update_lines()
        self.recalculate_bounds()
        self.update_patch_polygon()


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