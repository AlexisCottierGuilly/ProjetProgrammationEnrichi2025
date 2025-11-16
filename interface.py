import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

import polygon as poly
import polygon_generator as poly_gen
import polygon_optimization as poly_optim
import interface_utilities as interface_utils

from constants import *

import random
import time

"""
Functionalities
 - Place points (1, 2 = blue, red)
 - Create polygon (space)
 - Set seed (input field)
 - Set points (input field)
 - Step by step (next)
 - Random points (with r)
 - Move points
"""

mpl.rcParams.update({
    'figure.facecolor': '#121212',
    'axes.facecolor': '#121212',
    'axes.edgecolor': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'text.color': 'white',
    'grid.color': 'gray'
})


class PolygonInterface:
    def __init__(self, title="Polygon"):
        self.seed = 1
        self.constraint = MINIMIZE_PERIMETER

        self.points = []
        self.polygon = None

        self.reset_mode = RESET_RANDOM
        self.current_dataset = None
        self.save_file = "dataset_1.txt"
        self.auto_save = True

        self.draggable_point = None
        self.draggable_point_index = None

        self.auto_step = True
        self.step_delay = 0 #0.01

        self.fig = plt.figure(facecolor="#101010")
        self.fig.set_size_inches(10, 6, forward=True)
        self.ax = self.fig.add_subplot(111, facecolor='#050505')

        self.blue_points_plot, = self.ax.plot([], [], 'o', color='blue')
        self.red_points_plot, = self.ax.plot([], [], 'o', color='red')

        self.initialize_communication()

        self.buttons = []
        self.point_textbox = None
        self.currently_writing = False
        self.setup_buttons()

        self.num_blue, self.num_red = 5, 5
        self.set_random_points()

        self.create_polygon()
        self.initialize_polygon()
        self.update_title()

    def initialize_communication(self):
        self.fig.canvas.mpl_connect('key_press_event', self.key_pressed)
        self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_moved)
        self.fig.canvas.mpl_connect('button_press_event', self.mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.mouse_release)

    def setup_buttons(self):
        self.fig.subplots_adjust(bottom=0.2)

        bar_width = 0.2
        x_center = 0.85
        x_start = x_center - bar_width / 2

        step_ax = self.fig.add_axes([x_start, 0.2, bar_width, 0.075])  #[0.7, 0.05, 0.1, 0.075])
        step_button = Button(step_ax, "Step")
        step_button.on_clicked(lambda event: self.step())
        interface_utils.customize_button(step_button, mpl.rcParams)
        self.buttons.append(step_button)  # buttons[0]

        textbox_width = bar_width / 1.75
        add_point_ax = self.fig.add_axes([x_start, 0.35, textbox_width, 0.075])
        add_point_textbox = TextBox(add_point_ax, "")
        add_point_textbox.on_text_change(lambda text: self.update_add_point(text, add_point_textbox))
        add_point_textbox.currently_setting_value = False

        def set_text(text, textbox):
            textbox.currently_setting_value = True
            textbox.set_val(text)
            textbox.currently_setting_value = False

        def update_color(color, textbox):
            for side in ["bottom", "top", "left", "right"]:
                textbox.ax.spines[side].set_edgecolor(color)

        add_point_textbox.set_text = lambda text: set_text(text, add_point_textbox)
        add_point_textbox.update_color = lambda c: update_color(c, add_point_textbox)
        interface_utils.customize_button(add_point_textbox, mpl.rcParams)
        self.point_textbox = add_point_textbox

        add_width = bar_width / 3
        space = bar_width - add_width - textbox_width
        s = x_start + textbox_width + space
        add_point_validation_ax = self.fig.add_axes([s, 0.35, add_width, 0.075])
        add_point_validation_button = Button(add_point_validation_ax, "+")
        add_point_validation_button.on_clicked(lambda event: self.add_point(add_point_textbox))
        interface_utils.customize_button(add_point_validation_button, mpl.rcParams)
        self.buttons.append(add_point_validation_button)  # buttons[1]

        self.fig.text(x_start + textbox_width / 2, 0.45, "Point", ha="center", va="center")
        self.fig.text(x_start + textbox_width + space + add_width / 2, 0.45, "Add", ha="center", va="center")

    def update_add_point(self, string, textbox):
        if textbox.currently_setting_value:
            return

        self.currently_writing = True

        textbox.set_text("".join([char for char in textbox.text.upper() if char in "-0123456789(),.BR "]))

        if len(textbox.text) > 1 and "R" in textbox.text and textbox.text[0] != "R":
            textbox.cursor_index -= 1
            textbox.set_val("R" + textbox.text[1:].replace("R", ""))
        if len(textbox.text) > 1 and "B" in textbox.text and textbox.text[0] != "B":
            textbox.cursor_index -= 1
            textbox.set_val("B" + textbox.text[1:].replace("B", ""))

        if len(textbox.text) != 0:
            first_char = textbox.text[0]
            if first_char not in "RB":
                start = "B"

                textbox.cursor_index += 1
                textbox.set_val(start + textbox.text)

            if len(textbox.text) > 1 and textbox.text[1] != "(":
                insertion = "("
                textbox.cursor_index += 1
                textbox.set_val(textbox.text[0] + insertion + textbox.text[1:])

        color = "blue" if "B" in self.point_textbox.text else "red" if "R" in self.point_textbox.text else "white"
        self.point_textbox.update_color(color)
        plt.draw()

    def add_point(self, textbox):
        """
        The input format of the new point is for example:
        B(5.2,4), or B(5,4.2
        or R(-8,2)
        """

        self.currently_writing = False
        string = textbox.text

        try:
            string = string.replace(")", "")
            string = string.replace(" ", "")

            point_state, rest = string.split("(")
            state = poly.INCLUDED if point_state == "B" else poly.EXCLUDED
            first_number, second_number = rest.split(",")
            x = float(first_number)
            y = float(second_number)

            pt = poly.Point(x, y, state)

            plot = self.blue_points_plot if state == poly.INCLUDED else self.red_points_plot
            x = plot.get_xdata() + [pt.x]
            y = plot.get_ydata() + [pt.y]
            plot.set_data([x, y])

            self.points.append(pt)

            if self.auto_save:
                self.save_points(self.save_file)

            self.initialize_polygon()
            self.update_graphics()

        except ValueError:
            print("Wrong point format")

    def mouse_press(self, event):
        # Left click
        if event.button == 1 or event.button == 3:
            if event.inaxes is self.point_textbox.ax:
                self.currently_writing = True
            else:
                self.currently_writing = False

            prop = 1/50

            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()

            x_size = (x_max - x_min) * prop
            y_size = (y_max - y_min) * prop

            pt_radius = max(x_size, y_size)

            mouse_pos = poly.Point(event.xdata, event.ydata)
            if mouse_pos.x and mouse_pos.y:
                clicked_point = interface_utils.get_pressed_point(self.points, pt_radius, mouse_pos)

                if clicked_point is not None:
                    self.draggable_point = clicked_point
                    plot = self.blue_points_plot if clicked_point.state == poly.INCLUDED else self.red_points_plot
                    self.draggable_point_index = interface_utils.get_point_index(clicked_point, plot)
                    if self.draggable_point_index == -1:
                        print("POINT PRESS ERROR")

                    if event.button == 3:
                        self.points.remove(self.draggable_point)
                        if self.auto_save:
                            self.save_points(self.save_file)
                        self.update_points()
                        self.draggable_point = None
                        self.draggable_point_index = None

    def mouse_moved(self, event):
        if self.draggable_point is not None:
            new_pos = event.xdata, event.ydata
            if new_pos[0] and new_pos[1]:
                plot = self.blue_points_plot if self.draggable_point.state == poly.INCLUDED else self.red_points_plot
                interface_utils.modify_point(new_pos, self.draggable_point, self.draggable_point_index, plot)

                self.initialize_polygon()
                plt.draw()

    def mouse_release(self, event):
        if self.auto_save and self.draggable_point is not None:
            self.save_points(self.save_file)

        self.draggable_point = None
        self.draggable_point_index = None

        self.initialize_polygon()

    def key_pressed(self, event):
        if self.currently_writing:
            if event.key == "enter":
                self.add_point(self.point_textbox)
            return

        if event.key == " ":
            self.step()
        elif event.key == "c":
            if self.constraint == MINIMIZE_PERIMETER:
                self.constraint = MINIMIZE_AREA
            else:
                self.constraint = MINIMIZE_PERIMETER
            self.initialize_polygon()
            self.update_graphics()
        elif event.key == "h":
            if self.polygon is not None:
                self.polygon.polygon_patch.set_visible(not self.polygon.polygon_patch.get_visible())
                plt.draw()
        elif event.key == "r":
            if self.reset_mode == RESET_RANDOM or self.current_dataset is None:
                self.set_random_points()
            else:
                self.load_dataset(self.current_dataset)
            self.initialize_polygon()
            self.update_graphics()
        elif event.key == "m":
            self.save_points(self.save_file)
        elif event.key == "c":
            self.remove_all_points()
            self.initialize_polygon()
            self.update_graphics()
        elif event.key == "a":
            self.auto_step = not self.auto_step
        if event.key == "enter":
            self.initialize_polygon()
            self.update_graphics()
        elif event.key == "backspace":
            if self.draggable_point is not None:
                self.points.remove(self.draggable_point)
                self.update_points()

                self.draggable_point = None
                self.draggable_point_index = None

                self.initialize_polygon()
                self.update_graphics()
        elif event.key == "1" or event.key == "2":
            if event.xdata and event.ydata:
                pt = poly.Point(event.xdata, event.ydata)
                if event.key == "1":
                    pt.state = poly.INCLUDED
                    plot = self.blue_points_plot
                else:
                    pt.state = poly.EXCLUDED
                    plot = self.red_points_plot

                self.draggable_point = pt
                self.draggable_point_index = len(plot.get_xdata())
                x = plot.get_xdata() + [pt.x]
                y = plot.get_ydata() + [pt.y]

                plot.set_data([x, y])
                self.points.append(pt)

                self.initialize_polygon()
                self.update_graphics()

    def remove_all_points(self):
        self.points = []
        self.update_points()

    def set_random_points(self):
        self.points = poly_gen.get_random_points(self.seed, self.num_blue, self.num_red)
        self.update_points()

    def load_dataset(self, filepath):
        self.points = interface_utils.load_dataset(filepath)
        self.update_points()

    def save_points(self, filepath, log=True):
        interface_utils.save_points(self.points, filepath)
        if log:
            print(f"Points saved as '{filepath}'.")

    def update_points(self):
        self.draggable_point = None
        self.draggable_point_index = None

        self.blue_points_plot.set_data([[], []])
        self.red_points_plot.set_data([[], []])

        blue_x, blue_y = [], []
        red_x, red_y = [], []
        for pt in self.points:
            if pt.state == poly.INCLUDED:
                blue_x.append(pt.x)
                blue_y.append(pt.y)
            elif pt.state == poly.EXCLUDED:
                red_x.append(pt.x)
                red_y.append(pt.y)

        self.blue_points_plot.set_data([blue_x, blue_y])
        self.red_points_plot.set_data([red_x, red_y])

    def create_polygon(self):
        self.polygon = poly.Polygon()
        self.ax.add_patch(self.polygon.polygon_patch)

    def initialize_polygon(self):
        self.polygon.convex_hull(self.points)
        self.resize_limits()

        if self.auto_step:
            self.step()

    def step(self):
        while True:
            modified = self.polygon.optimize(self.points, update_bounds=False, update_patch=False, constraint=self.constraint)

            if not modified or not self.auto_step:
                break
            elif self.step_delay > 0:
                self.update_graphics()
                plt.pause(self.step_delay)
        self.update_graphics()

    def update_title(self):
        peri = area = 0
        if self.polygon is not None:
            peri = self.polygon.get_perimeter()
            area = self.polygon.get_area()

        if self.reset_mode == RESET_RANDOM or self.current_dataset is None:
            title = f"Seed {self.seed}"
        else:
            title = f"Dataset '{self.current_dataset}'"

        self.ax.set_title(f"{title}\nP: {peri:.3f} u | A: {area:.3f} u^2")

    def update_graphics(self):
        if self.polygon is not None:
            self.polygon.update_patch_polygon()
            self.update_title()
        plt.draw()

    def show(self):
        plt.show()

    def resize_limits(self):
        self.polygon.recalculate_bounds()

        if len(self.polygon.points) >= 3:
            spacing_factor = 1.25
            offset = self.polygon.bounds[0]
            size = max(self.polygon.bounds[1]) / 2
        else:
            offset = [0, 0]
            spacing_factor = 1
            size = 10

        self.ax.set_xlim(
            -size * spacing_factor + offset[0],
            size * spacing_factor + offset[0]
        )
        self.ax.set_ylim(
            -size * spacing_factor + offset[1],
            size * spacing_factor + offset[1]
        )
        self.ax.set_aspect('equal')


interface = PolygonInterface()

interface.current_dataset = "dataset.txt"
interface.load_dataset(interface.current_dataset)
interface.reset_mode = RESET_DATASET
interface.initialize_polygon()
interface.update_graphics()

interface.show()
