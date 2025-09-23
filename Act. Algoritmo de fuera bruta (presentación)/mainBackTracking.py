import numpy as np

contador_latinos = 0

def es_valido(matriz, fila, col, num):
    if num in matriz[fila, :]:
        return False
    
    if num in matriz[:, col]:
        return False
        
    return True

def resolver_con_backtracking(matriz, fila, col):
    global contador_latinos
    n = matriz.shape[0]

    if fila == n:
        contador_latinos += 1
        print(f"\n¡Éxito! Se encontró el Cuadrado Latino (#{contador_latinos}).")
        print(matriz)
        return

    siguiente_fila = fila
    siguiente_columna = col + 1
    if siguiente_columna == n:
        siguiente_fila = fila + 1
        siguiente_columna = 0

    for numero_a_probar in range(1, n + 1):
        if es_valido(matriz, fila, col, numero_a_probar):   
            matriz[fila, col] = numero_a_probar
            resolver_con_backtracking(matriz, siguiente_fila, siguiente_columna)
            
            matriz[fila, col] = 0

print("--- Generador de Cuadrados Latinos (Método Backtracking) ---")    
n = int(input("Introduce el tamaño (n): "))

matriz_np = np.zeros((n, n), dtype=int)

print(f"\nIniciando búsqueda inteligente con backtracking para n={n}...")

resolver_con_backtracking(matriz_np, 0, 0)

print("\n-------------------------------------------------")
print("--- RESUMEN FINAL ---")
print(f"La búsqueda por backtracking ha finalizado.")
print(f"Se encontraron {contador_latinos} Cuadrados Latinos válidos.")