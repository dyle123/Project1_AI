import time
from collections import deque
from utils.map_visualizer import MapVisualizer
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import sys
import tkinter as tk
from tkinter import messagebox
import heapq

def bfs(city_map):
    start, goal = None, None
    for i, row in enumerate(city_map):
        for j, val in enumerate(row):
            if val == 'S':
                start = (i, j)
            elif val == 'G':
                goal = (i, j)

    if start is None or goal is None:
        print("Start or Goal not found in the city map.")
        return None

    rows, cols = len(city_map), len(city_map[0])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    queue = deque([start])
    visited = set()
    visited.add(start)
    came_from = {start: None}
    
    while queue:
        current = queue.popleft()
        
        if current == goal:
            return reconstruct_path(came_from, start, goal)
        
        for direction in directions:
            next_row, next_col = current[0] + direction[0], current[1] + direction[1]
            if 0 <= next_row < rows and 0 <= next_col < cols and city_map[next_row][next_col] != '-1':
                next_node = (next_row, next_col)
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append(next_node)
                    came_from[next_node] = current

    return None

def dfs(city_map):
    start, goal = None, None
    for i, row in enumerate(city_map):
        for j, val in enumerate(row):
            if val == 'S':
                start = (i, j)
            elif val == 'G':
                goal = (i, j)

    if start is None or goal is None:
        print("Start or Goal not found in the city map.")
        return None

    stack = [start]  # Stack for DFS
    originate = {start: None}
    rows, cols = len(city_map), len(city_map[0])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while stack:
        curr = stack.pop()

        if curr == goal:
            return reconstruct_path(originate, start, goal)

        for direction in directions:
            next_row, next_col = curr[0] + direction[0], curr[1] + direction[1]
            if 0 <= next_row < rows and 0 <= next_col < cols and city_map[next_row][next_col] != '-1':
                next_node = (next_row, next_col)
                if next_node not in originate:
                    stack.append(next_node)
                    originate[next_node] = curr

    return None

def uniform_cost_search(city_map):
    import heapq
    start, goal = None, None
    for i, row in enumerate(city_map):
        for j, val in enumerate(row):
            if val == 'S':
                start = (i, j)
            elif val == 'G':
                goal = (i, j)

    if start is None or goal is None:
        print("Start or Goal not found in the city map.")
        return None

    pq = [(0, start)]  # Priority queue for UCS (cost, node)
    cost_so_far = {start: 0}
    originate = {start: None}
    rows, cols = len(city_map), len(city_map[0])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while pq:
        current_cost, curr = heapq.heappop(pq)

        if curr == goal:
            return reconstruct_path(originate, start, goal)

        for direction in directions:
            next_row, next_col = curr[0] + direction[0], curr[1] + direction[1]
            if 0 <= next_row < rows and 0 <= next_col < cols and city_map[next_row][next_col] != '-1':
                next_node = (next_row, next_col)
                new_cost = current_cost + 1  # Assuming each step has a cost of 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    heapq.heappush(pq, (new_cost, next_node))
                    originate[next_node] = curr

    return None

def reconstruct_path(came_from, start, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path

def reconstruct_path(originate, start, goal):
    path = []
    curr = goal

    while curr != start:
        path.append(curr)
        curr = originate[curr]

    path.append(start)
    path.reverse()

    return path

def select_algorithm():
    root = tk.Tk()
    root.title("Select Algorithm")
    root.geometry("400x500")

    def on_algorithm_select(algo):
        nonlocal selected_algorithm
        selected_algorithm = algo
        root.quit()  # Close the Tkinter window

    selected_algorithm = None

    label = tk.Label(root, text="Select Algorithm", font=("Arial", 18, "bold"))
    label.pack(pady=20)

    # Create buttons for each algorithm
    algorithms = ['BFS', 'DFS', 'UCS', 'GBFS', 'A*']
    for algo in algorithms:
        button = tk.Button(root, text=algo, font=("Arial", 14), command=lambda a=algo: on_algorithm_select(a))
        button.pack(pady=5, padx=30)

    # Add a cancel button
    cancel_button = tk.Button(root, text="Cancel", font=("Arial", 14), command=root.quit)
    cancel_button.pack(pady=10)

    root.mainloop()

    # Destroy the root window after mainloop ends
    root.destroy()
    
    if selected_algorithm is None:
        print("No algorithm selected.")
        sys.exit()
        plt.close()
    
    return selected_algorithm
def greedy_best_first_search(city_map, start, goal, heuristic):
    line = [(heuristic(start, goal), start)]  # Priority queue
    originate = {start: None}
    
    while line:
        _, curr = heapq.heappop(line)
        
        if curr == goal:
            break
        
        for neighbor in get_neighbors(city_map, curr):
            if neighbor not in originate:
                priority = heuristic(neighbor, goal)
                heapq.heappush(line, (priority, neighbor))
                originate[neighbor] = curr
    
    if goal not in originate:
        return None  # No path found
    else:
        return reconstruct_path(originate, start, goal)

def get_neighbors(grid, node):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []

    x, y = node

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] != '-1':
            neighbors.append((nx, ny))

    return neighbors



