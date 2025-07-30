import pygame
from types import SimpleNamespace
import re

class Universe():
    def __init__(self, cell_size:int, simulation_size:tuple, cell_colour:tuple, grid_colour:tuple, config:str):
        self.verbose = True
        self.bypass = False
        self.loaded_config = False

        valid_configuration, config_string, msg = self.valid_config(config)
        self.print(msg)

        if valid_configuration:
            self.load_config(config_string, cell_colour, grid_colour)
        else:
            self.print("No Config File >> Starting Blank Universe")
            self.setup_universe(
                cell_size,
                simulation_size,
                cell_colour,
                grid_colour
            )
    
    def setup_universe(self, cell_size:int, simulation_size:tuple, cell_colour:tuple, grid_colour:tuple, ids:list=[]):
        """Sets up all universe class attributes"""

        # Set of all cells (so we can't accidentally include duplicates)
        self.previous_state = set(ids)
        self.live_cells = set(ids)
        self.starting_config = set(ids)

        self.cell_colour = cell_colour
        self.grid_colour = grid_colour

        # Size of the window in (width, height)
        self.SIM_SIZE = SimpleNamespace()
        self.SIM_SIZE.width, self.SIM_SIZE.height = simulation_size

        # Size of a single cell
        self.cell_size = cell_size

        self.verbose = False
        self.sim_running = False
        self.sim_paused = True

        # if we didn't load a config
        if not self.loaded_config:
            self.saved_config = (False, "")
        
    def valid_config(self, config_file:str):
        """Checks if we received a valid configuration file"""
        if config_file != None:
            config_string = ""
            path = f"configurations/{config_file}"

            # Open file and read string
            with open(path) as f:
                config_string = f.read()
                f.close()

            # self.print("Read Config String: " + config_string)

            pattern = r'^\d+_\d+,\d+,(?:\d+_\d+(?:/\d+_\d+)*)$'

            matched = re.match(pattern, config_string)

            if matched: self.saved_config = (True, config_file.removesuffix(".clog"))

            # Return nothing if we didn't match otherwise return the reconfigured string
            return (matched, "", "Invalid Configuration") if not matched else (matched, config_string, "Valid")

        else:
            return False, "", "No File Entered"

    def load_config(self, config_string:str, cell_colour:tuple, grid_colour:tuple):
        """Loads a configuration string into the universe"""

        # Splitting config into separate parts
        parts = config_string.split(",")
        dimensions, cell_size, ids = parts

        # Converting strings into data
        dimensions = (int(n) for n in dimensions.split("_"))
        cell_size = int(cell_size)
        ids = ids.split("/")

        self.loaded_config = True

        self.setup_universe(
            cell_size=cell_size,
            simulation_size=dimensions,
            cell_colour=cell_colour,
            grid_colour=grid_colour,
            ids=ids
        )

    def save_config(self, config_name:str="", new_save=False):
        """Save config to the configuration folder"""

        def write_to_file(path, save_str) -> bool:
            # Open file and write string to file
            with open(path, "w") as f:
                res = f.write(save_str)
                f.close()

            return res == len(save_string)

        # Get save string
        save_string = self.starting_config_to_string()

        # First time they save the config, set flag to true
        if self.saved_config[0] == False or new_save == True:
            self.saved_config = (True, config_name)

            path = f"configurations/{config_name}.clog"

            res = write_to_file(path, save_string)

            # Return a check to see if we added the string correctly
            return res
        else:
            # We are just autosaving changes so use saved config
            path = f"configurations/{self.saved_config[1]}.clog"

            res = write_to_file(path, save_string)

            # Return a check to see if we added the string correctly
            return res
    
    def starting_config_to_string(self) -> str:
        """Convert starting configuration to a string"""
        dimensions = f"{self.SIM_SIZE.width}_{self.SIM_SIZE.height}"
        cell_size = f"{self.cell_size}"
        string_ids = "/".join(self.starting_config)

        return ",".join([dimensions, cell_size, string_ids])
    
    def coords_to_id(self, coordinate:tuple) -> str:
        """Converts coordinates into a string id"""
        x, y = coordinate
        return f"{x // self.cell_size}_{y // self.cell_size}"

    def id_to_coords(self, id:str) -> tuple:
        """Converts an ID back into coordinates"""
        coords = (int(n) * self.cell_size for n in id.split("_"))
        return coords

    def draw_grid(self, screen) -> None:
        """Draws the grid representing the available cells"""

        # Loop through all x and y coordinates for the grid
        for x in range(0, self.SIM_SIZE.width, self.cell_size):
            for y in range(0, self.SIM_SIZE.height, self.cell_size):
                # Draw a rect in all positions
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, self.grid_colour, rect, 1)

    def update(self, screen):
        # Run rules if simulation is running
        if self.sim_running and not self.sim_paused:
            # Update previous state
            self.rules()

            self.previous_state = set([e for e in self.live_cells])

        self.draw(screen)
     
    def draw(self, screen) -> None:
        """Draws the updated universe"""

        # Draw the grid if we are not running
        if self.sim_paused:
            self.draw_grid(screen)

        # Draw the live cells
        self.draw_cells(screen)

    def handle_click(self, coords:tuple) -> None:
        """Handle a user clicking on the grid"""

        if self.sim_paused:
            # Convert coordinate to ID
            id = self.coords_to_id(coords)

            # Check if we already had this cell in
            if id in self.live_cells:
                self.live_cells.remove(id)
                if not self.sim_running: 
                    self.starting_config.remove(id)
            else:
                self.live_cells.add(id)
                if not self.sim_running: self.starting_config.add(id)
        else:
            self.print("Cannot Update Config During Sim Runtime")
        
    def draw_cells(self, screen) -> None:
        """Draw currently live cells to the screen"""

        # Loop through all cell ids
        for cell in self.live_cells:

            # Convert cell IDs to coordinates
            x, y = self.id_to_coords(cell)

            # Draw rectangle at this coordinate
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(screen, self.cell_colour, rect)
        
    def toggle_run_simulation(self):
        """Start and stop the simulation"""

        # If the simulation wasn't running before
        if not self.sim_running:
            self.sim_running = not self.sim_running
            self.sim_paused = not self.sim_paused

            if self.sim_running: self.previous_state = set([e for e in self.live_cells])

            self.print(f"Simulation {"Started" if self.sim_running else "Stopped"}")
        else:
            # Pause functionality
            self.sim_paused = not self.sim_paused

            if not self.sim_paused:
                self.previous_state = set([e for e in self.live_cells])
            
            self.print(f"Simulation {"Paused" if self.sim_paused else "Restarted"}")
        
    def toggle_verbose(self):
        """Toggles whether we print debug statements"""

        self.verbose = not self.verbose
        print(f"Verbose Mode: {"On" if self.verbose else "Off"}")
    
    def print(self, msg:str, bypass=False):
        """Prints custom message if we are in verbose"""

        if self.verbose or bypass:
            print(f"[Universe] {msg}")
        
    def get_neighbours(self, id:str):
        """Get all live or dead neighbours of a certain cell"""

        grid_x, grid_y = [int(n) for n in id.split("_")]
        neighbours = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # If we are at the actual id, skip
                if (dx == 0 and dy == 0) or \
                grid_x + dx < 0 or \
                grid_x + dx > (self.SIM_SIZE.width // self.cell_size) - 1 or \
                grid_y + dy < 0 or \
                grid_y + dy > (self.SIM_SIZE.height // self.cell_size) - 1: 
                    continue
                else:
                    neighbour_id = f"{grid_x + dx}_{grid_y + dy}"
                    neighbours.append(neighbour_id)
                
        return neighbours

    def get_live_neighbours(self, id:str):
        """Get all live neighbours of a certain cell"""
        
        neighbours = self.get_neighbours(id)
        live = []

        for neighbour_id in neighbours:
            if neighbour_id in self.previous_state:
                live.append(neighbour_id)
                
        return live
    
    def get_dead_neighbours(self, id:str):
        """Get all dead neighbours of a certain cell"""
        
        neighbours = self.get_neighbours(id)
        dead = []

        for neighbour_id in neighbours:
            if neighbour_id not in self.previous_state:
                dead.append(neighbour_id)
                
        return dead

    def rules(self):
        """Run all rules on the simulation"""
        self.underpopulation()
        self.overpopulation()
        self.reproduction()

    def underpopulation(self):
        """Underpopulation rule"""
        for id in self.previous_state:
            if len(self.get_live_neighbours(id)) < 2:
                self.print(f"Removing {id}! (Underpopulation)")
                self.live_cells.remove(id)
    
    def overpopulation(self):
        """Overpopulation rule"""
        for id in self.previous_state:
            if len(self.get_live_neighbours(id)) > 3:
                self.print(f"Removing {id}! (Overpopulation)")
                self.live_cells.remove(id)

    def reproduction(self):
        """Reproduction rule"""
        neighbours_to_check = set()

        # Generate list of all cells to check
        for id in self.previous_state:
            for neighbour in self.get_dead_neighbours(id):
                neighbours_to_check.add(neighbour)
            
        for n in neighbours_to_check:
            # Check if they have exactly 3 live neighbours
            if len(self.get_live_neighbours(n)) == 3:
                # Reproduce!
                self.print(f"Adding {id} (Reproduction)!")
                self.live_cells.add(n)
