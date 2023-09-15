#!/usr/bin/python3
import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import heapq
import math
import os
from tqdm import tqdm

class slice:

    #TODO
    # 1) get verticies needs conditionals to deal with duplicates
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

                point1, point2, z = line[0], line[1], z_plane

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

    # too slow, going with greedy method for now
    def two_opt(self, points):
        order = list(range(len(points)))
        improvement = True
        while improvement:
            improvement = False
            for i in range(1, len(points) - 1):
                for j in range(i + 1, len(points)):
                    if j - i == 1:
                        continue
                    new_order = order[:i] + order[i:j][::-1] + order[j:]
                    new_distance = self.total_distance(points, new_order)
                    if new_distance < self.total_distance(points, order):
                        order = new_order
                        improvement = True
            if improvement:
                pass#print(f"Improved distance: {self.total_distance(points, order)}")
        return order
    
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
            
            
        
        return path

    def do_dikstras_on_layers(self):

        intersection_points = self.get_intersections()

        print(rf"Finding Optimal Printing Path: {len(intersection_points)} Total Layers")
        pbar = tqdm(total=len(intersection_points), desc="layer")

        #[cross_section[p] for p in self.two_opt(cross_section)]
        for cross_section in intersection_points:
            #print(self.greedy(cross_section))
            #print(self.greedy(cross_section))
            self.extrusion_paths.append(np.array(self.greedy(cross_section)))
            pbar.update(1)
        pbar.close()
        #return np.array(self.extrusion_paths)

    #=====================================================================================================================
  
    def simulate(self):

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        layer_count = len(self.extrusion_paths)
        pbar = tqdm(total=layer_count, desc="simulation")
        for path in self.extrusion_paths:
            for point in path:
                ax.scatter(point[0], point[1], point[2])
                plt.draw()
                plt.show(block=False)
            pbar.update(1)
            plt.pause(0.0001)
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
        self.get_raw_layers()
        self.get_line_points()
        self.calculate_extrusion_layers()
        self.do_dikstras_on_layers()

        self.generate_gcode()

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
        print("Simulation Finished!")
        os.system("pause")
