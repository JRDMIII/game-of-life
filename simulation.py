import pygame
from universe import Universe
import re

def main(config: str):
    # Setting up pygame environment
    pygame.init()

    SCREEN_WIDTH = 1800
    SCREEN_HEIGHT = 1000
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont("Arial", 12)

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

    sim_speeds = [
        3,  # x1
        6,  # x2
        12, # x4
        24, # x8
        48, # x16
        96  # x32
    ]
    edit_speed = 60
    current_speed = 0

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                universe.handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:

                # Slow down simulation
                if event.key == pygame.K_k:
                    if universe.sim_running:
                        current_speed = max(current_speed - 1, 0)
                
                # Speed up simulation
                elif event.key == pygame.K_l:
                    if universe.sim_running:
                        current_speed = min(current_speed + 1, len(sim_speeds) - 1)

                # Start simulation
                elif event.key == pygame.K_RETURN:
                    current_speed = 2
                    universe.toggle_run_simulation()

                # Turn on verbose (debug lines)
                elif event.key == pygame.K_d:
                    universe.toggle_verbose()

                # Save starting configuration
                elif event.key == pygame.K_s:
                    mods = pygame.key.get_mods()

                    if mods & pygame.KMOD_SHIFT and mods & pygame.KMOD_CTRL:
                        save_configuration(universe, True)
                    else:
                        save_configuration(universe)


        # Fill the background of the screen with black
        SCREEN.fill((10, 10, 10))

        universe.update(SCREEN)

        # Show current speed
        sim_speed_text = FONT.render(f"Simulation Speed: x{2**current_speed}", True, (255, 255, 255))
        
        spacing = 15
        start = 10

        if not universe.sim_paused:
            SCREEN.blit(sim_speed_text, (10, start))

        generation_text = FONT.render(f"Generation: {universe.generation}", True, (255, 255, 255))
        population_text = FONT.render(f"Population: {len(universe.live_cells)} cells", True, (255, 255, 255))
        stale_text = FONT.render(f"Simulation Stale: {universe.sim_stale}", True, (255, 255, 255))

        SCREEN.blit(generation_text, (10, start + spacing))
        SCREEN.blit(population_text, (10, start + (2 * spacing)))
        SCREEN.blit(stale_text, (10, start + (3 * spacing)))

        # Update the display
        pygame.display.flip()
        
        FPS = edit_speed if universe.sim_paused else sim_speeds[current_speed]

        # Cap frame rate
        CLOCK.tick(FPS)

    pygame.quit()

def save_configuration(universe: Universe, new=False):
    """Save configuration"""
    if universe.saved_config[0] == True and new == False:
        # If we already saved the config, just autosave to that file
        universe.save_config()
        print(f"[Main Sim] Saved to {universe.saved_config[1]}")
    else:
        valid_save_name = False

        while valid_save_name == False:
            config_save_name = [
                inquirer.Text("config_name", 
                    message="Enter a name for your configuration",
                    validate=lambda _, x: re.match(r'^[A-Za-z0-9_-]+$', x)
                )
            ]

            config_name = inquirer.prompt(config_save_name)["config_name"]

            # Get all .clog files in the directory
            files = [f for f in os.listdir("configurations") if re.search('.clog', f)]

            # Check if we would be overwriting a file
            if config_name + ".clog" in files:

                # Ask user if they want to overwrite the file
                overwrite = [
                    inquirer.List('overwrite',
                        message="File exists. Do you want to overwrite?",
                        choices=["Yes", "No"],
                        carousel=True
                    )
                ]

                ans = inquirer.prompt(overwrite)["overwrite"]
                
                if ans == "Yes":
                    valid_save_name = True
                else:
                    valid_save_name = False
            else:
                valid_save_name = True

        # Save config
        universe.save_config(config_name, new)

if __name__ == "__main__":
    import os
    import inquirer

    if not os.path.isdir("configurations"):
        print("[Main] Added /configurations folder")
        os.mkdir("configurations")

    # Get all .clog files in the directory
    files = [f for f in os.listdir("configurations") if re.search('.clog', f)]

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
    
    config:str = chosen["config"]

    if config == "No Config (Start from Scratch)": config = None
        
    main(config)