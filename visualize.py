import pygame
import os
from maps import default_names

ImageLocations = {
    "Alaska": [8, 47], 
    "NW_Territory": [66, 33], 
    "Greenland": [200, 1], 
    "Alberta": [73, 94],
    "Ontario": [129, 86], 
    "Quebec": [179, 81], 
    "W_US": [69, 139], 
    "E_US": [118, 141], 
    "C_America": [77, 202],
    #South America
    "Venezuela": [135, 269], 
    "Brazil": [149, 295], 
    "Peru": [123, 305], 
    "Argentina": [158, 379],
    #Africa
    "N_Africa": [301, 263], 
    "Egypt": [378, 278], 
    "E_Africa": [416, 317], 
    "Congo": [382, 358], 
    "S_Africa": [385, 410], 
    "Madagascar": [473, 432],
    #Australia
    "Indonesia": [602, 349], 
    "New_Guinea": [682, 337], 
    "W_Australia": [639, 410], 
    "E_Australia": [700, 400],
    #Europe
    "Iceland": [300, 76], 
    "Great_Britain": [268, 113], 
    "Scandanavia": [353, 51],
    "Ukraine": [400, 50], 
    "N_Europe": [345, 127], 
    "S_Europe": [355, 182], 
    "W_Europe": [ 291, 180 ],
    #Asia
    "Mid_East": [414, 223], 
    "Afghanistan": [476, 140], 
    "Ural": [512, 28], 
    "Siberia": [531, 2],
    "Yakutsk": [ 607, 20 ], 
    "Kamchatka": [647, 27], 
    "Irkutsk": [593, 79], 
    "Mongolia": [600, 128],
    "Japan": [697, 127], 
    "China": [554, 159], 
    "India": [527, 217], 
    "Siam": [604, 259]
}

IMG_DIR = './risk-map'

# pygame setup
pygame.init()
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 12)

Images = {}
Rects = {}

map = pygame.image.load(os.path.join(IMG_DIR, 'map.png'))
maprect = map.get_rect()

for t_name in default_names:
    img = pygame.image.load(os.path.join(IMG_DIR, f'{t_name}.png'))
    imagerect = img.get_rect()
    imagerect.topleft = ImageLocations[t_name]
    Images[t_name] = img
    Rects[t_name] = imagerect

screen = pygame.display.set_mode((maprect.width, maprect.height))
clock = pygame.time.Clock()
running = True

def draw_map(to, risk_state = None, player_colors = None):
    for t_name in default_names:
        if risk_state is not None:
            pass
        Images[t_name].fill((190, 0, 0, 100), special_flags=pygame.BLEND_MULT)
        to.blit(Images[t_name], Rects[t_name])
        text_surface = my_font.render(f'1', False, (0, 0, 0))
        pygame.draw.circle(to, (255, 255, 255), Rects[t_name].center, 10)
        to.blit(text_surface, Rects[t_name].scale_by(.05))

def create_map(risk_state = None, player_colors = None):
    img = map.copy()
    draw_map(img, risk_state, player_colors)
    return img

pygame.image.save(create_map(), "out.png")

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    draw_map()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()