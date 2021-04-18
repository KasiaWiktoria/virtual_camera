import sys, pygame
from pygame import K_q, K_w, K_a, K_s, K_e, K_d, K_z, K_x, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_PERIOD, K_COMMA
from read_file import read_objects_from_file
from construction import Construction
from define_visibility import *

viewoprt_distance = 500
y_size = 800
x_size = 1200
screen_size = (x_size, y_size)

X, Y, Z = 0, 1, 2
step = 0.5
radian_step = 0.01
zoom_step = 5

filename = "cubes.txt"

rotation_keys = {
    K_q: (X, -radian_step),
    K_a: (X, radian_step),
    K_w: (Y, -radian_step),
    K_s: (Y, radian_step),
    K_e: (Z, -radian_step),
    K_d: (Z, radian_step)
}

move_keys = {
    K_UP: (Y, -step),
    K_DOWN: (Y, step),
    K_RIGHT:(X, step),
    K_LEFT: (X, -step),
    K_PERIOD: (Z, -step),
    K_COMMA: (Z, step)
}

zoom_keys = {
    K_z: zoom_step,
    K_x: -zoom_step
}

pygame.init()
screen = pygame.display.set_mode(screen_size)
shapes = read_objects_from_file(filename)
construction = Construction(shapes)


y = 400
lines = cross_lines(construction, y, viewoprt_distance, screen_size)
v_lines, u_lines = find_visible(construction, y, lines, [], [])
print(v_lines[0])


while True:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)

    pressed = pygame.key.get_pressed()
    for key in move_keys:
        if pressed[key]:
            construction.translate(*move_keys[key])
    for key in rotation_keys:
        if pressed[key]:
            construction.rotate(*rotation_keys[key])
    for key in zoom_keys:
        if pressed[key]:
            viewoprt_distance += zoom_keys[key]
        
    construction.draw_only_visible(viewoprt_distance, screen, screen_size)

    pygame.display.flip()

