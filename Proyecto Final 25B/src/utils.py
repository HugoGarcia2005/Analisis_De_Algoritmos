# src/utils.py
import os
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- CONSTANTES GLOBALES ---
PADDING = 0
OUTPUT_SCALE = 1
ERROR_THRESHOLD = 15 
GIF_DISPLAY_SIZE = (320, 320)

def get_unique_run_dir(base_name="resultados"):
    counter = 1
    while True:
        dir_name = f"{base_name}_{counter}"
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            return dir_name
        counter += 1

def show_graph_window(root, title, x_label, y_label, data_series):
    new_window = tk.Toplevel(root)
    new_window.title(title)
    new_window.geometry("600x500")
    new_window.config(bg="#3E3E3E")

    fig = plt.Figure(figsize=(6, 5), dpi=100, facecolor="#3E3E3E")
    ax = fig.add_subplot(111, facecolor="#2D2D2D")
    
    for label, x_val, y_val, marker_style in data_series:
        ax.plot(x_val, y_val, marker=marker_style, label=label)

    ax.set_title(title, color="#E0E0E0")
    ax.set_xlabel(x_label, color="#E0E0E0")
    ax.set_ylabel(y_label, color="#E0E0E0")
    ax.tick_params(colors="#E0E0E0")
    ax.grid(True, color='#555555')
    
    for spine in ax.spines.values():
        spine.set_color('#555555')

    legend = ax.legend()
    if legend:
        legend.get_frame().set_facecolor('#555555')
        for text in legend.get_texts():
            text.set_color('#E0E0E0')

    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)