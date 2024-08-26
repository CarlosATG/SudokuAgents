import numpy as np
import random
import math

# Función para calcular el número de conflictos en el tablero de Sudoku
def contar_conflictos(tablero):
    conflictos = 0

    # Verificar conflictos en las columnas
    for col in range(9):
        columna = [tablero[fila][col] for fila in range(9)]
        conflictos += len(columna) - len(set(columna))

    # Verificar conflictos en las subcuadrículas
    for fila in range(0, 9, 3):
        for col in range(0, 9, 3):
            subcuadricula = [tablero[r][c] for r in range(fila, fila + 3) for c in range(col, col + 3)]
            conflictos += len(subcuadricula) - len(set(subcuadricula))

    return conflictos

# Función para generar una solución vecina
def generar_vecino(tablero, posiciones_fijas):
    nuevo_tablero = [fila[:] for fila in tablero]

    fila = random.choice(range(9))
    while fila in posiciones_fijas:
        fila = random.choice(range(9))

    col1, col2 = random.sample(range(9), 2)
    nuevo_tablero[fila][col1], nuevo_tablero[fila][col2] = nuevo_tablero[fila][col2], nuevo_tablero[fila][col1]

    return nuevo_tablero

# Algoritmo de Recocido Simulado modificado
def recocido_simulado_sudoku(tablero_inicial, max_iteraciones=50000):
    posiciones_fijas = [(i, j) for i in range(9) for j in range(9) if tablero_inicial[i][j] != 0]

    # Llenar las posiciones vacías restantes aleatoriamente en cada fila
    tablero = []
    for fila in range(9):
        fila_actual = [num for num in tablero_inicial[fila] if num != 0]
        numeros_restantes = [num for num in range(1, 10) if num not in fila_actual]
        random.shuffle(numeros_restantes)
        tablero.append([tablero_inicial[fila][col] if tablero_inicial[fila][col] != 0 else numeros_restantes.pop() for col in range(9)])

    conflictos_actuales = contar_conflictos(tablero)
    temperatura = 1.0
    tasa_enfriamiento = 0.99  # Enfriamiento más lento para mejor exploración
    temperatura_minima = 1e-5  # Temperatura mínima más baja para mejor ajuste fino

    iteracion = 0
    lista_conflictos = []  # Lista para almacenar los conflictos en cada iteración
    configuraciones_con_5_conflictos = []  # Array para almacenar las configuraciones con exactamente 5 conflictos

    while iteracion < max_iteraciones:
        nuevo_tablero = generar_vecino(tablero, posiciones_fijas)
        nuevos_conflictos = contar_conflictos(nuevo_tablero)

        # Si la nueva solución es mejor o igual a la anterior, la aceptamos
        if nuevos_conflictos < conflictos_actuales:
            tablero = nuevo_tablero
            conflictos_actuales = nuevos_conflictos
            temperatura *= tasa_enfriamiento  # Reducir la temperatura solo si hay una mejora

        # Almacenar configuraciones con exactamente 5 conflictos
        if conflictos_actuales == 5:
            configuraciones_con_5_conflictos.append(np.array(tablero))

        # Detener si encontramos una solución con 0 conflictos
        if conflictos_actuales == 0:
            break

        lista_conflictos.append(conflictos_actuales)  # Almacenar el número de conflictos en la lista
        iteracion += 1

    # Calcular el promedio de conflictos
    promedio_conflictos = sum(lista_conflictos) / len(lista_conflictos)

    return tablero, conflictos_actuales, iteracion, promedio_conflictos, configuraciones_con_5_conflictos

# Función de cruce (crossover) para combinar dos tableros de Sudoku
def crossover(tablero1, tablero2):
    # Intercambiar filas aleatoriamente para crear un nuevo tablero
    nuevo_tablero = []
    for i in range(9):
        if random.random() > 0.5:
            nuevo_tablero.append(tablero1[i])
        else:
            nuevo_tablero.append(tablero2[i])
    return np.array(nuevo_tablero)

# Función de mutación para introducir cambios menores en un tablero de Sudoku
def mutacion(tablero, tasa_mutacion=0.1):
    nuevo_tablero = tablero.copy()
    for fila in range(9):
        if random.random() < tasa_mutacion:
            col1, col2 = random.sample(range(9), 2)
            nuevo_tablero[fila][col1], nuevo_tablero[fila][col2] = nuevo_tablero[fila][col2], nuevo_tablero[fila][col1]
    return nuevo_tablero

# Función para ejecutar el algoritmo genético
def algoritmo_genetico(configuraciones, generaciones=100, tasa_mutacion=0.1):
    poblacion = configuraciones.copy()

    for generacion in range(generaciones):
        nueva_poblacion = []

        # Crear la nueva población mediante cruce y mutación
        while len(nueva_poblacion) < len(poblacion):
            padres = random.sample(poblacion, 2)
            hijo = crossover(padres[0], padres[1])
            hijo = mutacion(hijo, tasa_mutacion)
            nueva_poblacion.append(hijo)

        # Evaluar la nueva población y seleccionar los mejores tableros
        poblacion.extend(nueva_poblacion)
        poblacion.sort(key=contar_conflictos)
        poblacion = poblacion[:len(configuraciones)]  # Mantener el tamaño de la población

        # Imprimir progreso
        mejor_conflictos = contar_conflictos(poblacion[0])
        print(f"Generación {generacion+1}: Mejor tablero tiene {mejor_conflictos} conflictos")

        # Detener si se encuentra una solución sin conflictos
        if mejor_conflictos == 0:
            print("Se ha encontrado una solución óptima (0 conflictos).")
            return poblacion[0]

    return poblacion[0]  # Devolver el mejor tablero encontrado

# Ejemplo de un tablero de Sudoku con exactamente 15 elementos
tablero_inicial = [
    [5, 0, 0, 0, 7, 0, 0, 0, 0],
    [0, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 0, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 0],
    [4, 0, 0, 8, 0, 3, 0, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Ejecutar el recocido simulado para encontrar configuraciones con 5 conflictos
tablero_resuelto, conflictos, iteraciones, promedio_conflictos, configuraciones_con_5_conflictos = recocido_simulado_sudoku(tablero_inicial)

# Imprimir el resultado del recocido simulado
print("Conflictos finales:", conflictos)
print("Iteraciones:", iteraciones)
print("Promedio de conflictos:", promedio_conflictos)
print("Número de configuraciones con 5 conflictos:", len(configuraciones_con_5_conflictos))
print(np.array(tablero_resuelto))

# Ejecutar el algoritmo genético sobre las configuraciones con 5 conflictos
if configuraciones_con_5_conflictos:
    mejor_sudoku = algoritmo_genetico(configuraciones_con_5_conflictos)
    print("Mejor Sudoku encontrado con algoritmo genético:")
    print(np.array(mejor_sudoku))
    print("Conflictos finales en esta configuración:", contar_conflictos(mejor_sudoku))
else:
    print("No se encontraron configuraciones con 5 conflictos.")
