from pygame import draw
import numpy as np
from math import cos, sin
from functools import reduce


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
    for line in shape.get_lines_2d(viewoprt_distance, screen_size):
        p1 = line[0]
        p2 = line[1]
        draw.line(screen, color, p1, p2, thickness)

def find_min_max_area(construction):
    x_min = 999999999
    y_min = 999999999
    x_max = -9999999999
    y_max = -9999999999

    for shape in construction.get_objects():
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

def get_straight(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]

    A = y1-y2
    B = x2-x1
    C = (y2 - y1)*x1 - (x2 - x1)*y1

    return A, B, C

def get_x(y, p1,p2):
    A, B, C = get_straight(p1,p2)
    x = - (B * y + C) /A
    return x

def get_z (y, p1, p2):
    x1, y1, z1 = [c for c in p1]
    x2, y2, z2 = [c for c in p2]

    z = z1 + (y-y1)/(y2-y1)*(z2-z1)
    return z


def distance_from_camera(x,y,z):
    return sqrt(x**2 + y**2 + z**2)

def get_point_ids(shape, edge_id):
    return shape.get_edges()[edge_id]

def find_coordinates(shape, p1_id, p2_id):
    p1 = shape.get_vertices()[p1_id]
    p2 = shape.get_vertices()[p2_id]
    return p1, p2

def find_polygons(shape, p1_id, p2_id):
    walls = shape.get_walls()
    polygons = []

    for wall_id, wall in enumerate(walls):
        if p1_id in wall and p2_id in wall:
            polygons.append(wall_id)

    return polygons

def cross_lines(construction, y, viewoprt_distance, screen_size):
    cross_lines = []

    for shape_id, shape in enumerate(construction.get_objects()):
        lines = list(shape.get_lines_2d(viewoprt_distance, screen_size))
        for edge_id, line in enumerate(lines):
            if (y > line[0][1] and y < line[1][1]) or (y > line[1][1] and y < line[0][1]):
                p1_id, p2_id = get_point_ids(shape, edge_id)

                line_dict = {}
                line_dict['shape_id'] = shape_id
                line_dict['polygons'] = find_polygons(shape, p1_id, p2_id)
                line_dict['3d_coordinates'] = list(find_coordinates(shape, p1_id, p2_id))
                line_dict['2d_coordinates'] = line
                cross_lines.append(line_dict)
    return cross_lines

def find_visible_lines(y, lines, construction):
    visible_lines = []

    closest_line = find_closest_line(y, lines)
    print(f'closest_line: {closest_line}')
    visible_lines.append(closest_line)
    lines.remove(closest_line)
    
    l_end = find_polygon_end(construction, y, closest_line, lines)
    if l_end is None:
            print('1. Koniec bryły poza krawędzią ekranu!')
    lines_to_remove, cover_lines = lines_between_edges(y, closest_line, l_end, lines)
    lines.remove(l_end)
    for l_r in lines_to_remove:
            lines.remove(l_r)
    
    if cover_lines == []:
        visible_lines.append(l_end)
    else:
        l = find_closest_line(y, cover_lines)
        l_end = find_polygon_end(construction, y, l, lines)

        lines_to_remove, cover_lines = lines_between_edges(y, l, l_end, lines)
        lines.remove(l_end)
        for l_r in lines_to_remove:
                lines.remove(l_r)

        if l_end is None:
            print('2. Koniec bryły poza krawędzią ekranu!')
            # screen_edge = 
            # lines_to_remove, cover_lines = lines_between_edges(y, l_end, screen_edge, lines)
            # lines.remove(lines_to_remove)
    
        



    cover_lines = [closest_line]
    counter = 0
    
    while cover_lines != []:
        counter += 1
        l = find_closest_line(y, cover_lines)
        l_end = find_polygon_end(construction, y, l, lines)
        print(counter)
        if l_end is None:
            print('Koniec bryły poza krawędzią ekranu!')
        visible_lines.append(l)
        lines.remove(l)
        lines_to_remove, cover_lines = lines_between_edges(y, l, l_end, lines)
        for l_r in lines_to_remove:
            lines.remove(l_r)
    
    visible_lines.append(l_end)
    lines.remove(l_end)

    if lines != []:
        [visible_lines.append(v_l) for v_l in find_visible_lines(y, lines, construction)]
    
    return visible_lines


