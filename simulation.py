import pygame
from universe import Universe

# Setting up pygame environment
pygame.init()

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 10)
FPS_CAP = 165

# Setting up the display
pygame.display.set_caption("Conway's Game of Life")
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

SQUARE_COLOUR = (255, 255, 255)
GRID_COLOUR = (60, 60, 60)

universe = Universe(
    cell_size=20,
    simulation_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
    cell_colour=SQUARE_COLOUR,
    grid_colour=GRID_COLOUR
)

# Bool to control the main loop
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            universe.handle_click(mouse_pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                universe.toggle_run_simulation()
            if event.key == pygame.K_d:
                universe.toggle_verbose()

    # Fill the background of the screen with black
    SCREEN.fill((10, 10, 10))

    universe.draw(SCREEN)

    # Update the display
    pygame.display.flip()
    
    # Cap frame rate
    CLOCK.tick(FPS_CAP)

pygame.quit()