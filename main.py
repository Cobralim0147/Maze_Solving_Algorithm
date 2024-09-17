import math
import heapq

# Define special cell class
class SpecialCell:
    def __init__(self, x, y, effect):
        self.x = x
        self.y = y
        self.effect = effect  # Effect can be 'gravity', 'speed', 'teleport', 'remove_treasures'

    def apply_effect(self, cell_details, dests, path):
        if self.effect == 'increase_gravity':
            cell_details.energy *= 2
        elif self.effect == 'reduce_speed':
            cell_details.energy *= 2  # Since steps double, energy for the cell doubles
        elif self.effect == 'reduce_gravity':
            cell_details.energy /= 2
        elif self.effect == 'increase_speed':
            cell_details.energy /= 2  # Since steps halve, energy for the cell halves
        elif self.effect == 'remove_treasures':
            return dests == []
        elif self.effect == 'teleport':
            if len(path) >= 3:  # Check if there are at least 3 cells in the path
                return path[-3]  # Return the coordinates of the cell two steps back
        return None


# Define the Cell class
class Cell:
    def __init__(self):
        self.parent_i = -1
        self.parent_j = -1
        self.f = float('inf')
        self.g = float('inf')
        self.h = 0
        self.energy = 1.0
        self.actual_energy = 1.0  # New attribute to store the actual energy cost


# Define the size of the grid
maze_size = [6, 10]
special_cells = [
    SpecialCell(2, 8, 'increase_gravity'), SpecialCell(1, 1, 'reduce_speed'), SpecialCell(4, 2, 'reduce_speed'),
    SpecialCell(1, 6, 'teleport'), SpecialCell(3, 5, 'teleport'), SpecialCell(1, 3, 'remove_treasures'),  # Traps
    SpecialCell(0, 4, 'reduce_gravity'), SpecialCell(3, 1, 'reduce_gravity'), SpecialCell(5, 5, 'increase_speed'),
    SpecialCell(2, 7, 'increase_speed')  # Rewards
]

# Define the directions for odd and even columns in the hexagonal grid
directions_odd = [(-1, 0), (-1, 1), (0, 1), (1, 0), (0, -1), (-1, -1)]
directions_even = [(-1, 0), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]

# Define the direction name for odd and even columns in the hexagonal grid
direction_names_odd = ['N', 'NE', 'SE', 'S', 'SW', 'NW']
direction_names_even = ['N', 'NE', 'SE', 'S', 'SW', 'NW']

# Create reverse lookup dictionaries for directions
reverse_directions_odd = {v: k for k, v in zip(direction_names_odd, directions_odd)}
reverse_directions_even = {v: k for k, v in zip(direction_names_even, directions_even)}

# Check if a cell is valid (within the grid)
def is_valid(row, col):
    return (row >= 0) and (row < maze_size[0]) and (col >= 0) and (col < maze_size[1])

# Check if a cell is unblocked
def is_unblocked(grid, row, col, special_cells):
    # Check if the cell is unblocked and not a trap
    return grid[row][col] == 1 and all(
        not (cell.x == row and cell.y == col and cell.effect == 'remove_treasures') for cell in special_cells)

# Check if a cell is the destination
def is_destination(row, col, dests):
    return (row, col) in dests

# Check if a cell is special and apply the effect if so
def apply_special_cell_effect(row, col, cell_details, special_cells, dests, path):
    for special_cell in special_cells:
        if special_cell.x == row and special_cell.y == col:
            result = special_cell.apply_effect(cell_details[row][col], dests, path)
            if result is not None:
                return result
            # Update the actual_energy based on the effect
            cell_details[row][col].actual_energy = cell_details[row][col].energy
            return True
    return False

# Calculate the heuristic value of a cell (Euclidean distance to destination)
def calculate_h_value(row, col, dests):
    return min(math.sqrt((row - dest[0]) ** 2 + (col - dest[1]) ** 2) for dest in dests)

