from PIL import Image, ImageDraw

# --- PARÁMETROS DE CONFIGURACIÓN ---
PADDING = 0
OUTPUT_SCALE = 1
# Umbral de error: un valor más bajo resultará en más detalle (y más tiempo de procesamiento)
ERROR_THRESHOLD = 15 
# Profundidad máxima del árbol para evitar recursiones infinitas
MAX_DEPTH = 8


def weighted_average(hist):
    """Devuelve el promedio de color ponderado y el error de un histograma de píxeles."""
    total = sum(hist)
    value, error = 0, 0
    if total > 0:
        value = sum(i * x for i, x in enumerate(hist)) / total
        error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
        error = error ** 0.5
    return value, error


def color_from_histogram(hist):
    """Devuelve el color RGB promedio de un histograma dado."""
    r, re = weighted_average(hist[:256])
    g, ge = weighted_average(hist[256:512])
    b, be = weighted_average(hist[512:768])
    e = re * 0.2989 + ge * 0.5870 + be * 0.1140
    return (int(r), int(g), int(b)), e


class QuadtreeNode(object):
    """Nodo para el Quadtree que contiene una subsección de una imagen."""

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
        """Divide la sección de la imagen en cuatro cajas iguales."""
        l, t, r, b = self.box
        
        # FIX: Asegurarse de que las coordenadas sean enteros para el crop
        lr = int(l + (r - l) / 2)
        tb = int(t + (b - t) / 2)

        tl = QuadtreeNode(img, (l, t, lr, tb), self.depth + 1)
        tr = QuadtreeNode(img, (lr, t, r, tb), self.depth + 1)
        bl = QuadtreeNode(img, (l, tb, lr, b), self.depth + 1)
        br = QuadtreeNode(img, (lr, tb, r, b), self.depth + 1)
        self.children = [tl, tr, bl, br]


class Quadtree(object):
    """Árbol con nodos que contienen secciones de una imagen."""

    def __init__(self, image, max_depth=10):
        self.root = QuadtreeNode(image, image.getbbox(), 0)
        self.width, self.height = image.size
        self.max_depth = 0

        self._build_tree(image, self.root, max_depth)

    def _build_tree(self, image, node, max_depth):
        """Construye el árbol recursivamente hasta alcanzar la profundidad máxima o el umbral de error."""
        if (node.depth >= max_depth) or (node.error <= ERROR_THRESHOLD):
            if node.depth > self.max_depth:
                self.max_depth = node.depth
            node.leaf = True
            return

        node.split(image)
        for child in node.children:
            self._build_tree(image, child, max_depth)

    def get_leaf_nodes(self, depth):
        """Obtiene todos los nodos en una profundidad/nivel dado."""
        if depth > self.max_depth:
            raise ValueError('La profundidad solicitada es mayor que la del árbol')

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
        """Crea un objeto de imagen de Pillow a partir de un nivel/profundidad del árbol."""
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

    def create_gif(self, file_name, duration=500, loop=0):
        """Crea un GIF a partir de cada nivel del árbol."""
        images = []
        # Imagen final para mostrarla por más tiempo
        end_product_image = self._create_image_from_depth(self.max_depth)
        
        # Genera una imagen por cada nivel de profundidad
        for i in range(self.max_depth + 1):
            image = self._create_image_from_depth(i)
            images.append(image)
        
        # Agrega la imagen final varias veces para que se aprecie mejor
        for _ in range(3):
            images.append(end_product_image)

        print(f"Creando GIF con {len(images)} fotogramas...")
        images[0].save(
            file_name,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=loop)

# --- BLOQUE PRINCIPAL PARA EJECUTAR EL CÓDIGO ---
if __name__ == '__main__':
    # 1. CAMBIA ESTE VALOR AL NOMBRE DE TU IMAGEN
    IMAGE_PATH = 'img.jpg' # Por ejemplo: 'mi_foto.png'
    
    # 2. NOMBRE DEL ARCHIVO GIF DE SALIDA
    OUTPUT_GIF_PATH = 'quadtree_animation.gif'

    try:
        print(f"Cargando imagen desde '{IMAGE_PATH}'...")
        image = Image.open(IMAGE_PATH)
        
        # Asegurarse de que la imagen esté en modo RGB
        image = image.convert('RGB')

        print("Construyendo el Quadtree. Esto puede tardar un momento...")
        quadtree = Quadtree(image, max_depth=MAX_DEPTH)

        print(f"La profundidad máxima del árbol es: {quadtree.max_depth}")
        
        quadtree.create_gif(OUTPUT_GIF_PATH)
        
        print(f"¡Éxito! El GIF ha sido guardado como '{OUTPUT_GIF_PATH}' en el mismo directorio.")

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar la imagen '{IMAGE_PATH}'.")
        print("Asegúrate de que el archivo de imagen esté en la misma carpeta que este script y que el nombre sea correcto.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")