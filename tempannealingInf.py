# annealing.py
import math
import random
from typing import List
from simulador import simula_ordem_eventos, read_file

# Apenas eventos garantidamente presentes no mapa.txt
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
        print("⚠️ Ordem inicial inválida (custo infinito). Verifique se todos os eventos estão acessíveis.")
        return atual, custo_atual

    melhor = atual[:]
    melhor_custo = custo_atual
    temperatura = temperatura_inicial

    while temperatura > temperatura_minima:
        vizinho = gerar_vizinho(atual)
        custo_vizinho = avaliar_ordem_funcao(vizinho, mapa, inicio, fim)

        delta = custo_vizinho - custo_atual
        print(f"Temp: {temperatura:.1f} | Custo atual: {custo_atual:.2f} | Melhor: {melhor_custo:.2f}", end='\r')

        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            atual = vizinho
            custo_atual = custo_vizinho
            if custo_vizinho < melhor_custo:
                melhor = vizinho
                melhor_custo = custo_vizinho

        temperatura *= taxa_resfriamento

    return melhor, melhor_custo

if __name__ == "__main__":
    mapa, inicio, fim = read_file("mapa.txt")
    melhor_ordem, custo = simulated_annealing(eventos_validos, mapa, inicio, fim, simula_ordem_eventos)

    print("\nMelhor ordem de eventos encontrada:")
    print(melhor_ordem)
    print(f"Custo total com essa ordem: {custo:.2f}")
