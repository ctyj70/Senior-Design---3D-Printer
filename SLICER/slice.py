#!/usr/bin/python3
import numpy as np
from stl import mesh
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import heapq
import sys
import math
from threading import Thread
import os
from tqdm import tqdm

# Global Var for handling threads.
renderPlot = True 

class slice:
    
    #TODO
    # 1) get verticies needs conditionals to deal with duplicates (Already solved?)
    # 2) line calculation
    # 3) dikstras algorithm
    
    def __init__(self, obj:mesh, extrusion_size, step_size):
        self.obj = obj
        self.extrusion_size = extrusion_size # diameter of extrusion beed
        self.step_size = step_size
        self.model = None # all verticies ideally orginized using dikstra but probably will just be bag type thing
        self.layers = [] # printable verticies for each extrusion layer
        self.layer_lines = [] # these lines are used to calculate where a point on the next layer should go
        self.extrusion_paths = []

    def is_in(self, point, verticies):
        for p in verticies:
            if np.array_equal(p, point):
                return True
        return False

    def get_vertices(self):

        print("Building Rough Model")

        verticies = []
        for i in self.obj.v0:
            if not self.is_in(i, verticies):
                verticies.append(i)
        for i in self.obj.v1:
            if not self.is_in(i, verticies):
                verticies.append(i)
        for i in self.obj.v2:
            if not self.is_in(i, verticies):
                verticies.append(i)

        self.model = verticies
        return verticies
    
    # assuming that the bottom of the object will always start at zero
    def gather_bottom_verticies(self, verticies):
        #gather z=0 points
        bottom_verticies = []
        for v in verticies:
            if v[2] == 0.:
                bottom_verticies.append(v)
        return bottom_verticies

    # will only explore points with z=0.0: this is hardcoded, eventually switch
    # to layers or repurpose for the break away layer
    def do_base_layer(self, verticies, step_size):
        bottom_verticies = self.gather_bottom_verticies(verticies)
        #print("Base layer verticies: ", bottom_verticies)
        

    def euclidian_distance(self, p1, p2):
        return np.linalg.norm(np.array(p1)-np.array(p2))
    
    def get_raw_layers(self):  # this is so slow, can be optimized
        # z-axis
        self.raw_layers = []
        zaxis = []

        print("Extracting Raw Layers")
        #pbar = tqdm(total=len(self.model)*2)

        for i in self.model:
            if i[2] not in zaxis:
                zaxis.append(i[2])
            #pbar.update(1)
        zaxis.sort()
        for zlayer in zaxis:
            layer = []
            for p in self.model:
                if p[2] == zlayer:
                    """
                    Will improve in the future
                    tempZAXIS = p[-1:]
                    print("point:")
                    p = np.delete(p, 2)
                    p = np.append(p, round(tempZAXIS[0],1))
                    print(p)
                    """
                    layer.append(p)
            
            self.raw_layers.append(layer)

            #pbar.update(1)
        #pbar.close()

    def get_line_points(self):

        print("Interpolating Vertically Along Raw Layer Points")

        self.layer_lines = []

        for i, layer in enumerate(self.raw_layers):
            for point in layer:
                if i == 0: # bottom layer (look above)
                    closest_point = min(
                        self.raw_layers[i+1], key=lambda x: self.euclidian_distance(x, point)
                        )
                    new_line = (point,closest_point)
                    if not self.is_in(new_line, self.layer_lines) and not self.is_in(new_line[::-1], self.layer_lines):
                        self.layer_lines.append(new_line)
                        print(new_line)
                    
                elif i == len(self.raw_layers)-1: # top layer (look below)
                    closest_point = min(
                        self.raw_layers[i-1], key=lambda x: self.euclidian_distance(x, point)
                        )
                    new_line = (point,closest_point)
                    if not self.is_in(new_line, self.layer_lines) and not self.is_in(new_line[::-1], self.layer_lines):
                        self.layer_lines.append(new_line)
                        print(new_line)

                else: # middle layer (look above and below)
                    closest_point_above = min(
                        self.raw_layers[i+1], key=lambda x: self.euclidian_distance(x, point)
                        )
                    new_line_above = (point,closest_point_above)
                    if not self.is_in(new_line_above, self.layer_lines) and not self.is_in(new_line[::-1], self.layer_lines):
                        self.layer_lines.append(new_line_above)
                        print(new_line)

                    closest_point_below = min(
                        self.raw_layers[i-1], key=lambda x: self.euclidian_distance(x, point)
                        )
                    new_line_below = (point,closest_point_below)
                    if not self.is_in(new_line_below, self.layer_lines) and not self.is_in(new_line[::-1], self.layer_lines):
                        self.layer_lines.append(new_line_below)
                        print(new_line)
        #print(np.array(self.layer_lines).shape)
        
    
    def calculate_extrusion_layers(self):
        height = abs(self.raw_layers[-1][-1][-1])
        self.extrusion_layers = [i for i in np.arange(0, height, self.extrusion_size)]
        """
        for point in self.raw_layers:
            if not point[-1][-1] in self.extrusion_layers:
                tempInt = 0
                while not tempInt > len(self.extrusion_layers) - 1 and point[-1][-1] > self.extrusion_layers[tempInt]: # [!] Fix this loop later
                    tempInt += 1
                    print("test")
                self.extrusion_layers.insert(tempInt, point[-1][-1])
        """
    def normal(point1, point2, point3):
        vector1 = point2 - point1
        vector2 = point3 - point1
        cross_product = np.cross(vector1, vector2)
        normal = cross_product / np.linalg.norm(cross_product)
        return normal
    
    def get_intersections(self):  # returns list of 2D matricies for dikstras

        print("Scanning... Building Extrusion Map")

        intersection_points = []
        for z_plane in self.extrusion_layers:
            plane = []
            for line in self.layer_lines:

                point1 = line[0] 
                point2 = line[1] 
                z = z_plane

                if point1[2] == point2[2]:
                    print("The line is parallel to the z-plane")
                    return None
                
                # Find the point of intersection with the z-plane
                t = -point1[2] / (point2[2] - point1[2])
                x = point1[0] + t * (point2[0] - point1[0])
                y = point1[1] + t * (point2[1] - point1[1])
                plane.append([x, y, z])
            intersection_points.append(plane)
        return intersection_points

    def total_distance(self, points, order):
        return sum(self.euclidian_distance(points[i], points[j]) for i, j in zip(order, order[1:] + [order[0]]))

    # was originally too slow to do
    # this was due to utilizing dijkstra's to check
    # EVERY possible pathing, which is incredibly difficult and tedious.
    # we use a "shallow dijkstra" which sets each point as having 10
    # connections between one another.
    def two_opt(self, points):
        endRange = len(points)
        newPosition = []
        order = list(range(len(points)))
        improvement = False
        #print("Total Size:\n" + str(len(points)))
        for i in range(1, len(points) - 1):
            if (10 > len(points) - (i + 1)):
                endRange = len(points)
            else:
                endRange = i + 10
            for j in range(i + 1, endRange):
                if j - i == 1:
                    continue
                new_order = order[:i] + order[i:j][::-1] + order[j:]
                new_distance = self.total_distance(points, new_order)
                if new_distance < self.total_distance(points, order):
                    order = new_order
                    improvement = True
        #if improvement:
            #print(f"Improved distance: {self.total_distance(points, order)}\n")
        for position in order:
            newPosition.append(points[position])
        return newPosition
    
    def closest_point(self, current_point, points):
        min_dist = float('inf')
        for p in points:
            dist = self.euclidian_distance(current_point, p)
            if dist < min_dist:
                min_dist = dist
                next_hop = p
        return next_hop


    def greedy(self, graph):
        visited = [graph[0]]
        unvisited = graph[1:]
        while unvisited:
            closest = self.closest_point(visited[-1], unvisited)
            visited.append(closest)
            unvisited.remove(closest)
        return visited

    def do_dikstras_on_layers(self):
        #self.show_linesandlayers()
        intersection_points = self.get_intersections()
        #self.show_intersection()
        
        print(rf"Finding Optimal Printing Path: {len(intersection_points)} Total Layers")
        pbar = tqdm(total=len(intersection_points), desc="layer")
        sectionPath = []
        tempSection = []
        previousSection = []
        
        for cross_section in intersection_points:
            #tempSection = cross_section.copy()
            # [!!] make this work with a temp variable
            #print(previousSection)
            #print(tempSection.sort() == previousSection.sort())
            #if not (tempSection.sort() == previousSection.sort() and len(previousSection) > 0):
            sectionPath = self.two_opt(cross_section)
            self.extrusion_paths.append(np.array(sectionPath))
            # print(previousSection == cross_section)
            previousSection = cross_section
            pbar.update(1)
        pbar.close()
        #return np.array(self.extrusion_paths)

    #=====================================================================================================================
  
    def simulate(self):
        global renderPlot
        initalPoint = []
        storedPointX = []
        storedPointY = []
        storedX = 0
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        layer_count = len(self.extrusion_paths)
        pbar = tqdm(total=layer_count, desc="simulation")
        for path in self.extrusion_paths: #layers
            for point in path: #individual points
                # Line Checker
                # [!!] Add some checks here to ensure the lines look
                # a little more broken up
                #"""
                """
                storedZ = point[2]
                if (len(initalPoint) == 0): initalPoint = point
                if (len(storedPointX) == 0):
                    storedPointX.append(point[0])
                    storedPointY.append(point[1])
                elif not (abs(point[0] - storedPointX[-1]) + abs(point[1] - storedPointY[-1]) > 50):
                    storedPointX.append(point[0])
                    storedPointY.append(point[1])
                else:
                    if (len(storedPointX) > 1):
                        ax.plot(storedPointX,storedPointY, storedZ, zdir='z', linestyle = 'solid')
                    
                    ax.scatter(point[0], point[1], point[2])
                    storedPointX = []
                    storedPointY = []
                    storedZ = 0
                    initalPoint = []
                """
                if (len(initalPoint) == 0): initalPoint = point
                storedPointX.append(point[0])
                storedPointY.append(point[1])
                storedZ = point[2]
                #"""
                #ax.scatter(point[0], point[1], point[2])
                plt.draw()
                plt.show(block=False)
            #"""
            
            storedPointX.append(initalPoint[0])
            storedPointY.append(initalPoint[1])
            ax.plot(storedPointX,storedPointY, storedZ, zdir='z', linestyle = 'solid')
            #"""
            pbar.update(1)
            storedPointX = []
            storedPointY = []
            storedZ = 0
            initalPoint = []
            plt.pause(0.1)
        
        pbar.close()
        
    
    def show_model(self, show_mine=True):
        if show_mine:
            x,y,z = [],[],[]
            for i in self.model:
                x.append(i[0])
                y.append(i[1])
                z.append(i[2])
            fig = plt.figure()
            ax = plt.axes(projection='3d')
            #ax.set_box_aspect((np.ptp(x), np.ptp(y), np.ptp(z))) # uncomment for exact proportions
            ax.scatter3D(x,y,z)
            plt.show()
        else:
            # Create a new plot
            figure = plt.figure()
            axes = mplot3d.Axes3D(figure)

            # Load the STL files and add the vectors to the plot
            axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.obj.vectors))

            # Auto scale to the mesh size
            scale = model.points.flatten()
            axes.auto_scale_xyz(scale, scale, scale)

            # Show the plot to the screen
            plt.show()
    
    def show_intersection(self):
        x,y,z = [],[],[]
        for i in self.get_intersections():
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        #ax.set_box_aspect((np.ptp(x), np.ptp(y), np.ptp(z))) # uncomment for exact proportions
        ax.scatter3D(x,y,z)
        plt.show()
    
    def show_linesandlayers(self):
        x,y,z = [],[],[]
        print("Now, layers")
        print(self.layer_lines)
        print(self.extrusion_layers)
        """
        for i in self.extrusion_layers:
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        #ax.set_box_aspect((np.ptp(x), np.ptp(y), np.ptp(z))) # uncomment for exact proportions
        ax.scatter3D(x,y,z)
        plt.show()
        """
    # path is a list of verticies the pen needs to travel between in millimeters
    # assuming that "path" is already orginized in the order the extruder should move
    # Axis: [x, y, z]
    def generate_gcode(self):
        # origin is [0,0,0]
        order_axi = ['X', 'Y', 'Z']
        command_list = []
        for path in self.extrusion_paths:
            for point in path:
                line = "G1 "
                for count, i in enumerate(point):
                    if i != 0:
                        line += rf"{order_axi[count]}{i} "
                command_list.append(line)
        f = open(".\\Finished G-Code\\" + modelName.replace(r'.stl', r'.gcode'), "a")
        for command in command_list:
            print(command)
            f.write((command) + "\n")
        
        
    def main(self):
        self.get_vertices()
        #self.show_model()
        self.get_raw_layers()
        self.get_line_points()
        self.calculate_extrusion_layers()
        self.do_dikstras_on_layers()

        self.generate_gcode()

    def systemWait():
        global renderPlot
    
        print("Simulation Finished!")
        os.system("pause")
        renderPlot = False
        

path = os.getcwd()
modelName = ''
INPUTNAME = 'INPUT STL FILE HERE'
with os.scandir(path) as itr:
    for entry in itr:
        if entry.name == INPUTNAME:
            for filename in os.listdir(path + '\\' + INPUTNAME):
                modelName = filename
if modelName == '':
    print("ERROR -- NO FILE INPUT INTO FOLDER\nINSERT STL FILE IN \"INPUT STL FILE HERE\"")
    os.system("pause")
else:
    model = mesh.Mesh.from_file(os.getcwd() + '\\' + INPUTNAME + '\\' + filename)
    os.replace(path + '\\' + INPUTNAME + '\\' + filename, path + r'\Finished Models\\' + filename)
    slicer = slice(model, 0.5, -1)
    slicer.main()
    print("G-Code Slicing Finished. Simulate G-Code?[Y/N]")
    answer = input()
    if (answer.capitalize() == "Y"):
        slicer.simulate()
        bonusThread = Thread(target=slice.systemWait)
        bonusThread.start()
        while (renderPlot):
            plt.draw()
            plt.show(block=False)
            plt.pause(1)
        plt.close()
        

