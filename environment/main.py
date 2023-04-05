from risk import Risk
from player import RandomPlayer

risk = Risk([RandomPlayer(0, 1), RandomPlayer(1), RandomPlayer(2), RandomPlayer(3), RandomPlayer(4), RandomPlayer(5)], max_turns=500000)
risk.claim_territories()
risk.setup_armies()
risk.play()