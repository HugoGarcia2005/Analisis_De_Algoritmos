# Proyecto Final 25B
# Equipo Tr3s
# Garcia Saldivar Hugo Gabriel
# Maciel Vargas Oswaldo Daniel

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import time
from PIL import Image, ImageTk

# --- IMPORTACIONES MODULARES ---
from src.utils import (
    get_unique_run_dir, show_graph_window, 
    GIF_DISPLAY_SIZE
)
from src.greedy.huffman import (
    quantize_image_data, calculate_frequencies, 
    build_huffman_tree, generate_huffman_codes, 
    save_huffman_bin_pure_codes
)
from src.divide_conquer.quadtree_dc import QuadtreeDivideAndConquer
from src.dynamic_prog.quadtree_dp import QuadtreeDynamicProgramming

# --- VARIABLES GLOBALES GUI ---
gif_frames_data = []
gif_animation_job = None
huffman_preview_image = None
quad_preview_image_static = None
current_gif_path = None 

# --- GUI UTILS ---
def load_huffman_preview(label, image_path):
    global huffman_preview_image
    try:
        img = Image.open(image_path)
        img.thumbnail(GIF_DISPLAY_SIZE, Image.Resampling.LANCZOS)
        huffman_preview_image = ImageTk.PhotoImage(img)
        label.config(image=huffman_preview_image, text="")
    except Exception as e:
        print(f"Error cargando preview huffman: {e}")
        label.config(text="Error al cargar imagen")

def load_static_image(label, image_path):
    global quad_preview_image_static
    try:
        img = Image.open(image_path)
        img.thumbnail(GIF_DISPLAY_SIZE, Image.Resampling.LANCZOS)
        quad_preview_image_static = ImageTk.PhotoImage(img)
        label.config(image=quad_preview_image_static, text="")
    except Exception as e:
        print(f"Error cargando imagen estatica: {e}")
        label.config(text="Error al cargar imagen")

def load_and_play_gif(gif_label, gif_path):
    global gif_frames_data, gif_animation_job
    if gif_animation_job:
        gif_label.after_cancel(gif_animation_job)
        gif_animation_job = None  
    gif_frames_data = []
    try:
        gif = Image.open(gif_path)
        for i in range(gif.n_frames):
            gif.seek(i)
            frame = gif.copy()
            frame.thumbnail(GIF_DISPLAY_SIZE, Image.Resampling.LANCZOS) 
            gif_frames_data.append(ImageTk.PhotoImage(frame))
        if gif_frames_data:
            gif_label.config(text="") 
            animate_gif_frame(gif_label, 0)
    except Exception as e:
        print(f"Error al cargar GIF: {e}")

def animate_gif_frame(gif_label, frame_index):
    global gif_frames_data, gif_animation_job
    if not gif_frames_data: return
    gif_label.config(image=gif_frames_data[frame_index])
    next_index = (frame_index + 1) % len(gif_frames_data)
    gif_animation_job = gif_label.after(500, animate_gif_frame, gif_label, next_index)

# --- THREADS DE EJECUCIÓN ---

