import tkinter as tk
from tkinter import font
import numpy as np
import itertools

VELOCIDAD_ANIMACION = 1

COLORS = {
    "background": "#2E2E2E",
    "frame_bg": "#3C3C3C",
    "text": "#EAEAEA",
    "button_bg": "#555555",
    "button_active": "#6A6A6A",
    "entry_bg": "#3C3C3C",
    "error": "#FF5555"
}

def es_cuadrado_latino_np(matriz):
    n = matriz.shape[0]

    for i in range(n):
        if len(np.unique(matriz[i, :])) != n: 
            return False

    for j in range(n):
        if len(np.unique(matriz[:, j])) != n: 
            return False
    return True

combinaciones_iter = None
total_matrices = 0
matrix_index = 0
found_squares = []
matrix_labels = []
n_val = 0

def process_next_matrix():
    global matrix_index, found_squares
    
    try:
        combinacion = next(combinaciones_iter)
        matrix_index += 1
        
        matriz_np = np.array(combinacion).reshape((n_val, n_val))
        for i in range(n_val):
            for j in range(n_val):
                matrix_labels[i][j].config(text=str(matriz_np[i, j]))
        
        status_label.config(text=f"Generando matriz {matrix_index} de {total_matrices}...")
        
        if es_cuadrado_latino_np(matriz_np):
            found_squares.append({
                "index": matrix_index,
                "latino_num": len(found_squares) + 1,
                "matrix": matriz_np
            })
            
        window.after(VELOCIDAD_ANIMACION, process_next_matrix)

    except StopIteration:
        finalize_process()

def finalize_process():
    """Se ejecuta cuando todas las matrices han sido procesadas."""
    status_label.config(text=f"Proceso finalizado. Se encontraron {len(found_squares)} cuadrados latinos.")
    start_button.config(state="normal", text="Comenzar")

    if found_squares:
        options = [f"Matriz #{item['index']} (Latino #{item['latino_num']})" for item in found_squares]
        selected_square_var.set(options[0])
        
        option_menu = tk.OptionMenu(results_frame, selected_square_var, *options, command=display_selected_square)
        option_menu.config(bg=COLORS["button_bg"], fg=COLORS["text"], activebackground=COLORS["button_active"], relief=tk.FLAT, highlightthickness=0)
        option_menu["menu"].config(bg=COLORS["button_bg"], fg=COLORS["text"])
        option_menu.pack(pady=10)
        
        display_selected_square(options[0])

def display_selected_square(selected_value):
    target_index = int(selected_value.split(' ')[1].replace('#', ''))
    
    for square_info in found_squares:
        if square_info["index"] == target_index:
            matrix_to_display = square_info["matrix"]
            for i in range(n_val):
                for j in range(n_val):
                    matrix_labels[i][j].config(text=str(matrix_to_display[i, j]))
            break

def start_process():
    """Función que se llama al presionar el botón 'Comenzar'."""
    global n_val, combinaciones_iter, total_matrices, matrix_index, found_squares, matrix_labels

    try:
        n_val = int(n_entry.get())
        if not (1 <= n_val <= 10):
            status_label.config(text="Error: Introduce un número entre 1 y 10.", fg=COLORS["error"])
            return
    except ValueError:
        status_label.config(text="Error: Entrada no válida.", fg=COLORS["error"])
        return

    for widget in matrix_frame.winfo_children(): widget.destroy()
    for widget in results_frame.winfo_children(): widget.destroy()
    status_label.config(text="", fg=COLORS["text"])
    
    found_squares = []
    matrix_index = 0
    total_matrices = n_val**(n_val*n_val)
    numeros = range(1, n_val + 1)
    combinaciones_iter = itertools.product(numeros, repeat=n_val*n_val)

    matrix_labels = []
    font_size = max(10, 40 - n_val * 5)
    cell_font = font.Font(family="Courier", size=font_size, weight="bold")
    for i in range(n_val):
        row_labels = []
        for j in range(n_val):
            label = tk.Label(matrix_frame, text="-", font=cell_font, width=3,
                             bg=COLORS["frame_bg"], fg=COLORS["text"], anchor="center")
            label.grid(row=i, column=j, padx=10, pady=10)
            row_labels.append(label)
        matrix_labels.append(row_labels)
        
    start_button.config(state="disabled", text="Procesando...")
    
    window.after(100, process_next_matrix)


window = tk.Tk()
window.title("Generador de Cuadrados Latinos")
window.geometry("600x700")
window.configure(bg=COLORS["background"])

main_frame = tk.Frame(window, bg=COLORS["background"], padx=20, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

top_frame = tk.Frame(main_frame, bg=COLORS["background"])
top_frame.pack(fill=tk.X, pady=(0, 10))

tk.Label(top_frame, text="Valor de n:", font=("Helvetica", 12), bg=COLORS["background"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=(0, 10))
n_entry = tk.Entry(top_frame, width=5, bg=COLORS["entry_bg"], fg=COLORS["text"], insertbackground=COLORS["text"], relief=tk.FLAT, font=("Helvetica", 12))
n_entry.pack(side=tk.LEFT, padx=(0, 20))
start_button = tk.Button(top_frame, text="Comenzar", command=start_process, 
                         bg=COLORS["button_bg"], fg=COLORS["text"], relief=tk.FLAT,
                         activebackground=COLORS["button_active"], activeforeground=COLORS["text"],
                         font=("Helvetica", 11))
start_button.pack(side=tk.LEFT)

matrix_frame = tk.Frame(main_frame, bg=COLORS["frame_bg"], padx=10, pady=10)
matrix_frame.pack(pady=10)

status_label = tk.Label(main_frame, text="Introduce un valor para ""n"" (1-3)", font=("Helvetica", 11), bg=COLORS["background"], fg=COLORS["text"])
status_label.pack(pady=(10, 0))
results_frame = tk.Frame(main_frame, bg=COLORS["background"])
results_frame.pack(pady=10)
selected_square_var = tk.StringVar(window)

window.mainloop()