import multiprocessing
import tkinter as tk
import importlib
from utils.map_visualizer import MapVisualizer
import sys

def run_level(file_path, level):
    level_module_name = f"level{level}"
    level_module = importlib.import_module(level_module_name)
    run_function = getattr(level_module, "run")
    run_function(file_path, level)  # Pass level to the run function

class MainApp:
    def __init__(self):
        self.file_path = None
        self.city_map = None
        self.visualizer = None
        self.level = None  # Initialize self.level here
        self.show_menu()

    def show_menu(self):
        self.root = tk.Tk()
        self.root.title("Select Level")
        self.root.geometry("400x400")

        label = tk.Label(self.root, text="MENU", font=("Arial", 24, "bold"))
        label.pack(pady=20)

        for i in range(1, 5):
            tk.Button(self.root, text=f"Level {i}", font=("Arial", 14), command=lambda i=i: self.select_level(i)).pack(pady=5)

        tk.Button(self.root, text="Cancel", font=("Arial", 14), command=self.on_cancel).pack(pady=5)

        self.root.mainloop()

    def on_cancel(self):
        self.root.destroy()
        sys.exit()  # Exit the program

    def select_level(self, level):
        self.level = level  # Set level here
        self.root.destroy()
        self.show_file_selection()

    def show_file_selection(self):
        self.root = tk.Tk()
        self.root.title("Select Test Case")
        self.root.geometry("400x450")

        label = tk.Label(self.root, text=f"Select File for Level {self.level}", font=("Arial", 18, "bold"))
        label.pack(pady=20)

        for i in range(1, 6):
            file_name = f"input{i}_level{self.level}.txt"
            button = tk.Button(self.root, text=f"File {i}", font=("Arial", 14), command=lambda f=file_name: self.select_file(f))
            button.pack(pady=5)

        tk.Button(self.root, text="Cancel", font=("Arial", 14), command=self.on_cancel_file_selection).pack(pady=5)

        self.root.mainloop()

    def on_cancel_file_selection(self):
        self.root.destroy()
        self.show_menu()  # Go back to level selection menu

    def select_file(self, file_name):
        self.file_path = file_name
        self.root.destroy()
        self.initialize_visualizer()

    def initialize_visualizer(self):
        if self.file_path:
            visualizer = MapVisualizer(self.file_path, self.level)
            n, m, t, f, city_map = visualizer.read_maps(self.file_path)

            self.visualizer = MapVisualizer(city_map, self.level)
            self.city_map = city_map

            run_process = multiprocessing.Process(target=run_level, args=(self.file_path, self.level))
            run_process.start()
            run_process.join()

if __name__ == "__main__":
    MainApp()
