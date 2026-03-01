# MODO: MÍNIMO - Objetivo: Conectar todas las ciudades pavimentando la menor cantidad de kilómetros.
import networkx as nx
import matplotlib.pyplot as plt

# --- CLASE AUXILIAR: UNION-FIND (Estructura de Datos) ---
# Esta clase es el "cerebro" matemático de Kruskal para evitar formar anillos/circuitos (ciclos) cerrados.
class UnionFind:
    def __init__(self, ciudades):
        # Al principio, cada ciudad es "jefa" de su propio grupo aislado.
        self.padre = {ciudad: ciudad for ciudad in ciudades}
    
    def encontrar_raiz(self, ciudad):
        # Busca recursivamente quién es el líder del grupo al que pertenece esta ciudad.
        if self.padre[ciudad] == ciudad:
            return ciudad
        return self.encontrar_raiz(self.padre[ciudad])
    
    def unir_grupos(self, ciudad_A, ciudad_B):
        # Buscamos a los líderes de los grupos de la ciudad A y la ciudad B
        raiz_A = self.encontrar_raiz(ciudad_A)
        raiz_B = self.encontrar_raiz(ciudad_B)
        
        # Si tienen líderes diferentes, significa que pertenecen a grupos separados y podemos unirlos de forma segura.
        if raiz_A != raiz_B:
            self.padre[raiz_A] = raiz_B # El líder A ahora se subordina al líder B (se fusionan).
            return True  # Unión exitosa, no hay ciclo.
        
        # Si tienen el mismo líder, significa que ya estaban conectados por otro camino. Unirlos crearía un ciclo (anillo).
        return False # Unión rechazada.

# --- FUNCIÓN DE INGRESO DE DATOS (Interacción con el usuario) ---
def planificar_carreteras():
    G = nx.Graph() # Creamos un grafo vacío (nuestro mapa).
    print("\n--- PLANIFICADOR DE CARRETERAS ESTATALES ---")
    print("Ingresa las posibles carreteras: Ciudad_A Ciudad_B Kilómetros")
    print("Ejemplo: Guadalajara Zapopan 15")
    print("Escribe 'fin' para terminar y calcular la ruta más barata.\n")

    while True:
        entrada = input(">> Ingresa tramo (Origen Destino KM): ")
        if entrada.lower() == 'fin': # Condición de salida del bucle.
            break
        try:
            datos = entrada.split() # Separamos el texto por espacios en una lista.
            if len(datos) != 3:     # Validamos que siempre sean 3 datos.
                print("⚠️ Error: Ingresa 3 valores.")
                continue
            
            # Asignamos los datos a variables con nombres lógicos.
            origen, destino, km = datos[0], datos[1], int(datos[2])
            G.add_edge(origen, destino, weight=km) # Agregamos la carretera posible al mapa.
        except ValueError:
            print("⚠️ Error: Los kilómetros deben ser un número entero.")
    return G

# --- ALGORITMO KRUSKAL MÍNIMO ---
def ejecutar_kruskal_minimo():
    G = planificar_carreteras() # Pedimos al usuario que llene el mapa.
    
    if len(G.edges) == 0: # Si no hay carreteras ingresadas, terminamos.
        print("Mapa vacío. Cancelando.")
        return

    # 1. Preparación Visual
    pos = nx.spring_layout(G, seed=42, weight=None, k=2.0)
    plt.ion() # Modo interactivo para animar.
    fig, ax = plt.subplots(figsize=(10, 7)) # Tamaño de la ventana.
    
    # 2. ORDENAMIENTO (El secreto de Kruskal Mínimo)
    # Kruskal siempre revisa TODAS las aristas ordenadas de menor a mayor.
    # Así garantiza que siempre elegirá pavimentar las carreteras más cortas primero.
    carreteras_ordenadas = sorted(G.edges(data=True), key=lambda x: x[2]['weight'])
    
    uf = UnionFind(G.nodes())   # Instanciamos nuestra herramienta detectora de ciclos.
    carreteras_aprobadas = []   # Guardará los tramos que SÍ se van a construir.
    carreteras_rechazadas = []  # Guardará los tramos que sobran (forman anillos).
    costo_total = 0             # Acumulador de kilómetros totales.
    
    print(f"\n{'='*50}")
    print(f" EVALUANDO PROYECTOS (DE MENOR A MAYOR COSTO) ")
    print(f"{'='*50}\n")
    
    paso = 1
    # 3. BUCLE PRINCIPAL: Evaluamos cada carretera en orden
    for u, v, data in carreteras_ordenadas:
        km = data['weight'] # Extraemos los kilómetros de esta ruta.
        
        # --- DIBUJAR ESTADO BASE ---
        ax.clear()
        ax.set_title(f"Plan de Asfalto Óptimo - Tramo {paso}\nAnalizando: {u}-{v} ({km} km)", fontsize=14)
        
        # Dibujamos las carreteras base (grises punteadas)
        nx.draw(G, pos, ax=ax, with_labels=False, node_color='lightgray', edge_color='lightgray', style='dotted', node_size=2000)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
        
        # Dibujamos las carreteras ya aprobadas (verdes) y rechazadas (rojas punteadas)
        if carreteras_aprobadas:
            nx.draw_networkx_edges(G, pos, edgelist=carreteras_aprobadas, edge_color='green', width=3, ax=ax)
        if carreteras_rechazadas:
            nx.draw_networkx_edges(G, pos, edgelist=carreteras_rechazadas, edge_color='red', style='dashed', alpha=0.5, ax=ax)
            
        # Dibujamos la carretera que estamos evaluando en ESTE momento (azul grueso)
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='blue', width=4, ax=ax)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", font_color="black") # Textos siempre arriba
        
        plt.pause(1.5) # Pausa para ver qué ruta está analizando la IA.
        
        # --- LÓGICA DE DETECCIÓN DE CICLOS ---
        # Le preguntamos a UnionFind si al construir este tramo conectaríamos ciudades nuevas o formaríamos un círculo innecesario.
        if uf.unir_grupos(u, v):
            print(f"Tramo {paso}: {u} -> {v} ({km} km) - APROBADO (Conecta nueva zona)")
            carreteras_aprobadas.append((u, v)) # La guardamos como definitiva.
            costo_total += km                   # Sumamos los kilómetros al presupuesto total.
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='lime', width=5, ax=ax) # Parpadeo verde de éxito.
        else:
            print(f"Tramo {paso}: {u} -> {v} ({km} km) - RECHAZADO (Redundante, ya hay acceso)")
            carreteras_rechazadas.append((u, v)) # La marcamos como innecesaria.
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='red', width=5, ax=ax)  # Parpadeo rojo de rechazo.

        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", font_color="black")
        plt.pause(1.0)
        paso += 1

    # --- RESULTADO FINAL EN PANTALLA ---
    ax.clear()
    ax.set_title(f"Red de Carreteras Optimizada\nTotal a pavimentar: {costo_total} km", fontsize=16, color='green')
    
    # Dibujamos el mapa final, solo con las rutas verdes limpias.
    nx.draw(G, pos, ax=ax, with_labels=False, node_color='#90EE90', edge_color='lightgray', style='dotted', node_size=2000)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
    nx.draw_networkx_edges(G, pos, edgelist=carreteras_aprobadas, edge_color='green', width=3)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", font_color="black")
    
    print(f"\n{'='*50}")
    print(f"PROYECTO FINALIZADO. Kilómetros totales: {costo_total}")
    
    plt.ioff()
    plt.show() # Mantenemos la ventana gráfica abierta.

# Punto de entrada principal
if __name__ == "__main__":
    ejecutar_kruskal_minimo()