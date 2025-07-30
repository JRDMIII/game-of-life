import pygame
from types import SimpleNamespace

class Universe():
    def __init__(self, cell_size:int, simulation_size:tuple, cell_colour:tuple, grid_colour:tuple):
        # Set of all cells (so we can't accidentally include duplicates)
        self.live_cells = set()
        self.cell_colour = cell_colour
        self.grid_colour = grid_colour

        # Size of the window in (width, height)
        self.SIM_SIZE = SimpleNamespace()
        self.SIM_SIZE.width, self.SIM_SIZE.height = simulation_size

        # Size of a single cell
        self.cell_size = cell_size
        self.verbose = False
        self.sim_running = False
    
    def coords_to_id(self, coordinate: tuple) -> str:
        """Converts coordinates into a string id"""
        x, y = coordinate
        return f"{x // self.cell_size}_{y // self.cell_size}"

    def id_to_coords(self, id: str) -> tuple:
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
            
    def draw(self, screen) -> None:
        """Draws the updated universe"""

        # Draw the grid
        if not self.sim_running:
            self.draw_grid(screen)

        # Draw the live cells
        self.draw_cells(screen)

    def handle_click(self, coords:tuple) -> None:
        """Handle a user clicking on the grid"""

        # Convert coordinate to ID
        id = self.coords_to_id(coords)

        # Check if we already had this cell in
        if id in self.live_cells: self.live_cells.remove(id)
        else: self.live_cells.add(id)
        
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

        self.sim_running = not self.sim_running
        self.print(f"Simulation {"Started" if self.sim_running else "Stopped"}")
        
    def toggle_verbose(self):
        """Toggles whether we print debug statements"""
        
        self.verbose = not self.verbose
        print(f"Verbose Mode: {"On" if self.verbose else "Off"}")
    
    def print(self, msg: str):
        """Prints custom message if we are in verbose"""

        if self.verbose:
            print(f"[Universe] {msg}")