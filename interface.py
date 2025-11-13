import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

import polygon as poly
import polygon_generator as poly_gen
import polygon_optimization as poly_optim
import interface_utilities as interface_utils

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
        self.seed = None

        self.points = []
        self.polygon = None

        self.draggable_point = None
        self.draggable_point_index = None

        self.auto_step = True
        self.step_delay = 0.01

        self.fig = plt.figure(facecolor="#101010")
        self.ax = self.fig.add_subplot(111, facecolor='#050505')

        self.blue_points_plot, = self.ax.plot([], [], 'o', color='blue')
        self.red_points_plot, = self.ax.plot([], [], 'o', color='red')

        self.initialize_communication()

        self.buttons = []
        self.setup_buttons()

        self.num_blue, self.num_red = 25, 25
        self.set_random_points()

        self.create_polygon()
        self.initialize_polygon()

    def initialize_communication(self):
        self.fig.canvas.mpl_connect('key_press_event', self.key_pressed)
        self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_moved)
        self.fig.canvas.mpl_connect('button_press_event', self.mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.mouse_release)

    def setup_buttons(self):
        self.fig.subplots_adjust(bottom=0.2)

        step_ax = self.fig.add_axes([0.7, 0.05, 0.1, 0.075])
        step_button = Button(step_ax, "Step")
        step_button.on_clicked(lambda event: self.step())
        interface_utils.customize_button(step_button, mpl.rcParams)

        self.buttons.append(step_button)

    def mouse_press(self, event):
        # Left click
        if event.button == 1:
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

    def mouse_moved(self, event):
        if self.draggable_point is not None:
            if event.button == 1:
                new_pos = event.xdata, event.ydata
                if new_pos[0] and new_pos[1]:
                    plot = self.blue_points_plot if self.draggable_point.state == poly.INCLUDED else self.red_points_plot
                    interface_utils.modify_point(new_pos, self.draggable_point, self.draggable_point_index, plot)
                    plt.draw()

    def mouse_release(self, event):
        self.draggable_point = None
        self.draggable_point_index = None

        self.initialize_polygon()

    def key_pressed(self, event):
        if event.key == " ":
            self.step()
        elif event.key == "r":
            self.set_random_points()
            self.initialize_polygon()
            self.update_graphics()
        elif event.key == "1":
            if event.xdata and event.ydata:
                pt = poly.Point(event.xdata, event.ydata)
                pt.state = poly.INCLUDED
                self.draggable_point = pt
                self.draggable_point_index = len(self.blue_points_plot.get_xdata())
                x = self.blue_points_plot.get_xdata() + [pt.x]
                y = self.blue_points_plot.get_ydata() + [pt.y]
                self.blue_points_plot.set_data([[x], [y]])
                plt.draw()

    def set_random_points(self):
        self.points = poly_gen.get_random_points(self.seed, self.num_blue, self.num_red)
        self.update_points()

    def update_points(self):
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
            modified = self.polygon.optimize(self.points, update_bounds=False, update_patch=False)
            self.update_graphics()

            if not modified or not self.auto_step:
                break
            else:
                plt.pause(self.step_delay)

    def update_graphics(self):
        self.polygon.update_patch_polygon()
        plt.draw()

    def show(self):
        plt.show()

    def resize_limits(self):
        self.polygon.recalculate_bounds()

        spacing_factor = 1.25
        offset = self.polygon.bounds[0]
        size = max(self.polygon.bounds[1]) / 2

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

interface.show()
interface.update_graphics()
