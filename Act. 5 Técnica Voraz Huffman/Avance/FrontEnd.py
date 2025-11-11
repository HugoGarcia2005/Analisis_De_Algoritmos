# Act. 5: Técnica Voraz Huffman (Equipo Tr3s)
# Hugo Gabriel Garcia Saldivar
# Oswaldo Daniel Maciel Vargas

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os 

def update_text_widget(widget, text, append=True):
    """
    Función simple para actualizar un widget de texto.
    """
    widget.config(state=tk.NORMAL)
    if not append:
        widget.delete("1.0", tk.END)
    widget.insert(tk.END, text + "\n")
    widget.see(tk.END)
    widget.config(state=tk.DISABLED)

def create_gui():
    """Crea, estiliza y lanza la ventana principal de la GUI con Tkinter."""
    
    BG_COLOR = "#3E3E3E"       
    FG_COLOR = "#E0E0E0"       
    FRAME_BG = "#2D2D2D"     
    BUTTON_BG = "#555555"    
    BUTTON_ACTIVE = "#666666" 
    DISABLED_BG = "#4A4A4A"   
    DISABLED_FG = "#888888"   
    ENTRY_BG = "#555555"
    TEXT_BG = "#2D2D2D"
    
    root = tk.Tk()
    root.title("Frontend - Compresión Huffman (Equipo Tr3s)")
    root.geometry("1000x700") 
    root.config(bg=BG_COLOR)

    style = ttk.Style()
    style.theme_use('clam') 
    style.configure('.', background=BG_COLOR, foreground=FG_COLOR, bordercolor=FRAME_BG)
    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
    style.configure('TLabelFrame', 
                    background=BG_COLOR, 
                    foreground=FG_COLOR, 
                    bordercolor=BUTTON_BG)
    style.configure('TLabelFrame.Label', 
                    background=BG_COLOR, 
                    foreground=FG_COLOR,
                    font=("Arial", 10, "bold"))
    style.configure('TButton', 
                    background=BUTTON_BG, 
                    foreground=FG_COLOR, 
                    bordercolor=BUTTON_BG,
                    font=("Arial", 10, "bold"))
    style.map('TButton',
        background=[('active', BUTTON_ACTIVE), ('disabled', DISABLED_BG)],
        foreground=[('disabled', DISABLED_FG)]
    )
    style.configure('TEntry', 
                    fieldbackground=ENTRY_BG, 
                    foreground=FG_COLOR, 
                    insertcolor=FG_COLOR, 
                    bordercolor=BUTTON_BG)
    style.map('TEntry',
        fieldbackground=[('disabled', DISABLED_BG)],
        foreground=[('disabled', DISABLED_FG)])

    root.grid_rowconfigure(0, weight=0)  
    root.grid_rowconfigure(1, weight=1)  
    root.grid_columnconfigure(0, weight=1) 

    image_path_var = tk.StringVar()

    frame_controls = ttk.LabelFrame(root, text="Configurar y Ejecutar")
    frame_controls.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
    frame_controls.grid_columnconfigure(0, weight=1) 
    frame_controls.grid_columnconfigure(1, weight=0) 

    frame_path = ttk.Frame(frame_controls, style='TFrame') 
    frame_path.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    ttk.Label(frame_path, text="Selecciona un archivo:").pack(side=tk.LEFT, padx=(0, 5))
    path_entry = ttk.Entry(frame_path, textvariable=image_path_var, state="readonly", width=70)
    path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    browse_button = ttk.Button(frame_path, text="Examinar")
    browse_button.pack(side=tk.LEFT, padx=(5, 0))
    
    frame_config = ttk.Frame(frame_controls, style='TFrame') 
    frame_config.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    
    clear_button = ttk.Button(frame_config, text="Limpiar")
    clear_button.pack(side=tk.RIGHT, padx=(0, 5))

    start_button = ttk.Button(frame_config, text="Iniciar Compresión")
    start_button.config(state="disabled") 
    start_button.pack(side=tk.RIGHT, padx=(5, 20)) 

    frame_resultados_base = ttk.Frame(root, style='TFrame')
    frame_resultados_base.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    frame_resultados_base.grid_columnconfigure(0, weight=1) 
    frame_resultados_base.grid_columnconfigure(1, weight=1)
    frame_resultados_base.grid_rowconfigure(0, weight=1)

    frame_consola = ttk.LabelFrame(frame_resultados_base, text="Salida de Consola")
    frame_consola.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
    
    txt_consola = scrolledtext.ScrolledText(
        frame_consola,
        wrap=tk.WORD,
        font=("Courier New", 10), 
        state=tk.DISABLED,
        background=TEXT_BG,
        foreground=FG_COLOR,
        insertbackground=FG_COLOR,
        borderwidth=0,
        highlightthickness=0
    )
    txt_consola.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    frame_comparacion = ttk.LabelFrame(frame_resultados_base, text="Resultados de Compresión")
    frame_comparacion.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

    txt_resultados = tk.Text(
        frame_comparacion,
        font=("Arial", 12, "bold"),
        state=tk.DISABLED,
        wrap=tk.WORD,
        background=TEXT_BG,
        foreground=FG_COLOR,
        insertbackground=FG_COLOR,
        borderwidth=0,
        highlightthickness=0
    )
    txt_resultados.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    
    def clear_results_callback():
        """Callback del boton 'Limpiar': resetea las cajas de texto."""
        print("Limpiando resultados...")
        update_text_widget(txt_consola, "Listo para un nuevo archivo.", append=False)
        update_text_widget(txt_resultados, "", append=False)
    
    clear_button.config(command=clear_results_callback)

    def select_image_callback():
        """Callback del boton 'Examinar': Abre el diálogo y valida."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo .txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if file_path and file_path.endswith(".txt"):
            image_path_var.set(file_path)
            start_button.config(state="normal") 
            clear_results_callback() 
            update_text_widget(txt_consola, f"Archivo cargado: {os.path.basename(file_path)}", append=False)
        elif file_path:
            image_path_var.set("¡Error! Selecciona un archivo .txt")
            start_button.config(state="disabled")
        else:
            start_button.config(state="disabled")
    
    browse_button.config(command=select_image_callback)

    def start_analysis_callback():
        """
        Callback del boton 'Iniciar'
        """
        file_path = image_path_var.get()

        if not file_path:
            messagebox.showwarning("Falta Archivo", "Por favor, selecciona un archivo .txt primero.")
            return

        start_button.config(state="disabled")
        clear_button.config(state="disabled")
        
        update_text_widget(txt_consola, "Iniciando proceso...", append=False)
        update_text_widget(txt_resultados, "", append=False)
        
        print(f"STUB: Iniciando compresión para {file_path}")
        
        update_text_widget(txt_consola, "Proceso 'stub' finalizado. (Aquí iría la salida).", append=True)
        update_text_widget(txt_resultados, "(Aquí iría la comparación)", append=False)

        start_button.config(state="normal")
        clear_button.config(state="normal")

    start_button.config(command=start_analysis_callback)
    
    update_text_widget(txt_consola, "Por favor, carga un archivo.txt para comprimir.", append=False)
    
    root.mainloop()

if __name__ == '__main__':
    create_gui()