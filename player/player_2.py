import socket
import json
import pygame
import sys

HOST = "127.0.0.1"
PORT = 5000

WIDTH, HEIGHT = 700, 700
RED   = (255, 0, 0)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:

    soc.connect((HOST, PORT))

    join_obj = {
        'id' : 'abc',
        'type' : 'JOIN'
    }

    soc.sendall((json.dumps(join_obj) + '\n').encode())

    data_sent_by_server = json.loads(soc.recv(1024))

    if data_sent_by_server['type'] == 'WELCOME':
        player_pos_x = data_sent_by_server['x']
        player_pos_y = data_sent_by_server['y']

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BATTLE-ARENA")

    pygame.draw.circle(screen, RED, (player_pos_x, player_pos_y), 10) 

    clock = pygame.time.Clock()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player_pos_x += 1 
        player_pos_y += 0

        screen.fill((0, 0, 0))
        pygame.draw.circle(screen, RED, (player_pos_x, player_pos_y), 10) 
        pygame.display.flip()  

        clock.tick(60)

    soc.close()
    pygame.quit()
    sys.exit()



