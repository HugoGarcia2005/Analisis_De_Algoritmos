import base64
from io import BytesIO
from timeit import default_timer as timer

import numpy as np
import tmap as tm
import pandas as pd
from faerun import Faerun
from PIL import Image

CFG = tm.LayoutConfiguration()
CFG.node_size = 1 / 55

print("Cargando datos desde los archivos CSV...")
test_df = pd.read_csv("fashion-mnist_test.csv")

LABELS = test_df['label'].values
IMAGES = test_df.drop('label', axis=1).values

print("Datos cargados correctamente.")
IMAGE_LABELS = []


def main():
    dims = 1024
    enc = tm.Minhash(28 * 28, 42, dims)
    lf = tm.LSHForest(dims * 2, 128)

    print("Converting images ...")
    for image in IMAGES:
        img = Image.fromarray(np.uint8(np.split(np.array(image), 28)))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        IMAGE_LABELS.append(
            "data:image/bmp;base64," + str(img_str).replace("b'", "").replace("'", "")
        )
    tmp = []
    for _, image in enumerate(IMAGES):
        tmp.append(tm.VectorFloat(image / 255))

    print("Running tmap ...")
    start = timer()
    lf.batch_add(enc.batch_from_weight_array(tmp))
    lf.index()
    x, y, s, t, _ = tm.layout_from_lsh_forest(lf, CFG)
    print("tmap: " + str(timer() - start))

    legend_labels = [
        (0, "T-shirt/top"),
        (1, "Trouser"),
        (2, "Pullover"),
        (3, "Dress"),
        (4, "Coat"),
        (5, "Sandal"),
        (6, "Shirt"),
        (7, "Sneaker"),
        (8, "Bag"),
        (9, "Ankle boot"),
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
    faerun.plot("fmnist", template="url_image")


if __name__ == "__main__":
    main()