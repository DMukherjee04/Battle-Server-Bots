import socket 
import asyncio
import json
import random
import math

HOST = "127.0.0.1"
PORT = 5000

MAP_START = 10
MAP_END = 690

SHOOT_CD = 5
HIT_RADII = 15
DAMAGE = 20 
MOVE_CAPPED_AT = 20 ## how much player can move per tick is also capped at 20
SPEED = 5

players = {}
inputs = {}
projectiles = {}
connections = set()

projectile_count = 1

tick_count = 1

def random_coor_generator():
    num = random.randint(MAP_START, MAP_END)
    return num

async def broadcast(data, exclude = None):

    connections_to_discard = []

    loop = asyncio.get_running_loop()
    
    for connection_soc in connections:
        if connection_soc is not exclude:
            try: 
                await loop.sock_sendall(connection_soc,((json.dumps(data)) + '\n').encode())
            except(ConnectionResetError, BrokenPipeError, OSError):
                connections_to_discard.append(connection_soc)

    for connection_soc in connections_to_discard:
        connections.discard(connection_soc)

def all_players(exclude = None):    

    all_players = {}

    for key in players.keys():
        if key != exclude:
            all_players[f"{key}"] = players[f"{key}"]
    return all_players

def projectile_handling(): 

    proj_to_pop = []
    dead_players = []
    for key_proj, proj in list(projectiles.items()):

        if proj['owner'] in players:

            proj['x'] += proj['vx'] 
            proj['y'] += proj['vy']

            if proj['x'] > MAP_END or proj['y'] > MAP_END or proj['x'] < MAP_START or proj['y'] < MAP_START:
                    proj_to_pop.append(key_proj)
                    continue
    
            for key_player, player in list(players.items()): ## hitbox proper definition : done
                dx = player['x'] - proj['x']
                dy = player['y'] - proj['y']
                if dx * dx + dy * dy <= HIT_RADII * HIT_RADII and key_player != proj['owner'] and player['hp'] > 0: ## hitbox
                    player['hp'] = max(0, player['hp'] - DAMAGE) 
                    if player['hp'] <= 0:
                        dead_players.append(key_player)  
                    proj_to_pop.append(key_proj)
                    break
        else:

            proj_to_pop.append(key_proj)

    for key_player_to_pop in dead_players:
        if key_player_to_pop is not None:
            players.pop(key_player_to_pop, None)
            print(f"player : {key_player_to_pop} died...")
            asyncio.create_task(broadcast({ ## broadcasting an event is handled seperately
                'type' : 'DEAD',
                'id' : key_player_to_pop
            }))

    for key_proj_to_pop in proj_to_pop:
        projectiles.pop(key_proj_to_pop, None)
        print(f"projectile {key_proj_to_pop} removed...")

def update_world_state(): ## to update world state
    
    global projectile_count

    for key, player in list(players.items()):
        player['shoot_cd'] = max(0, player['shoot_cd'] - 1)
        
    for key, cmd in list(inputs.items()):

        if cmd['type'] == 'MOVE': ## handling MOVE

            dx = max((-1) * MOVE_CAPPED_AT, min(MOVE_CAPPED_AT, cmd['dx']))
            dy = max((-1) * MOVE_CAPPED_AT, min(MOVE_CAPPED_AT, cmd['dy']))

            if key in players:

                players[key]['x'] += dx
                players[key]['y'] += dy

                players[key]['x'] = max(MAP_START, min(MAP_END, players[key]['x']))
                players[key]['y'] = max(MAP_START, min(MAP_END, players[key]['y']))

        elif cmd['type'] == 'ATTACK' and players[key]['shoot_cd'] <= 0: ## handling ATTACK

            shoot_dir_x = cmd['direction'][0]
            shoot_dir_y = cmd['direction'][1]
            shoot_dir_mag = math.sqrt(shoot_dir_x * shoot_dir_x + shoot_dir_y * shoot_dir_y)
            if shoot_dir_mag > 0:
                shoot_dir_x /= shoot_dir_mag
                shoot_dir_y /= shoot_dir_mag

            if key in players:

                projectiles[projectile_count] = {
                    'owner' : key,
                    'x' : players[key]['x'],
                    'y' : players[key]['y'],
                    'vx' : SPEED * shoot_dir_x, ## think of it like vector, dx -> units in i cap, speed * dx -> velocity
                    'vy' : SPEED * shoot_dir_y
                }
                projectile_count += 1
                players[key]['shoot_cd'] = SHOOT_CD

    projectile_handling()

    world_state = {
        'type' : 'STATE',
        'players' : dict(players),
        'projectiles' : dict(projectiles)
    }
    
    inputs.clear()
    asyncio.create_task(broadcast(world_state)) 

