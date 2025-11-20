import heapq
import random

# ------------------------------------
#           CREAR GRAFO RANDOM
# ------------------------------------
def crear_grafo(num_nodos=6, num_aristas=9, peso_min=1, peso_max=20):
    """
    Genera un grafo aleatorio no dirigido y ponderado, sin aristas duplicadas.
    Cada ejecución produce un grafo diferente.
    """
    grafo = {i: [] for i in range(num_nodos)}
    usadas = set()
    
    # Semilla aleatoria diferente cada vez
    random.seed(None)
    
    while len(usadas) < num_aristas:
        u = random.randint(0, num_nodos - 1)
        v = random.randint(0, num_nodos - 1)
        if u == v:
            continue

        arista = tuple(sorted((u, v)))
        if arista in usadas:
            continue

        peso = random.randint(peso_min, peso_max)
        usadas.add(arista)

        grafo[u].append((v, peso))
        grafo[v].append((u, peso))

    return grafo

# ------------------------------------
#              PRIM (heap)
# ------------------------------------
def prim_mst(grafo, inicio=0):
    visitado = set()
    mst = []
    heap = [(0, inicio, None)]

    while heap and len(visitado) < len(grafo):
        costo, nodo, padre = heapq.heappop(heap)
        if nodo in visitado:
            continue
        visitado.add(nodo)
        if padre is not None:
            mst.append((padre, nodo, costo))
        for vecino, peso in grafo[nodo]:
            if vecino not in visitado:
                heapq.heappush(heap, (peso, vecino, nodo))
    return mst

# ------------------------------------
#              KRUSKAL (Union-Find)
# ------------------------------------
def kruskal_mst(grafo):
    aristas = []
    for u in grafo:
        for v, peso in grafo[u]:
            if u < v:  # Evitar duplicados
                aristas.append((peso, u, v))
    aristas.sort()

    padre = {n: n for n in grafo}
    rango = {n: 0 for n in grafo}

    def find(n):
        if padre[n] != n:
            padre[n] = find(padre[n])
        return padre[n]

    def union(a, b):
        ra = find(a)
        rb = find(b)
        if ra != rb:
            if rango[ra] < rango[rb]:
                padre[ra] = rb
            elif rango[ra] > rango[rb]:
                padre[rb] = ra
            else:
                padre[rb] = ra
                rango[ra] += 1
            return True
        return False

    mst = []
    for peso, u, v in aristas:
        if union(u, v):
            mst.append((u, v, peso))
    return mst

# ------------------------------------
#       IMPRESIÓN DEL GRAFO
# ------------------------------------
def imprimir_matriz(grafo):
    num_nodos = len(grafo)
    matriz = [[0]*num_nodos for _ in range(num_nodos)]
    for u in grafo:
        for v, peso in grafo[u]:
            matriz[u][v] = peso
    print("Matriz de adyacencia del grafo:")
    for fila in matriz:
        print(fila)

# ------------------------------------
#                MAIN
# ------------------------------------
def main():
    grafo = crear_grafo()
    imprimir_matriz(grafo)

    while True:
        print("\n=== MENÚ ===")
        print("1. Ejecutar Prim")
        print("2. Ejecutar Kruskal")
        print("3. Generar otro grafo")
        print("4. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            mst = prim_mst(grafo)
            print("\nAristas seleccionadas por PRIM:")
            total = sum(peso for _, _, peso in mst)
            for u, v, peso in mst:
                print(f"{u} -- {v}  (peso {peso})")
            print("Peso total del MST:", total)

        elif opcion == "2":
            mst = kruskal_mst(grafo)
            print("\nAristas seleccionadas por KRUSKAL:")
            total = sum(peso for _, _, peso in mst)
            for u, v, peso in mst:
                print(f"{u} -- {v}  (peso {peso})")
            print("Peso total del MST:", total)

        elif opcion == "3":
            print("\nGenerando nuevo grafo...")
            grafo = crear_grafo()
            imprimir_matriz(grafo)

        elif opcion == "4":
            print("\nSaliendo...\n")
            break

        else:
            print("Opción no válida, intenta de nuevo.")

# ------------------------------------
# EJECUTAR
# ------------------------------------
if __name__ == "__main__":
    main()
