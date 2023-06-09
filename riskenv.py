import gymnasium as gym
from gymnasium.spaces import Dict, Discrete, MultiDiscrete, Graph, Box
from riskstate import *
from maps import default_map, default_names
from visualize import ImageLocations, IMG_DIR, TextBoxLocation, TextRect
import numpy as np 
import random
import pygame
import os

class RiskEnv(gym.Env):
    """Custom Environment that follows gym interface."""
    # metadata = {"render.modes": ["human"], "render_fps": 60}

    def __init__(self, n_players=2, random_players = False, randomizedSetUp = False):
        super().__init__()

        self.risk = new_game(n_players, randomizedSetUp=randomizedSetUp)

        self.observation_unit_max = 10
        self.n_players = n_players

        self.colors = {}
        if n_players == 2:
            self.colors[0] = ( 255, 0, 0, 100 )
            self.colors[1] = ( 0, 255, 0, 100 )
        else:
            for i in range(n_players):
                self.colors[i] = ( random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 100 )
        self.colors[-1] = ( 128, 128, 128, 100 )

        self.random_players = random_players
        self.randomizedSetUp = randomizedSetUp

        n_territories = self.risk.n_territories()
        self.n_phases = len(Phases)
        self.MAX_ARMIES = 30
        self.last_action = None

        self.action_space = Discrete( n_territories + 1 )


        self.observation_space = Dict( {
            "Phase": Discrete(self.n_phases),
            "Owners":  MultiDiscrete(np.full((n_territories,), 2)),
            "Armies":  MultiDiscrete(np.full((n_territories,), self.MAX_ARMIES)),
            "ValidMoves":  MultiDiscrete(np.full((n_territories,), 2)),
        } )
        # self.observation_space = MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))

        self.render_mode = "human"
        self.window = None
        self.fps = 60

        self.invalid_moves = 0
    
    def _init_render(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 12)
        self.images = {}
        self.rects = {}
        self.map = pygame.image.load(os.path.join(IMG_DIR, 'map.png'))
        self.maprect = self.map.get_rect()
        for t_name in default_names:
            img = pygame.image.load(os.path.join(IMG_DIR, f'{t_name}.png'))
            imagerect = img.get_rect()
            imagerect.topleft = ImageLocations[t_name]
            self.images[t_name] = img
            self.rects[t_name] = imagerect
        self.window = pygame.display.set_mode( (self.maprect.width, self.maprect.height) )
        self.clock = pygame.time.Clock()
        pass
    
    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            self._init_render()
        canvas = pygame.Surface((self.window.get_width(), self.window.get_height()))
        canvas.fill("black")
        # self.window.fill("black")
        # self.window.blit(self.map, self.maprect)
        canvas.blit(self.map, self.maprect)
        for idx, t_name in enumerate(default_names):
            if self.risk is not None:
                pass
            img = self.images[t_name].copy()
            img.fill(self.colors[self.risk.territories[idx, OWNER]], special_flags=pygame.BLEND_MULT)
            canvas.blit(img, self.rects[t_name])
            text_surface = self.font.render(f'{self.risk.territories[idx, ARMIES]}', False, (0, 0, 0))
            pygame.draw.circle(canvas, (255, 255, 255), self.rects[t_name].center, 10)
            canvas.blit(text_surface, self.rects[t_name].center)

        # DRAW LAST MOVE
        # if self.last_action != None and self.last_action != self.risk.DO_NOTHING:
        #     text_surface = self.font.render(f'{self.risk.territories[self.last_action, ARMIES]}', False, (0, 0, 0))
        #     pygame.draw.circle(canvas, (0, 0, 255), self.rects[default_names[self.last_action]].center, 15)
        #     canvas.blit(text_surface, self.rects[default_names[self.last_action]].center)


        # text_surface = self.font.render(f'{type(self.risk)}', False, (0, 0, 0))
        # canvas.blit(text_surface, TextRect)

        # if type(self.risk) == RecruitmentPhase:
        #     pass
        # elif type(self.risk) == FirstFromAttackPhase:
        #     pass
        # elif type(self.risk) == FirstToAttackPhase:
        #     pass
        # elif type(self.risk) == ContinueAttackPhase:
        #     pass
        # elif type(self.risk) == ReinforcePhase:
        #     pass
        # elif type(self.risk) == SubsequentAttackPhase:
        #     pass
        # elif type(self.risk) == FortifyPhase1:
        #     pass
        # elif type(self.risk) == FortifyPhase2:
        #     pass
        # elif type(self.risk) == FortifyPhase3:
        #     pass

        self.window.blit(canvas, canvas.get_rect())
        pygame.display.update()
        self.clock.tick(self.fps)

    def get_observation(self):
        current_phase_index = Phases.index(type(self.risk).__name__)
        # obs = {
        #     "Phase": np.array([current_phase_index]),
        #     "Territories": self.risk.territories
        # }
        n_territories = self.risk.n_territories()
        obs = {
            "Phase": np.array([ 1.0 if i == current_phase_index else 0.0 for i in range(len(Phases)) ]),
            "Owners": self.risk.territories[:, OWNER],
            "Armies": self.risk.territories[:, ARMIES],
            # "ValidMoves": np.full((n_territories,), 0.0, dtype=np.float32)
            "ValidMoves": np.array( [ 1.0 if self.risk.is_valid(x) else 0.0 for x in range(n_territories) ])
        }
        return obs 
        # return self.risk.territories 
        
    
    def step(self, action):
        info = {} 
        # Train against random players (agent is at index 0)
        if self.random_players and self.risk.current_player != 0:
            res, state = self.risk.step(random.choice(self.risk.action_space()))
            reward = 0 
        else:
            res, state = self.risk.step(action)
            if res == Move.INVALID:
                self.invalid_moves += 1
                # print(f"\r>> AI Has made an invalid moves in {type(self.risk).__name__} X ({self.invalid_moves})", end='')
            else:
                # print()
                self.invalid_moves = 0
            reward = 100 if self.risk.won else -1 if res == Move.INVALID else -5
            self.risk.won = False
        self.risk = state
        obs = self.get_observation()
        # obs = self.risk.territories
        self.last_action = int(action)
        return (obs, reward, self.risk.finished(), info)

    def reset(self, seed=None, options=None):
        self.risk = new_game(self.n_players, self.randomizedSetUp)
        return self.get_observation()
    

    def render(self, mode = None):
        if self.render_mode == "human":
            self._render_frame()

    def close(self):
        ...