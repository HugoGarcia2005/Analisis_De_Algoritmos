# src/dynamic_prog/quadtree_dp.py
from src.utils import ERROR_THRESHOLD
from src.divide_conquer.quadtree_dc import QuadtreeBase, QuadtreeNode

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
        # Lógica BOTTOM-UP (Programación Dinámica / Poda)
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
