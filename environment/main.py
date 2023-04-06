import cProfile
from risk import Risk
from player import RandomPlayer, SmartPlayer

# risk = Risk([SmartPlayer(0), RandomPlayer(1), RandomPlayer(2), RandomPlayer(3), RandomPlayer(4), RandomPlayer(5)], max_turns=10000)
# risk = Risk([SmartPlayer(0), RandomPlayer(1), RandomPlayer(2)], max_turns=10000)
risk = Risk([SmartPlayer(0), SmartPlayer(1), SmartPlayer(2), SmartPlayer(3), SmartPlayer(4), SmartPlayer(5)], max_turns=10000)
# risk = Risk([RandomPlayer(0), RandomPlayer(1)], max_turns=10000)

cProfile.run('risk.play()')