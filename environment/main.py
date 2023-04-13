import cProfile
import numpy as np
from risk import Risk, Phase

# risk = Risk([SmartPlayer(0), RandomPlayer(1), RandomPlayer(2), RandomPlayer(3), RandomPlayer(4), RandomPlayer(5)], max_turns=10000)
# risk = Risk([SmartPlayer(0), RandomPlayer(1), RandomPlayer(2)], max_turns=10000)
# risk = Risk([SmartPlayer(0), SmartPlayer(1), SmartPlayer(2), SmartPlayer(3), SmartPlayer(4), SmartPlayer(5)], max_turns=10000)
# risk = Risk([RandomPlayer(0), RandomPlayer(1)], max_turns=10000)
# cProfile.run('risk.play()')

print('Welcome to Risk')
n_players = int(input("n_players: "))
risk = Risk(n_players, True)

print('Generating the map')
risk.setup()

while not risk.finished:
    print(f'Turn for Player {risk.current_player}:')
    print(f'Game phase: {risk.phase.name}')
    if risk.phase == Phase.RECRUITMENT:
        moves = risk.get_moves()
        armies = moves[0]
        placement = dict.fromkeys(moves[1], 0)
        for m in moves[1]:
            print(f'{m}. {risk.names[m]}')
        while armies > 0:
            print(f'{armies} armies to place in...')
            i = int(input('index? '))
            n = min(int(input('n? ')), armies)
            placement[i] += n
            armies -= n
        risk.step(np.array([(k,v) for k,v in placement.items()]))
    input("not implemented")