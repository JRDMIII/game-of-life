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
    <p><em>Figure 1: Boids simulation in Python</em></p>
</div>

With a more realistic grid size and a darker colour so the grid isn't so overpowering we get this something like this:

<div align="center">
    <img src="./assets/new_grid.png" width="400" />
    <p><em>Figure 1: Boids simulation in Python</em></p>
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

[^1]: [Wikipedia](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) - Conway's Game of Life