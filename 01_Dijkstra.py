import networkx as nx            # Importamos la librería NetworkX, usada para crear y manipular la estructura matemática del grafo (nodos y aristas).
import matplotlib.pyplot as plt  # Importamos PyPlot de Matplotlib, que nos permitirá dibujar la ventana gráfica con el mapa interactivo.
import time                      # Importamos la librería time para poder hacer pausas (sleep) y simular que el sistema está pensando.

# La clase Ubicacion (antes Vertice) representa cada punto o zona en la ciudad (nuestros nodos).
class Ubicacion:
    def __init__(self, i):
        self.id = i                 # Guardamos el nombre del lugar (ej. 'Almacén'), que sirve como identificador único.
        self.rutas = []             # Creamos una lista vacía que guardará tuplas con los vecinos y el tiempo de viaje hacia ellos.
        self.visitado = False       # Bandera booleana: False significa que aún no hemos analizado sus rutas definitivas.
        self.padre = None           # Rastreador: Guarda de qué ubicación venimos para poder reconstruir el camino de regreso al final.
        self.tiempo_total = float('inf') # Inicializamos el tiempo en Infinito porque al principio no sabemos cuánto tardamos en llegar aquí.

    # Método para registrar una calle que conecta esta ubicación con otra.
    def agregar_ruta(self, v, tiempo):
        if v not in self.rutas:             # Verificamos que la ruta no exista ya en la lista para evitar duplicados.
            self.rutas.append((v, tiempo))  # Agregamos la tupla (nombre_del_destino, tiempo_en_minutos) a la lista de rutas.

