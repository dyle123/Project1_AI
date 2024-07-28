import heapq
import matplotlib.pyplot as plt
from tkinter import messagebox
import time
import tkinter as tk
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from map_visualizer import MapVisualizer

class Node:
    def __init__(self, x, y, fuel, cost, time, parent=None):
        self.x = x
        self.y = y
        self.fuel = fuel
        self.cost = cost
        self.time = time
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

def a_star_search(grid, start, goal, max_fuel, max_time, gas_stations, toll_booths, paths=None, agent_id=''):
    rows, cols = grid.shape
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    toll_map = { (i, j): cost for (i, j, cost) in toll_booths }

    def is_within_bounds(x, y):
        return 0 <= x < rows and 0 <= y < cols

    def get_neighbors(x, y):
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_within_bounds(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def heuristic(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    open_set = []
    heapq.heappush(open_set, Node(start[0], start[1], max_fuel, 0, 0))
    came_from = {}
    cost_so_far = {}
    came_from[(start[0], start[1], max_fuel)] = None
    cost_so_far[(start[0], start[1], max_fuel)] = 0

    while open_set:
        current = heapq.heappop(open_set)
        if (current.x, current.y) == (goal[0], goal[1]) and current.time <= max_time:
            path = []
            while current:
                path.append((current.x, current.y))
                current = came_from[(current.x, current.y, current.fuel)]
            return path[::-1]

        for neighbor in get_neighbors(current.x, current.y):
            nx, ny = neighbor
            if grid[nx, ny] == -1:
                continue

            new_fuel = current.fuel - 1
            new_time = current.time + 1  # Time to move to the next cell
            if (nx, ny) in gas_stations:
                new_fuel = max_fuel
                new_time += 1  # Additional time to refuel

            toll_cost = toll_map.get((nx, ny), 0)
            new_cost = current.cost + 1 + toll_cost
            new_time += toll_cost  # Additional time spent at the toll booth

            if new_fuel >= 0 and new_time <= max_time and ((nx, ny, new_fuel) not in cost_so_far or new_cost < cost_so_far[(nx, ny, new_fuel)]):
                if paths and agent_id != 'S':
                    s_path = paths.get('S', [])
                    if new_time < len(s_path) and (nx, ny) == s_path[new_time]:
                        continue  # Avoid collision by not moving into S agent's path

                    # Check for potential collisions
                    collision = False
                    for adj_agent_id, adj_path in paths.items():
                        if adj_agent_id == agent_id or new_time >= len(adj_path):
                            continue
                        adj_x, adj_y = adj_path[new_time]
                        if (nx, ny) == (adj_x, adj_y) or (nx, ny) in [(adj_x + dx, adj_y + dy) for dx, dy in directions]:
                            collision = True
                            break

                    if collision:
                        continue  # Skip this move if it causes collision

                cost_so_far[(nx, ny, new_fuel)] = new_cost
                priority = new_cost + heuristic(nx, ny, goal[0], goal[1])
                heapq.heappush(open_set, Node(nx, ny, new_fuel, new_cost, new_time))
                came_from[(nx, ny, new_fuel)] = current

    return []


def run_agents_to_goals(grid, agents, goals, max_fuel, max_time, gas_stations, toll_booths):
    results = {}
    paths = {}
    
    # First, find the path for the 'S' agent
    s_agent = next(agent for agent in agents if agent[2] == 'S')
    s_start = (s_agent[0], s_agent[1])
    s_goal = next(goal for goal in goals if goal[2] == 'G')
    s_path = a_star_search(grid, s_start, s_goal, max_fuel, max_time, gas_stations, toll_booths, None, 'S')
    paths['S'] = s_path
    results['S'] = s_path

    # Then, find paths for other agents
    for agent in agents:
        if agent[2] == 'S':
            continue
        agent_id = agent[2]
        start = (agent[0], agent[1])
        goal = next((g for g in goals if g[2] == 'G' + agent_id[1:]), None)
        if goal:
            goal = (goal[0], goal[1])
            path = a_star_search(grid, start, goal, max_fuel, max_time, gas_stations, toll_booths, paths, agent_id)
            results[agent_id] = path

    # Sort the results by agent_id
    sorted_results = dict(sorted(results.items(), key=lambda item: (len(item[0]), item[0])))

    return sorted_results

def simulate_agents(grid, agents, goals, max_fuel, max_time, gas_stations, toll_booths):
    results = run_agents_to_goals(grid, agents, goals, max_fuel, max_time, gas_stations, toll_booths)
    
    # Initialize positions
    positions = {agent[2]: (agent[0], agent[1]) for agent in agents}
    completed = set()
    time_step = 0
    
    # Simulate step by step
    while time_step < max_time:
        next_positions = {}
        for agent_id, path in results.items():
            if agent_id in completed:
                continue
            if time_step < len(path) - 1:
                next_pos = path[time_step + 1]
                next_positions[agent_id] = next_pos
            else:
                completed.add(agent_id)

        # Check for collisions
        occupied_positions = set()
        collisions = set()
        for agent_id, pos in next_positions.items():
            if pos in occupied_positions:
                collisions.add(agent_id)
            else:
                occupied_positions.add(pos)

        # Resolve collisions by making conflicting agents wait
        final_positions = {}
        for agent_id, pos in next_positions.items():
            if agent_id in collisions:
                final_positions[agent_id] = positions[agent_id]  # Stay in the same place
            else:
                final_positions[agent_id] = pos

        # Update positions
        positions.update(final_positions)
        
        # Check if all agents have reached their goals
        if len(completed) == len(agents):
            break
        
        time_step += 1

    return results

def parse_input(file_path):
    with open(file_path, 'r') as file:
        n, m, t, f = map(int, file.readline().strip().split())
        grid = []
        agents = []
        goals = []
        gas_stations = []
        toll_booths = []
        pairs = {}
        for i in range(n):
            row = file.readline().strip().split()
            for j in range(m):
                if row[j].startswith('S') and len(row[j]) > 1 and row[j][1:].isdigit():
                    agent_key = row[j]
                    agents.append((i, j, agent_key))
                    if agent_key not in pairs:
                        pairs[agent_key] = None
                    row[j] = 0
                elif row[j].startswith('G') and len(row[j]) > 1 and row[j][1:].isdigit():
                    goal_key = row[j]
                    goals.append((i, j, row[j]))
                    agent_key = 'S' + goal_key[1:]
                    if agent_key in pairs:
                        pairs[agent_key] = (i, j, goal_key)
                    else:
                        pairs[agent_key] = (i, j, goal_key)
                    row[j] = 0
                elif row[j] == 'S':
                    agents.append((i, j, 'S'))
                    row[j] = 0
                elif row[j] == 'G':
                    goals.append((i, j, 'G'))
                    row[j] = 0
                elif row[j].startswith('F') and len(row[j]) > 1 and row[j][1:].isdigit():
                    gas_stations.append((i, j))
                    row[j] = 0
                elif row[j].isdigit():
                    if int(row[j]) > 0:
                        toll_booths.append((i, j, int(row[j])))
                    row[j] = int(row[j])
                else:
                    row[j] = int(row[j])
            grid.append(row)

    for agent_key, goal in pairs.items():
        if goal is None:
            raise ValueError(f"Agent {agent_key} does not have a corresponding goal.")
    
    return np.array(grid), t, f, agents, goals, gas_stations, toll_booths

def print_grid(grid, agents, goals, gas_stations, toll_booths, path):
    grid_copy = grid.copy()
    for agent in agents:
        grid_copy[agent[0], agent[1]] = 'A'
    for goal in goals:
        grid_copy[goal[0], goal[1]] = 'G'
    for station in gas_stations:
        grid_copy[station[0], station[1]] = 'F'
    for booth in toll_booths:
        grid_copy[booth[0], booth[1]] = 'T'

    for node in path:
        grid_copy[node[0], node[1]] = '*'

    print('\n'.join([' '.join(map(str, row)) for row in grid_copy]))



def run(file_path, level):
    if not file_path:
        return
    else:
        # Reload the city map
        visualizer = MapVisualizer(file_path, level)
        grid, max_toll, max_fuel, agents, goals, gas_stations, toll_booths = parse_input(file_path)
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

        #path_time, path_fuel = calcu_time_fuel(city_map,grid, start, goal, t,f,gas_stations, toll_booths)

        if start is None or goal is None:
            print("Start or Goal not found in the city map.")
            return   
        
        #path, return_flag = get_a_star(city_map,grid, start, goal, t, f,gas_stations, toll_booths)
        toll_booth_flags = []  # Danh sách để lưu trữ trạng thái của các ô đặc biệt
        toll_booth_values = []  # Danh sách để lưu trữ giá trị của các ô đặc biệt
        toll_booth_positions = []  # Danh sách để lưu trữ vị trí của các ô đặc biệt
        path = None
        if path is None:
            output_file_path = file_path.replace("input", "output")
            with open(output_file_path, 'w') as output_file:
                results = simulate_agents(grid, agents, goals, max_fuel, max_toll, gas_stations, toll_booths)
                for agent_id, path in results.items():
                    if path:
                        output_file.write(f"{agent_id}\n")
                        for node in path:
                            output_file.write(f"({node[0]},{node[1]}) ")
                        output_file.write("\n")


            visualizer.display_map(city_map,0,0)
            plt.pause(0.5)
            answer = messagebox.askyesno("Repeat", "Do you want to try another file?")
            plt.close()  # Ensure this closes the matplotlib figure
            if answer:
                from main import MainApp
                main_app = MainApp()
                main_app.show_file_selection()  # Allow user to select a new file
        
    
    # Close the Tkinter window if it’s still open
    root = tk.Tk()
    root.quit()
    root.destroy()
