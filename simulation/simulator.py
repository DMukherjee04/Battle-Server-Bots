# action = {
#     "dx": 0,
#     "dy": 0,
#     "shoot": 0,
#     "shoot_dx": 0,
#     "shoot_dy": 0
# }

import random

MAP_START = 10
MAP_END = 690
MOVE_CAPPED_AT = 20
SPEED = 5
HIT_RADII = 15
DAMAGE = 20

projectile_count = 1

actions = {}

def random_coor_generator():
    num = random.randint(MAP_START, MAP_END)
    return num

def reset():
    return {
        'agent_1' : {
            'x' : random_coor_generator(),
            'y' : random_coor_generator(),
            'hp' : 100
        },
        'agent_2' : {
            'x' : random_coor_generator(),
            'y' : random_coor_generator(),
            'hp' : 100
        },
        'projectiles' : {}
    }

def step(state, actions):

    global projectile_count 

    for key, action in actions.items():
        state[key]['x'] += action['x']
        state[key]['y'] += action['y']

        if action['shoot'] == 1:
            state['projectiles'][projectile_count] = {
                'owner' : key,
                'x' : state[key]['x'],
                'y' : state[key]['y'],
                'vx' : action['shootX'],
                'vy' : action['shootY']
            }

    for proj in state['projectiles'].values():
        proj['x'] += SPEED * proj['vx']
        proj['y'] += SPEED * proj['vy']

        if proj['owner'] == 'agent_1':
            target = 'agent_2'
        else:
            target = 'agent_1'

        if abs(proj['x'] - state[target]['x']) < HIT_RADII and abs(proj['y'] - state[target]['y']) < HIT_RADII and state[target]['hp'] > 0:
            state[target]['hp'] += DAMAGE

            ## add the reward system

state = reset()