# La clase Mapa controla la lógica principal del algoritmo de Dijkstra.
class Mapa:
    def __init__(self):
        self.ubicaciones = {}       # Diccionario que almacenará todos los objetos 'Ubicacion'. Clave: Nombre, Valor: Objeto.

    # Método para crear un nuevo lugar en el mapa.
    def agregar_ubicacion(self, id):
        if id not in self.ubicaciones:              # Si el lugar no existe en nuestro diccionario...
            self.ubicaciones[id] = Ubicacion(id)    # ...lo instanciamos a partir de la clase Ubicacion y lo guardamos.

    # Método para crear una calle (arista bidireccional) entre dos lugares existentes.
    def agregar_calle(self, a, b, tiempo):
        if a in self.ubicaciones and b in self.ubicaciones: # Comprobamos que ambos lugares existan en el mapa.
            self.ubicaciones[a].agregar_ruta(b, tiempo)     # Conectamos el lugar 'A' hacia el lugar 'B' con su tiempo.
            self.ubicaciones[b].agregar_ruta(a, tiempo)     # Conectamos el lugar 'B' hacia el lugar 'A' (hace la calle de doble sentido).

    # Método auxiliar para encontrar, de una lista de lugares, cuál tiene el menor tiempo acumulado.
    def minimo(self, lista):
        if len(lista) > 0:                                  # Si la lista de lugares no está vacía...
            m = self.ubicaciones[lista[0]].tiempo_total     # Asumimos temporalmente que el primer elemento es el que tiene el menor tiempo.
            v = lista[0]                                    # Guardamos el nombre de ese primer elemento.
            for e in lista:                                 # Recorremos todos los elementos de la lista.
                if m > self.ubicaciones[e].tiempo_total:    # Si encontramos un lugar con un tiempo menor al que teníamos guardado...
                    m = self.ubicaciones[e].tiempo_total    # ...actualizamos el tiempo mínimo encontrado.
                    v = e                                   # ...y guardamos el nombre de este nuevo lugar "ganador".
            return v                                        # Retornamos el nombre del lugar con la ruta más rápida conocida hasta ahora.
        return None                                         # Si la lista estaba vacía, retornamos None (nada).

    # Método para reconstruir el itinerario final una vez que Dijkstra terminó de calcular.
    def obtener_ruta(self, a, b):
        ruta = []                                       # Creamos una lista vacía para guardar los pasos.
        actual = b                                      # Empezamos desde el lugar de DESTINO (hacia atrás).
        while actual is not None:                       # Mientras no lleguemos al origen...
            ruta.append(actual)                         # ...agregamos el lugar actual a la ruta.
            actual = self.ubicaciones[actual].padre     # ...y retrocedemos al lugar desde donde llegamos a este (su padre).
        ruta.reverse()                                  # Como construimos la ruta al revés (Destino -> Origen), invertimos la lista.
        return [ruta, self.ubicaciones[b].tiempo_total] # Devolvemos una lista con el itinerario completo y el tiempo total que tomó.

    # Implementación central del algoritmo de Dijkstra, adaptado a terminología GPS.
    def calcular_ruta_optima(self, origen):
        print(f"\n--- [SISTEMA GPS] CALCULANDO RUTA ÓPTIMA DESDE: '{origen}' ---")
        
        if origen in self.ubicaciones:                      # Verificamos que el punto de partida exista en el mapa.
            self.ubicaciones[origen].tiempo_total = 0       # Regla de oro de Dijkstra: La distancia del origen a sí mismo es siempre 0.
            actual = origen                                 # Definimos el origen como nuestro nodo actual para empezar a explorar.
            noVisitados = list(self.ubicaciones.keys())     # Creamos una lista con todos los lugares del mapa; todos están "no visitados" al inicio.

            # Bucle de preparación: reseteamos valores en caso de que el algoritmo se ejecute varias veces.
            for v in self.ubicaciones:
                if v != origen:                                 # A todos los lugares que NO son el origen...
                    self.ubicaciones[v].tiempo_total = float('inf') # ...les asignamos un tiempo infinito (aún no sabemos cómo llegar).
                self.ubicaciones[v].padre = None                # Borramos cualquier rastro de rutas anteriores (padres).

            # Bucle principal de Dijkstra: Se ejecuta mientras haya lugares sin visitar.
            while len(noVisitados) > 0:
                print(f"\n--> Ubicación actual: [{actual}]")
                time.sleep(0.5) # Pausa de medio segundo para hacer la consola legible y visual.

                # Exploración: Revisamos todos los vecinos conectados directamente a la ubicación actual.
                for destino_vecino, tiempo_tramo in self.ubicaciones[actual].rutas:
                    if self.ubicaciones[destino_vecino].visitado == False: # Solo evaluamos vecinos que no hayan sido cerrados/visitados permanentemente.
                        
                        print(f"    Evaluando ruta hacia '{destino_vecino}' (Toma {tiempo_tramo} min)...", end=" ")
                        
                        # RELAJACIÓN MATEMÁTICA: Calculamos cuánto tardaríamos en llegar al vecino si pasamos por nuestra ubicación actual.
                        tiempo_calculado = self.ubicaciones[actual].tiempo_total + tiempo_tramo
                        
                        # Si este nuevo tiempo calculado es MENOR al tiempo que el vecino ya tenía registrado...
                        if tiempo_calculado < self.ubicaciones[destino_vecino].tiempo_total:
                            self.ubicaciones[destino_vecino].tiempo_total = tiempo_calculado # ...encontramos un atajo, Actualizamos su tiempo total.
                            self.ubicaciones[destino_vecino].padre = actual                  # ...y registramos que para lograr este atajo, debemos venir de 'actual'.
                            print(f"¡Ruta rápida! Tiempo estimado: {tiempo_calculado} min.")
                        else:
                            print("Descartada.") # El camino nuevo es más lento que uno que ya conocíamos, no hacemos nada.
                        time.sleep(0.2) # Pequeña pausa de lectura.

                self.ubicaciones[actual].visitado = True    # Ya exploramos todos los caminos desde este lugar, lo marcamos como visitado permanentemente.
                noVisitados.remove(actual)                  # Lo sacamos de la lista de lugares pendientes.
                
                # Para la siguiente iteración, nos movemos al lugar "no visitado" que tenga el menor tiempo acumulado actualmente.
                actual = self.minimo(noVisitados)
                
                # Condición de seguridad: Si quedan nodos sin visitar pero todos tienen tiempo infinito, están aislados (no hay calles hacia ellos). Rompemos el ciclo.
                if actual is None and len(noVisitados) > 0:
                    break


