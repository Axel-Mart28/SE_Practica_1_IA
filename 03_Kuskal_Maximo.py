# MODO: MÁXIMO - Objetivo: Conectar todos los tanques usando las tuberías que soporten la MAYOR cantidad de flujo de agua.
import networkx as nx
import matplotlib.pyplot as plt

# --- CLASE AUXILIAR: UNION-FIND (Estructura de Datos) ---
# Funciona exactamente igual que en la versión mínima: previene ciclos.
class UnionFind:
    def __init__(self, tanques):
        self.padre = {tanque: tanque for tanque in tanques}
    
    def encontrar_raiz(self, tanque):
        if self.padre[tanque] == tanque:
            return tanque
        return self.encontrar_raiz(self.padre[tanque])
    
    def unir_grupos(self, tanque_A, tanque_B):
        raiz_A = self.encontrar_raiz(tanque_A)
        raiz_B = self.encontrar_raiz(tanque_B)
        
        if raiz_A != raiz_B:
            self.padre[raiz_A] = raiz_B 
            return True 
        return False

# --- FUNCIÓN DE INGRESO DE DATOS (Interacción con el usuario) ---
def planificar_acueducto():
    G = nx.Graph() 
    print("\n--- DISEÑO DE ACUEDUCTO DE ALTO FLUJO ---")
    print("Ingresa las posibles tuberías: Tanque_A Tanque_B Litros_Por_Segundo")
    print("Ejemplo: Presa Planta_Tratamiento 500")
    print("Escribe 'fin' para terminar y buscar las tuberías más grandes.\n")

    while True:
        entrada = input(">> Ingresa tubo (Origen Destino L/s): ")
        if entrada.lower() == 'fin': 
            break
        try:
            datos = entrada.split() 
            if len(datos) != 3:     
                print("⚠️ Error: Ingresa 3 valores.")
                continue
            
            # Cambiamos las variables para reflejar el problema de las tuberías.
            origen, destino, litros = datos[0], datos[1], int(datos[2])
            G.add_edge(origen, destino, weight=litros) 
        except ValueError:
            print("⚠️ Error: Los litros deben ser un número entero.")
    return G

# --- ALGORITMO KRUSKAL MÁXIMO ---
def ejecutar_kruskal_maximo():
    G = planificar_acueducto() 
    
    if len(G.edges) == 0: 
        print("Mapa vacío. Cancelando.")
        return

    # 1. Preparación Visual
    pos = nx.spring_layout(G, seed=42) 
    plt.ion() 
    fig, ax = plt.subplots(figsize=(10, 7)) 
    
    # 2. ORDENAMIENTO (El secreto de Kruskal Máximo)
    # ATENCIÓN AQUÍ: Se añade `reverse=True`. 
    # Ahora Kruskal revisa primero los números MÁS GRANDES. Priorizará usar las tuberías más gruesas.
    tubos_ordenados = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
    
    uf = UnionFind(G.nodes())   
    tubos_aprobados = []   
    tubos_rechazados = []  
    capacidad_total = 0             
    
    print(f"\n{'='*50}")
    print(f" EVALUANDO TUBERÍAS (DE MAYOR A MENOR CAPACIDAD) ")
    print(f"{'='*50}\n")
    
    paso = 1
    # 3. BUCLE PRINCIPAL: Evaluamos cada tubo (empezando por los más grandes)
    for u, v, data in tubos_ordenados:
        flujo = data['weight'] # Extraemos los Litros por segundo.
        
        # --- DIBUJAR ESTADO BASE ---
        ax.clear()
        ax.set_title(f"Diseño de Acueducto Máximo - Paso {paso}\nAnalizando Tubo: {u}-{v} ({flujo} L/s)", fontsize=14)
        
        nx.draw(G, pos, ax=ax, with_labels=False, node_color='#add8e6', edge_color='lightgray', style='dotted', node_size=2000)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
        
        if tubos_aprobados:
            nx.draw_networkx_edges(G, pos, edgelist=tubos_aprobados, edge_color='#1E90FF', width=3, ax=ax) # Azul fuerte para tubos de agua aprobados.
        if tubos_rechazados:
            nx.draw_networkx_edges(G, pos, edgelist=tubos_rechazados, edge_color='red', style='dashed', alpha=0.5, ax=ax)
            
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='purple', width=4, ax=ax) # Morado para evaluación.
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", font_color="black")
        
        plt.pause(1.5) 
        
        # --- LÓGICA DE DETECCIÓN DE CICLOS ---
        if uf.unir_grupos(u, v):
            print(f"Paso {paso}: Tubo {u} -> {v} ({flujo} L/s) - APROBADO (Conecta tanques)")
            tubos_aprobados.append((u, v)) 
            capacidad_total += flujo       # Sumamos el flujo asegurado al sistema.
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='lime', width=5, ax=ax) 
        else:
            print(f"Paso {paso}: Tubo {u} -> {v} ({flujo} L/s) - RECHAZADO (Redundante, formaría un ciclo)")
            tubos_rechazados.append((u, v)) 
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='red', width=5, ax=ax)  

        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", font_color="black")
        plt.pause(1.0)
        paso += 1

    # --- RESULTADO FINAL EN PANTALLA ---
    ax.clear()
    ax.set_title(f"Red de Acueducto Optimizada (Alto Flujo)\nFlujo Base del Sistema: {capacidad_total} L/s", fontsize=16, color='#1E90FF')
    
    nx.draw(G, pos, ax=ax, with_labels=False, node_color='#87CEEB', edge_color='lightgray', style='dotted', node_size=2000)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
    nx.draw_networkx_edges(G, pos, edgelist=tubos_aprobados, edge_color='#1E90FF', width=4) # Tubos gruesos
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", font_color="black")
    
    print(f"\n{'='*50}")
    print(f"DISEÑO FINALIZADO. Flujo base garantizado: {capacidad_total} L/s")
    
    plt.ioff()
    plt.show() 

# Punto de entrada principal
if __name__ == "__main__":
    ejecutar_kruskal_maximo()