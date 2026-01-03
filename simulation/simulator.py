import random

MOVE_CAPPED_AT = 20
MAP_START = 10
MAP_END = 690

projectile_count = 1

actions = {}

def random_coor_generator():
    num = random.randint(MAP_START, MAP_END)
    return num

def reset():
    return {
        'player' : {
            'x' : random_coor_generator(),
            'y' : random_coor_generator(),
            'hp' : 100
        },
        'enemy' : {
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

    ## write whatever is not controlled by actions

state = reset()


