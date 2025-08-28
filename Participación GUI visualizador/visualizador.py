import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# Parámetros generales
ANCHO = 800
ALTO = 300
N_BARRAS = 40
VAL_MIN, VAL_MAX = 5, 100
RETARDO_MS = 5  # velocidad de animación

# Algoritmo: Selection Sort
def selection_sort_steps(data, draw_callback):
    n = len(data)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            draw_callback(activos=[i, j, min_idx]); yield
            if data[j] < data[min_idx]:
                min_idx = j
        data[i], data[min_idx] = data[min_idx], data[i]
        draw_callback(activos=[i, min_idx]); yield
    draw_callback(activos=[])

#Algoritmo: Bubble Sort
def bubble_sort_steps (data, draw_callback):
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            draw_callback(activos=[i, j]); yield #
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
        draw_callback(activos=[i, j]); yield #
    draw_callback(activos=[]) #
    #return data

#Algoritmo: Quick sort
def quick_sort_steps(data, draw_callback, start=0, end=None):
    if end is None:
        end = len(data) - 1
    
    if start >= end:
        draw_callback(activos=[])
        yield
        return
    mid = (start + end) // 2
    pivote_val = sorted([data[start], data[mid], data[end]])[1]
    pivote_idx = start if data[start] == pivote_val else mid if data[mid] == pivote_val else end
    
    data[pivote_idx], data[end] = data[end], data[pivote_idx]
    draw_callback(activos=[end, pivote_idx])
    yield
    
    i = start - 1
    for j in range(start, end):
        draw_callback(activos=[j, end, i])
        yield
        if data[j] <= data[end]:
            i += 1
            data[i], data[j] = data[j], data[i]
            draw_callback(activos=[i, j, end])
            yield
    data[i + 1], data[end] = data[end], data[i + 1]
    pivote_pos = i + 1
    draw_callback(activos=[pivote_pos])
    yield
    
    yield from quick_sort_steps(data, draw_callback, start, pivote_pos - 1)
    yield from quick_sort_steps(data, draw_callback, pivote_pos + 1, end)

def merge_sort_steps(data, draw_callback, start=0, end=None):
    if end is None:
        end = len(data) - 1
    
    if start >= end:
        draw_callback(activos=[])
        yield
        return
    mid = (start + end) // 2
    yield from merge_sort_steps(data, draw_callback, start, mid)
    yield from merge_sort_steps(data, draw_callback, mid + 1, end)
    yield from merge(data, start, mid, end, draw_callback)

def merge(data, start, mid, end, draw_callback):
    izquierda = data[start:mid + 1]
    derecha = data[mid + 1:end + 1]
    
    i = j = 0
    k = start
    
    while i < len(izquierda) and j < len(derecha):
        draw_callback(activos=[start + i, mid + 1 + j, k])
        yield
        
        if izquierda[i] <= derecha[j]:
            data[k] = izquierda[i]
            i += 1
        else:
            data[k] = derecha[j]
            j += 1
        k += 1
        draw_callback(activos=[k - 1])
        yield
    
    while i < len(izquierda):
        data[k] = izquierda[i]
        i += 1
        k += 1
        draw_callback(activos=[k - 1])
        yield
    
    while j < len(derecha):
        data[k] = derecha[j]
        j += 1
        k += 1
        draw_callback(activos=[k - 1])
        yield
    draw_callback(activos=list(range(start, end + 1)))
    yield

#Selector de algoritmos
def algorithm_selector():
    algorithm = combo.get()
    if algorithm == "Selection Sort":
        ordenar_selection()
    elif algorithm == "Bubble Sort":
        ordenar_bubble()
    elif algorithm == "Quick Sort":
        ordenar_quick()
    elif algorithm == "Merge Sort":
        ordenar_merge()
    else:
        messagebox.showwarning("Algoritmo no seleccionado", "⚠️ Selecciona un algoritmo")
    return None


# Función de dibujo
def dibujar_barras(canvas, datos, activos=None):
    canvas.delete("all")
    if not datos: return
    n = len(datos)
    margen = 10
    ancho_disp = ANCHO - 2 * margen
    alto_disp = ALTO - 2 * margen
    w = ancho_disp / n
    esc = alto_disp / max(datos)
    for i, v in enumerate(datos):
        x0 = margen + i * w
        x1 = x0 + w * 0.9
        h = v * esc
        y0 = ALTO - margen - h
        y1 = ALTO - margen
        color = "#4e79a7"
        if activos and i in activos:
            color = "#f28e2b"
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
    canvas.create_text(6, 6, anchor="nw", text=f"n={len(datos)}", fill="#666")

# Aplicación principal
datos = []
root = tk.Tk()
root.title("Visualizador - Selection Sort")
canvas = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
canvas.pack(padx=10, pady=10)

def generar():
    global datos
    random.seed(time.time())
    datos = [random.randint(VAL_MIN, VAL_MAX) for _ in range(N_BARRAS)]
    dibujar_barras(canvas, datos)

def ordenar_selection():
    if not datos: return
    gen = selection_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    def paso():
        try:
            next(gen)
            root.after(RETARDO_MS, paso)
        except StopIteration:
            pass
    paso()

def ordenar_bubble():
    if not datos: return
    gen = bubble_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    def paso():
        try:
            next(gen)
            root.after(RETARDO_MS, paso)
        except StopIteration:
            pass
    paso()

def ordenar_quick():
    if not datos: return
    gen = quick_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    def paso():
        try:
            next(gen)
            root.after(RETARDO_MS, paso)
        except StopIteration:
            pass
    paso()

def ordenar_merge():
    if not datos: return
    gen = merge_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    def paso():
        try:
            next(gen)
            root.after(RETARDO_MS, paso)
        except StopIteration:
            pass
    paso()

panel = tk.Frame(root)
panel.pack(pady=6)
tk.Button(panel, text="Generar", command=generar).pack(side="left", padx=5)
algorithms = ["Selection Sort","Bubble Sort","Quick Sort","Merge Sort"]
combo = ttk.Combobox(panel, values=algorithms)
combo.set("Selecciona algoritmo") 
combo.pack(side="left", padx=5)
tk.Button(panel, text="Ejecutar", command=algorithm_selector).pack(side="bottom", padx=5)

generar()
root.mainloop()
