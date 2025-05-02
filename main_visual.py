# main_visual.py
import pygame
import time
from simulador import read_file, personagens_base, dificuldades_eventos, custo_evento, pelo_menos_um_vivo, simula_ordem_eventos
from annealing import simulated_annealing

TILE_SIZE = 3
screen = None
colors = {
    'mountain': (100, 100, 100), 'snow': (240, 240, 240), 'forest': (34, 139, 34),
    'water': (0, 105, 148), 'rocks': (139, 69, 19), 'free': (236, 185, 139),
    'events': (255, 255, 0), 'start': (255, 0, 255), 'end': (255, 0, 0),
    'visited': (128, 0, 128), 'current': (255, 203, 219), '#':(60,60,60),
    'final_path': (180, 0, 255)
}

def init_pygame_window(mapa):
    global screen
    screen = pygame.display.set_mode((len(mapa[0]) * TILE_SIZE, len(mapa) * TILE_SIZE))
    pygame.display.set_caption("Skyrim IA - Visualização")

def draw_map(mapa):
    screen.fill((0, 0, 0))
    for j in range(len(mapa)):
        for i in range(len(mapa[0])):
            char = mapa[j][i]
            color = colors.get('free')
            if char == 'M': color = colors['mountain']
            elif char == 'A': color = colors['water']
            elif char == 'N': color = colors['snow']
            elif char == 'F': color = colors['forest']
            elif char == 'R': color = colors['rocks']
            elif char == '.': color = colors['free']
            elif char == '0': color = colors['start']
            elif char == 'P': color = colors['end']
            elif char == '#': color = colors['#']
            elif char in dificuldades_eventos:
                color = colors['events']
            pygame.draw.rect(screen, color, (i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.display.flip()

def find_position(c, mapa):
    for j, linha in enumerate(mapa):
        i = linha.find(c)
        if i != -1:
            return (i, j)
    return None

def get_value(c):
    return {'.': 1, '0': 1, 'P': 1, 'M': 50, 'A': 20, 'N': 15, 'F': 10, 'R': 5, '#': 10000}.get(c, 1)

def busca_visual(mapa, start, end):
    from queue import PriorityQueue
    fronteira = PriorityQueue()
    fronteira.put((0, start))
    custo_g = {start: 0}
    came_from = {}
    visitados = set()

    while not fronteira.empty():
        _, atual = fronteira.get()
        if atual in visitados:
            continue
        visitados.add(atual)

        pygame.draw.rect(screen, colors['current'], (atual[0]*TILE_SIZE, atual[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.display.update()
        pygame.event.pump()
        time.sleep(0.001)

        if atual == end:
            caminho = []
            while atual != start:
                caminho.append(atual)
                atual = came_from[atual]
            caminho.append(start)
            caminho.reverse()
            for c in caminho:
                pygame.draw.rect(screen, colors['final_path'], (c[0]*TILE_SIZE, c[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.display.flip()
            return custo_g[end], caminho

        x_max, y_max = len(mapa[0]), len(mapa)
        dirs = [(0,1),(1,0),(0,-1),(-1,0)]
        for dx, dy in dirs:
            nx, ny = atual[0]+dx, atual[1]+dy
            if 0 <= nx < x_max and 0 <= ny < y_max:
                viz = (nx, ny)
                if viz in visitados:
                    continue
                custo = get_value(mapa[ny][nx])
                novo = custo_g[atual] + custo
                if viz not in custo_g or novo < custo_g[viz]:
                    custo_g[viz] = novo
                    came_from[viz] = atual
                    fronteira.put((novo, viz))
    return float('inf'), []

if __name__ == "__main__":
    eventos = ['1','2','3','4','5','6','7','8','9','B','C','D','E','G','H','I','J','K','O']
    mapa, inicio, fim = read_file("mapa_skyrim.txt")
    init_pygame_window(mapa)

    melhor_ordem, custo_total = simulated_annealing(eventos, mapa, inicio, fim, simula_ordem_eventos)
    energia = {k: v[1] for k, v in personagens_base.items()}
    atual = inicio
    draw_map(mapa)

    for ev in melhor_ordem:
        alvo = find_position(ev, mapa)
        custo, caminho = busca_visual(mapa, atual, alvo)
        vivos = [p for p in energia if energia[p] > 0]
        top2 = sorted(vivos, key=lambda p: -personagens_base[p][0])[:2]
        tempo_evento = custo_evento(top2, ev, energia)
        print(f"Evento {ev}: caminho {len(caminho)} tiles, tempo {tempo_evento:.2f} com {top2}")
        atual = alvo
        time.sleep(0.3)

    _, final_caminho = busca_visual(mapa, atual, fim)
    print(f"Destino final alcançado: custo total {custo_total:.2f}")

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
