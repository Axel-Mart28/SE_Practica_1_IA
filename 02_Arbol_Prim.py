# En este programa el usuario ingresa los edificios y las distancias para simular el tendido de una red de fibra óptica.
import networkx as nx            # Librería matemática para manejar la estructura de la red (nodos y conexiones).
import matplotlib.pyplot as plt  # Librería para dibujar la animación de cómo se va construyendo la red paso a paso.

# Función para que el ingeniero (usuario) ingrese los planos de la red manualmente.
def planificar_red_fibra(): 
    G = nx.Graph() # Creamos un grafo vacío que representará nuestro plano de la ciudad/empresa.
    
    # Imprimimos las instrucciones en pantalla
    print("\n--- PLANIFICADOR DE RED DE FIBRA ÓPTICA ---")
    print("Ingresa las posibles conexiones en el formato: Edificio1 Edificio2 MetrosDeCable")
    print("Ejemplo: Oficinas Taller 50 (Conecta Oficinas con Taller usando 50 metros de cable)")
    print("Escribe 'fin' cuando termines de agregar todas las rutas posibles.\n")

    # Bucle infinito que se repetirá hasta que el usuario escriba 'fin'
    while True: 
        entrada = input(">> Ingresa tramo (Origen Destino Metros): ")
        
        if entrada.lower() == 'fin': # Si el usuario escribe 'fin', rompemos el bucle.
            break
        
        try:
            # Separamos el texto ingresado por los espacios (ej. ["Oficinas", "Taller", "50"])
            datos = entrada.split()
            
            # Validamos que el usuario haya ingresado exactamente 3 datos
            if len(datos) != 3:
                print("⚠️ Error: Debes ingresar 3 valores separados por espacios.")
                continue # Volvemos al inicio del bucle sin procesar esta línea
            
            u = datos[0]          # El primer dato es el nombre del primer edificio (texto)
            v = datos[1]          # El segundo dato es el nombre del segundo edificio (texto)
            w = int(datos[2])     # El tercer dato son los metros de cable, lo convertimos a número entero.
            
            # Agregamos esta posible conexión de red al plano (Grafo)
            G.add_edge(u, v, weight=w)
            print(f"   [+] Tramo registrado: {u} <--- {w} metros ---> {v}")
            
        except ValueError: # Atrapamos el error si el usuario pone letras en lugar de números para los metros.
            print("⚠️ Error: Los metros de cable deben ser un número entero.")

    return G # Devolvemos el plano completo con todas las opciones ingresadas.


