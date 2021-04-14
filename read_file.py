from construction import object_3D

def read_objects_from_file(filename):
    f = open(filename, "r")
    shapes = []
    objects_in_file = f.read().split('vertices')
    for o in objects_in_file:
      if 'edges' in o:
        vertices_list = []
        edges_list = []
        vertices, edges = o.split('edges')
        vertices = vertices.split('\n')
        edges = edges.split('\n')
        for v in vertices:
            if ',' in v:
                vertices_list.append([float(coordinate) for coordinate in v.split(',')])
        for e in edges:
            if ',' in e:
                edges_list.append([int(coordinate) for coordinate in e.split(',')])
        shape = object_3D(vertices_list,edges_list)
        shapes.append(shape)
    return shapes
