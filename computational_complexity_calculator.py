import polygon as poly
import polygon_generator as poly_gen
import parameter_optimization as para_optim
import time
import matplotlib.pyplot as plt

# y = 9.766625735328421e-09x^3.128842516245288
# 2.2495241356997548e-08x^3.004414107026635

iterations_per_num = 10
num_points = [5, 10, 25, 35, 50, 75, 100, 150, 200, 300, 450, 650]

# O(n^2.96862) using Desmos

stats = {n: [] for n in num_points}  # num_points: [time1, time2, ...]

x_range = y_range = [-5, 5]

for num in num_points:
    print(f"Measuring polygons with {num} points.")
    for i in range(iterations_per_num):
        print(f"\tIteration {i + 1}", end=" ")
        pts = poly_gen.get_random_points(num // 2, num // 2, x_range, y_range)
        polygon = poly.Polygon(pts)

        polygon.convex_hull(pts)

        t = time.time()
        polygon.max_optimize(pts, update_patch=False, update_bounds=False)
        elapsed_time = time.time() - t

        print(f"({elapsed_time:.5f} secs)")

        stats[num].append(elapsed_time)

results = [sum(times) / len(times) for times in list(stats.values())]

print("\n".join([f"{num_points[i]}\t{results[i]}" for i in range(len(num_points))]))

# Calculate the y = ax^b that is the closest to the data
data = [(num_points[i], results[i]) for i in range(len(num_points))]
a, b = para_optim.find_parameters(data, 0.001)  # or 100000 iterations max
prediction_data = [a * x ** b for x in num_points]

print(f"Prediction: y = {a}x^{b}")

plt.plot(num_points, results)
plt.plot(num_points, prediction_data, color="yellow")

plt.show()
