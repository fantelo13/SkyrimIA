import math
import random
from typing import List
from simulador import read_file, simula_ordem_eventos_sem_energia

# Eventos válidos no mapa
eventos_validos = ['1','2','3','4','5','6','7','8','9','B','C','D','E','G','H','I','J','K','O']

def gerar_vizinho(ordem: List[str]) -> List[str]:
    nova = ordem[:]
    i, j = random.sample(range(len(nova)), 2)
    nova[i], nova[j] = nova[j], nova[i]
    return nova

def simulated_annealing(
    ordem_inicial: List[str], mapa, inicio, fim,
    avaliar_ordem_funcao,
    temperatura_inicial=1000.0, taxa_resfriamento=0.995, temperatura_minima=1.0
):
    atual = ordem_inicial[:]
    custo_atual = avaliar_ordem_funcao(atual, mapa, inicio, fim)
    if custo_atual == float("inf"):
        print("⚠️ Ordem inicial inválida (custo infinito).")
        return atual, custo_atual

    melhor = atual[:]
    melhor_custo = custo_atual
    temperatura = temperatura_inicial
    iteracoes = 0

    while temperatura > temperatura_minima:
        iteracoes += 1
        vizinho = gerar_vizinho(atual)
        custo_vizinho = avaliar_ordem_funcao(vizinho, mapa, inicio, fim)

        delta = custo_vizinho - custo_atual
        print(f"Temp: {temperatura:.1f} | Iter: {iteracoes} | Custo atual: {custo_atual:.2f} | Melhor: {melhor_custo:.2f}", end='\r')

        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            atual = vizinho
            custo_atual = custo_vizinho
            if custo_vizinho < melhor_custo:
                melhor = vizinho
                melhor_custo = custo_vizinho

        temperatura *= taxa_resfriamento

    print("\n--- Resultados do Simulated Annealing ---")
    print("Ordem inicial:", ordem_inicial)
    print("Melhor ordem final:", melhor)
    print(f"Custo total: {melhor_custo:.2f}")
    print(f"Iterações totais: {iteracoes}")

    return melhor, melhor_custo

if __name__ == "__main__":
    mapa, inicio, fim = read_file("mapa_skyrim.txt")
    melhor_ordem, custo = simulated_annealing(eventos_validos, mapa, inicio, fim, simula_ordem_eventos_sem_energia)


#Ordem Retornada: ['1', 'E', 'H', '9', 'G', '5', 'C', 'O', 'D', 'I', 'J', 'K', '8', 'B', '6', '4', '3', '7', '2']