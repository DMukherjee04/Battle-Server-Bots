import socket
import json
import pygame
import sys
import math

HOST = "127.0.0.1"
PORT = 5000

WIDTH, HEIGHT = 700, 750
SKY_BLUE =  (120, 180, 255)
MAGENTA = (255, 80, 255)

world_players = {}
world_projectiles = {}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:

    soc.connect((HOST, PORT))

    soc.setblocking(False)

    pygame.init()

    font = pygame.font.Font(None, 20)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BATTLE-ARENA")

    clock = pygame.time.Clock()

    running = True
    buffer = ''
    to_print = []

    max_msg = 3

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

            msg = None

            if recv_obj['type'] == 'STATE':

                world_players = recv_obj['players']
                world_projectiles = recv_obj['projectiles']
                        
            elif recv_obj['type'] == 'JOINED':

               msg = f"id : {recv_obj['id']} joined..."

            elif recv_obj['type'] == 'DEAD':

                msg = f"id : {recv_obj['id']} died..."

            elif recv_obj['type'] == 'LEFT':

                msg = f"id : {recv_obj['id']} left..."

            if msg:
                to_print.append(msg)
                if len(to_print) > max_msg:
                    to_print.pop(0)

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 700))

        for i, msg in enumerate(to_print): 
            text_surface = font.render(msg, True, (0, 0, 0))
            screen.blit(text_surface, (10, 700 + i * 15))

        for key, player in world_players.items():
            x = player['x']
            y = player['y']

            pygame.draw.circle(screen, SKY_BLUE, (x, y), 10)

            label = font.render(key, True, (255, 255, 255))
            label_rect = label.get_rect(center = (x, y - 18))
            screen.blit(label, label_rect)

        for key, projectile in list(world_projectiles.items()): 
            pygame.draw.circle(screen, MAGENTA, (round(projectile['x']), round(projectile['y'])), 5) 

        pygame.display.flip() 

        clock.tick(60)

    soc.close()
    pygame.quit()
    sys.exit()
