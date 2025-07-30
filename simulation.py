import pygame
from universe import Universe

def main(config):
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

    # Bool to control the main loop
    running = True

    SQUARE_COLOUR = (255, 255, 255)
    GRID_COLOUR = (60, 60, 60)

    universe = Universe(
        cell_size=20,
        simulation_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        cell_colour=SQUARE_COLOUR,
        grid_colour=GRID_COLOUR,
        config=config
    )

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

if __name__ == "__main__":
    import os
    import inquirer

    if not os.path.isdir("configurations"):
        print("[Main] Added /configurations folder")
        os.mkdir("configurations")

    # Get all .clog files in the directory
    files = [f for f in os.listdir("configurations") if ".clog" in f]

    config = None

    # If there is a config to select from
    if files:
        choose_config = [
        inquirer.List('config',
                message="Select a configuration",
                choices=["No Config (Start from Scratch)"] + files,
                carousel=True
            ),
        ]
        chosen = inquirer.prompt(choose_config)
    
    config = chosen["config"]

    if config == "No Config (Start from Scratch)": config = None

    main(config)