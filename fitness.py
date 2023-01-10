import time
from collections import deque
import gpac
import random
import statistics


def manhattan_distance(location0, location1):
    '''calculate the Manhattan distance between two input points'''
    return sum([abs(coord[0] - coord[1]) for coord in zip(list(location0), list(location1))]) # overkill

def parse_map(filename):
    game_map = list()
    with open(filename) as file:
        line = file.readline()
        line = line.rstrip('\n').split(' ')
        width, height = int(line[0]), int(line[1])
        game_map = [[None for y in range(height)] for x in range(width)]
        y = -1
        while line := file.readline():
            for x, char in enumerate(line):
                if char == '~':
                    game_map[x][y] = 0
                elif char == '#':
                    game_map[x][y] = 1
            y -= 1
    return game_map

def play_GPac(pac_controller, ghost_controller=None, game_map=None, **kwargs):
    '''
    Fitness function that plays a game using the provided pac_controller
    with optional ghost controller and game map specifications.

    Returns Pac-Man score from a full game as well as the game log.
    '''

    # default generic game map
    if game_map is None:
        size = 21
        game_map = [[1 for __ in range(size)] for _ in range(size)]
        for i in range(size):
            game_map[0][i] = 0
            game_map[i][0] = 0
            game_map[size//2][i] = 0
            game_map[i][size//2] = 0
            game_map[-1][i] = 0
            game_map[i][-1] = 0
    # parse game map from file
    elif isinstance(game_map, str):
        game_map = parse_map(game_map)
    # assume you've passed an acceptable game map
    else:
        pass
    game = gpac.GPacGame(game_map, **kwargs)
    
    # game loop
    while not game.gameover:
        for player in game.players:
            actions = game.get_actions(player)
            s_primes = game.get_observations(actions, player)
            selected_action_idx = None
            # select ghost actions using provided strategy
            if 'm' not in player:
                if ghost_controller is None:
                    # provided random ghost controller
                    selected_action_idx = random.choice(range(len(actions)))
                else:
                    # 2c TODO: add logic to use ghost controllers in competitive co-evolution
                    pass
            
            # select Pac-Man action(s) using provided strategy 
            else:
                if pac_controller is None:
                    # random pac-man controller for demo purposes
                    selected_action_idx = random.choice(range(len(actions)))
                else:
                    # YOUR 2A CODE GOES HERE###############################################
                    # 2a TODO: score states stored in s_prime
                    pass
                    
                    # 2a TODO: assign index of state with the best score to selected_action_idx
                    pass
                    
                    # YOUR CODE (PROBABLY) ENDS HERE#######################################
            # print(selected_action_idx)
            # print(actions)
            game.register_action(actions[selected_action_idx], player)
        
        game.step()
    return game.score, game.log