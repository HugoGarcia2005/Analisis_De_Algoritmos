import base64
from io import BytesIO
from timeit import default_timer as timer

import numpy as np
import tmap as tm
import pandas as pd
from faerun import Faerun
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# --- CONFIGURACIÓN GLOBAL (VERSIÓN COMPATIBLE) ---
CFG = tm.LayoutConfiguration()
CFG.node_size = 1 / 55
CFG.k = 20
CFG.kc = 20

# --- FUNCIÓN AUXILIAR PARA PREPROCESAR IMÁGENES ---
def process_images_for_faerun(images_data):
    image_labels = []
    for image in images_data:
        img = Image.fromarray(np.uint8(np.split(np.array(image), 28)))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        image_labels.append("data:image/bmp;base64," + str(img_str).replace("b'", "").replace("'", ""))
    return image_labels

# --- FUNCIÓN CENTRAL: GENERAR LAYOUT 3D ESFÉRICO ---
def generate_3d_sphere_layout(name, images_data, initial_labels=None, n_clusters=None, legend_map=None):
    print(f"\n--- Iniciando la generación de la esfera 3D para '{name}' ---")
    
    # 1. Preparar imágenes para Faerun (base64)
    image_labels_faerun = process_images_for_faerun(images_data)

    # 2. Ejecutar tmap para X, Y
    dims = 1024
    enc = tm.Minhash(28 * 28, 42, dims)
    lf = tm.LSHForest(dims * 2, 128)

    print(f"[{name}] Ejecutando tmap...")
    start = timer()
    tmp = [tm.VectorFloat(image / 255) for image in images_data]
    lf.batch_add(enc.batch_from_weight_array(tmp))
    lf.index()
    x, y, s, t, _ = tm.layout_from_lsh_forest(lf, CFG) 
    print(f"[{name}] tmap finalizado en: {timer() - start:.2f}s")

    # 3. Generar Z con PCA
    print(f"[{name}] Calculando la tercera dimensión (eje z) con PCA...")
    pca_z = PCA(n_components=1)
    z = pca_z.fit_transform(images_data / 255.0).flatten()
    print(f"[{name}] Eje 'z' calculado.")

    # 4. NORMALIZAR Y ESCALAR PARA OBTENER UNA FORMA ESFÉRICA UNIFORME
    print(f"[{name}] Normalizando coordenadas para una forma esférica proporcionada...")
    
    coords_raw = np.vstack((x, y, z)).T
    center = np.mean(coords_raw, axis=0)
    centered_coords = coords_raw - center
    max_range = np.max(np.abs(centered_coords))
    
    if max_range > 0:
        scaled_coords = centered_coords / max_range
    else:
        scaled_coords = centered_coords
        
    x_scaled, y_scaled, z_scaled = scaled_coords[:, 0], scaled_coords[:, 1], scaled_coords[:, 2]
    print(f"[{name}] Coordenadas escaladas para formar esférica.")

    # 5. Determinar etiquetas para colorear
    final_labels = initial_labels
    legend_to_use = legend_map
    if n_clusters is not None and initial_labels is None:
        print(f"[{name}] Creando {n_clusters} clústeres con KMeans para colorear...")
        coords_2d_for_clustering = np.vstack((x, y)).T
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        final_labels = kmeans.fit_predict(coords_2d_for_clustering)
        legend_to_use = [(i, f"Categoría {i+1}") for i in range(n_clusters)]

    # 6. Configurar Faerun
    faerun = Faerun(clear_color="#050505", view="free", coords=False)
    
    faerun.add_scatter(
        name.replace(" ", "") + "_Scatter",
        {"x": x_scaled, "y": y_scaled, "z": z_scaled, "c": final_labels, "labels": image_labels_faerun},
        colormap="gist_rainbow",
        shader="smoothCircle", 
        point_scale=5.0,
        max_point_size=20,
        has_legend=True, categorical=True,
        legend_labels=legend_to_use,
    )
    faerun.add_tree(
        name.replace(" ", "") + "_Tree", 
        {"from": s, "to": t}, 
        point_helper=name.replace(" ", "") + "_Scatter", 
        color="#555555",
    )
    
    # <-- CORRECCIÓN AQUÍ: Se pasa el nombre del archivo SIN la extensión .html
    filename = f"fmnist_{name.replace(' ', '_').lower()}_esfera"
    faerun.plot(filename, template="url_image")
    print(f"✅ ¡Éxito! Visualización '{filename}.html' generada correctamente.")


# --- FUNCIÓN PRINCIPAL QUE ORQUESTA TODO ---
def main():
    print("Cargando el gran conjunto de datos desde el archivo CSV...")
    try:
        train_df = pd.read_csv("fashion-mnist_test.csv")
        print("Datos cargados correctamente.")

        # --- LEYENDAS ESPECÍFICAS ---
        full_legend_labels = [
            (0, "T-shirt/top"), (1, "Trouser"), (2, "Pullover"), (3, "Dress"),
            (4, "Coat"), (5, "Sandal"), (6, "Shirt"), (7, "Sneaker"),
            (8, "Bag"), (9, "Ankle boot"),
        ]
        bag_legend_labels = [
            (0, "Mochilas / Equipaje"), (1, "Bolsos de Hombro"), (2, "Carteras / Clutch"),
            (3, "Bolsos de Mano"), (4, "Bolsos Tote"), (5, "Maletines"),
            (6, "Bolsos Cruzados"), (7, "Riñoneras / Pequeños"),
        ]

        # 1. Generar el clúster de TODAS LAS PRENDAS en 3D esférico
        all_items_images = train_df.drop('label', axis=1).values
        all_items_labels = train_df['label'].values
        generate_3d_sphere_layout(
            name="Todos los Artículos", 
            images_data=all_items_images, 
            initial_labels=all_items_labels, 
            legend_map=full_legend_labels
        )
        
        # 2. Generar el subcluster de BOLSOS en 3D esférico
        bags_df = train_df[train_df['label'] == 8].copy()
        bag_images = bags_df.drop('label', axis=1).values
        generate_3d_sphere_layout(
            name="Bolsos", 
            images_data=bag_images, 
            n_clusters=8,
            legend_map=bag_legend_labels
        )
        
        print("\n¡Proceso de generación de esferas 3D completado con éxito!")

    except FileNotFoundError:
        print("Error: El archivo 'fashion-mnist_train.csv' no se encontró.")

if __name__ == "__main__":
    main()