async def server_tick_loop(): ## tick loop fnc

    global tick_count
    
    while True:
        print(tick_count) ## to see if ticks are working properly
        update_world_state()
        tick_count += 1
        await asyncio.sleep(0.033)

async def client_handling(conn):

    conn.setblocking(False)

    loop = asyncio.get_running_loop()
    buffer = ''
    player_id = None

    while True:

        try:
            data = await loop.sock_recv(conn, 1024)
        except(ConnectionResetError, BrokenPipeError, OSError):
            break
        
        buffer += data.decode()

        while '\n' in buffer:

            line, buffer = buffer.split('\n', 1)
            if not line.strip():
                continue
            recv_obj = json.loads(line)

            if recv_obj['type'] == 'JOIN' :

                player_id = recv_obj['id']

                sent_obj_to_joinee = { ## to the player who joined
                    'type': 'WELCOME',
                    'id': recv_obj['id'],
                    'x' : random_coor_generator(),
                    'y' : random_coor_generator(),
                    'hp' : 100,
                    'players' : all_players(recv_obj['id'])
                }

                joinee_pos_x = sent_obj_to_joinee['x']
                joinee_pos_y = sent_obj_to_joinee['y']

                players[f"{recv_obj['id']}"] = { ## updating players obj
                    'x' : joinee_pos_x,
                    'y' : joinee_pos_y,
                    'hp' : 100, 
                    'shoot_cd' : 0
                }

                joined_player_info = { ## to all the other players, letting them know who joined 
                    'type': 'JOINED',                    
                    'id' : recv_obj['id'],
                    'x' : joinee_pos_x,
                    'y' : joinee_pos_y,
                    'hp' : 100
                }

                asyncio.create_task(broadcast(joined_player_info, conn)) ## broadcast who joined

                try:
                    await loop.sock_sendall(conn,((json.dumps(sent_obj_to_joinee)) + '\n').encode())
                except(ConnectionResetError, BrokenPipeError, OSError):
                    break
                
            elif recv_obj['type'] == 'ATTACK' : 

                inputs[player_id] = {
                    'type' : 'ATTACK',
                    'direction' : (recv_obj['directionX'], recv_obj['directionY']),
                }

            elif recv_obj['type'] == 'MOVE' : 

                inputs[player_id] = {
                    'type' : 'MOVE',
                    'dx' : recv_obj['dx'],
                    'dy' : recv_obj['dy']
                }

    players.pop(player_id, None)
    leave_obj = {
        'id' : player_id,
        'type' : 'LEFT'
    }
    print(f"player : {leave_obj['id']} left...")
    asyncio.create_task(broadcast(leave_obj, conn)) ## broadcast leave to all players other than that player
    connections.discard(conn)
    conn.close()

async def main(s):

    s.setblocking(False)
    s.listen()
    loop = asyncio.get_running_loop()

    asyncio.create_task(server_tick_loop()) ## loop will go on

    while True:

        conn, addr = await loop.sock_accept(s)
        print(f"Connected by {addr}")
        connections.add(conn)
        asyncio.create_task(client_handling(conn))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_soc:
    
    server_soc.bind((HOST, PORT))
    asyncio.run(main(server_soc))
