# Act. 5: Técnica Voraz Huffman (Equipo Tr3s)
# Hugo Gabriel Garcia Saldivar
# Oswaldo Daniel Maciel Vargas

import heapq  
from collections import Counter 
import os 

class NodoHuffman:
    def __init__(self, char, freq, izq=None, der=None):
        self.char = char
        self.freq = freq
        self.izq = izq
        self.der = der
    def __lt__(self, otro):
        return self.freq < otro.freq

def calcular_frecuencias(texto):
    """
    Lee un string y devuelve un diccionario con la frecuencia de cada carácter.
    """
    return Counter(texto)

def construir_arbol_huffman(frecuencias):
    """
    Construye el árbol de Huffman usando una cola de prioridad.
    Devuelve el nodo raíz del árbol.
    """
    cola_prioridad = []
    for char, freq in frecuencias.items():
        nodo = NodoHuffman(char, freq)
        heapq.heappush(cola_prioridad, nodo)
    
    while len(cola_prioridad) > 1:
        nodo_izq = heapq.heappop(cola_prioridad)
        nodo_der = heapq.heappop(cola_prioridad)
        
        freq_suma = nodo_izq.freq + nodo_der.freq
        nodo_padre = NodoHuffman(char=None, freq=freq_suma, izq=nodo_izq, der=nodo_der)
        
        heapq.heappush(cola_prioridad, nodo_padre)
        
    return heapq.heappop(cola_prioridad) if cola_prioridad else None


def generar_codigos_huffman(arbol_raiz):
    """
    Recorre el árbol para generar el mapa de códigos binarios.
    """
    codigos = {}
    
    def _recorrer_arbol(nodo_actual, codigo_actual):
        if nodo_actual is None:
            return
        
        if nodo_actual.char is not None:
            if codigo_actual == "":
                codigos[nodo_actual.char] = "0"
            else:
                codigos[nodo_actual.char] = codigo_actual
            return

        _recorrer_arbol(nodo_actual.izq, codigo_actual + "0")
        _recorrer_arbol(nodo_actual.der, codigo_actual + "1")

    _recorrer_arbol(arbol_raiz, "")
    return codigos

def codificar_texto(texto, mapa_codigos):
    """
    Traduce el texto original a su representación binaria de Huffman.
    """
    texto_codificado = ""
    for char in texto:
        texto_codificado += mapa_codigos[char]
    return texto_codificado

def decodificar_texto(texto_codificado, arbol_raiz):
    """
    Traduce el string binario de Huffman de vuelta al texto original.
    """
    if arbol_raiz is None:
        return ""
        
    texto_decodificado = ""
    nodo_actual = arbol_raiz

    if arbol_raiz.char is not None:
        return arbol_raiz.char * len(texto_codificado)

    for bit in texto_codificado:
        if bit == '0':
            nodo_actual = nodo_actual.izq
        else:
            nodo_actual = nodo_actual.der
        
        if nodo_actual.char is not None:
            texto_decodificado += nodo_actual.char
            nodo_actual = arbol_raiz
            
    return texto_decodificado

def guardar_comprimido(ruta_archivo, texto_codificado):
    """
    Guarda el texto codificado (string '0' y '1') en un nuevo archivo binario.
    Devuelve la ruta del nuevo archivo.
    """
    ruta_salida = "Comprimido.bin"
    
    bits_padding = 8 - (len(texto_codificado) % 8)
    if bits_padding == 8:
        bits_padding = 0
    
    info_padding = "{:08b}".format(bits_padding)
    texto_codificado_con_padding = info_padding + texto_codificado + ("0" * bits_padding)

    array_bytes = bytearray()
    for i in range(0, len(texto_codificado_con_padding), 8):
        byte = texto_codificado_con_padding[i:i+8]
        array_bytes.append(int(byte, 2)) 
    
    try:
        with open(ruta_salida, 'wb') as f_out:
            f_out.write(array_bytes)
    except IOError as e:
        print(f"Error al escribir el archivo comprimido: {e}")
        return None
    
    return ruta_salida

def main():
    ruta_archivo_original = "archivo.txt" 
    
    print(f"--- Iniciando Compresión para: '{ruta_archivo_original}' ---")

    try:
        with open(ruta_archivo_original, 'r', encoding='utf-8') as f:
            texto_original = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo_original}'")
        print("Por favor, asegúrate de que el archivo exista en la misma carpeta que el script.")
        return
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return

    if not texto_original:
        print("El archivo está vacío. No hay nada que comprimir.")
        return

    frecuencias = calcular_frecuencias(texto_original)
    print("\n--- Frecuencias Calculadas ---")
    print(f"Total de caracteres únicos: {len(frecuencias)}")
    print("-" * 30)

    arbol_raiz = construir_arbol_huffman(frecuencias)
    
    mapa_codigos = generar_codigos_huffman(arbol_raiz)
    
    print("--- Códigos de Huffman ---")
    
    items_ordenados_por_freq = sorted(
        mapa_codigos.items(), 
        key=lambda item: frecuencias[item[0]], 
        reverse=True
    )
    
    for char, code in items_ordenados_por_freq:
        freq = frecuencias[char]
        print(f"  Freq: {freq:<7} | Char: {repr(char):<6} | Código: {code}") 
    
    print("-" * 30)

    texto_codificado = codificar_texto(texto_original, mapa_codigos)
    
    texto_decodificado = decodificar_texto(texto_codificado, arbol_raiz)
    print("--- Verificación de Decodificación ---")
    if texto_decodificado == texto_original:
        print("¡Éxito! El texto decodificado coincide con el original.")
    else:
        print("¡Error! El texto decodificado NO coincide con el original.")
    print("-" * 30)

    print("--- Comparación de Tamaño ---")
    ruta_comprimido = guardar_comprimido(ruta_archivo_original, texto_codificado)
    
    if ruta_comprimido:
        try:
            tamano_original_bytes = os.path.getsize(ruta_archivo_original)
            tamano_comprimido_bytes = os.path.getsize(ruta_comprimido)
            
            print(f"Tamaño Original   ('{ruta_archivo_original}'): {tamano_original_bytes} bytes")
            print(f"Tamaño Comprimido ('{ruta_comprimido}'): {tamano_comprimido_bytes} bytes")
            
            if tamano_comprimido_bytes < tamano_original_bytes:
                reduccion = 100 * (1 - tamano_comprimido_bytes / tamano_original_bytes)
                print(f"\n¡Compresión Exitosa! Reducción del {reduccion:.2f}%")
            else:
                print("\nLa compresión no fue efectiva (el 'overhead' fue mayor que la ganancia).")
                print("Esto es normal para archivos de texto muy pequeños.")
        
        except FileNotFoundError:
            print("Error al comparar tamaños de archivo.")

if __name__ == "__main__":
    main()