# Calculate the heuristic value of a cell (Euclidean distance to destination)
def trace_path(cell_details, src, dest,updateEnergy):
    path = []
    row, col = dest
    total_energy = 0

    directions_movement = []

    while not (cell_details[row][col].parent_i == row and cell_details[row][col].parent_j == col):
        temp_row = cell_details[row][col].parent_i
        temp_col = cell_details[row][col].parent_j

        direction_key = (row - temp_row, col - temp_col)
        if temp_col % 2 == 0:
            direction = reverse_directions_even.get(direction_key)
        else:
            direction = reverse_directions_odd.get(direction_key)

        directions_movement.append((direction, (temp_row, temp_col), (row, col)))

        path.append((row, col))
        #if(cell_details[row][col].actual_energy == 0.5):
        #    updateEnergy = updateEnergy * 2
        #total_energy += updateEnergy
        #total_energy += cell_details[row][col].actual_energy  # Use actual_energy instead of energy
        row, col = temp_row, temp_col

    path.append((row, col))
    #total_energy += cell_details[row][col].actual_energy  # Use actual_energy for the source cell

    path.reverse()
    directions_movement.reverse()

    for move in directions_movement:
        direction, start, end = move
        if direction:
            print("*************************************************************")
            print(f"\nDirection taken: {direction}")
            print(f"Moved from {start} to {end}")
            print(f"Energy consumed: {updateEnergy}\n")
            #print(f"hello{cell_details[end[0]][end[1]].actual_energy}")
            total_energy += updateEnergy
            if(cell_details[end[0]][end[1]].actual_energy == 0.5):
                updateEnergy = updateEnergy / 2
            if(cell_details[end[0]][end[1]].actual_energy == 2):
                updateEnergy = updateEnergy * 2
            if apply_special_cell_effect(end[0], end[1], cell_details, special_cells, dest, path):
                print("#################################")
                print(f"Special cell effect applied at {end}")
                print("#################################")
                print()

    print("The Path is:")
    for i in path:
        print("->", i, end=" ")
    print()
    print(f"Total energy consumed for this path: {total_energy}")
    print()

    return total_energy, updateEnergy

# A* Search Algorithm
def a_star_search(grid, src, dests):
    current_energy = 1.0
    total_energy_all_paths = 0  # Initialize total energy for all paths

    # Create a closed list and initialize it to false
    closed_list = [[False for _ in range(maze_size[1])] for _ in range(maze_size[0])]

    # Create a 2D array of cells to hold the details of that cell
    cell_details = [[Cell() for _ in range(maze_size[1])] for _ in range(maze_size[0])]

    i, j = src[0], src[1]
    cell_details[i][j].f = 0.0
    cell_details[i][j].g = 0.0
    cell_details[i][j].h = 0.0
    cell_details[i][j].parent_i = i
    cell_details[i][j].parent_j = j

    # Create an open list
    open_list = []
    heapq.heappush(open_list, (0.0, (i, j)))

    while open_list:
        p = heapq.heappop(open_list)
        i, j = p[1]
        closed_list[i][j] = True

        if j % 2 == 0:
            directions = directions_even
        else:
            directions = directions_odd

        for direction in directions:
            new_i, new_j = i + direction[0], j + direction[1]

            if is_valid(new_i, new_j):
                if is_destination(new_i, new_j, dests):
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    energy_for_path, current_energy = trace_path(cell_details, src, (new_i, new_j),current_energy)
                    total_energy_all_paths += energy_for_path  # Accumulate energy for each path
                    # Remove the reached destination from the list and continue searching
                    dests.remove((new_i, new_j))
                    if not dests:
                        print(f"Total energy consumed for all paths: {total_energy_all_paths}")
                        return
                    # Reset the search from the new destination
                    open_list = []
                    closed_list = [[False for _ in range(maze_size[1])] for _ in range(maze_size[0])]
                    heapq.heappush(open_list, (0.0, (new_i, new_j)))
                    cell_details[new_i][new_j].f = 0.0
                    cell_details[new_i][new_j].g = 0.0
                    cell_details[new_i][new_j].h = 0.0
                    cell_details[new_i][new_j].parent_i = new_i
                    cell_details[new_i][new_j].parent_j = new_j
                    break

                if not closed_list[new_i][new_j] and is_unblocked(grid, new_i, new_j, special_cells):
                    # Apply special cell effect before calculating new costs
                    apply_special_cell_effect(new_i, new_j, cell_details, special_cells, dests, [])

                    g_new = cell_details[i][j].g + cell_details[new_i][new_j].actual_energy
                    h_new = calculate_h_value(new_i, new_j, dests)
                    f_new = g_new + h_new

                    if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                        heapq.heappush(open_list, (f_new, (new_i, new_j)))
                        cell_details[new_i][new_j].f = f_new
                        cell_details[new_i][new_j].g = g_new
                        cell_details[new_i][new_j].h = h_new
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j

    print("Failed to find the Destination Cell")
    return

def main():
    # Define the grid (1 for unblocked, 0 for blocked)
    grid = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
        [0, 1, 1, 0, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    # Define the source and destinations
    src = [0, 0]
    dests = [(4, 3), (1, 4), (3, 7), (3, 9)]

    # Run A* Search Algorithm
    a_star_search(grid, src, dests)

if __name__ == "__main__":
    main()