def run_huffman_thread(image_path, run_dir, root, start_button, clear_button, target_tolerance, 
                       huffman_label, stats_label):
    try:
        print(f"\n--- INICIANDO HUFFMAN (Target Error: {target_tolerance}) ---")
        
        HUFFMAN_DIR = os.path.join(run_dir, "resultados_huffman")
        os.makedirs(HUFFMAN_DIR, exist_ok=True)
        
        steps = list(range(10, target_tolerance, 10))
        steps.append(target_tolerance)
        if target_tolerance == 0 and not steps: steps = [0]
        
        x_errors = []
        y_times = []
        y_sizes_bin = [] 
        y_sizes_png = []
        
        final_bin_size = 0
        final_png_size = 0
        final_time = 0
        
        image_orig = Image.open(image_path).convert('RGB')

        for step_error in steps:
            print(f"> Procesando Error = {step_error} ...")
            start_time = time.perf_counter()
            
            quantized_pixels, quantized_image = quantize_image_data(image_orig, step_error)
            freqs = calculate_frequencies(quantized_pixels)
            tree = build_huffman_tree(freqs)
            codes = generate_huffman_codes(tree)
            
            temp_bin_path = save_huffman_bin_pure_codes(quantized_pixels, codes, HUFFMAN_DIR, f"temp_{step_error}.bin")
            step_size_bin = os.path.getsize(temp_bin_path) / 1024
            
            temp_png_path = os.path.join(HUFFMAN_DIR, f"temp_{step_error}.png")
            quantized_image.save(temp_png_path)
            step_size_png = os.path.getsize(temp_png_path) / 1024
            
            if step_error != target_tolerance:
                os.remove(temp_bin_path)
                os.remove(temp_png_path)
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            
            x_errors.append(step_error)
            y_times.append(total_time)
            y_sizes_bin.append(step_size_bin)
            y_sizes_png.append(step_size_png)
            
            print(f"  Tiempo: {total_time*1000:.2f} ms | Bin: {step_size_bin:.1f}KB | PNG: {step_size_png:.1f}KB")
            
            if step_error == target_tolerance:
                print(">> Guardando resultados finales...")
                final_time = total_time 
                
                bin_path = os.path.join(HUFFMAN_DIR, "imagen_huffman.bin")
                if os.path.exists(temp_bin_path):
                    os.rename(temp_bin_path, bin_path)
                
                preview_path_final = os.path.join(HUFFMAN_DIR, f"vista_huffman_final.png")
                if os.path.exists(temp_png_path):
                    os.rename(temp_png_path, preview_path_final)
                
                final_bin_size = step_size_bin
                final_png_size = step_size_png
                
                root.after(0, lambda: load_huffman_preview(huffman_label, preview_path_final))
                
                stats_text = f"Peso (.bin): {final_bin_size:.2f} KB | Peso (.png): {final_png_size:.2f} KB\nTiempo: {final_time:.4f} s"
                root.after(0, lambda: stats_label.config(text=stats_text))

        root.after(0, lambda: show_graph_window(
            root, 
            "Complejidad Temporal (Huffman)", 
            "Nivel de Error (Tolerancia)", 
            "Tiempo (s)", 
            [("Huffman", x_errors, y_times, "o")]
        ))
        
        root.after(0, lambda: show_graph_window(
            root, 
            "Complejidad Espacial (Huffman)", 
            "Nivel de Error (Tolerancia)", 
            "Peso Archivo (KB)", 
            [("Peso .bin", x_errors, y_sizes_bin, "o"),
             ("Peso .png", x_errors, y_sizes_png, "s")]
        ))
        
        messagebox.showinfo("Éxito Huffman", "Proceso completado.")

    except Exception as e:
        print(f"Error en Huffman: {e}")
        messagebox.showerror("Error", f"Error en Huffman:\n{e}")
    finally:
        root.after(0, lambda: start_button.config(state="normal"))
        root.after(0, lambda: clear_button.config(state="normal"))


def run_quadtree_thread(image_path, max_n, run_dir, root, start_button, clear_button, 
                        gif_label, stats_label, gif_button):
    global current_gif_path
    try:
        print(f"\n--- INICIANDO QUADTREE (Max N: {max_n}) ---")
        
        root.after(0, lambda: gif_label.config(text="Procesando..."))
        
        QUADTREE_DIR = os.path.join(run_dir, "resultados_quadtree")
        GIF_DIR = os.path.join(QUADTREE_DIR, 'gif')
        FRAMES_DIR = os.path.join(QUADTREE_DIR, 'frames')
        os.makedirs(GIF_DIR, exist_ok=True)
        os.makedirs(FRAMES_DIR, exist_ok=True)

        depths_n = []
        times_dc = []
        times_dp = []
        sizes_png = [] 
        
        final_time_dc = 0
        final_file_size = 0 

        image = Image.open(image_path).convert('RGB')
        
        print("Tarea 1: Análisis de Complejidad")
        for n in range(1, max_n + 1):
            start_time_dc = time.perf_counter()
            qt_dc = QuadtreeDivideAndConquer(image, max_depth=n) 
            time_taken_dc = time.perf_counter() - start_time_dc
            
            start_time_dp = time.perf_counter()
            _ = QuadtreeDynamicProgramming(image, max_depth=n)
            time_taken_dp = time.perf_counter() - start_time_dp
            
            temp_img = qt_dc._create_image_from_depth(n)
            temp_path = os.path.join(QUADTREE_DIR, f"temp_{n}.png")
            temp_img.save(temp_path)
            size_kb = os.path.getsize(temp_path) / 1024
            sizes_png.append(size_kb)
            os.remove(temp_path) 
            
            depths_n.append(n)
            times_dc.append(time_taken_dc)
            times_dp.append(time_taken_dp)
            
            print(f"N={n} | D&C: {time_taken_dc*1000:.2f}ms | DP: {time_taken_dp*1000:.2f}ms | Size: {size_kb:.1f}KB")
            
            if n == max_n:
                final_time_dc = time_taken_dc 

        if depths_n:
            root.after(0, lambda: show_graph_window(
                root, 
                "Complejidad Temporal (Quadtree)", 
                "Profundidad (N)", 
                "Tiempo (s)", 
                [("Divide y Venceras", depths_n, times_dc, "o"), 
                 ("Programacion Dinamica", depths_n, times_dp, "s")]
            ))

            root.after(0, lambda: show_graph_window(
                root, 
                "Complejidad Espacial (Quadtree)", 
                "Profundidad (N)", 
                "Peso Imagen .png (KB)", 
                [("Divide y Venceras", depths_n, sizes_png, "o"),
                 ("Programacion Dinamica", depths_n, sizes_png, "s")] 
            ))

        print("Tarea 2: Generación Visual")
        quadtree_dc = QuadtreeDivideAndConquer(image, max_depth=max_n)
        gif_path_dc, final_img_path = quadtree_dc.create_gif('quadtree_dc', GIF_DIR, FRAMES_DIR)
        
        current_gif_path = gif_path_dc
        final_file_size = os.path.getsize(final_img_path) / 1024 

        root.after(0, lambda: load_static_image(gif_label, final_img_path))
        root.after(0, lambda: stats_label.config(text=f"Peso (.png): {final_file_size:.2f} KB\nTiempo: {final_time_dc:.4f} s"))
        root.after(0, lambda: gif_button.config(state="normal"))
        
        quadtree_dp = QuadtreeDynamicProgramming(image, max_depth=max_n)
        quadtree_dp.create_gif('quadtree_dp', GIF_DIR, FRAMES_DIR)
        
        print(f"Proceso Quadtree completado.")

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")
    finally:
        root.after(0, lambda: start_button.config(state="normal"))
        root.after(0, lambda: clear_button.config(state="normal"))

