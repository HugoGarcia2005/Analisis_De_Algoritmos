import numpy as np

# Usaremos una variable global para llevar la cuenta, ya que la función recursiva
# no puede devolver valores de forma sencilla para este propósito.
contador_latinos = 0

def es_valido(matriz, fila, col, num):
    """
    Verifica si es seguro colocar un número en una celda específica.
    Revisa si el número ya existe en la fila o columna actual.
    """
    # Revisar si el número 'num' ya está en la fila 'fila'
    if num in matriz[fila, :]:
        return False
    
    # Revisar si el número 'num' ya está en la columna 'col'
    if num in matriz[:, col]:
        return False
        
    return True

def resolver_con_backtracking(matriz, fila, col):
    """
    Función recursiva que intenta llenar la matriz celda por celda.
    """
    global contador_latinos
    n = matriz.shape[0]

    # --- Caso Base: Si hemos llenado todas las celdas ---
    # Si la fila es igual a 'n', significa que hemos completado la última fila con éxito.
    if fila == n:
        # ¡Hemos encontrado una solución válida! La imprimimos.
        contador_latinos += 1
        print(f"\n¡Éxito! Se encontró el Cuadrado Latino (#{contador_latinos}).")
        print(matriz)
        return

    # --- Lógica Recursiva ---
    # Calculamos cuál será la siguiente celda a rellenar
    siguiente_fila = fila
    siguiente_columna = col + 1
    if siguiente_columna == n:
        siguiente_fila = fila + 1
        siguiente_columna = 0

    # Intentamos colocar cada número posible (de 1 a n) en la celda actual
    for numero_a_probar in range(1, n + 1):
        # 1. Comprobamos si el movimiento es válido
        if es_valido(matriz, fila, col, numero_a_probar):
            
            # 2. Si es válido, colocamos el número
            matriz[fila, col] = numero_a_probar
            
            # 3. Llamamos a la función para que resuelva la siguiente celda
            resolver_con_backtracking(matriz, siguiente_fila, siguiente_columna)
            
            # 4. BACKTRACK: Deshacemos la elección.
            # Cuando la recursión termina, limpiamos la celda para que el bucle `for`
            # pueda probar el siguiente número en esta misma celda.
            matriz[fila, col] = 0

# --- Programa Principal ---
print("--- Generador de Cuadrados Latinos (Método Backtracking) ---")    
n = int(input("Introduce el tamaño (n): "))

# Creamos una matriz inicial vacía (llena de ceros)
matriz_np = np.zeros((n, n), dtype=int)

print(f"\nIniciando búsqueda inteligente con backtracking para n={n}...")

# Iniciamos el proceso desde la primera celda (0, 0)
resolver_con_backtracking(matriz_np, 0, 0)

# --- Resumen Final ---
print("\n-------------------------------------------------")
print("--- RESUMEN FINAL ---")
# Nota: El backtracking no "analiza" un número total de matrices, sino que
# explora un "árbol de posibilidades". Por eso el resumen es diferente.
print(f"La búsqueda por backtracking ha finalizado.")
print(f"Se encontraron {contador_latinos} Cuadrados Latinos válidos.")