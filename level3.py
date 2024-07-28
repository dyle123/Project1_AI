import heapq
import matplotlib.pyplot as plt
from tkinter import messagebox
import time
import tkinter as tk
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from utils.map_visualizer import MapVisualizer



def a_star(grid, start, goal, committed_time, max_fuel, gas_stations, toll_booths):
    rows, cols = len(grid), len(grid[0])
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(node):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []
        for d in directions:
            neighbor = (node[0] + d[0], node[1] + d[1])
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor[0]][neighbor[1]] != -1:
                result.append(neighbor)
        return result

    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, max_fuel, [start]))

    while open_set:
        _, cost, current, fuel, path = heapq.heappop(open_set)
        
        if current == goal and cost <= committed_time:
            return path, cost

        for neighbor in get_neighbors(current):
            new_cost = cost + 1
            new_fuel = fuel - 1

            if new_fuel < 0:
                continue

            for gas_station in gas_stations:
                if neighbor == (gas_station[0], gas_station[1]):
                    new_fuel = max_fuel
                    new_cost += gas_station[2]

            for toll_booth in toll_booths:
                if neighbor == (toll_booth[0], toll_booth[1]):
                    new_cost += toll_booth[2]

            if new_cost <= committed_time:
                heuristic_cost = heuristic(neighbor, goal)
                heapq.heappush(open_set, (new_cost + heuristic_cost, new_cost, neighbor, new_fuel, path + [neighbor]))


    return None, None


def parse_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    n, m, committed_time, max_fuel = map(int, lines[0].strip().split())

    grid = []
    agents = []
    goals = []
    gas_stations = []
    toll_booths = []

    for i in range(1, len(lines)):
        line = lines[i].strip().split()
        grid_row = []
        for j, value in enumerate(line):
            if value == 'S':
                agents.append((i - 1, j, 'S'))
                grid_row.append(0)
            elif value == 'G':
                goals.append((i - 1, j))
                grid_row.append(0)
            elif value.startswith('F'):
                gas_stations.append((i - 1, j, int(value[1:])))
                grid_row.append(0)
            elif value.isdigit():
                toll_booths.append((i - 1, j, int(value)))
                grid_row.append(int(value))
            else:
                grid_row.append(int(value))
        grid.append(grid_row)

    return grid, committed_time, max_fuel, agents, goals, gas_stations, toll_booths


def get_a_star(city_map,grid, start, goal, t, f,gas_stations, toll_booths):
    path,cost = a_star(grid, start, goal, t, f,gas_stations, toll_booths)
    if path is None:
        return path, 0
    else:
        total_fuel = f+1
        total_time = -1
        return_path = []
        #duyệt path trả về 
        for step in path:
            i,j = step
            return_path.append(step)
            total_time += 1
            total_fuel -= 1
            if city_map[i][j].isdigit() and int(city_map[i][j]) > 0:
                total_time += int(city_map[i][j])
            if isinstance(city_map[i][j], str) and len(city_map[i][j]) > 1 and city_map[i][j][0] == 'F':
                total_time += int(city_map[i][j][1:])
                total_fuel = f
            if total_time  > t and (total_fuel < 0 and step != goal):
                return return_path,-1
            elif total_time > t:
                return return_path, -2
            elif total_fuel < 0 and step != goal:
                return return_path, -3
            
        return path,1
    
def calcu_time_fuel( city_map,grid, start, goal, t, f,gas_stations, toll_booths):
        path,cost = a_star(grid, start, goal, t,f,gas_stations, toll_booths)  # Use self to call the method
        if path is None:
            return None,None
        else:
            total_fuel_consumed = -1
            total_time = -1
            for step in path:
                i, j = step
                total_fuel_consumed += 1
                total_time += 1
                if city_map[i][j].isdigit() and int(city_map[i][j]) > 0:
                    total_time += int(city_map[i][j])
                if isinstance(city_map[i][j], str) and len(city_map[i][j]) > 1 and city_map[i][j][0] == 'F':
                    total_time += int(city_map[i][j][1:])
            return total_time, total_fuel_consumed


def run(file_path, level):
    if not file_path:
        return
    x= 0
    while True:
        # Reload the city map
        visualizer = MapVisualizer(file_path, level)
        grid, t, f, start, goal, gas_stations, toll_booths = parse_input(file_path)
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
        x+=1
        if x == 1: 
            path_time, path_fuel = calcu_time_fuel(city_map,grid, start, goal, t,f,gas_stations, toll_booths)

        if start is None or goal is None:
            print("Start or Goal not found in the city map.")
            return   
        
        path, return_flag = get_a_star(city_map,grid, start, goal, t, f,gas_stations, toll_booths)
        toll_booth_flags = []  # Danh sách để lưu trữ trạng thái của các ô đặc biệt
        toll_booth_values = []  # Danh sách để lưu trữ giá trị của các ô đặc biệt
        toll_booth_positions = []  # Danh sách để lưu trữ vị trí của các ô đặc biệt
        if path is None:
            visualizer.display_map(city_map, path_time,path_fuel)
            plt.pause(0.5)
            messagebox.showinfo("Result", "No path found.")
        else:
            

            if return_flag == 1:
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
                    visualizer.display_map(city_map, path_time, path_fuel, path=path, current_pos=step)
                    
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
                visualizer.display_map(city_map, path_time,path_fuel)
                
                # Draw the path line from start to goal
                path_x = [step[1]  for step in path]  # X-coordinates (columns)
                path_y = [step[0]  for step in path]  # Y-coordinates (rows)
                
                # Overlay path on top of the map
                visualizer.ax.plot(path_x, path_y, color='moccasin', linewidth=3.5)
                plt.draw()
                plt.pause(0.1)
            else:
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
                    visualizer.display_map(city_map, path_time, path=path, current_pos=step)
                    
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
                visualizer.display_map(city_map, path_time,path_fuel)
                
                # Draw the path line from start to goal
                path_x = [step[1] for step in path]  # X-coordinates (columns)
                path_y = [step[0] for step in path]  # Y-coordinates (rows)
                
                # Overlay path on top of the map
                visualizer.ax.plot(path_x, path_y, color='moccasin', linewidth=3.5)
                plt.draw()
                plt.pause(0.1)
                if return_flag == -1:
                    messagebox.showinfo("Result", "Limit time and Limit fuel.")
                elif return_flag == -2:
                    messagebox.showinfo("Result", "Limit time.")
                elif return_flag == -3:
                    messagebox.showinfo("Result", "Limit fuel.")

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
