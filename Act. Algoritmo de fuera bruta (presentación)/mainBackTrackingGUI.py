import tkinter as tk
from tkinter import font
import numpy as np
import time

VELOCIDAD_ANIMACION = 0.01

COLORS = {
    "background": "#2E2E2E",
    "frame_bg": "#3C3C3C",
    "text": "#EAEAEA",
    "button_bg": "#555555",
    "button_active": "#6A6A6A",
    "entry_bg": "#3C3C3C",
    "error": "#FF5555"
}

found_squares = []
contador_latinos = 0

def es_valido(matriz, fila, col, num):
    if num in matriz[fila, :]: return False
    if num in matriz[:, col]: return False
    return True

def resolver_con_backtracking_gui(matriz, fila, col):
    global contador_latinos
    n = matriz.shape[0]

    if fila == n:
        contador_latinos += 1
        
        solucion = matriz.copy()
        found_squares.append({
            "latino_num": contador_latinos,
            "matrix": solucion
        })
        
        status_label.config(text=f"¡Encontrado Cuadrado Latino #{contador_latinos}!")
        for i in range(n):
            for j in range(n):
                matrix_labels[i][j].config(text=str(solucion[i, j]))
        
        window.update_idletasks()
        time.sleep(VELOCIDAD_ANIMACION)
        return

    siguiente_fila, siguiente_columna = (fila, col + 1) if col + 1 < n else (fila + 1, 0)

    for num in range(1, n + 1):
        if es_valido(matriz, fila, col, num):
            matriz[fila, col] = num
            resolver_con_backtracking_gui(matriz, siguiente_fila, siguiente_columna)
            matriz[fila, col] = 0 

def finalize_process():
    status_label.config(text=f"Búsqueda finalizada. Se encontraron {len(found_squares)} cuadrados latinos.")
    start_button.config(state="normal", text="Comenzar")

    if found_squares:
        options = [f"Cuadrado Latino #{item['latino_num']}" for item in found_squares]
        selected_square_var.set(options[0])
        
        option_menu = tk.OptionMenu(results_frame, selected_square_var, *options, command=display_selected_square)
        option_menu.config(bg=COLORS["button_bg"], fg=COLORS["text"], activebackground=COLORS["button_active"], relief=tk.FLAT, highlightthickness=0)
        option_menu["menu"].config(bg=COLORS["button_bg"], fg=COLORS["text"])
        option_menu.pack(pady=10)
        
        display_selected_square(options[0])

def display_selected_square(selected_value):
    target_num = int(selected_value.split('#')[-1])
    
    for square_info in found_squares:
        if square_info["latino_num"] == target_num:
            matrix_to_display = square_info["matrix"]
            n = matrix_to_display.shape[0]
            for i in range(n):
                for j in range(n):
                    matrix_labels[i][j].config(text=str(matrix_to_display[i, j]))
            break

def start_process():
    global n_val, found_squares, contador_latinos, matrix_labels

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
    contador_latinos = 0
    
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
    status_label.config(text=f"Iniciando búsqueda con backtracking para n={n_val}...")
    window.update_idletasks() 

    matriz_inicial = np.zeros((n_val, n_val), dtype=int)
    resolver_con_backtracking_gui(matriz_inicial, 0, 0)
    
    finalize_process()

window = tk.Tk()
window.title("Generador de Cuadrados Latinos (Backtracking)")
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

status_label = tk.Label(main_frame, text="Introduce un valor para 'n' (1 - 10)", font=("Helvetica", 11), bg=COLORS["background"], fg=COLORS["text"])
status_label.pack(pady=(10, 0))
results_frame = tk.Frame(main_frame, bg=COLORS["background"])
results_frame.pack(pady=10)
selected_square_var = tk.StringVar(window)

window.mainloop()