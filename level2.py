import heapq
import matplotlib.pyplot as plt
from tkinter import messagebox
import time
import tkinter as tk
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from map_visualizer import MapVisualizer

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid, start, goal, t):
    n, m = len(grid), len(grid[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    best_path = None
    best_g_score = float('inf')

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()

            if g_score[goal] <= t:
                return path
            elif g_score[goal] < best_g_score:
                best_path = path
                best_g_score = g_score[goal]
        
        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < n and 0 <= neighbor[1] < m and grid[neighbor[0]][neighbor[1]] != '-1':
                tentative_g_score = g_score[current] + 1 + (int(grid[neighbor[0]][neighbor[1]]) if grid[neighbor[0]][neighbor[1]].isdigit() else 0)
                
                if tentative_g_score <= t and (neighbor not in g_score or tentative_g_score < g_score[neighbor]):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

                # Update best path regardless of time constraint
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return best_path

def get_a_star(city_map, start, goal, t):
    path = a_star(city_map, start, goal, t)
    if path is None:
        return path, 0
    else:
        total = -1
        return_path = []
        #duyệt path trả về 
        for step in path:
            i,j = step
            return_path.append(step)
            total+= 1
            if city_map[i][j].isdigit() and int(city_map[i][j]) > 0:
                total += int(city_map[i][j])
            if total > t:
                return return_path,-1
            
        return path,1
    
def calcu_time( city_map, start, goal, t):
        path = a_star(city_map, start, goal, t)  # Use self to call the method
        if path is None:
            return 0
        else:
            total = -1
            for step in path:
                i, j = step
                total += 1
                if city_map[i][j].isdigit() and int(city_map[i][j]) > 0:
                    total += int(city_map[i][j])
            return total


def run(file_path, level):
    if not file_path:
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

        path_time = calcu_time(city_map, start, goal, t)

        if start is None or goal is None:
            print("Start or Goal not found in the city map.")
            return   
        
        path, return_flag = get_a_star(city_map, start, goal, t)
        toll_booth_flags = []  # Danh sách để lưu trữ trạng thái của các ô đặc biệt
        toll_booth_values = []  # Danh sách để lưu trữ giá trị của các ô đặc biệt
        toll_booth_positions = []  # Danh sách để lưu trữ vị trí của các ô đặc biệt
        if path is None:
            visualizer.display_map(city_map, path_time, 0)
            plt.pause(1)
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
                    visualizer.display_map(city_map, path_time,0, path=path, current_pos=step)
                    
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
                visualizer.display_map(city_map, path_time,0)
                
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
                    visualizer.display_map(city_map, path_time,0, path=path, current_pos=step)
                    
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
                visualizer.display_map(city_map, path_time,0)
                
                # Draw the path line from start to goal
                path_x = [step[1] for step in path]  # X-coordinates (columns)
                path_y = [step[0] for step in path]  # Y-coordinates (rows)
                
                # Overlay path on top of the map
                visualizer.ax.plot(path_x, path_y, color='moccasin', linewidth=3.5)
                plt.draw()
                plt.pause(0.1)
                messagebox.showinfo("Result", "Limit time.")

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
