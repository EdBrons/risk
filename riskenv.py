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
        self.random_players = random_players

        n_territories = self.risk.n_territories()
        self.n_phases = len(Phases)
        self.MAX_ARMIES = 30

        self.action_space = Discrete( n_territories )

        # self.observation_space = Dict( {
        #     "Phase": Discrete(self.n_phases),
        #     "Territories": MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))
        # } )
        self.observation_space = MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))

        self.render_mode = "human"
        self.window = None
        self.fps = 60
    
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
        for t_name in default_names:
            if self.risk is not None:
                pass
            # self.images[t_name].fill((190, 0, 0, 100), special_flags=pygame.BLEND_MULT)
            canvas.blit(self.images[t_name], self.rects[t_name])
            text_surface = self.font.render(f'1', False, (0, 0, 0))
            pygame.draw.circle(canvas, (255, 255, 255), self.rects[t_name].center, 10)
            canvas.blit(text_surface, self.rects[t_name].center)
        self.window.blit(canvas, canvas.get_rect())
        pygame.display.update()
        self.clock.tick(self.fps)

    def get_observation(self):
        current_phase_index = Phases.index(type(self.risk).__name__)
        # obs = {
        #     "Phase": np.array([current_phase_index]),
        #     "Territories": self.risk.territories
        # }
        # return obs 
        return self.risk.territories 
        
    
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
            reward = 1 if self.risk.won else -1 if res.VALID else -5
        self.risk = state
        # obs = dict(Phase=np.array([Phases.index(type(self.risk).__name__)]), Territories = self.risk.territories)
        obs = self.risk.territories
        return (obs, reward, self.risk.finished() , info)

    def reset(self):
        self.risk = new_game(self.n_players)
        return self.get_observation()
    

    def render(self, mode):
        if self.render_mode == "human":
            self._render_frame()

    def close(self):
        ...