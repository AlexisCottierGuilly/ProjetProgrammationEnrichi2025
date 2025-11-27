import polygon as poly
import polygon_generator as poly_gen
import parameter_optimization as para_optim
import time
import matplotlib.pyplot as plt

"""
This program estimated the computational complexity
of the polygon generator function, with multiple
number of points to approximate the function
    y = ax^b

Function that represents the computational complexity.
"""

# ~O(n^3)

iterations_per_num = 5
num_points = [5, 10, 25, 35, 50, 75, 100, 150, 200, 250, 300, 350]  #, 400, 450, 650, 800]

# O(n^2.96862) using Desmos

stats = {n: [] for n in num_points}  # num_points: [time1, time2, ...]

x_range = y_range = [-5, 5]

for num in num_points:
    print(f"Measuring polygons with {num} points.")
    for i in range(iterations_per_num):
        print(f"\tIteration {i + 1}", end=" ")
        pts = poly_gen.get_random_points(None, num // 2, num // 2, x_range, y_range)
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
a, b, error = para_optim.find_parameters(data, 0.00025)  # or 100000 iterations max

prediction_data = []
prediction_x = []
prediction_pts = 1000
step = max(num_points) / 1000
for i in range(prediction_pts):
    n = i * step
    prediction_x.append(n)
    prediction_data.append(a * n ** b)

print(f"Prediction: y = {a}x^{b} (error: {error})")

plt.plot(num_points, results, color="blue")
plt.plot(prediction_x, prediction_data, color="orange", linestyle="--")

plt.grid()
plt.title("Computational Complexity Calculator")

plt.legend(["Data", f"Approximation\nO(n^{b:.3f})"])

plt.show()
