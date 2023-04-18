import cProfile
import numpy as np
from risk import Risk, Phase, ARMIES, OWNER

# risk = Risk([SmartPlayer(0), RandomPlayer(1), RandomPlayer(2), RandomPlayer(3), RandomPlayer(4), RandomPlayer(5)], max_turns=10000)
# risk = Risk([SmartPlayer(0), RandomPlayer(1), RandomPlayer(2)], max_turns=10000)
# risk = Risk([SmartPlayer(0), SmartPlayer(1), SmartPlayer(2), SmartPlayer(3), SmartPlayer(4), SmartPlayer(5)], max_turns=10000)
# risk = Risk([RandomPlayer(0), RandomPlayer(1)], max_turns=10000)
# cProfile.run('risk.play()')

print('Welcome to Risk')
n_players = int(input("n_players: "))
risk = Risk(n_players, True)

print('Generating the map')
risk.random_setup()

while not risk.finished:
    print(f'Turn for Player {risk.current_player}:')
    print(f'Game phase: {risk.phase.name}')
    my_id = risk.current_player
    if risk.phase == Phase.RECRUITMENT:
        moves = risk.get_moves()
        armies = moves[0]
        placement = dict.fromkeys(moves[1], 0)
        for m in moves[1]:
            print(f'{m}. {risk.names[m]}({risk.territories[m, ARMIES]})')
        while armies > 0:
            print(f'{armies} armies to place in...')
            i = int(input('index? '))
            n = min(int(input('n? ')), armies)
            placement[i] += n
            armies -= n
        risk.step(np.array([[v, k] for k,v in placement.items() if v > 0]))
    elif risk.phase == Phase.FIRST_ATTACK:
        moves = risk.get_moves()
        print('Choose an attack to make: ')
        at = -1
        while not at in range(len(moves)):
            print(at)
            for i, m in enumerate(moves):
                print(f'{i}. {risk.names[m[0]]}({risk.territories[m[0], ARMIES]}) -> {risk.names[m[1]]}({risk.territories[m[1], ARMIES]})')
            at = int(input('Attack: '))
        risk.step(moves[at])
    elif risk.phase == Phase.CONTINUE_ATTACK:
        print(f'Attacking {risk.names[risk.frm]}({risk.territories[risk.frm, ARMIES]}) -> {risk.names[risk.to]}({risk.territories[risk.to, ARMIES]})')
        moves = risk.get_moves()
        m = -1
        while m not in [0, 1]:
            m = int(input('Continue your attack? 1: yes, 0: no'))
        m = (m == 1)
        risk.step(m)
    elif risk.phase == Phase.SUBS_ATTACK: #BUG: if there are no valid places to attack we get stuck here
        moves = risk.get_moves()
        at = -1
        while not at in range(len(moves)):
            print(at)
            for i, m in enumerate(moves):
                print(f'{i}. {risk.names[m[0]]}({risk.territories[m[0], ARMIES]}) -> {risk.names[m[1]]}({risk.territories[m[1], ARMIES]})')
            at = int(input('Attack: '))
        risk.step(moves[at])
    elif risk.phase == Phase.REINFORCE_ATTACK:
        print(f'Reinforcing from {risk.names[risk.frm]}({risk.territories[risk.frm, ARMIES]}) -> {risk.names[risk.to]}({risk.territories[risk.to, ARMIES]})')
        moves = risk.get_moves()
        m = -1
        while m not in range(moves + 1):
            m = int(input(f'How many men to reinforce? range: 0-{moves}: '))
        risk.step(m)
    elif risk.phase == Phase.FORTIFY:
        # fuck fortify phase
        moves = risk.get_moves()
        print(moves)
        for i, m in enumerate(moves):
            print(f'{i}. {risk.names[m[0]]}({risk.territories[m[0], ARMIES]}) -> {risk.names[m[1]]}({risk.territories[m[1], ARMIES]})')
        risk.step(None)