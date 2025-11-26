import polygon as poly
import polygon_generator as poly_gen
import polygon_utilities as poly_utls
from constants import *

import time
import sys
import math
import random
import matplotlib.pyplot as plt
from colorama import init, Fore

from multiprocessing import Pool

init(autoreset=True)
NUMBER_OF_THREADS = 8


def update_bar(current, total, best_perimeter):
    percentage = current / total * 100
    bar = '#' * int(percentage / 2) + '-' * (50 - int(percentage / 2))
    bar = f"{current} [{bar}] {total} (Current best: {best_perimeter:.4f} u)"
    sys.stdout.write(f'\r{bar}')
    sys.stdout.flush()


def compare_graphs(p1, p2, points):
    def on_key_press(pressed_key, polygon):
        if pressed_key.key == 'h':
            if polygon.polygon_patch.get_alpha() == 0:
                polygon.polygon_patch.set_alpha(0.5)
            else:
                polygon.polygon_patch.set_alpha(0)
            plt.draw()


    fig = plt.figure(facecolor="#101010")
    ax = fig.add_subplot(111, facecolor='#050505')

    included_x, included_y = [], []
    excluded_x, excluded_y = [], []
    for pt in points:
        if pt.state == poly.INCLUDED:
            included_x.append(pt.x)
            included_y.append(pt.y)
        else:
            excluded_x.append(pt.x)
            excluded_y.append(pt.y)

    ax.plot(included_x, included_y, 'o', color='blue')
    ax.plot(excluded_x, excluded_y, 'o', color='red')

    p1.update_patch_polygon()
    p2.update_patch_polygon()

    p1.polygon_patch.set_edgecolor((0, 1, 0, 0.75))
    ax.add_patch(p1.polygon_patch)

    p2.polygon_patch.set_edgecolor((1, 0, 0, 0.5))
    ax.add_patch(p2.polygon_patch)

    plt.style.use('dark_background')
    plt.title("Original Polygon")

    fig.canvas.mpl_connect('key_press_event', lambda k: on_key_press(k, p2))

    plt.show()


def contains_all_blues_and_exclude_reds(polygon, points):
    pts_without_extremities = []
    for pt in points:
        if pt not in polygon.points:
            pts_without_extremities.append(pt)

    for pt in pts_without_extremities:
        included = polygon.point_in_polygon(pt)
        if pt.state == poly.INCLUDED and not included:
            return False
        elif pt.state == poly.EXCLUDED and included:
            return False

    return True


def get_all_combinations(points, n):
    # Choose only a few points
    combinations = []
    nb_pts = len(points)
    indexes = list(range(n))  # [0, 1, 2, 3, ... n]
    while True:
        combinations.append([points[i] for i in indexes])
        for i in range(n - 1, -1, -1):
            if indexes[i] != i + nb_pts - n:
                break

        else:
            return combinations

        indexes[i] += 1
        for j in range(i + 1, n):
            indexes[j] = indexes[j - 1] + 1


def get_all_permutations(points):
    # Implementation of the Heap’s algorithm
    nb_pts = len(points)

    permutations = []
    pts_copy = points[:]
    counter = [0] * nb_pts

    permutations.append(pts_copy[:])

    k = 0
    while k < nb_pts:
        if counter[k] < k:
            if k % 2 == 0:
                pts_copy[0], pts_copy[k] = pts_copy[k], pts_copy[0]
            else:
                pts_copy[counter[k]], pts_copy[k] = pts_copy[k], pts_copy[counter[k]]

            permutations.append(pts_copy[:])
            counter[k] += 1
            k = 0
        else:
            counter[k] = 0
            k += 1

    return permutations


def get_total_iterations(n):
    total = 0
    for k in range(3, n+1):
        total += math.comb(n, k) * math.factorial(k)
    return total