# --- GUI MAIN ---

def create_gui():
    root = tk.Tk()
    root.title("Compresión de Imágenes | Equipo Tr3s")
    root.geometry("1100x700") 

    BG_COLOR = "#3E3E3E"       
    FG_COLOR = "#E0E0E0"       
    FRAME_BG = "#2D2D2D"     
    BUTTON_BG = "#555555"    
    BUTTON_ACTIVE = "#666666" 
    DISABLED_BG = "#4A4A4A"   
    DISABLED_FG = "#888888"   
    ENTRY_BG = "#555555"       
    
    root.config(bg=BG_COLOR)

    style = ttk.Style()
    style.theme_use('clam') 
    style.configure('.', background=BG_COLOR, foreground=FG_COLOR, bordercolor=FRAME_BG)
    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
    style.configure('TLabelFrame', background=BG_COLOR, foreground=FG_COLOR, bordercolor=BUTTON_BG)
    style.configure('TLabelFrame.Label', background=BG_COLOR, foreground=FG_COLOR)
    style.configure('TButton', background=BUTTON_BG, foreground=FG_COLOR, bordercolor=BUTTON_BG)
    style.map('TButton',
        background=[('active', BUTTON_ACTIVE), ('disabled', DISABLED_BG)],
        foreground=[('disabled', DISABLED_FG)]
    )
    style.configure('TEntry', fieldbackground=ENTRY_BG, foreground=FG_COLOR, insertcolor=FG_COLOR, bordercolor=BUTTON_BG)
    
    style.configure('TSpinbox', fieldbackground="white", foreground="black", insertcolor="black", arrowcolor="black")
    style.map('TCombobox', 
              fieldbackground=[('readonly', 'white')],
              foreground=[('readonly', 'black')],
              selectbackground=[('readonly', '#cccccc')],
              selectforeground=[('readonly', 'black')])
    
    root.grid_rowconfigure(0, weight=1)  
    root.grid_rowconfigure(1, weight=10) 
    root.grid_columnconfigure(0, weight=2) 
    root.grid_columnconfigure(1, weight=3) 
    root.grid_columnconfigure(2, weight=3) 
    
    image_path_var = tk.StringVar()
    n_var = tk.IntVar(value=8) 
    algo_var = tk.StringVar() 

    frame_controls = ttk.LabelFrame(root, text="Configuración")
    frame_controls.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
    
    ttk.Label(frame_controls, text="Imagen:").pack(anchor="w", padx=5, pady=(10,0))
    path_entry = ttk.Entry(frame_controls, textvariable=image_path_var, state="readonly")
    path_entry.pack(fill=tk.X, padx=5, pady=2)
    
    lbl_orig_size = ttk.Label(frame_controls, text="Peso Original: -", anchor="w", font=("Arial", 9))

    def select_image():
        path = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")])
        if path:
            image_path_var.set(path)
            try:
                size_kb = os.path.getsize(path) / 1024
                lbl_orig_size.config(text=f"Peso Original: {size_kb:.2f} KB")
            except Exception as e:
                print(f"Error size: {e}")
                lbl_orig_size.config(text="Peso Original: Error")

    ttk.Button(frame_controls, text="Examinar...", command=select_image).pack(fill=tk.X, padx=5, pady=5)
    lbl_orig_size.pack(fill=tk.X, padx=5, pady=(0, 5)) 
    
    ttk.Separator(frame_controls, orient='horizontal').pack(fill='x', pady=10)

    lbl_param = ttk.Label(frame_controls, text="Profundidad Máxima (N):")
    lbl_param.pack(anchor="w", padx=5)
    
    spin_param = ttk.Spinbox(frame_controls, from_=1, to=12, textvariable=n_var, style='TSpinbox')
    spin_param.pack(fill=tk.X, padx=5, pady=2)
    
    ttk.Label(frame_controls, text="Algoritmo:").pack(anchor="w", padx=5, pady=(10,0))
    algo_combo = ttk.Combobox(frame_controls, textvariable=algo_var, state="readonly", style='TCombobox')
    algo_combo['values'] = ("Quadtree (D&C y DP)", "Huffman (Técnica Voraz)")
    algo_combo.current(0) 
    algo_combo.pack(fill=tk.X, padx=5, pady=2)
    
    def on_algo_change(event):
        if algo_var.get() == "Huffman (Técnica Voraz)":
            lbl_param.config(text="Factor de Error (0-100):")
            spin_param.config(from_=0, to=100)
        else:
            lbl_param.config(text="Profundidad Máxima (N):")
            spin_param.config(from_=1, to=12)

    algo_combo.bind("<<ComboboxSelected>>", on_algo_change)
    
    ttk.Separator(frame_controls, orient='horizontal').pack(fill='x', pady=20)
    
    start_button = ttk.Button(frame_controls, text="INICIAR PROCESO")
    start_button.pack(fill=tk.X, padx=5, pady=10, ipady=5)
    
    def open_gif_command():
        if current_gif_path and os.path.exists(current_gif_path):
            load_and_play_gif(gif_label, current_gif_path)
        else:
            messagebox.showerror("Error", "No se encontró el archivo GIF.")

    btn_view_gif = ttk.Button(frame_controls, text="Ver Animación GIF", state="disabled", command=open_gif_command)
    btn_view_gif.pack(fill=tk.X, padx=5, pady=10)
    
    clear_button = ttk.Button(frame_controls, text="Limpiar Todo")
    clear_button.pack(fill=tk.X, padx=5, pady=5)

    frame_gif = ttk.LabelFrame(root, text="Quadtree (D&C y DP)")
    frame_gif.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=10)
    
    gif_label = ttk.Label(frame_gif, text="Esperando...", anchor="center")
    gif_label.pack(fill=tk.BOTH, expand=True)
    
    lbl_quad_stats = ttk.Label(frame_gif, text="Peso (.png): - \nTiempo: -", anchor="center", font=("Arial", 10, "bold"))
    lbl_quad_stats.pack(fill=tk.X, pady=5)

    frame_huff = ttk.LabelFrame(root, text="Huffman (Técnica Voraz)")
    frame_huff.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)
    
    huffman_label = ttk.Label(frame_huff, text="Esperando...", anchor="center")
    huffman_label.pack(fill=tk.BOTH, expand=True)
    
    lbl_huff_stats = ttk.Label(frame_huff, text="Peso (.bin): - | Peso (.png): -\nTiempo: -", anchor="center", font=("Arial", 10, "bold"))
    lbl_huff_stats.pack(fill=tk.X, pady=5)

    def clear_results():
        global gif_animation_job, current_gif_path
        if gif_animation_job: gif_label.after_cancel(gif_animation_job)
        gif_label.config(image='', text="Esperando...")
        huffman_label.config(image='', text="Esperando...")
        lbl_quad_stats.config(text="Peso (.png): - \nTiempo: -")
        lbl_huff_stats.config(text="Peso (.bin): - | Peso (.png): -\nTiempo: -")
        lbl_orig_size.config(text="Peso Original: -")
        btn_view_gif.config(state="disabled")
        current_gif_path = None

    clear_button.config(command=clear_results)

    def start_analysis():
        img_path = image_path_var.get()
        param_val = n_var.get()
        selection = algo_var.get()

        if not img_path:
            messagebox.showwarning("Atención", "Selecciona una imagen primero.")
            return

        RUN_DIR = get_unique_run_dir("resultados")
        
        start_button.config(state="disabled")
        clear_button.config(state="disabled")
        btn_view_gif.config(state="disabled") 
        
        if selection == "Huffman (Técnica Voraz)":
            t = threading.Thread(
                target=run_huffman_thread,
                args=(img_path, RUN_DIR, root, start_button, clear_button, param_val, huffman_label, lbl_huff_stats),
                daemon=True
            )
            t.start()
        else:
            t = threading.Thread(
                target=run_quadtree_thread,
                args=(img_path, param_val, RUN_DIR, root, start_button, clear_button, gif_label, lbl_quad_stats, btn_view_gif),
                daemon=True
            )
            t.start()

    start_button.config(command=start_analysis)
    root.mainloop()

if __name__ == '__main__':

    create_gui()
