from typing import List, Tuple, Dict
from copy import deepcopy
from queue import PriorityQueue

Personagem = Tuple[str, float, int]
Evento = str
Coord = Tuple[int, int]

personagens_base: Dict[str, Tuple[float, int]] = {
    "Dragonborn": (1.8, 5),
    "Hadvar": (1.6, 5),
    "Lydia": (1.4, 5),
    "Farengar": (1.3, 5),
    "Balgruuf": (1.2, 5),
    "Delphine": (1.0, 5),
}

dificuldades_eventos: Dict[str, int] = {
    "1": 55, "2": 60, "3": 65, "4": 70, "5": 75, "6": 80, "7": 85, "8": 90, "9": 95,
    "B": 120, "C": 125, "D": 130, "E": 135, "G": 150, "H": 155, "I": 160,
    "J": 170, "K": 180, "O": 100
}

def custo_evento(personagens_usados: List[str], evento: Evento, energia: Dict[str, int]) -> float:
    if not personagens_usados:
        print(f"[ERRO] Nenhum personagem selecionado para o evento '{evento}'.")
        return float("inf")
    if evento not in dificuldades_eventos:
        return 0.0
    soma_poder = sum(personagens_base[p][0] for p in personagens_usados if energia[p] > 0)
    if soma_poder == 0:
        print(f"[ERRO] Nenhum personagem com energia para evento '{evento}'.")
        return float("inf")
    tempo = dificuldades_eventos[evento] / soma_poder
    for p in personagens_usados:
        if energia[p] > 0:
            energia[p] -= 1
    return tempo

def pelo_menos_um_vivo(energia: Dict[str, int]) -> bool:
    return any(v > 0 for v in energia.values())

def simula_ordem_eventos_sem_energia(ordem: List[Evento], mapa, coord_inicio: Coord, coord_fim: Coord) -> float:
    def get_value(c):
        return {'.': 1, '0': 1, 'P': 1, 'M': 50, 'A': 20, 'N': 15, 'F': 10, 'R': 5, '#': 10000}.get(c, 1)

    def get_value_from_map(mapa, coord):
        return get_value(mapa[coord[1]][coord[0]])

    def get_neighborhood(mapa, coord):
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        x_max, y_max = len(mapa[0]), len(mapa)
        return [(coord[0]+dx, coord[1]+dy) for dx, dy in directions
                if 0 <= coord[0]+dx < x_max and 0 <= coord[1]+dy < y_max and get_value_from_map(mapa, (coord[0]+dx, coord[1]+dy)) < 10000]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def busca(mapa, start, end):
        fronteira = PriorityQueue()
        fronteira.put((0, start))
        custo_g = {start: 0}
        came_from = {}

        while not fronteira.empty():
            _, atual = fronteira.get()
            if atual == end:
                return custo_g[atual]
            for vizinho in get_neighborhood(mapa, atual):
                novo_custo = custo_g[atual] + get_value_from_map(mapa, vizinho)
                if vizinho not in custo_g or novo_custo < custo_g[vizinho]:
                    custo_g[vizinho] = novo_custo
                    prioridade = novo_custo + manhattan(vizinho, end)
                    fronteira.put((prioridade, vizinho))
                    came_from[vizinho] = atual
        print(f"[ERRO] Caminho de {start} até {end} falhou.")
        return float("inf")

    def find_position(c, mapa):
        for j, linha in enumerate(mapa):
            i = linha.find(c)
            if i != -1:
                return (i, j)
        return None

    custo_total = 0.0
    posicao_atual = coord_inicio

    for evento in ordem:
        posicao_evento = find_position(evento, mapa)
        if posicao_evento is None:
            print(f"[ERRO] Evento '{evento}' não encontrado no mapa.")
            return float("inf")

        custo_caminho = busca(mapa, posicao_atual, posicao_evento)
        if custo_caminho == float("inf"):
            print(f"[ERRO] Falha ao alcançar evento '{evento}' saindo de {posicao_atual} para {posicao_evento}.")
            return float("inf")

        custo_total += custo_caminho
        posicao_atual = posicao_evento

    custo_final = busca(mapa, posicao_atual, coord_fim)
    if custo_final == float("inf"):
        print(f"[ERRO] Caminho final de {posicao_atual} até {coord_fim} falhou.")
        return float("inf")

    custo_total += custo_final
    return custo_total

def read_file(filename: str):
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines()]
        start = end = (0, 0)
        for j, line in enumerate(lines):
            if '0' in line:
                start = (line.find('0'), j)
            if 'P' in line:
                end = (line.find('P'), j)
        return lines, start, end
