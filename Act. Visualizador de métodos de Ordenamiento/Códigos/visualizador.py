import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

ANCHO = 800
ALTO = 300
MIN_BARS, MAX_BARS = 3, 1_000
N_BARRAS = 40  
VAL_MIN, VAL_MAX = 5, 100
RETARDO_MS = 50  

COLOR_FONDO = "#333333"
COLOR_BOTONES = "#555555"
COLOR_TEXTO = "#FFFFFF"
COLOR_BOTON_ACCION = "#555555"
COLOR_BARRAS = "#67D618"
COLOR_BARRAS_ACTIVAS = "#6418D6"

tiempo_inicio = 0
tiempo_fin = 0
temporizador_activo = False

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

def bubble_sort_steps(data, draw_callback):
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            draw_callback(activos=[i, j]); yield
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
        draw_callback(activos=[i, j]); yield
    draw_callback(activos=[])

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
    draw_callback(activos=[])
    yield

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
    draw_callback(activos=[])
    yield

def iniciar_temporizador():
    global tiempo_inicio, temporizador_activo
    tiempo_inicio = time.time()
    temporizador_activo = True
    actualizar_tiempo_label("Tiempo: 0.000s")

def detener_temporizador():
    global tiempo_fin, temporizador_activo
    tiempo_fin = time.time()
    temporizador_activo = False
    tiempo_transcurrido = (tiempo_fin - tiempo_inicio) * 1000
    actualizar_tiempo_label(f"Tiempo: {tiempo_transcurrido:.2f}ms")

def actualizar_tiempo_label(texto):
    tiempo_label.config(text=texto)

def algorithm_selector():
    global temporizador_activo
    
    if temporizador_activo:
        detener_temporizador()
    
    algorithm = combo.get()
    if algorithm == "Selection Sort":
        gen = selection_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    elif algorithm == "Bubble Sort":
        gen = bubble_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    elif algorithm == "Quick Sort":
        gen = quick_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    elif algorithm == "Merge Sort":
        gen = merge_sort_steps(datos, lambda activos=None: dibujar_barras(canvas, datos, activos))
    else:
        messagebox.showwarning("Algoritmo no seleccionado", "⚠️ Selecciona un algoritmo")
        return
    
    iniciar_temporizador()
    
    def paso():
        try:
            next(gen)
            root.after(retardo_var.get(), paso)
        except StopIteration:
            detener_temporizador()
    
    paso()

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
        color = COLOR_BARRAS
        if activos and i in activos:
            color = COLOR_BARRAS_ACTIVAS
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
    canvas.create_text(6, -1, anchor="nw", text=f"N={len(datos)}", fill=COLOR_TEXTO)

def generar():
    global datos, temporizador_activo
    
    if temporizador_activo:
        detener_temporizador()
    
    random.seed(time.time())
    datos = [random.randint(VAL_MIN, VAL_MAX) for _ in range(N_BARRAS)]
    dibujar_barras(canvas, datos)
    actualizar_tiempo_label("Tiempo: -- ms")

def change_n():
    global N_BARRAS, temporizador_activo
    
    if temporizador_activo:
        detener_temporizador()
    
    try:
        val = int(entry.get())
        if val < MIN_BARS or val > MAX_BARS:
            raise ValueError
        if val == N_BARRAS:
            messagebox.showwarning("Alerta", "⚠️ Ya se generaron este número de barras")
            return
        else:
            N_BARRAS = val
            generar()
    except ValueError:
        messagebox.showwarning("Valor inválido", f"⚠️ Ingresa un número entero entre {MIN_BARS} y {MAX_BARS}")

def shuffle_data():
    global datos, temporizador_activo
    
    if temporizador_activo:
        detener_temporizador()
    
    random.shuffle(datos)
    dibujar_barras(canvas, datos)
    actualizar_tiempo_label("Tiempo: --")

