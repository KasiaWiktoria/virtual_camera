from pygame import draw
import numpy as np
from math import cos, sin

def translation_matrix(x,y,z):
    return ((1,0,0,x),
            (0,1,0,y),
            (0,0,1,z),
            (0,0,0,1))

def rotation_matrix(α, β, γ):
    return ((cos(β)*cos(γ),                         -cos(β)*sin(γ),                         sin(β),         0),
            (cos(α)*sin(γ) + sin(α)*sin(β)*cos(γ),  cos(α)*cos(γ) - sin(γ)*sin(α)*sin(β),   -cos(β)*sin(α), 0),
            (sin(γ)*sin(α) - cos(α)*sin(β)*cos(γ),  cos(α)*sin(γ)*sin(β) + sin(α)*cos(γ),   cos(α)*cos(β),  0),
            (0,                                     0,                                      0,              1))

def translate(array_4d, translation_vector):
    result = []
    for v in array_4d:
        translate_point = np.matmul(translation_matrix(*translation_vector), v)
        result.append(translate_point)
    return result

def rotate(array_4d, rotation_vector):
    result = []
    for v in array_4d:
        rotate_point = np.matmul(rotation_matrix(*rotation_vector), v)
        result.append(rotate_point)
    return result


def move_to_center(point, screen_size):
    return [round(coordinates + frame / 2) for coordinates, frame in zip(point, screen_size)]

def transform_to_4d_array(array_3d):
    l = len(array_3d)
    return np.concatenate((array_3d, np.ones([l, 1])), axis=1)


def project_to_2d(points_3d, viewoprt_distance, screen_size):
    points_2d = []
    for point in points_3d:
        d = 1/viewoprt_distance
        projection_matrix = np.array(  [[1,0,0,0],
                                        [0,1,0,0],
                                        [0,0,1,0],
                                        [0,0,d,0]])
        point_2d = np.matmul(projection_matrix, point)

        z = point_2d[2]
        if z > 1:
            normalize_point_2d = point_2d * viewoprt_distance / z
        else:
            normalize_point_2d = point_2d * viewoprt_distance**2
        
        normalize_point_2d *= -1
        center_point = move_to_center(normalize_point_2d[:2], screen_size)
        points_2d.append(center_point)
    return points_2d

def get_transformations(vertices, translation, rotation):
    array_4d = transform_to_4d_array(vertices)
    after_translation = translate(array_4d, translation)
    after_rotation = rotate(after_translation, rotation)
    return after_rotation

def draw_shape(shape, viewoprt_distance, screen, screen_size, thickness=1, color=(255, 255, 255)):
    for p1, p2 in shape.get_lines_2d(viewoprt_distance, screen_size):
        draw.line(screen, color, p1, p2, thickness)

def find_min_max_area(construction):
    x_min = 999999999
    y_min = 999999999
    x_max = -9999999999
    y_max = -9999999999

    for shape in construction.get_objects():
        #for x in shape.vertices[:][0]
        tmp_x_min = min(shape.get_vertices()[:,[0]])[0]
        tmp_x_max = max(shape.get_vertices()[:,[0]])[0]
        tmp_y_min = min(shape.get_vertices()[:,[1]])[0]
        tmp_y_max = max(shape.get_vertices()[:,[1]])[0]
        if tmp_x_min < x_min:
          x_min = tmp_x_min
        if tmp_x_max > x_max:
          x_max = tmp_x_max
        if tmp_y_min < y_min:
          y_min = tmp_y_min
        if tmp_y_max > y_max:
          y_max = tmp_y_max
        
    return (x_min,x_max), (y_min,y_max)

def get_straight(x1,y1,x2,y2):
    a = (y2 - y1)/(x2 - x1)
    b = y1 - a * x1
    return (a,b)