def best_perimeter_task(combinations, points, counter, lock):
    current_best = None
    current_best_peri = -1
    iterations = 0
    added_iterations = 0

    for combination in combinations:
        for permutation in get_all_permutations(combination):
            iterations += 1
            p = poly.Polygon(permutation, create_patch=False, update_bounds=False)

            peri = p.get_perimeter()
            if current_best is None or peri < current_best_peri:
                if contains_all_blues_and_exclude_reds(p, points):
                    current_best = p
                    current_best_peri = peri

    return {"best_peri": current_best_peri, "best_poly": current_best, "i": iterations}


def separate_combinations(combinations, n):
    blocks_steps = len(combinations) // n
    blocks = []
    for i in range(n):
        start = i * blocks_steps
        if i < n - 1:
            blocks.append(combinations[start:start + blocks_steps])
        else:
            blocks.append(combinations[start:])

    return blocks


def get_best_perimeter_polygon(points, callback=None, nb_threads=NUMBER_OF_THREADS):
    # Choose a random point path
    # For each point, take it or leave it, in a random order
    current_best = None
    current_best_peri = -1

    theorical_max = get_total_iterations(len(points))
    i = 0

    with Pool(nb_threads) as pool:
        for k in range(3, len(points) + 1):
            all_combinations = get_all_combinations(points, k)
            combinations_blocks = separate_combinations(all_combinations, nb_threads)
            infos_blocks = [(combinations_blocks[i], points, None, None) for i in range(len(combinations_blocks))]

            results = pool.starmap(best_perimeter_task, infos_blocks)
            for result in results:
                i += result["i"]
                if current_best is None or (result["best_peri"] != -1 and result["best_peri"] < current_best_peri):
                    current_best_peri = result["best_peri"]
                    current_best = result["best_poly"]

            if current_best_peri is not None:
                callback(i, theorical_max, current_best_peri)

    return current_best


def get_min_perimeter_include_exclude(points, calculated_min=None, constraint=MINIMIZE_PERIMETER):
    """
    Test all polygons created by generating all include/exclude step orders

    :param points: The set of blue and red points
    :param calculated_min: The perimeter calculated by the actual algorithm
    :return: (polygon with the smallest perimeter, perimeter)
    """

    min_peri = None
    min_peri_poly = None

    hull = poly.Polygon()
    hull.convex_hull(points)
    hull.update_lines()

    current_search = [hull]
    i = 0
    while current_search:
        next_search = []
        for search in current_search:
            problematic_reds = poly_utls.get_included_excluded(points, search)
            problematic_blues = poly_utls.get_excluded_included(points, search, constraint)
            problematic_pts = problematic_reds + problematic_blues

            if len(problematic_pts) == 0:
                peri = search.get_perimeter() if constraint == MINIMIZE_PERIMETER else search.get_area()
                if min_peri is None or peri < min_peri:
                    min_peri = peri
                    min_peri_poly = search
                continue

            for pt in problematic_pts:
                for j in range(len(search.lines)):
                    new_poly = poly.Polygon(search.points.copy(), search.lines.copy(), create_patch=None, update_bounds=False)
                    # Insert the point pt at the position of the line
                    ln = search.lines[j]
                    l1 = poly.Line(ln.point1, pt)
                    l2 = poly.Line(pt, ln.point2)

                    del new_poly.lines[j]
                    new_poly.lines.insert(j, l2)
                    new_poly.lines.insert(j, l1)
                    idx = new_poly.points.index(ln.point2)
                    new_poly.points.insert(idx, pt)

                    next_search.append(new_poly)
                    if calculated_min is not None and constraint == MINIMIZE_PERIMETER:
                        peri = new_poly.get_perimeter()
                        # print(f"Peri: {peri} | Calculated: {calculated_min}")
                        if peri > calculated_min:
                            del next_search[-1]
                            continue

                    intersects = poly_utls.multiple_intersects_with_polygon([l1, l2], new_poly)
                    if intersects:
                        del next_search[-1]

        current_search = next_search

        if i % 1 == 0:
            print(f"Iteration {i + 1} | Current min: {min_peri} u")

        i += 1
        if i > 100000:
            print("Too many iterations (100000)")
            break

    return min_peri, min_peri_poly


