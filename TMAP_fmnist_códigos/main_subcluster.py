import base64
from io import BytesIO
from timeit import default_timer as timer

import numpy as np
import tmap as tm
import pandas as pd
from faerun import Faerun
from PIL import Image
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt # <--- 1. Importación añadida

# --- CONFIGURACIÓN GLOBAL ---
CFG = tm.LayoutConfiguration()
CFG.node_size = 1 / 55

# --- FUNCIÓN PARA EL CLÚSTER ORIGINAL (TODAS LAS PRENDAS) ---
def generate_full_cluster(df):
    print("\n--- Iniciando la generación del clúster completo ---")
    LABELS = df['label'].values
    IMAGES = df.drop('label', axis=1).values
    
    IMAGE_LABELS = []
    
    dims = 1024
    enc = tm.Minhash(28 * 28, 42, dims)
    lf = tm.LSHForest(dims * 2, 128)

    print("Convirtiendo todas las imágenes...")
    for image in IMAGES:
        img = Image.fromarray(np.uint8(np.split(np.array(image), 28)))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        IMAGE_LABELS.append(
            "data:image/bmp;base64," + str(img_str).replace("b'", "").replace("'", "")
        )
    
    tmp = [tm.VectorFloat(image / 255) for image in IMAGES]

    print("Ejecutando tmap en el dataset completo...")
    start = timer()
    lf.batch_add(enc.batch_from_weight_array(tmp))
    lf.index()
    x, y, s, t, _ = tm.layout_from_lsh_forest(lf, CFG)
    print(f"tmap (completo) finalizado en: {timer() - start:.2f}s")

    legend_labels = [
        (0, "T-shirt/top"), (1, "Trouser"), (2, "Pullover"), (3, "Dress"),
        (4, "Coat"), (5, "Sandal"), (6, "Shirt"), (7, "Sneaker"),
        (8, "Bag"), (9, "Ankle boot"),
    ]

    faerun = Faerun(clear_color="#111111", view="front", coords=False)
    faerun.add_scatter(
        "FMNIST",
        {"x": x, "y": y, "c": LABELS, "labels": IMAGE_LABELS},
        colormap="tab10", shader="smoothCircle", point_scale=2.5,
        max_point_size=10, has_legend=True, categorical=True,
        legend_labels=legend_labels,
    )
    faerun.add_tree(
        "FMNIST_tree", {"from": s, "to": t}, point_helper="FMNIST", color="#666666"
    )
    faerun.plot("fmnist", template="url_image")
    print("✅ Visualización 'fmnist.html' generada correctamente.")

# --- FUNCIÓN PARA EL SUBCLÚSTER DE BOLSOS ---
def generate_bag_subcluster(df):
    print("\n--- Iniciando la generación del subcluster de bolsos ---")
    bags_df = df[df['label'] == 8].copy()
    IMAGES = bags_df.drop('label', axis=1).values
    
    print(f"Se encontraron {len(IMAGES)} bolsos para el subcluster.")
    
    IMAGE_LABELS = []
    
    dims = 1024
    enc = tm.Minhash(28 * 28, 42, dims)
    lf = tm.LSHForest(dims * 2, 128)

    print("Convirtiendo las imágenes de los bolsos...")
    for image in IMAGES:
        img = Image.fromarray(np.uint8(np.split(np.array(image), 28)))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        IMAGE_LABELS.append(
            "data:image/bmp;base64," + str(img_str).replace("b'", "").replace("'", "")
        )
        
    tmp = [tm.VectorFloat(image / 255) for image in IMAGES]

    print("Ejecutando tmap en el subcluster de bolsos...")
    start = timer()
    lf.batch_add(enc.batch_from_weight_array(tmp))
    lf.index()
    x, y, s, t, _ = tm.layout_from_lsh_forest(lf, CFG)
    print(f"tmap (bolsos) finalizado en: {timer() - start:.2f}s")
    
    print("Creando 4 subcategorías de bolsos con KMeans...")
    coords = np.vstack((x, y)).T
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    new_labels = kmeans.fit_predict(coords)

    # <--- 2. INICIO DEL NUEVO BLOQUE CON MATPLOTLIB ---
    print("Generando visualización de imágenes aleatorias de cada clúster...")
    n_clusters = 4
    n_examples = 9

    fig, axs = plt.subplots(n_clusters, n_examples, figsize=(10, 5))
    fig.suptitle('Muestras Aleatorias de Cada Clúster de Bolsos', fontsize=16)

    for i in range(n_clusters):
        indices = np.where(new_labels == i)[0]
        
        # Prevenir error si un clúster tiene menos de 9 imágenes
        num_to_sample = min(n_examples, len(indices))
        if num_to_sample > 0:
            random_indices = np.random.choice(indices, size=num_to_sample, replace=False)
        else:
            random_indices = []

        axs[i, 0].set_ylabel(f"Tipo {i+1}", rotation=0, size='large', labelpad=30)
        
        for j, idx in enumerate(random_indices):
            image = IMAGES[idx].reshape(28, 28)
            ax = axs[i, j]
            ax.imshow(image, cmap='gray')
            ax.axis('off')
        
        # Ocultar ejes de subplots no utilizados
        for j in range(num_to_sample, n_examples):
            axs[i, j].axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()
    # <--- FIN DEL NUEVO BLOQUE ---

    legend_labels_bags = [
        (0, "Tipo de Bolso 1"), (1, "Tipo de Bolso 2"), (2, "Tipo de Bolso 3"),
        (3, "Tipo de Bolso 4"),
    ]

    faerun = Faerun(clear_color="#111111", view="front", coords=False)
    faerun.add_scatter(
        "BolsosFMNIST",
        {"x": x, "y": y, "c": new_labels, "labels": IMAGE_LABELS},
        colormap="tab10", shader="smoothCircle", point_scale=2.5,
        max_point_size=10, has_legend=True, categorical=True,
        legend_labels=legend_labels_bags,
    )
    faerun.add_tree(
        "BolsosFMNIST_tree", {"from": s, "to": t}, point_helper="BolsosFMNIST", color="#666666"
    )
    faerun.plot("fmnist_bolsos", template="url_image")
    print("✅ Visualización 'fmnist_bolsos.html' generada correctamente.")


# --- FUNCIÓN PRINCIPAL QUE ORQUESTA TODO ---
def main():
    print("Cargando datos desde el archivo CSV...")
    try:
        test_df = pd.read_csv("fashion-mnist_test.csv")
        print("Datos cargados correctamente.")
        
        # 1. Generar el clúster con todas las prendas
        generate_full_cluster(test_df)
        
        # 2. Generar el subcluster solo con los bolsos
        generate_bag_subcluster(test_df)
        
        print("\n¡Proceso completado con éxito!")

    except FileNotFoundError:
        print("Error: El archivo 'fashion-mnist_test.csv' no se encontró.")
        print("Por favor, asegúrate de que el archivo esté en la misma carpeta que el script.")


if __name__ == "__main__":
    main()