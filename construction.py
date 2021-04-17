from functions import get_transformations, project_to_2d, draw_shape
from numpy import array

class object_3D:

    def __init__(self, vertices, edges, walls):
        self.__vertices = array(vertices)
        self.__edges = edges
        self.__walls = walls
        self.__translation = [0, 0, 0]
        self.__rotation = [0, 0, 0]

    def get_lines_2d(self, viewoprt_distance, screen_size):
        after_transformations = get_transformations(self.__vertices, self.__translation, self.__rotation)
        perspective_location = project_to_2d(after_transformations, viewoprt_distance, screen_size)
        return [[perspective_location[v1], perspective_location[v2]] for v1, v2 in self.__edges]

    def rotate(self, axis, angle):
        self.__rotation[axis] += angle
    
    def translate(self, axis, step):
        self.__translation[axis] += step

    def get_vertices(self):
      return self.__vertices

    def get_edges(self):
      return self.__edges

    def get_walls(self):
      return self.__walls


class Construction:

    def __init__(self, objects):
        self.__objects = objects

    def draw(self, viewoprt_distance, screen, screen_size):
        for object in self.__objects:
            draw_shape(object, viewoprt_distance, screen, screen_size)
    
    def rotate(self, axis, angle):
        for object in self.__objects:
            object.rotate(axis,angle)

    def translate(self, axis, step):
        for object in self.__objects:
            object.translate(axis,step)

    def get_objects(self):
      return self.__objects