# Función principal que ejecuta la lógica de Prim (La Inteligencia Artificial que optimiza el cableado)
def optimizar_cableado_prim():
    # 1. LLAMAMOS A LA FUNCIÓN DE INGRESO PARA OBTENER EL PLANO
    G = planificar_red_fibra()
    
    # Verificamos si el usuario ingresó al menos una conexión. Si no, cerramos el programa.
    if len(G.nodes) == 0: 
        print("El plano está vacío. Cancelando instalación...")
        return

    # Calculamos posiciones fijas para dibujar los edificios y que no se muevan en cada paso de la animación.
    pos = nx.spring_layout(G, seed=42) 

    # --- 2. PREPARACIÓN DEL ENTORNO VISUAL ---
    plt.ion() # Activamos el modo interactivo de Matplotlib para poder animar el proceso en tiempo real.
    fig, ax = plt.subplots(figsize=(10, 7)) # Creamos la ventana gráfica.
    
    # Preguntamos en qué edificio se conectará el servidor principal (Nodo de inicio)
    nodos_disponibles = list(G.nodes)
    start_node = input(f"\n¿En qué edificio pondremos el servidor principal? (Opciones: {nodos_disponibles}): ")
    
    # Si el usuario escribe mal el nombre, forzamos a que inicie en el primer edificio de la lista.
    if start_node not in nodos_disponibles:
        start_node = nodos_disponibles[0] 
        print(f"Entrada inválida. Instalando servidor por defecto en: {start_node}")

    tramos_elegidos = []                 # Lista para guardar los cables que SÍ vamos a instalar de forma definitiva.
    edificios_conectados = {start_node}  # Conjunto que rastrea qué edificios ya tienen internet. Empezamos con el principal.
    todos_los_edificios = set(G.nodes()) # Conjunto con la meta final: todos los edificios del plano.
    
    print(f"\n{'='*50}")
    print(f" INICIANDO INSTALACIÓN ÓPTIMA (ALGORITMO DE PRIM) ")
    print(f"{'='*50}\n")

    # --- 3. BUCLE PRINCIPAL DE PRIM (El motor de la IA) ---
    step = 1 # Contador de pasos para la consola y el título del gráfico.
    
    # El algoritmo sigue corriendo MIENTRAS haya edificios sin conexión a internet.
    while len(edificios_conectados) < len(todos_los_edificios):
        ax.clear() # Limpiamos el gráfico del paso anterior para dibujar el nuevo.
        ax.set_title(f"Tendido de Fibra Óptica - Día de trabajo {step}", fontsize=15)

        # Dibujamos el "plano base" (todas las opciones posibles en gris y punteadas)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightblue', 
                edge_color='lightgray', node_size=2000, font_weight='bold', style='dashed')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

        # Variables para buscar el siguiente tramo de cable más corto (Lógica "Greedy" / Golosa)
        tramo_mas_barato = None
        metros_minimos = float('inf')
        opciones_disponibles = []

        # BÚSQUEDA DEL CABLE MÁS CORTO:
        conexion_encontrada = False # Bandera para saber si el plano permite conectar más edificios.
        
        # Revisamos todos los edificios que YA TIENEN internet...
        for u in edificios_conectados:
            # ...y miramos hacia todos sus vecinos en el plano base.
            for v in G.neighbors(u):
                # Si el vecino AÚN NO tiene internet (cruza la frontera entre lo conectado y lo no conectado)...
                if v not in edificios_conectados:
                    conexion_encontrada = True
                    metros = G[u][v]['weight'] # Vemos cuántos metros de cable pide ese tramo.
                    opciones_disponibles.append((u, v, metros)) # Lo anotamos como una opción válida.
                    
                    # Si este tramo pide MENOS cable que el récord mínimo actual, lo guardamos como el mejor candidato.
                    if metros < metros_minimos:
                        metros_minimos = metros
                        tramo_mas_barato = (u, v)

    # Si revisamos todo y no hay forma de llegar a los edificios faltantes (plano dividido), lanzamos alerta.
        if not conexion_encontrada:
            print("¡ALERTA! El diseño del plano está cortado. Hay edificios imposibles de conectar.")
            break

        # Imprimimos el estado actual en la consola para el usuario.
        print(f"--- Día {step} ---")
        print(f"Edificios con red: {edificios_conectados}")
        print(f"Opciones de cableado en la frontera: {opciones_disponibles}")
        
        # Si encontramos un tramo óptimo, lo instalamos.
        if tramo_mas_barato: 
            u, v = tramo_mas_barato
            print(f" >> INSTALANDO CABLE: ({u} hacia {v}) usando {metros_minimos} metros.")
            
            tramos_elegidos.append((u, v))  # Guardamos el tramo en el diseño final.
            edificios_conectados.add(v)     # Marcamos el nuevo edificio como "conectado".
            
            # --- DIBUJO DE LA INSTALACIÓN ACTUAL ---
            # Dibujamos de verde los cables ya instalados permanentemente.
            nx.draw_networkx_edges(G, pos, edgelist=tramos_elegidos, edge_color='green', width=3, ax=ax)
            # Resaltamos de rojo grueso el cable exacto que se está instalando en este momento.
            nx.draw_networkx_edges(G, pos, edgelist=[tramo_mas_barato], edge_color='red', width=4, ax=ax)
            # Pintamos de verde claro los edificios que ya tienen internet.
            nx.draw_networkx_nodes(G, pos, nodelist=list(edificios_conectados), node_color='#90EE90', node_size=2000, ax=ax)
        
        print("")
        plt.pause(2) # Hacemos una pausa de 2 segundos para que el usuario pueda ver la animación.
        step += 1    # Avanzamos al siguiente día/paso.

    # --- 4. RESULTADO FINAL ---
    ax.clear() # Limpiamos la pantalla por última vez.
    
    # Calculamos el costo total sumando los metros de todos los tramos elegidos.
    total_metros = sum([G[u][v]['weight'] for u,v in tramos_elegidos])
    
    ax.set_title(f"Red de Fibra Óptica Completada\nTotal de cable utilizado: {total_metros} metros", fontsize=15, color='green')
    
    # Dibujamos el plano final: Fondo en gris punteado, rutas elegidas en verde sólido, y nodos conectados en verde.
    nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightgray', edge_color='lightgray', style='dotted', node_size=2000)
    nx.draw_networkx_edges(G, pos, edgelist=tramos_elegidos, edge_color='green', width=3)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_nodes(G, pos, nodelist=list(edificios_conectados), node_color='#90EE90', node_size=2000)
    
    # Imprimimos el resumen en consola.
    print(f"INSTALACIÓN FINALIZADA. Presupuesto total requerido: {total_metros} metros de cable.")
    
    plt.ioff() # Apagamos el modo interactivo de animación.
    plt.show() # Dejamos la ventana gráfica abierta de forma permanente hasta que el usuario la cierre manualmente.

# Bloque de arranque del script
if __name__ == "__main__":
    optimizar_cableado_prim()