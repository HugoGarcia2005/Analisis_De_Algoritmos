# Proyecto Final 25B
# Equipo Tr3s
# Garcia Saldivar Hugo Gabriel
# Maciel Vargas Oswaldo Daniel

from PIL import Image, ImageDraw, ImageTk
import time 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import shutil 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import heapq 

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

# Huffman
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char 
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def quantize_image_data(image, tolerance):
    if tolerance <= 0:
        return list(image.getdata()), image
    
    pixels = list(image.getdata())
    quantized_pixels = []
    
    for r, g, b in pixels:
        new_r = (r // tolerance) * tolerance
        new_g = (g // tolerance) * tolerance
        new_b = (b // tolerance) * tolerance
        quantized_pixels.append((new_r, new_g, new_b))
        
    quantized_img = Image.new(image.mode, image.size)
    quantized_img.putdata(quantized_pixels)
    
    return quantized_pixels, quantized_img

def calculate_frequencies(pixels):
    freqs = {}
    for p in pixels:
        freqs[p] = freqs.get(p, 0) + 1
    return freqs

def build_huffman_tree(freqs):
    priority_queue = [HuffmanNode(char, freq) for char, freq in freqs.items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)

        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(priority_queue, merged)

    return priority_queue[0] if priority_queue else None

def generate_huffman_codes(node, current_code="", code_map=None):
    if code_map is None: code_map = {}
    if node is None: return
    if node.char is not None:
        code_map[node.char] = current_code
        return
    generate_huffman_codes(node.left, current_code + "0", code_map)
    generate_huffman_codes(node.right, current_code + "1", code_map)
    return code_map

def save_huffman_bin_pure_codes(pixels, code_map, output_folder, filename="imagen_huffman.bin"):
    bin_path = os.path.join(output_folder, filename)
    
    bit_string_list = []
    for p in pixels:
        bit_string_list.append(code_map[p])
    full_bit_string = "".join(bit_string_list)
    
    extra_padding = 8 - (len(full_bit_string) % 8)
    if extra_padding == 8: extra_padding = 0
    full_bit_string += ("0" * extra_padding)
    
    byte_array = bytearray()
    byte_array.append(extra_padding) 
    
    for i in range(0, len(full_bit_string), 8):
        byte = full_bit_string[i:i+8]
        byte_array.append(int(byte, 2))
        
    with open(bin_path, 'wb') as f:
        f.write(byte_array)
        
    return bin_path

# Quadtree
def weighted_average(hist):
    total = sum(hist)
    value, error = 0, 0
    if total > 0:
        value = sum(i * x for i, x in enumerate(hist)) / total
        error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
        error = error ** 0.5
    return value, error

def color_from_histogram(hist):
    r, re = weighted_average(hist[:256])
    g, ge = weighted_average(hist[256:512])
    b, be = weighted_average(hist[512:768])
    e = re * 0.2989 + ge * 0.5870 + be * 0.1140
    return (int(r), int(g), int(b)), e

class QuadtreeNode(object):
    def __init__(self, img, box, depth):
        self.box = box
        self.depth = depth
        self.children = None
        self.leaf = False
        image = img.crop(box)
        self.width, self.height = image.size
        hist = image.histogram()
        self.color, self.error = color_from_histogram(hist)

    def is_leaf(self):
        return self.leaf

    def split(self, img):
        l, t, r, b = self.box
        lr = int(l + (r - l) / 2)
        tb = int(t + (b - t) / 2)
        tl = QuadtreeNode(img, (l, t, lr, tb), self.depth + 1)
        tr = QuadtreeNode(img, (lr, t, r, tb), self.depth + 1)
        bl = QuadtreeNode(img, (l, tb, lr, b), self.depth + 1)
        br = QuadtreeNode(img, (lr, tb, r, b), self.depth + 1)
        self.children = [tl, tr, bl, br]

class QuadtreeBase(object):
    def __init__(self, image):
        self.root = None
        self.width, self.height = image.size
        self.max_depth = 0 

    def get_leaf_nodes(self, depth):
        if depth > self.max_depth:
            depth = self.max_depth
        leaf_nodes = []
        def get_leaf_nodes_recursion(node, target_depth):
            if node.is_leaf() or node.depth == target_depth:
                leaf_nodes.append(node)
            elif node.children is not None:
                for child in node.children:
                    get_leaf_nodes_recursion(child, target_depth)
        get_leaf_nodes_recursion(self.root, depth)
        return leaf_nodes

    def _create_image_from_depth(self, depth):
        m = OUTPUT_SCALE
        dx, dy = (PADDING, PADDING)
        image = Image.new('RGB', (int(self.width * m + dx), int(self.height * m + dy)))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width * m, self.height * m), (0, 0, 0))
        leaf_nodes = self.get_leaf_nodes(depth)
        for node in leaf_nodes:
            l, t, r, b = node.box
            box = (l * m + dx, t * m + dy, r * m - 1, b * m - 1)
            draw.rectangle(box, node.color)
        return image

    def create_gif(self, base_name, gif_dir, frames_dir, duration=500, loop=0):
        folder_name = f"{base_name}_frames"
        frames_folder_path = os.path.join(frames_dir, folder_name)
        os.makedirs(frames_folder_path, exist_ok=True)
        
        gif_file_path = os.path.join(gif_dir, f"{base_name}.gif")
        images = []
        
        end_product_image = self._create_image_from_depth(self.max_depth)
        final_img_path = os.path.join(gif_dir, f"{base_name}_final.png")
        end_product_image.save(final_img_path)
        
        for i in range(self.max_depth + 1):
            image = self._create_image_from_depth(i)
            images.append(image)
            try:
                frame_path = os.path.join(frames_folder_path, f"frame_{i:02d}.png")
                image.save(frame_path)
            except Exception as e:
                print(f"Advertencia: No se pudo guardar el fotograma {frame_path}. Error: {e}")
        
        for _ in range(3):
            images.append(end_product_image)
            
        print(f"Creando GIF en '{gif_file_path}'...")
        images[0].save(
            gif_file_path, 
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=loop)
        
        return gif_file_path, final_img_path

class QuadtreeDivideAndConquer(QuadtreeBase):
    def __init__(self, image, max_depth=10):
        super().__init__(image)
        self.root = QuadtreeNode(image, image.getbbox(), 0)
        self.max_depth = 0 
        self._build_tree_dc(image, self.root, max_depth)

    def _build_tree_dc(self, image, node, max_depth):
        if (node.depth >= max_depth) or (node.error <= ERROR_THRESHOLD):
            if node.depth > self.max_depth:
                self.max_depth = node.depth
            node.leaf = True
            return
        node.split(image)
        for child in node.children:
            self._build_tree_dc(image, child, max_depth)

class QuadtreeDynamicProgramming(QuadtreeBase):
    def __init__(self, image, max_depth=10):
        super().__init__(image)
        self.root = QuadtreeNode(image, image.getbbox(), 0)
        self._build_full_tree_dp(image, self.root, max_depth)
        self._prune_tree_dp(self.root)
        self.max_depth = 0
        self._update_max_depth(self.root)

    def _build_full_tree_dp(self, image, node, max_depth):
        if node.depth < max_depth:
            node.split(image) 
            for child in node.children:
                self._build_full_tree_dp(image, child, max_depth)
        else:
            node.leaf = True

    def _prune_tree_dp(self, node):
        if not node.children:
            return
        for child in node.children:
            self._prune_tree_dp(child)
        if (node.error <= ERROR_THRESHOLD):
            node.leaf = True
            node.children = None
        else:
            node.leaf = False
            
    def _update_max_depth(self, node):
        if node.is_leaf():
            if node.depth > self.max_depth:
                self.max_depth = node.depth
        elif node.children:
            for child in node.children:
                self._update_max_depth(child)

# GUI
gif_frames_data = []
gif_animation_job = None
huffman_preview_image = None
quad_preview_image_static = None
current_gif_path = None 

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
        y_sizes_png = [] # Nuevo: Para comparar con PNG
        
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

# GUI Main
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