datos = []
root = tk.Tk()
root.title("Visualizador de Algoritmos de Ordenamiento")
root.configure(bg=COLOR_FONDO)

style = ttk.Style()
style.theme_use('clam') 

style.configure('TCombobox', 
    fieldbackground=COLOR_BOTONES,  
    background=COLOR_BOTONES,       
    foreground=COLOR_TEXTO,         
    selectbackground=COLOR_BOTONES,  
    selectforeground=COLOR_TEXTO)  

style.map('TCombobox', 
    fieldbackground=[('readonly', COLOR_BOTONES)],
    background=[('readonly', COLOR_BOTONES)],
    foreground=[('readonly', COLOR_TEXTO)])

frame_superior = tk.Frame(root, bg=COLOR_FONDO)
frame_superior.pack(fill="x", padx=10, pady=5)

frame_medio = tk.Frame(root, bg=COLOR_FONDO)
frame_medio.pack(fill="both", expand=True, padx=10, pady=5)

frame_inferior = tk.Frame(root, bg=COLOR_FONDO)
frame_inferior.pack(fill="x", padx=10, pady=5)

frame_tiempo = tk.Frame(root, bg=COLOR_FONDO)
frame_tiempo.pack(fill="x", padx=10, pady=(10, 0))

tiempo_label = tk.Label(frame_tiempo, text="Tiempo: --", bg=COLOR_FONDO, fg=COLOR_TEXTO, font=('Arial', 12, 'bold'))
tiempo_label.pack(side="right", padx=10)

tk.Label(frame_superior, text="Algoritmo:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=5)
algorithms = ["Selection Sort", "Bubble Sort", "Quick Sort", "Merge Sort"]
combo = ttk.Combobox(frame_superior, values=algorithms, width=20)
combo.set("Selecciona algoritmo")
combo.pack(side="left", padx=5)

tk.Label(frame_superior, text="Número de barras:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=(100, 5))
entry_var = tk.IntVar(value=N_BARRAS)
entry = tk.Entry(frame_superior, textvariable=entry_var, width=5, bg=COLOR_BOTONES, fg=COLOR_TEXTO)
entry.pack(side="left", padx=5)
change_n_btn = tk.Button(frame_superior, text="Cambiar", command=change_n,bg=COLOR_BOTON_ACCION, fg=COLOR_TEXTO)
change_n_btn.pack(side="left", padx=5)

tk.Label(frame_superior, text="Genera nuevos datos para N:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=(100, 5))
generate_btn = tk.Button(frame_superior, text="Generar", command=generar,bg=COLOR_BOTON_ACCION, fg=COLOR_TEXTO)
generate_btn.pack(side="left", padx=5)

canvas = tk.Canvas(frame_medio, width=ANCHO, height=ALTO, bg=COLOR_FONDO, highlightthickness=0)
canvas.pack(fill="both", expand=True)

tk.Label(frame_inferior, text="Mezclar elementos actuales:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=5)
shuffle_btn = tk.Button(frame_inferior, text="Shuffle", command=shuffle_data,bg=COLOR_BOTON_ACCION, fg=COLOR_TEXTO)
shuffle_btn.pack(side="left", padx=5)

tk.Label(frame_inferior, text="0ms", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=(20, 5))
retardo_var = tk.IntVar(value=RETARDO_MS)
retardo_slider = tk.Scale(frame_inferior, from_=0, to=200, orient="horizontal", variable=retardo_var, length=300, bg=COLOR_BOTONES, fg=COLOR_TEXTO, highlightthickness=0)
retardo_slider.pack(side="left", padx=5)
tk.Label(frame_inferior, text="200ms", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=5)

tk.Label(frame_inferior, text="Comenzar ordenamiento:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=(20, 5))
sort_btn = tk.Button(frame_inferior, text="Ordenar", command=algorithm_selector, bg=COLOR_BOTON_ACCION, fg=COLOR_TEXTO)
sort_btn.pack(side="left", padx=5)

generar()
root.mainloop()