# FUNCION PARA DIBUJAR EL GRAFO EN UNA VENTANA VISUAL
def graficar_resultado(mapa_obj, ruta_optima):
    G = nx.Graph() # Instanciamos un objeto Grafo vacío de la librería NetworkX.
    
    # 1. Traducir nuestros datos a NetworkX
    for u_id, u_obj in mapa_obj.ubicaciones.items():
        G.add_node(u_id) # Agregamos el nombre del lugar como un nodo visual.
        for vecino, tiempo in u_obj.rutas:
            G.add_edge(u_id, vecino, weight=tiempo) # Agregamos la calle (arista) y su tiempo (peso).

    # 2. Configurar la física visual (Layout)
    pos = nx.spring_layout(G, seed=42) # 'spring_layout' distribuye los nodos para que no se empalmen. 'seed=42' congela la posición para que siempre se vea igual.
    
    plt.figure(figsize=(10, 7)) # Abrimos una nueva ventana de Matplotlib con un tamaño de 10x7 pulgadas.
    
    # 3. Dibujar la estructura base (nodos azules)
    nx.draw(G, pos, with_labels=True, node_color='#A0CBE2', node_size=2500, font_size=10, font_weight="bold")
    
    # 4. Dibujar los textos de los minutos sobre las líneas (calles)
    edge_labels = nx.get_edge_attributes(G, 'weight') # Extraemos todos los pesos (tiempos) de las aristas.
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='blue')

    # 5. Resaltar el camino ganador (verde)
    path_edges = list(zip(ruta_optima, ruta_optima[1:])) # Convierte ['A', 'B', 'C'] en pares [('A','B'), ('B','C')] para colorear las calles correctas.
    
    # Repintamos los nodos que pertenecen a la ruta óptima de color verde.
    nx.draw_networkx_nodes(G, pos, nodelist=ruta_optima, node_color='#90EE90', node_size=2500)
    # Repintamos las aristas que pertenecen a la ruta óptima de color verde y más gruesas (width=4).
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='green', width=4)

    plt.title("Sistema de Navegación Logística - Ruta Sugerida") # Título de la ventana.
    plt.show() # Ordenamos a Python que detenga la ejecución aquí y muestre la ventana en pantalla.


# --- BLOQUE PRINCIPAL INTERACTIVO (Donde arranca el programa) ---
if __name__ == "__main__":
    mapa = Mapa() # Creamos la instancia principal de nuestro sistema.
    
    # 1. Registramos los lugares disponibles en el sistema.
    lugares = ['Almacen', 'Centro Historico', 'Plaza Norte', 'Zona Industrial', 'Casa del Cliente']
    for lugar in lugares:
        mapa.agregar_ubicacion(lugar)

    # 2. Agregamos las conexiones (calles) y el tráfico en minutos de nuestra ciudad virtual.
    mapa.agregar_calle('Almacen', 'Centro Historico', 15)
    mapa.agregar_calle('Almacen', 'Plaza Norte', 20)
    mapa.agregar_calle('Centro Historico', 'Plaza Norte', 10)
    mapa.agregar_calle('Centro Historico', 'Zona Industrial', 25)
    mapa.agregar_calle('Plaza Norte', 'Zona Industrial', 12)
    mapa.agregar_calle('Zona Industrial', 'Casa del Cliente', 8)
    mapa.agregar_calle('Centro Historico', 'Casa del Cliente', 35)

    # 3. --- INTERFAZ DE USUARIO EN CONSOLA ---
    print("\n" + "="*40)
    print(" B I E N V E N I D O   A L   G P S")
    print("="*40)
    print("Lugares disponibles en el mapa:")
    for lugar in lugares: # Mostramos la lista de lugares válidos para que el usuario sepa qué escribir.
        print(f" - {lugar}")
    print("="*40)

    # 4. Validar punto de partida ingresado por el usuario
    punto_partida = ""
    while punto_partida not in lugares: # Este bucle atrapa al usuario hasta que escriba un lugar válido.
        punto_partida = input("\nPor favor, escribe el lugar de PARTIDA: ")
        if punto_partida not in lugares:
            print("⚠️ Error: Ese lugar no está en el mapa. Revisa la ortografía.")

    # 5. Validar destino final ingresado por el usuario
    destino_final = ""
    while destino_final not in lugares: # Mismo bucle de validación, pero para el destino.
        destino_final = input("Por favor, escribe el lugar de DESTINO: ")
        if destino_final not in lugares:
            print("⚠️ Error: Ese lugar no está en el mapa. Revisa la ortografía.")

    # 6. Procesamos la solicitud interactiva
    if punto_partida == destino_final: # Si el usuario pone el mismo origen y destino, no hay nada que calcular.
        print("\n¡Ya estás en tu destino! No es necesario calcular una ruta.")
    else:
        mapa.calcular_ruta_optima(punto_partida) # Arrancamos el motor de Inteligencia Artificial (Dijkstra).
        
        # 7. Imprimimos los resultados finales limpios en consola.
        ruta, tiempo_total = mapa.obtener_ruta(punto_partida, destino_final) # Extraemos los datos calculados.
        print(f"\n" + "="*40)
        print(f" RESUMEN DE RUTA PARA EL CONDUCTOR")
        print(f"="*40)
        print(f"Itinerario: {' -> '.join(ruta)}") # Une los elementos de la lista con una flechita visual.
        print(f"Tiempo total estimado: {tiempo_total} minutos")
        print(f"="*40)
        
        # 8. Finalmente, lanzamos la interfaz gráfica.
        print("\nDesplegando mapa virtual...")
        graficar_resultado(mapa, ruta)