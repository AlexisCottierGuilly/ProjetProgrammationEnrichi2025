import math
import random


def find_parameters(data, target_error=0.1):
    """
    Fit the model to a y = ax^b.
    Find the best possible constants a and b

    :param data: a list of points (nb_points, generation_time)
    :return: (a, b), where the time depending on the nb_points is y = ax^b
    """

    starts = [(1, 1)]
    current_params = starts
    i = 0
    while True:
        next_params = []
        next_errors = []
        for a, b in current_params:
            error = calculate_error(data, a, b)
            k = 0.01
            c = 0
            a_modif_factor = 1 + 0.75 / (1 + math.exp(-k * (error - c)))
            b_modif_factor = 1 + 0.045 / (1 + math.exp(-k * (error - c)))

            a_modif_factor *= random.uniform(0.5, 2)
            b_modif_factor *= random.uniform(0.5, 2)

            min_error = error
            min_error_params = None
            for j in range(6):
                if j == 0:
                    a1 = a / a_modif_factor
                    b1 = b * b_modif_factor
                elif j == 1:
                    a1 = a * a_modif_factor
                    b1 = b / b_modif_factor
                elif j == 2:
                    a1 = a
                    b1 = b / b_modif_factor
                elif j == 3:
                    a1 = a * a_modif_factor
                    b1 = b
                elif j == 4:
                    a1 = a
                    b1 = b * b_modif_factor
                elif j == 5:
                    a1 = a / a_modif_factor
                    b1 = b

                err = calculate_error(data, a1, b1)

                #print(f"a={a1}, b={b1}, err={err}")
                if err < min_error:
                    min_error = err
                    min_error_params = (a1, b1)

            if min_error == error:
                min_error_params = (a, b)

            next_params.append(min_error_params)
            next_errors.append(min_error)

        current_params = next_params

        min_err = min(next_errors)
        if min_err <= target_error:
            return *next_params[next_errors.index(min_err)], min_err

        i += 1
        #if i % 10 == 0:
        #    print(f"i: {i}, err: {min_err}")

        if i >= 100000:
            return *next_params[next_errors.index(min_err)], min_err


def calculate_error(data, a, b):
    """
    Calculate the error between the dataset and the predicted function
    of the form y = ax^b

    :param data: a list of points (nb_points, generation_time)
    :param a: parameter a in y = ax^b
    :param b: parameter b in y = ax^b
    :return: the error
    """

    total_error = 0
    for x, y in data:
        predicted_y = a * x ** b
        difference_squared = (y - predicted_y) ** 2
        total_error += difference_squared

    return total_error
