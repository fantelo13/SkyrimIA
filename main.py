from queue import PriorityQueue
import time
import pygame

class TreeNode:

    coord = None        #tupla com as coordenadas
    priority = None     #priority é o f_x para busca heuristica (f_x = g_x + h_x), h_x é a distância heuristica que falta ao destino
    value_gx = None     #g_x é a distância percorrida da origem até o nó atual
    children = []
    parent = None

    def __init__(self, coord, fx, gx = None):
        self.coord = coord
        if gx == None: # se nao for busca heuristica
            self.priority = fx
            self.value_gx = fx
        else:
            self.priority = fx
            self.value_gx = gx

    def get_coord(self):
        return self.coord
    
    def get_priority(self):
        return self.priority
    
    def get_value_gx(self):
        return self.value_gx

    def set_parent(self, value):
        self.parent = value
    
    def get_parent(self):
        return self.parent

    def add_child(self,value):
        self.children.append(value)

    def remove_child(self, value):
        self.children.remove(value)

    def __lt__(self, other):
        return self.priority < other.priority

# Globals
y = 0
x = 0

def read_file(filename):
    global x, y
    start = end = (0, 0)
    with open(filename) as file:
        lines = [line.strip() for line in file.readlines()]
        for j, line in enumerate(lines):
            if 'P' in line:
                end = (line.find('P'), j)
            if '0' in line:
                start = (line.find('0'), j)
    x = len(lines[0])
    y = len(lines)
    return lines, start, end

TILE_SIZE = 3
pygame.init()
screen= None
colors = {
    'mountain': (100, 100, 100), 'snow': (240, 240, 240), 'forest': (34, 139, 34),
    'water': (0, 105, 148), 'rocks': (139, 69, 19), 'free': (236, 185, 139),
    'events': (255, 255, 0), 'start': (255, 0, 255), 'end': (255, 0, 0),
    'visited': (128, 0, 128), 'current': (255, 203, 219), '#':(60,60,60)

}


events = {"1":55, "2":60, "3":65, "4":70, "5":75, "6":80,
    "7":85, "8":90, "9":95, "B":120, "C":125,
    "D":130, "E":135, "G":150, "H":155,
    "I":160, "J":170, "K":180, "O":100
}


characters = {"Dragonborn":[1.8, 5], 
              "Hadvar": [1.6, 5],
              "Lydia":[1.4, 5],
              "Farengar":[1.3, 5],
              "Balgruuf": [1.2,5],
              "Delphine":[1.0,5]}

def init_pygame_window():
    global screen
    screen = pygame.display.set_mode((x * TILE_SIZE, y * TILE_SIZE))
    pygame.display.set_caption("Explorando Skyrim!")



def draw_map(mapa):
    screen.fill((0, 0, 0))
    for j in range(y):
        for i in range(x):
            char = mapa[j][i]
            coord = (i, j)
            color = colors['free']

            if char == 'M': color = colors['mountain']
            elif char == 'A': color = colors['water']
            elif char == 'N': color = colors['snow']
            elif char == 'F': color = colors['forest']
            elif char == 'R': color = colors['rocks']
            elif char == '.': color = colors['free']
            elif char == '0': color = colors['start']
            elif char == 'P': color = colors['end']
            elif char == '#': color = colors["#"]
            elif char in events:
                color = colors['events']

            pygame.draw.rect(screen, color, (i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()

    
uso_personagens = {nome: dados[1] for nome, dados in characters.items()}
def custo_evento_com_personagem(c):
    if c not in events:
        return get_value(c)

    base = events[c]
    melhor_custo = base
    melhor_personagem = None

    for nome, (fator, _) in characters.items():
        if uso_personagens[nome] > 0:
            custo_reduzido = base / fator
            if custo_reduzido < melhor_custo:
                melhor_custo = custo_reduzido
                melhor_personagem = nome

    if melhor_personagem:
        uso_personagens[melhor_personagem] -= 1
        print(f"Usando {melhor_personagem} para reduzir custo de {c} para {melhor_custo:.2f}")
    return melhor_custo


# Path & Terrain
def get_value(c):
    if c in ['.', '0', 'P']: return 1
    if c == 'M': return 50
    if c == 'A': return 20
    if c == 'N': return 15
    if c == 'F': return 10
    if c == 'R': return 5
    if c == '#': return 10000
    if c in events: return events[c]
    return -1

def get_char_from_map(mapa, coord):
    return mapa[coord[1]][coord[0]]

def get_value_from_map(mapa, coord):
    return get_value(get_char_from_map(mapa, coord))


def get_neighborhood(mapa, coord):
    neighbors = []
    directions = [(0,1), (1,0), (0,-1), (-1,0)]
    for dx, dy in directions:
        nx, ny = coord[0]+dx, coord[1]+dy
        if 0 <= nx < x and 0 <= ny < y and get_value_from_map(mapa, (nx, ny)) > -1:
            neighbors.append((nx, ny))
    return neighbors

def manhattan_distance(_from, to):   #Euristica
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])