#------------------------------
def find_visible(construction, y, all_lines, visible_lines, unvisible_lines):
    lines_to_check = lists_diff(lists_diff(all_lines, visible_lines), unvisible_lines)

    closest_line = find_closest_line(y, lines_to_check)
    visible_lines.append(closest_line)
    lines_to_check.remove(closest_line)
    
    l_end = find_polygon_end(construction, y, closest_line, all_lines)

    if l_end is None:
            print('1. Koniec bryły poza krawędzią ekranu!')
    lines_to_remove, cover_lines = lines_between_edges(y, closest_line, l_end, lines_to_check)
    if l_end in lines_to_check:
        lines_to_check.remove(l_end)
    for l_r in lines_to_remove:
        lines_to_check.remove(l_r)
        unvisible_lines.append(l_r)
    
    if cover_lines == []:
        visible_lines.append(l_end)
    else:
        v_lines, unv_lines = find_visible(construction, y, all_lines, visible_lines, unvisible_lines)
        visible_lines += v_lines
        unvisible_lines += unv_lines

    return visible_lines, unvisible_lines


#------------------------------

def lists_diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def find_polygon_end(construction, y, line, lines):
    polygons = line['polygons']
    shape = construction.get_objects()[line['shape_id']]
    polygons_coordinates = []
    for p in polygons:
        polygons_coordinates.append(coordinates_for_polygon_vertices(shape, p))

    adjacent_lines = find_adjacent_lines(polygons_coordinates, lines)

    return find_closest_line(y, adjacent_lines)

def lines_between_edges(y, l1, l2, lines):
    lines_to_remove = []
    cover_lines = []

    x1 = get_x(y, l1['2d_coordinates'][0], l1['2d_coordinates'][1])
    x2 = get_x(y, l2['2d_coordinates'][0], l2['2d_coordinates'][1])
    z2 = get_z(y, l2['3d_coordinates'][0], l2['3d_coordinates'][1])
    
    for line in lines:
        x = get_x(y, line['2d_coordinates'][0], line['2d_coordinates'][1])
        z = get_z(y, line['3d_coordinates'][0], line['3d_coordinates'][1])
        if x > x1 and x < x2 or x > x2 and x < x1:
            if z > z2:
                lines_to_remove.append(line)
            else:
                cover_lines.append(line)
    return lines_to_remove, cover_lines


def coordinates_for_polygon_vertices(shape, polygon):
    polygon_vertices_coordinates = []
    polygon_points_isd = shape.get_walls()[polygon]

    for p_id in polygon_points_isd:
        polygon_vertices_coordinates.append(shape.get_vertices()[p_id])
    
    return polygon_vertices_coordinates


def find_adjacent_lines(polygons_coordinates, lines):
    adjacent_lines = []
    for line in lines:
        for polygon_coordinates in polygons_coordinates:
            if line_belong_to_polygon(line['3d_coordinates'], polygon_coordinates):
                adjacent_lines.append(line)
                #print(f'polygon edge: {line}')
    
    return adjacent_lines

def line_belong_to_polygon(line_coordinates, polygon_coordinates):
    
    points_cmp = False
    for vertice in polygon_coordinates:
        points_cmp = reduce(lambda i, j : i and j, map(lambda m, k: m == k, line_coordinates[0], vertice), True)
        #print(f'wynik porównania: {points_cmp}')
        if points_cmp:
            for vertice in polygon_coordinates:
                points_cmp = reduce(lambda i, j : i and j, map(lambda m, k: m == k, line_coordinates[1], vertice), True)
                if points_cmp:
                    #print(f'WSPÓŁRZĘDNA OK--- współrzędne lini: {vertice}, współrzędne wielokąta: {polygon_coordinates}')
                    return True


def find_closest_line(y, lines):
    z_min = 9999999999999
    closest_line = None
    len_lines = len(lines)

    for i, line in enumerate(lines):
        z = get_z(y, line['3d_coordinates'][0], line['3d_coordinates'][1])

        if z < z_min:
            z_min = z
            closest_line = line
        if i == len_lines - 1:
            return closest_line


# def find_left_line(y, lines):
#     x_min = 9999999999999

#     for line in lines:
#         x = get_x(y, line[1])
#         if x < x_min:
#             x_min = x
#             max_left_line = line
    
#     return max_left_line

# def find_visible_lines(lines, construction):
#     dv1 = 999999999999
#     dv2 = 999999999999

#     for p1, p2, line in lines:
#         d1 = distance_from_camera(p1)
#         d2 = distance_from_camera(p2)

#         if d1 > dv1 and d2 > dv1 and d1 > dv2 and d2 > dv2:
#             visible_line = line
#     return visible_line
