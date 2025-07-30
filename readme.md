# Dev Log: Boids

## The Theory
Conway's game of life is the equivalent of a LeBron James in computer science. Everyone knows about it and it it's bag is too deep. So I decided to make that my next project because why not! This is probably going to be a one-session project but always work a good dev log. Also going to try reference websites I find information on but we'll see how long I can be bothered with that.

The main theory behind this comes down to only 4 rules (found on Wikipedia[^1]) which make the universes and beings that come to be in these simulations (I've given each of them names for notation purposes):
1. **Underpopulation**: Any live cell with fewer than two live neighbours dies, as if by underpopulation.
2. **Harmony**: Any live cell with two or three live neighbours lives on to the next generation.
3. **Overpopulation**: Any live cell with more than three live neighbours dies, as if by overpopulation.
4. **Reproduction**: Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

Once these are implemented we can see a bunch of behaviours from starting configurations such as **gliders**, **still lifes** and **oscillators**.

## Log 1: Grid System
To start, we need to create the grid system on which the game will sit. Essentially, the environment needs to be split up into squares and hopefully each has an ID which allows for them to be retrieved immediately (instead of looping through every single square later down the line).

For example, when implementing the reproduction rule, we can just look at neighbours of the currently live cells as for a cell to become live it must be next to a live cell - this makes the program run a lot smoother as we aren't looping through hundreds of squares.

With a square size of 10x10 pixels, if we had a screen size of 1000x1000, we'd have 100 squares and therefore 100 IDs e.g. (392, 200) equates to "39_200" and (9, 12) equates to "0_1" in string format (made the id's legible). There could be a better way of doing this but for now this is what i've thought of.

First, I implemented a little bit of code to get the position of the mouse if the user clicks.

```python
for event in pygame.event.get():
    # ...
    elif event.type == pygame.MOUSEBUTTONDOWN:
        x, y = pygame.mouse.get_pos()
        print(x, y)
```

Now we can create our `Universe` class which will store the main simulation code - including the grid calculation code.

```python
class Universe():
    def __init__(self, cell_size:int, simulation_size:tuple):
        # Set of all cells (so we can't accidentally include duplicates)
        self.live_cells = set()

        # Size of the window in (width, height)
        self.simulation_size = simulation_size

        # Size of a single cell
        self.cell_size = cell_size
    
    def coords_to_id(self, coordinate: tuple) -> str:
        """Converts coordinates into a string id"""
        x, y = coordinate
        return f"{x // self.cell_size}_{y // self.cell_size}"

    def id_to_coords(self, id: str) -> tuple:
        """Converts an ID back into coordinates"""
        coords = (int(n) * self.cell_size for n in id.split("_"))
        return coords
```

To make sure it works i just set the screen size to 900 and made the cell size 300 so that we would get all combinations of ids from 0_0 to 2_2 to make sure it worked.

For the same of usability I wanted to now include a grid visual to show where the grid actually is. This seemed easy enough - all i'd need to do is draw a box in every cell the size of the cell.

```python
def draw_grid(self, screen) -> None:
    # Loop through all x and y coordinates for the grid
    for x in range(0, self.SIM_SIZE.width, self.cell_size):
        for y in range(0, self.SIM_SIZE.height, self.cell_size):
            # Draw a rect in all positions
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(screen, self.grid_colour, rect, 1)
    
    
def draw(self, screen) -> None:
    """Draws the updated universe"""
    self.draw_grid(screen)
```

That gives us this:

<div align="center">
    <img src="./assets/grid.png" width="400" />
    <p><em>Figure 1: Grid!</em></p>
</div>

With a more realistic grid size and a darker colour so the grid isn't so overpowering we get this something like this:

<div align="center">
    <img src="./assets/new_grid.png" width="400" />
    <p><em>Figure 2: Grid with smaller cells and less intense colour</em></p>
</div>

With this we now have both a grid and the ability to click and get a grid cell's id.

### Adding Cells to Grid
Now we have the grid we want to be able to add cells to the grid if the user clicks on a certain square. The flow for this that seems most logical is:
1. User clicks on grid
2. Universe converts this coordinate to an ID
3. If ID isn't in the set then add it, otherwise remove it
4. Loop through set of cells and draw each of them using the ID

Implemented like so:
```python
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
```

From here I added the `handle_click()` function to the events of the pygame loop:

```python
# Event handling
    for event in pygame.event.get():
        # ...
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            universe.handle_click(mouse_pos)
```

And now we have the ability to add squares to the grid to create our starting configuration!

<div align="center">
    <img src="./assets/cell_placement.gif" width="400" />
    <p><em>Figure 3: Placing cells on the grid</em></p>
</div>

## Log 2: Starting the Sim

Now we can set up the simulation, we need to be able to start it which is quite easy.

