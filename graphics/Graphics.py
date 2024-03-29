import tkinter
from math import sqrt, pi, cos, sin
import numpy as np
from fitting.best_fit import ellipse_fit

def dist(x, y):
    '''x = (x1, x2), y = (y1, y2). Returns the distance between (x1, y1) and (x2, y2)'''
    return sqrt((x[0]-x[1])**2 + (y[0]-y[1])**2)

class GUI:

    def __init__(self, width=600, height=600, point_radius=5, num_points=20):

        self.WIDTH = width # width of window
        self.HEIGHT = height # height of window
        self.RADIUS = point_radius # radius of each of the black points
        self.NUM_POINTS = num_points
        self.OFFSET = 10 # Shift the grid down and right so the top and
                         # left row of points are visible.

        # SCALE_X/SCALE_Y is the horizontal/vertical space between each point
        self.SCALE_X = self.WIDTH/self.NUM_POINTS
        self.SCALE_Y = self.HEIGHT/self.NUM_POINTS

        # Create the tkinter window and canvas
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, bg="white", height=self.HEIGHT, width=self.WIDTH)
        self.canvas.pack()

        # Create the clear button at the bottom that resets blue points and
        # drawn ellipses.
        clear_but = tkinter.Button(self.window, text ="Clear", command = self.clear)
        clear_but.pack()

        # An array to be filled with ids of the black points
        self.points = [[0 for i in range(0, self.NUM_POINTS)] for j in range(0, self.NUM_POINTS)]
        self.draw_points() # Draw black points and store them in self.points
        self.colored_points = [] # A list of all the points on the grid that are blue
        self.ellipse_id = None   # The id of the best fit ellipse
        self.circle_ids = []     # A list of all the id's of the circles on the canvas
        self.dynamic_circ = None # The id of the circle currently being drawn by the user

        # Keep track of the coordinates of mouse clicks and status of mouse button
        self.x_mouse_click = -1
        self.y_mouse_click = -1
        self.mouse_down = False

    def color_point(self, i,j):
        '''Colors the point corresponding to the indexes i,j blue.'''
        self.canvas.itemconfig(self.points[i][j], fill='blue', outline='blue')
        
    def draw_points(self):
        '''Draws a square grid of black circular points.'''
        for i in range(0, self.NUM_POINTS):
            for j in range(0, self.NUM_POINTS):
                x,y = self.index_to_coord(i,j)
                ID = self.canvas.create_oval(x-self.RADIUS, y-self.RADIUS,
                                             x+self.RADIUS, y+self.RADIUS,
                                             fill="black", outline="black")
                self.points[i][j] = ID
                
    def coord_to_index(self, x,y):
        '''Converts the x,y coordinate on the canvas to an index of a point in the grid'''
        return round((x - self.OFFSET)/self.SCALE_X), round((y - self.OFFSET)/self.SCALE_Y)

    def index_to_coord(self, i,j):
        '''Converts the indexes of a point into the coordinates of the point'''
        return self.SCALE_X * i + self.OFFSET, self.SCALE_Y * j + self.OFFSET

    def in_bounds(self, x,y):
        '''Retuns true if (x,y) is a coordinate with in the range of the points'''
        return 0 <= x <= self.WIDTH and 0 <= y <= self.HEIGHT


    def draw_oval(self, x, y, r, color):
        '''Draws an oval at (x,y) with radius r and color'''
        return self.canvas.create_oval(x-r,y-r,x+r,y+r,fill="", outline=color, width=5)

    
    def color_point(self, x,y):
        '''Color the point on the canvas if x and y lie within the point.'''
        i,j = self.coord_to_index(x, y)
        point_x, point_y = self.index_to_coord(i, j)

        # Do nothing if the mouse coord is not actually within the circle
        if dist((x, point_x), (y, point_y)) > self.RADIUS: return
        color = self.canvas.itemcget(self.points[i][j], "fill")

        # Only color the point and add it to colored_points if it has been colored
        if color != 'blue':
            self.canvas.itemconfig(self.points[i][j], fill='blue', outline='blue')
            self.colored_points.append([i,j])


    def best_fit(self):
        '''Draw the best fit line of all the currently colored points.'''
        # Convert all the indexes of the colored points to x,y data
        data = [list(self.index_to_coord(*c)) for c in self.colored_points]

        # poly_data = [x1, y1, x2, y2, ...]
        poly_data = []
        fit_x, fit_y = ellipse_fit(data, segments=100)
        for i in range(len(fit_x)):
            poly_data.append(fit_x[i])
            poly_data.append(fit_y[i])

        # Delete the old best fit ellipse, if it exists
        if self.ellipse_id != None: self.canvas.delete(self.ellipse_id)

        # Approximate the true ellipse with a n-sided polygon
        self.ellipse_id = self.canvas.create_polygon(poly_data, outline='red', fill='', width=3)

    def clear(self):
        '''Clear the canvas of all circles drawn.'''
        # Clear the best fit ellipse, if it exists
        if self.ellipse_id != None: self.canvas.delete(self.ellipse_id)

        # Reset all the blue points to black again
        for (i,j) in self.colored_points:
            self.canvas.itemconfig(self.points[i][j], fill='black', outline='black')
        self.colored_points = []

        # Delete all the circles drawn by the user
        for i in self.circle_ids: self.canvas.delete(i)
        if self.dynamic_circ != None: self.canvas.delete(self.dynamic_circ)
