import numpy as np
import itertools
import math

def es_cuadrado_latino_np(matriz):
    n = matriz.shape[0]

    for i in range(n):
        fila = matriz[i, :]
        if len(np.unique(fila)) != n:
            return False

    for j in range(n):
        columna = matriz[:, j]
        if len(np.unique(columna)) != n:
            return False
        
    return True


def llenar_y_verificar_matrices(n, combinaciones):
    print("\nRevisando cada matriz.")
    contador_latinos = 0
    
    for i, combinacion in enumerate(combinaciones):
        matriz_np = np.array(combinacion).reshape((n, n))
        
        if es_cuadrado_latino_np(matriz_np):
            contador_latinos = contador_latinos + 1
            print(f"\n¡Éxito! La matriz #{i+1} es un Cuadrado Latino (#{contador_latinos}).")
            print(matriz_np)
            
    return contador_latinos

print("--- Generador de Cuadrados Latinos ---")    
n = int(input("Introduce el tamaño (n): "))

total_matrices = pow(n, n*n)
print(f"\nGenerando {total_matrices:,} combinaciones posibles...")
numeros = range(1, n + 1)

combinaciones_planas = itertools.product(numeros, repeat=n*n)
cuadrados_encontrados = llenar_y_verificar_matrices(n, combinaciones_planas)

print("\n-------------------------------------------------")
print("--- RESUMEN FINAL ---")
print(f"Se analizaron un total de {total_matrices:,} matrices.")
print(f"Se encontraron {cuadrados_encontrados} Cuadrados Latinos válidos.")