# def is_min_perimeter(current_perimeter, min_perimeter, points_in_line, current_point, all_points, is_end):
#     print(current_perimeter)
#     if current_point is None:
#         for point in all_points:
#             return is_min_perimeter(current_perimeter, min_perimeter, points_in_line, point, all_points, False)
#
#     if len(points_in_line) > 0:
#         line = poly.Line(points_in_line[-1], current_point)
#         current_perimeter += line.get_length()
#
#     if current_perimeter >= min_perimeter:
#         return
#     if is_end:
#         polygon = poly.Polygon(points_in_line, update_bounds=False, create_patch=False)
#         if contains_all_blues_and_exclude_reds(polygon, all_points):
#             return False
#
#     points_in_line.append(current_point)
#
#     for point in all_points:
#         if point not in points_in_line:
#             print("as")
#             return is_min_perimeter(current_perimeter, min_perimeter, points_in_line, point, all_points, False)
#         elif point == points_in_line[0]:
#             return is_min_perimeter(current_perimeter, min_perimeter, points_in_line, point, all_points, True)
#
#     return True


if __name__ == "__main__":
    auto_test = False
    next_seed = None
    while True:
        # 159634519162366 (10x2 pts), 696232785600372 (4x2), très stylé, pour l'aire: 18658181112621 (8x2)
        if next_seed is None:
            seed = random.randint(1, 1_000_000_000_000_000)
        else:
            seed = next_seed

        next_seed = None
        constraint = MINIMIZE_AREA
        # seed = 1
        print(f"Seed: {seed} | Constraint: '{'perimeter' if constraint == MINIMIZE_PERIMETER else 'area'}'")

        data = poly_gen.get_random_points(seed, 7, 7)

        optimal = poly.Polygon()
        t = time.time()
        optimal.convex_hull(data)
        optimal.max_optimize(data, constraint=constraint)
        elapsed_time = time.time() - t

        perimeter = optimal.get_perimeter() if constraint == MINIMIZE_PERIMETER else optimal.get_area()
        print(f"Algorithm answer: {perimeter:.4f} u (in {elapsed_time:.4f} s)")

        t = time.time()

        #if is_min_perimeter(0, perimeter, [], None, data, False):
        #    print("It is the minimum perimeter")

        elapsed_time = time.time() - t
        #print(elapsed_time)

        t = time.time()
        #actual_min_polygon = get_best_perimeter_polygon(data, update_bar, NUMBER_OF_THREADS)
        actual_min_perimeter, actual_min_polygon = get_min_perimeter_include_exclude(data, perimeter, constraint)
        elapsed_time = time.time() - t

        if actual_min_polygon is None:
            print("Error...")

        actual_min_polygon.update_patch_polygon()
        actual_min_polygon.polygon_patch.set_alpha(0.5)
        actual_min_polygon.polygon_patch.set_linestyle("--")
        # actual_min_polygon.polygon_patch.set_fill(False)

        correct = round(actual_min_perimeter, 9) == round(perimeter, 9)
        color = Fore.GREEN if correct else Fore.RED
        print(color + f"\nActual answer: {actual_min_perimeter:.4f} u (in {elapsed_time:.4f} secs)" + Fore.BLACK)

        pts_optimal = sorted(optimal.points, key=lambda p: p.x)
        pts_actual = sorted(actual_min_polygon.points, key=lambda p: p.x)
        print(f"Same points? {pts_optimal == pts_actual}")

        if not auto_test:
            can_quit = False
            did_show_graph = False
            while not can_quit:
                s = input()
                if s == "s" and not did_show_graph:
                    compare_graphs(optimal, actual_min_polygon, data)
                    did_show_graph = True
                    continue
                elif s.isnumeric():
                    next_seed = int(s)
                can_quit = True
        else:
            print()

    # 813142566432053, 452551270535096, 445550995997911, 901016136321916, 333609186585783, 194595313759156, 339440507348159, 304227909683207
