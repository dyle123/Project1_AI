import heapq

def parse_input(file_path):
    with open(file_path, 'r') as file:
        n, m, t = map(int, file.readline().strip().split())
        grid = []
        for line in file:
            row = line.strip().split()
            if row:  
                if len(row) != m:
                    raise ValueError(f"Row length {len(row)} does not match specified m {m}. Row content: {row}")
                grid.append(row)
    if len(grid) != n:
        raise ValueError(f"Number of rows {len(grid)} does not match specified n {n}.")
    return n, m, t, grid

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid, start, goal, t):
    n, m = len(grid), len(grid[0])
    open_set = []
    heapq.heappush(open_set, (0, start, 0))  # (g_score, current_node, total_time)
    came_from = {}
    g_score = {start: 0}
    paths = []  # To store valid paths to the goal

    while open_set:
        current_g, current, current_time = heapq.heappop(open_set)
        
        if current == goal:
            # Reconstruct the path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()

            # Add the found path to the paths list with its g_score and total_time
            paths.append((path, len(path), current_time))  # (path, length, total_time)
            continue  # Don't break; keep looking for other paths

        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < n and 0 <= neighbor[1] < m and grid[neighbor[0]][neighbor[1]] != '-1':
                tentative_g_score = g_score[current] + 1 + (int(grid[neighbor[0]][neighbor[1]]) if grid[neighbor[0]][neighbor[1]].isdigit() else 0)
                
                if tentative_g_score <= t and (neighbor not in g_score or tentative_g_score < g_score[neighbor]):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(open_set, (tentative_g_score, neighbor, tentative_g_score))
    
    # If no paths were found
    if not paths:
        return None

    # Evaluate paths to find the best one
    best_path = None
    shortest_length = float('inf')
    best_time = float('inf')

    for path, length, total_time in paths:
        if total_time <= t:  # Path that satisfies the time constraint
            if length < shortest_length or (length == shortest_length and total_time < best_time):
                best_path = path
                shortest_length = length
                best_time = total_time

    # If no valid path was found within the time constraint, return the shortest one regardless of time
    if best_path is None:
        best_path = min(paths, key=lambda x: x[1])[0]  # Return the shortest path found

    return best_path



def main():
    input_file = 'input_level2.txt'
    output_file = 'output_level2.txt'
    
    try:
        n, m, t, grid = parse_input(input_file)
    except ValueError as e:
        print(f"Error parsing input file: {e}")
        return
    
    start = None
    goal = None
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 'S':
                start = (i, j)
            elif grid[i][j] == 'G':
                goal = (i, j)
    
    if not start or not goal:
        print("Invalid input: Start or Goal not defined.")
        return
    
    path = a_star_search(grid, start, goal, t)
    
    if path:
        with open(output_file, 'w') as file:
            file.write('S\n')
            for cell in path:
                file.write(f"({cell[0]}, {cell[1]}) ")
            file.write('\n')
    else:
        with open(output_file, 'w') as file:
            file.write("No valid path found.\n")

if __name__ == "__main__":
    main()
