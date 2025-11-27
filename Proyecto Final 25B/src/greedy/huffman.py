# src/greedy/huffman.py
import heapq
import os
from PIL import Image

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char 
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def quantize_image_data(image, tolerance):
    """Aplica el error (cuantización) para agrupar colores."""
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