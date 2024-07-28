import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

class MapVisualizer:
    def __init__(self, city_map, level):
        self.n, self.m = len(city_map), len(city_map[0])
        self.city_maps = [city_map]
        self.current_level = level - 1  # Adjusting for 0-based indexing
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        # Define color map for different types of cells
        self.cmap = ListedColormap(['white', 'darkgray', 'palegreen', 'lightpink', 'powderblue','gold' ])
        self.norm = BoundaryNorm([0, 1, 2, 3, 4, 5, 6], self.cmap.N)
        self.time_input = None  # Initialize time_input attribute

    def display_map(self, city_map,path_time,path_fuel ,  path=None, current_pos=None):
        self.ax.clear()
        
        # Convert city_map to a 2D NumPy array
        city_map_array = np.array(city_map, dtype=str)
        
        # Print details for debugging
        if city_map_array.ndim != 2:
            raise ValueError("city_map_array is not 2D, it has shape: {}".format(city_map_array.shape))
        
        n, m = city_map_array.shape

        # Convert city_map to map_array
        map_array = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                if city_map[i][j] == '0':
                    map_array[i][j] = 0  # Path
                elif city_map[i][j] == '-1':
                    map_array[i][j] = 1  # Building
                elif isinstance(city_map[i][j], str) and city_map[i][j][0] =='S':
                    map_array[i][j] = 2  # Start
                elif isinstance(city_map[i][j], str) and  city_map[i][j][0] =='G':
                    map_array[i][j] = 3  # Goa
                elif city_map[i][j].isdigit() and int(city_map[i][j]) > 0:
                    map_array[i][j] = 4  # Toll Booth
                elif isinstance(city_map[i][j], str) and len(city_map[i][j]) > 1 and city_map[i][j][0] == 'F' :
                    map_array[i][j] = 5

        

        # Display the city map
        self.ax.imshow(map_array, cmap=self.cmap, norm=self.norm, interpolation='none', origin='upper')

        if self.current_level + 1 != 1:  # Check if level is 2
                self.ax.set_title(f'Level {self.current_level + 1} (Time Input: {self.time_input}, Path Time: {path_time})')
                if self.current_level + 1 > 2:
                    self.ax.set_title(f'Level {self.current_level + 1} (Time Input: {self.time_input}, Path Time: {path_time}) \n (Total fuel consumed: {path_fuel})')
        else:
            self.ax.set_title(f'Level {self.current_level + 1}')
        
        self.ax.set_xticks(np.arange(-0.5, m, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
        self.ax.grid(which='minor', color='gray', linestyle='-', linewidth=1)
        self.ax.tick_params(which='minor', size=0)

        # Add text labels to the cells
        for i in range(n):
            for j in range(m):
                if isinstance(city_map[i][j], str) and city_map[i][j][0] =='S':
                    self.ax.text(j, i, city_map[i][j], ha='center', va='center', color='black',fontsize = 13.5)
                elif isinstance(city_map[i][j], str) and city_map[i][j][0] == 'G':
                    self.ax.text(j, i, city_map[i][j], ha='center', va='center', color='black',fontsize = 13.5)
                elif city_map[i][j].isdigit() and int(city_map[i][j]) > 0:
                    self.ax.text(j, i, city_map[i][j], ha='center', va='center', color='black',fontsize =13.5)
                elif isinstance(city_map[i][j], str) and len(city_map[i][j]) > 1 and city_map[i][j][0] == 'F':
                    self.ax.text(j, i, city_map[i][j], ha='center', va='center', color='black',fontsize =13.5)

        if path:
            # Overlay path on top of the map
            for (i, j) in path:
                if city_map[i][j] == '0':
                    self.ax.imshow(np.full_like(map_array, np.nan), cmap=ListedColormap(['none']), alpha=0.2, interpolation='none', origin='upper')
                elif city_map[i][j].isdigit() and int(city_map[i][j]) > 0:
                    pass  # Skip overlaying on toll booth cells

        if current_pos:
            # Highlight the current position of 'S'
            s_array = np.zeros((n, m))
            s_array[current_pos[0], current_pos[1]] = 2  # Start position in green
            self.ax.imshow(s_array, cmap=ListedColormap(['none', 'green']), alpha=0., interpolation='none', origin='upper')
        
        self.fig.canvas.draw_idle()
        plt.pause(0.05)
        return
    
    def read_maps(self, file_path):
        with open(file_path, 'r') as file:
            first_line = file.readline().strip().split()
            n, m, t, f = map(int, first_line)
            self.time_input = t  # Lưu trữ thời gian vào thuộc tính
            city_map = [file.readline().strip().split() for _ in range(n)]
        
        return n, m, t, f, city_map
    
    def on_key(self, event):
        if event.key == 'escape':
            plt.close(self.fig)
