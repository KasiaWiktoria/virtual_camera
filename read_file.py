from construction import object_3D

def read_objects_from_file(filename):
    f = open(filename, "r")
    shapes = []
    objects_in_file = f.read().split('vertices')
    for o in objects_in_file:
      if 'edges' in o and 'walls' in o:
        vertices_list = []
        edges_list = []
        walls_list = []
        vertices, e_w = o.split('edges')
        edges, walls = e_w.split('walls')
        vertices = vertices.split('\n')
        edges = edges.split('\n')
        walls = walls.split('\n')
        for v in vertices:
            if ',' in v:
                vertices_list.append([float(coordinate) for coordinate in v.split(',')])
        for e in edges:
            if ',' in e:
                edges_list.append([int(idx) for idx in e.split(',')])
        for w in walls:
            if ',' in w:
                walls_list.append([int(idx) for idx in w.split(',')])
        shape = object_3D(vertices_list, edges_list, walls_list)
        shapes.append(shape)
    return shapes
