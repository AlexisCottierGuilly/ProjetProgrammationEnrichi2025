import polygon as poly
import polygon_generator as poly_gen
import polygon_optimization as poly_optim
import time
import matplotlib.pyplot as plt


def max_optimize(p, points):
    while True:
        did_change = p.optimize(points, update_patch=False, update_bounds=False)
        if not did_change:
            break


iterations_per_num = 3
num_points = [5, 10, 25, 35, 50, 75, 100, 150, 200, 250, 350, 500]

# O(n^2.96862) using Desmos

stats = {n: [] for n in num_points}  # num_points: [time1, time2, ...]

x_range = y_range = [-5, 5]

for num in num_points:
    print(f"Measuring polygons with {num} points.")
    for i in range(iterations_per_num):
        print(f"\tIteration {i + 1}")
        pts = poly_gen.get_random_points(num // 2, num // 2, x_range, y_range)
        polygon = poly.Polygon(pts)

        polygon.set_points(poly_optim.convex_hull(pts).points)

        t = time.time()
        max_optimize(polygon, pts)
        elapsed_time = time.time() - t

        stats[num].append(elapsed_time)

results = [sum(times) / len(times) for times in list(stats.values())]

print("\n".join([f"{num_points[i]}: {results[i]}" for i in range(len(num_points))]))

plt.plot(num_points, results)
plt.show()
