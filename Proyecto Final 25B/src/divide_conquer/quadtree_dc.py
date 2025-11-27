# src/divide_conquer/quadtree_dc.py
from PIL import Image, ImageDraw
import os
from src.utils import PADDING, OUTPUT_SCALE, ERROR_THRESHOLD

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
    """Clase base compartida por D&C y DP"""
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
            
        images[0].save(gif_file_path, save_all=True, append_images=images[1:], duration=duration, loop=loop)
        return gif_file_path, final_img_path

class QuadtreeDivideAndConquer(QuadtreeBase):
    def __init__(self, image, max_depth=10):
        super().__init__(image)
        self.root = QuadtreeNode(image, image.getbbox(), 0)
        self.max_depth = 0 
        self._build_tree_dc(image, self.root, max_depth)

    def _build_tree_dc(self, image, node, max_depth):
        # Lógica TOP-DOWN (Divide y Vencerás)
        if (node.depth >= max_depth) or (node.error <= ERROR_THRESHOLD):
            if node.depth > self.max_depth:
                self.max_depth = node.depth
            node.leaf = True
            return
        node.split(image)
        for child in node.children:
            self._build_tree_dc(image, child, max_depth)