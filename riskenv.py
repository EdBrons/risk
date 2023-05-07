import gymnasium as gym
from gymnasium.spaces import Dict, Discrete, MultiDiscrete, Graph 
from riskstate import *
from maps import default_map, default_names
from visualize import ImageLocations, IMG_DIR
import numpy as np 
import random
import pygame
import os

class RiskEnv(gym.Env):
    """Custom Environment that follows gym interface."""
    # metadata = {"render.modes": ["human"], "render_fps": 60}

    def __init__(self, n_players=2, random_players = False):
        super().__init__()

        self.risk = new_game(n_players)
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

        n_territories = self.risk.n_territories()
        self.n_phases = len(Phases)
        self.MAX_ARMIES = 30

        self.action_space = Discrete( n_territories + 1 )

        self.observation_space = Dict( {
            "Phase": Discrete(self.n_phases),
            "Territories": MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))
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
        self.window.blit(canvas, canvas.get_rect())
        pygame.display.update()
        self.clock.tick(self.fps)

    def get_observation(self):
        current_phase_index = Phases.index(type(self.risk).__name__)
        obs = {
            "Phase": np.array([current_phase_index]),
            "Territories": self.risk.territories
        }
        return obs 
        # return self.risk.territories 
        
    
    def get_short_observation(self):
        obs = {} 
        for player in self.risk.active_players:
            obs[f"player_{player}"] = 0
            for country in self.risk.graph:
                if self.risk.territories[country, OWNER] == player:
                    obs[f"player_{player}"] += 1
        return obs, self.risk.turn

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
                print(f"\r>> AI Has made an invalid moves in {type(self.risk).__name__} X ({self.invalid_moves})", end='')
            else:
                print()
                self.invalid_moves = 0
            reward = 100 if self.risk.won else -1 if res == Move.INVALID else -5
            self.risk.won = False
        self.risk = state
        obs = dict(Phase=np.array([Phases.index(type(self.risk).__name__)]), Territories = self.risk.territories)
        # obs = self.risk.territories
        return (obs, reward, self.risk.finished() , info)

    def reset(self):
        self.risk = new_game(self.n_players)
        return self.get_observation()
    

    def render(self, mode):
        if self.render_mode == "human":
            self._render_frame()

    def close(self):
        ...