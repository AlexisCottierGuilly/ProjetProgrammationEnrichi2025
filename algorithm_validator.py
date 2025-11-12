import polygon as poly
import polygon_generator as poly_gen
import time
import sys
import math
import random
import matplotlib.pyplot as plt
from colorama import init, Fore

init(autoreset=True)


def update_bar(current, total, best_perimeter):
    percentage = current / total * 100
    bar = '#' * int(percentage / 2) + '-' * (50 - int(percentage / 2))
    bar = f"{current} [{bar}] {total} (Current best: {best_perimeter:.4f} u)"
    sys.stdout.write(f'\r{bar}')
    sys.stdout.flush()


def compare_graphs(p1, p2, points):
    def on_key_press(pressed_key, polygon):
        if pressed_key.key == 'h':
            if polygon.polygon_patch.get_edgecolor()[-1] != 0:
                polygon.polygon_patch.set_edgecolor((
                    polygon.polygon_patch.get_edgecolor()[0],
                    polygon.polygon_patch.get_edgecolor()[1],
                    polygon.polygon_patch.get_edgecolor()[2],
                    0
                ))
                polygon.polygon_patch.set_facecolor((
                    polygon.polygon_patch.get_facecolor()[0],
                    polygon.polygon_patch.get_facecolor()[1],
                    polygon.polygon_patch.get_facecolor()[2],
                    0
                ))
            else:
                polygon.polygon_patch.set_edgecolor((
                    polygon.polygon_patch.get_edgecolor()[0],
                    polygon.polygon_patch.get_edgecolor()[1],
                    polygon.polygon_patch.get_edgecolor()[2],
                    0.5
                ))
                polygon.polygon_patch.set_facecolor((
                    polygon.polygon_patch.get_facecolor()[0],
                    polygon.polygon_patch.get_facecolor()[1],
                    polygon.polygon_patch.get_facecolor()[2],
                    1
                ))
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


def get_best_perimeter_polygon(points, callback=None):
    # Choose a random point path
    # For each point, take it or leave it, in a random order
    current_best = None
    current_best_peri = -1

    theorical_max = get_total_iterations(len(points))
    i = 0
    for k in range(3, len(points) + 1):
        for combination in get_all_combinations(points, k):
            for permutation in get_all_permutations(combination):
                p = poly.Polygon(permutation)

                i += 1
                if i % 1000 == 0 and callback is not None:
                    callback(i, theorical_max, current_best_peri)

                peri = p.get_perimeter()
                if current_best is None or peri < current_best_peri:
                    if contains_all_blues_and_exclude_reds(p, points):
                        current_best = p
                        current_best_peri = peri

    callback(i, theorical_max, current_best_peri)

    return current_best


auto_test = True
while True:
    seed = random.randint(1, 1_000_000_000_000_000)
    print(f"Seed: {seed}")

    data = poly_gen.get_random_points(seed, 4, 4)

    optimal = poly.Polygon()
    optimal.convex_hull(data)
    optimal.max_optimize(data)

    perimeter = optimal.get_perimeter()
    print(f"Algorithm answer: {perimeter:.4f} u")

    t = time.time()
    actual_min_polygon = get_best_perimeter_polygon(data, update_bar)
    elapsed_time = time.time() - t

    actual_min_perimeter = actual_min_polygon.get_perimeter()

    correct = round(actual_min_perimeter, 9) == round(perimeter, 9)
    color = Fore.GREEN if correct else Fore.RED
    print(color + f"\nActual answer: {actual_min_perimeter:.4f} u (in {elapsed_time:.3f} secs)" + Fore.BLACK)

    pts_optimal = sorted(optimal.points, key=lambda p: p.x)
    pts_actual = sorted(actual_min_polygon.points, key=lambda p: p.x)
    print(f"Same points? {pts_optimal == pts_actual}")

    if not auto_test:
        s = input()
        if s == "s":
            compare_graphs(optimal, actual_min_polygon, data)
            input()
    else:
        print()

# 813142566432053, 452551270535096, 445550995997911, 901016136321916, 333609186585783, 194595313759156, 339440507348159, 304227909683207
