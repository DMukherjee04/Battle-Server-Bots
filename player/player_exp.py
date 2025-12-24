import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 700, 700
BLUE  = (0, 0, 255)

x = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BATTLE-ARENA")

pygame.draw.circle(screen, BLUE, (x, 0), 10) 
# Clock (controls FPS)
clock = pygame.time.Clock()

# Game loop
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game logic
    # (nothing yet)
    x +=1 
    # Draw / render
    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, BLUE, (x, 0), 10) 
     # Black background
    pygame.display.flip()  # Update screen

    # Limit FPS
    clock.tick(60)

pygame.quit()
sys.exit()
