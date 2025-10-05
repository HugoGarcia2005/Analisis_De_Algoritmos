"""
Visualización de datos de Fashion MNIST desde un CSV usando tmap.
"""
import base64
from io import BytesIO
from timeit import default_timer as timer
import numpy as np
import pandas as pd  # Se importa pandas para leer el CSV
import tmap as tm
from faerun import Faerun
from PIL import Image

# Configuración para el layout de tmap
CFG = tm.LayoutConfiguration()
CFG.node_size = 1 / 55

# --- SECCIÓN MODIFICADA ---
# Cargar datos de Fashion MNIST desde el archivo CSV
print("Cargando datos desde fashion-mnist_test.csv ...")
data = pd.read_csv("fashion-mnist_test.csv")

# La primera columna ('label') son las etiquetas
LABELS = data.iloc[:, 0].values
# El resto de las columnas son los datos de las imágenes
IMAGES = data.iloc[:, 1:].values
# --- FIN DE LA SECCIÓN MODIFICADA ---

IMAGE_LABELS = []

def main():
    """ Función Principal """

    # Inicializar y configurar tmap
    dims = 1024
    # El tamaño de cada imagen es 28*28 = 784 píxeles
    enc = tm.Minhash(784, 42, dims)
    lf = tm.LSHForest(dims * 2, 128)

    print("Convirtiendo imágenes para visualización ...")
    for image in IMAGES:
        # Reconstruir la imagen 28x28 desde el array plano de 784 píxeles
        img = Image.fromarray(image.reshape(28, 28).astype('uint8'))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        IMAGE_LABELS.append(
            "data:image/bmp;base64," + str(img_str).replace("b'", "").replace("'", "")
        )

    # Preparar los vectores para tmap
    tmp = []
    for _, image in enumerate(IMAGES):
        tmp.append(tm.VectorFloat(image / 255))

    print("Ejecutando tmap (esto puede tardar un momento) ...")
    start = timer()
    lf.batch_add(enc.batch_from_weight_array(tmp))
    lf.index()
    x, y, s, t, _ = tm.layout_from_lsh_forest(lf, CFG)
    print(f"tmap tardó: {timer() - start:.2f} segundos")

    legend_labels = [
        (0, "T-shirt/top"), (1, "Trouser"), (2, "Pullover"), (3, "Dress"),
        (4, "Coat"), (5, "Sandal"), (6, "Shirt"), (7, "Sneaker"),
        (8, "Bag"), (9, "Ankle boot"),
    ]

    faerun = Faerun(clear_color="#111111", view="front", coords=False)
    faerun.add_scatter(
        "FMNIST",
        {"x": x, "y": y, "c": LABELS, "labels": IMAGE_LABELS},
        colormap="tab10",
        shader="smoothCircle",
        point_scale=2.5,
        max_point_size=10,
        has_legend=True,
        categorical=True,
        legend_labels=legend_labels,
    )
    faerun.add_tree(
        "FMNIST_tree", {"from": s, "to": t}, point_helper="FMNIST", color="#666666"
    )
    faerun.plot("fmnist_csv", template="url_image")

if __name__ == "__main__":
    main()