We listen out for the user pressing the `Enter` key (I like the enter keyfor this) and when it is pressed we switch a flag in the simulation from off to on. This will:
 - Disable the ability to add cells to the grid on click
 - Begin running the rules of the simulation
 - Stop showing grid to make things look nicer during the sim

I would also like to add keybinds to speed up/slow down the simulation once it has started and write to the screen the current speed of the sim but we can see about that later as a polish.

For the basic function of starting and stopping, I created a variable in the universe called `sim_running` which can be toggled through pygame events.

```python
def toggle_run_simulation(self):
    """Start and stop the simulation"""

    self.sim_running = not self.sim_running
    print(f"Simulation {"Started" if self.sim_running else "Stopped"}")
```

```python
for event in pygame.event.get():
    # ...
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_KP_ENTER:
            universe.toggle_run_simulation()
```

Also added a little debug code to the universe at this point so I could turn on and off print statements in the universe class:

```python
def toggle_verbose(self):
    """Toggles whether we print debug statements"""

    self.verbose = not self.verbose
    print(f"Verbose Mode: {"On" if self.verbose else "Off"}")

def print(self, msg: str):
    """Prints custom message if we are in verbose"""
    
    if self.verbose:
        print(f"[Universe] {msg}")
```

With this, when we press enter, the simulation starts! We can also toggle on and off debugging using "D". I will look into speed up and slow down once we have some things to check

Now to actually have some updates occur...

## Log 3: Uploading and Saving Configs

It is nearly time for the fun part - implementing rules! Before that though, I wanted to quickly make a way to enter a starting configuration in string format rather than clicking because debugging will be much easier that way. With this, I will be able to put a file into the universe and it can then put all those cells on the screen.

I also wanted a way to save configurations to a folder (and possibly name them through the console?) just so things are nice and user friendly (we love features here).

```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument("--config", help="Path to starting configuration file", default=None)

    args = parser.parse_args()

    universe = Universe(
        cell_size=20,
        simulation_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        cell_colour=SQUARE_COLOUR,
        grid_colour=GRID_COLOUR,
        config=args.config
    )

```

This code let's us add a config to the running of the python file (if we want to and if we leave it blank it'll just be a blank universe) like this:

```console
python simulation.py --config /path/to/config
```

I updated this to only take files from within a `/configurations` folder for cleanliness and I've made configuration files have a postfix `.cgol` for "Conway's Game of Life" just to be fancy.

I realised this could get a little annoying if you typed in things wrong or didn't get it so instead I updated it to display all files in `/configurations` and let you pick one from there. If there were none, it skips this step.

```python
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

    main(config)
```

This felt a lot easier to use. Also allowed me to include more plain english to explain how to start from scratch. Now we can read the string in this file if it is a valid file and load the configuration.

First explaining the config string formatting:

1. Screen Width and Height
2. Cell Size
3. List of ids separated by slashes "/"

Note: Each of these properties should be separated by a comma

So putting a 20x20 cell in position (0, 0) and (5, 0) grid-wise on a 1500x900 would look like:

```
1500_900,20,0_0/5_0
```

This did actually require a lot of reconfiguring to get to work cleanly:

```python
def __init__(self, cell_size:int, simulation_size:tuple, cell_colour:tuple, grid_colour:tuple, config:str):
        if self.valid_config(config):
            self.load_config(config, cell_colour, grid_colour)
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
        self.live_cells = set(ids)

        self.cell_colour = cell_colour
        self.grid_colour = grid_colour

        # Size of the window in (width, height)
        self.SIM_SIZE = SimpleNamespace()
        self.SIM_SIZE.width, self.SIM_SIZE.height = simulation_size

        # Size of a single cell
        self.cell_size = cell_size

        self.verbose = False
        self.sim_running = False
        
    def valid_config(self, config_file):
        """Checks if we received a valid configuration file"""
        return config_file != None

    def load_config(self, config_file, cell_colour, grid_colour):
        """Loads a configuration file into the universe"""

        # Convert file name into relative path
        config_string = ""
        path = f"configurations/{config_file}"

        # Open file and read string
        with open(path) as f:
            config_string = f.read()
            f.close()

        self.print("Read Config String: " + config_string)

        # Splitting config into separate parts
        parts = config_string.split(",")
        dimensions, cell_size, ids = parts

        # Converting strings into data
        dimensions = (int(n) for n in dimensions.split("_"))
        cell_size = int(cell_size)
        ids = ids.split("/")

        self.setup_universe(
            cell_size=cell_size,
            simulation_size=dimensions,
            cell_colour=cell_colour,
            grid_colour=grid_colour,
            ids=ids
        )
```

But with this we had a configurations loading!

Now we can easily work on the simulation rules with the config files (I'll save configs later I want to see **Movement**).

[^1]: [Wikipedia](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) - Conway's Game of Life