import matplotlib.pyplot as plt
from collections import deque

def bfs(start, goal, city_map):
    rows, cols = len(city_map), len(city_map[0])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
    queue = deque([start])
    visited = set()
    visited.add(start)
    came_from = {start: None}
    
    while queue:
        current = queue.popleft()
        
        if current == goal:
            break
        
        for direction in directions:
            next_row, next_col = current[0] + direction[0], current[1] + direction[1]
            if 0 <= next_row < rows and 0 <= next_col < cols and city_map[next_row][next_col] != '-1':
                next_node = (next_row, next_col)
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append(next_node)
                    came_from[next_node] = current
    
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    
    return path

def run():
    input_file_name = input("Please enter the input file path: ")

    city_map = []
    with open(input_file_name, 'r') as file:
        for line in file:
            city_map.append(line.strip().split(','))

    start = (1, 1)  # Adjust start position as needed
    goal = (8, 3)   # Adjust goal position as needed

    path = bfs(start, goal, city_map)
    print("Path found:", path)
    display_map(city_map, path)

def display_map(city_map, path):
    rows, cols = len(city_map), len(city_map[0])
    fig, ax = plt.subplots()
    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    ax.xaxis.tick_top()

    for y in range(rows):
        for x in range(cols):
            if city_map[y][x] == '-1':
                ax.add_patch(plt.Rectangle((x, y), 1, 1, color='black'))
            elif (y, x) in path:
                ax.add_patch(plt.Rectangle((x, y), 1, 1, color='blue'))
            else:
                ax.add_patch(plt.Rectangle((x, y), 1, 1, color='white', edgecolor='black'))

    plt.gca().invert_yaxis()
    plt.show()