def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star(grid, start, goal):
    n, m = len(grid), len(grid[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        
        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < n and 0 <= neighbor[1] < m and grid[neighbor[0]][neighbor[1]] != '-1':
                # Chi phí di chuyển (g) cho mỗi ô
                tentative_g_score = g_score[current] + 1  # Giả định mỗi bước có chi phí là 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # Nếu không tìm thấy đường đi



def run(file_path, level):
    if not file_path:
        print("No file path provided.")
        return
    while True:
        # Reload the city map
        visualizer = MapVisualizer(file_path, level)
        n, m, t, f, city_map = visualizer.read_maps(file_path)

        if not city_map or not all(isinstance(row, list) for row in city_map):
            print("city_map is not a 2D list.")
            return

        row_lengths = set(len(row) for row in city_map)
        if len(row_lengths) != 1:
            print("Rows of city_map have different lengths.")
            return

        start = None
        goal = None
        for i, row in enumerate(city_map):
            for j, val in enumerate(row):
                if val == 'S':
                    start = (i, j)
                elif val == 'G':
                    goal = (i, j)

        if start is None or goal is None:
            print("Start or Goal not found in the city map.")
            return   
        
        
        # Hiển thị giao diện chọn thuật toán
        algorithm = select_algorithm()
        if not algorithm:
            continue

        # Run selected algorithm
        if algorithm == 'BFS':
            path = bfs(city_map)
        elif algorithm == 'DFS':
            path = dfs(city_map)
        elif algorithm == 'UCS':
            path = uniform_cost_search(city_map)
        elif algorithm == 'GBFS':
            path = greedy_best_first_search(city_map, start, goal, heuristic)
        elif algorithm == 'A*':
            path = a_star(city_map, start, goal)
        else:
            print("Unknown algorithm")
            continue
        toll_booth_flags = []  # Danh sách để lưu trữ trạng thái của các ô đặc biệt
        toll_booth_values = []  # Danh sách để lưu trữ giá trị của các ô đặc biệt
        toll_booth_positions = []  # Danh sách để lưu trữ vị trí của các ô đặc biệt

        if path is None:
            visualizer.display_map(city_map)
            plt.pause(1)
            messagebox.showinfo("Result", "No path found or limit time.")
        else:
    
                # Animate the movement of the Start block
                for step in path:
                    i, j = step

                    # Clear previous start position
                    if toll_booth_flags:
                     # Lấy ô đặc biệt cuối cùng để cập nhật lại
                        last_toll_booth_position = toll_booth_positions.pop()
                        last_toll_booth_value = toll_booth_values.pop()
                        city_map[last_toll_booth_position[0]][last_toll_booth_position[1]] = last_toll_booth_value
                        toll_booth_flags.pop()  # Cập nhật trạng thái của ô đặc biệt
                    else:
                        city_map[start[0]][start[1]] = '0'

                     # Set new start position
                    if (city_map[i][j].isdigit() and int(city_map[i][j]) > 0) or (isinstance(city_map[i][j], str) and len(city_map[i][j]) > 1 and city_map[i][j][0] == 'F'):
                        # Lưu giá trị và vị trí của ô đặc biệt
                        toll_booth_positions.append((i, j))
                        toll_booth_values.append(city_map[i][j])
                        toll_booth_flags.append(True)  # Đánh dấu rằng có ô đặc biệt

                    city_map[i][j] = 'S'
                                    
                    # Display the updated map
                    visualizer.display_map(city_map, path=path, current_pos=step)
                    
                    # Update start position
                    start = (i, j)
                    
                    # Pause to visualize movement
                    time.sleep(0.1)
                    
                    # Redraw the figure
                    plt.draw()
                    plt.pause(0.1)

                # Reset the map to show initial positions of 'S' and 'G'
                city_map[start[0]][start[1]] = '0'
                city_map[goal[0]][goal[1]] = 'G'
                city_map[path[0][0]][path[0][1]] = 'S'
                visualizer.display_map(city_map)
                
                # Draw the path line from start to goal
                path_x = [step[1]  for step in path]  # X-coordinates (columns)
                path_y = [step[0]  for step in path]  # Y-coordinates (rows)
                
                # Overlay path on top of the map
                visualizer.ax.plot(path_x, path_y, color='moccasin', linewidth=3.5)
                plt.draw()
                plt.pause(0.1)
        
        answer = messagebox.askyesno("Repeat", "Do you want to try another file?")
        plt.close()  # Ensure this closes the matplotlib figure
        if answer:
            from main import MainApp
            main_app = MainApp()
            main_app.show_file_selection()  # Allow user to select a new file
        else:
            break

    # Close the Tkinter window if it’s still open
    root = tk.Tk()
    root.quit()
    root.destroy()