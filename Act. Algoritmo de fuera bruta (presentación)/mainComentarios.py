"""
Versión del generador de 'súper fuerza bruta' utilizando la librería NumPy.
El objetivo es comparar la claridad y simplicidad del código.
"""
# Para usar NumPy, primero debemos importarlo. La comunidad usa 'np' como estándar.
import numpy as np
import itertools
import math


def es_cuadrado_latino_np(matriz):
    """
    Revisa si una matriz de NumPy es un Cuadrado Latino.
    
    Args:
        matriz (np.ndarray): La matriz de NumPy a verificar.

    Returns:
        bool: True si es válida, False si no lo es.
    """
    # En NumPy, para obtener el tamaño (n), usamos el atributo .shape
    n = matriz.shape[0]

    # --- Verificación de Filas ---
    for i in range(n):
        # np.unique encuentra los elementos únicos. Si la cantidad de únicos
        # no es igual a 'n', entonces había duplicados.
        fila = matriz[i, :]
        if len(np.unique(fila)) != n:
            return False

    # --- Verificación de Columnas ---
    # ¡Esta es la gran ventaja de NumPy! Podemos seleccionar columnas directamente.
    for j in range(n):
        # La sintaxis [:, j] significa "todas las filas, columna j".
        columna = matriz[:, j]
        if len(np.unique(columna)) != n:
            return False
            
    # Si pasó todas las pruebas, es un cuadrado latino.
    return True

def main():
    """
    Función principal que dirige el programa.
    """
    print("--- Generador de Cuadrados Latinos (Versión con NumPy) ---")
    
    n = int(input("Introduce el tamaño (n): "))


    # --- PASO 1: Generar combinaciones ---
    total_matrices = pow(n, n*n)
    print(f"\nGenerando {total_matrices:,} combinaciones posibles...")
    numeros = range(1, n + 1)
    combinaciones_planas = itertools.product(numeros, repeat=n*n)

    # --- PASO 2: Revisar cada combinación como una matriz NumPy ---
    print("\nRevisando cada matriz con la lógica de NumPy.")
    
    contador_latinos = 0
    for i, combinacion in enumerate(combinaciones_planas):
        
        # Aquí convertimos la combinación directamente en una matriz de n x n.
        # Es más directo que un bucle manual.
        matriz_np = np.array(combinacion).reshape((n, n))
        
        # Llamamos a nuestra nueva función de validación optimizada para NumPy
        if es_cuadrado_latino_np(matriz_np):
            contador_latinos = contador_latinos + 1
            print(f"\n¡Éxito! La matriz #{i+1} es un Cuadrado Latino (#{contador_latinos}).")
            # NumPy tiene su propio formato para imprimir matrices, es muy limpio.
            print(matriz_np)

    print("\n-------------------------------------------------")
    print("--- RESUMEN FINAL ---")
    print(f"Se analizaron un total de {total_matrices:,} matrices.")
    print(f"Se encontraron {contador_latinos} Cuadrados Latinos válidos.")


if __name__ == "__main__":
    main()