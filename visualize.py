import pygame
import os

# pygame setup
pygame.init()

map = pygame.image.load(os.path.join('risk-map', 'riskMap.png'))
imagerect = map.get_rect()

screen = pygame.display.set_mode((imagerect.width, imagerect.height))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    screen.blit(map, imagerect)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()