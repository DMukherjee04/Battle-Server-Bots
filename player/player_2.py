import socket
import json
import pygame
import sys

HOST = "127.0.0.1"
PORT = 5000

WIDTH, HEIGHT = 700, 700
RED   = (255, 0, 0)

world_players = {}
world_projectiles = {}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:

    soc.connect((HOST, PORT))

    soc.setblocking(False)

    join_obj = {
        'id' : 'abc',
        'type' : 'JOIN'
    }

    soc.sendall((json.dumps(join_obj) + '\n').encode())

    pygame.init()

    font = pygame.font.Font(None, 20)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BATTLE-ARENA")

    clock = pygame.time.Clock()

    running = True
    buffer = ''

    do_fire = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if do_fire:

            attack_obj = {
                'id' : 'xyz',
                'type' : 'ATTACK',
                'directionX' : 1,
                'directionY' : 1
            }

            soc.sendall((json.dumps(attack_obj) + '\n').encode())

            do_fire = False

        try:
            data = soc.recv(1024)

            if not data:
                break
            
        except(BlockingIOError):
            data = b""
        
        buffer += data.decode()

        while '\n' in buffer:

            line, buffer = buffer.split('\n', 1)
            if not line.strip():
                continue
            try:
                recv_obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if recv_obj['type'] == 'WELCOME':
                
                player_pos_x = recv_obj['x']
                player_pos_y = recv_obj['y']
                player_hp = recv_obj['hp']
                rest_of_the_playes = recv_obj['players']

                world_players[recv_obj['id']] = {
                    'x' : player_pos_x,
                    'y' : player_pos_y,
                    'hp' : player_hp
                }

                world_players.update(rest_of_the_playes)

            elif recv_obj['type'] == 'STATE':

                world_players = recv_obj['players']
                world_projectiles = recv_obj['projectiles']

        screen.fill((0, 0, 0))

        for key, player in world_players.items():
            x = player['x']
            y = player['y']

            pygame.draw.circle(screen, RED, (x, y), 10)

            label = font.render(key, True, (255, 255, 255))
            label_rect = label.get_rect(center = (x, y - 18))
            screen.blit(label, label_rect)

        for key, projectile in list(world_projectiles.items()): 
            pygame.draw.circle(screen, RED, (projectile['x'], projectile['y']), 5) 

        pygame.display.flip() 

        clock.tick(60)

    soc.close()
    pygame.quit()
    sys.exit()