def find_position(caractere,map):
    j = 0
    for line in map:
        if line.find(caractere)>-1:
            end = (line.find(caractere),j)
            return end
        j+=1


def busca(lst_eventos, mapa, start, end):
    global screen
    if screen is None:
        init_pygame_window()

    fronteira = PriorityQueue()
    fronteira.put((0, (start, 0)))
    visitados = set()
    came_from = {}
    n_tests = 0

    while not fronteira.empty():
        n_tests += 1
        _, (coord, g_atual) = fronteira.get()

        if coord in visitados:
            continue

        visitados.add(coord)

        pygame.draw.rect(screen, colors['visited'], (coord[0] * TILE_SIZE, coord[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, colors['current'], (coord[0] * TILE_SIZE, coord[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.display.update(pygame.Rect(coord[0] * TILE_SIZE, coord[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.event.pump()
        time.sleep(0.001)

        if coord == end:
            print(f"A* finalizado com {n_tests} testes")
            print(f"Custo final de {start} até {end}: {g_atual:.2f}")

            caminho = []
            atual = end
            while atual in came_from:
                caminho.append(atual)
                atual = came_from[atual]
            caminho.append(start)
            caminho.reverse()

            for passo in caminho:
                pygame.draw.rect(screen, colors['visited'], (passo[0] * TILE_SIZE, passo[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                pygame.display.update(pygame.Rect(passo[0] * TILE_SIZE, passo[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                pygame.event.pump()
                time.sleep(0.0005)

            if get_char_from_map(mapa, end) in events:
                lst_eventos.add(end)

            return caminho, g_atual

        for vizinho in get_neighborhood(mapa, coord):
            if vizinho not in visitados:
                custo = get_value_from_map(mapa, vizinho)
                if custo == 0 and get_char_from_map(mapa, vizinho) != get_char_from_map(mapa, end):
                    custo = 99999

                g_novo = g_atual + custo
                h = manhattan_distance(vizinho, end)
                f = g_novo + h
                fronteira.put((f, (vizinho, g_novo)))
                came_from[vizinho] = coord

    print("Caminho não encontrado")
    return [], float('inf')


#Combinatória
def combinatoria():
    return 

def calculoTempo():

    return


# Execução
mapa, start, end = read_file('mapa.txt')
init_pygame_window()
draw_map(mapa)  # Só uma vez no início
lst_eventos = set()
total_path = []
custo_total = 0

for objetivo in events:
    end = find_position(objetivo, mapa)
    result = busca(lst_eventos, mapa, start, end)
    total_path.extend(result[0])
    custo_total += result[1]
    start = end  # move o início para o próximo objetivo
    draw_map(mapa)
    for coord in total_path:
        pygame.draw.rect(screen, colors['visited'], pygame.Rect(coord[0] * TILE_SIZE, coord[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.display.flip()


# Finalmente, vá do último evento até o destino 'P'
end = find_position('P', mapa)
result = busca(lst_eventos,mapa, start, end)
total_path.extend(result[0])
custo_total += result[1]

print(f"\nCaminho completo realizado com sucesso!")
print(f" Custo total acumulado: {custo_total:.2f}")






