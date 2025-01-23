import heapq
import time
from collections import deque
import sys

def memoria_utilizada(obj):
    visitados = set()

    def tamanho_recur(o):
        if id(o) in visitados:
            return 0
        visitados.add(id(o))
        tamanho = sys.getsizeof(o)
        if isinstance(o, dict):
            tamanho += sum(tamanho_recur(k) + tamanho_recur(v) for k, v in o.items())
        elif isinstance(o, (list, tuple, set, frozenset)):
            tamanho += sum(tamanho_recur(i) for i in o)
        return tamanho

    return tamanho_recur(obj)

def eh_estado_meta(estado, n):
    encontrou_azul = False
    for bloco in estado:
        if bloco == 'A':
            encontrou_azul = True
        elif bloco == 'B' and encontrou_azul:
            return False
    return True

def sucessores(estado, n):
    posicao_vazia = estado.index('-')
    movimentos = []
    for deslocamento in range(-n, n + 1):
        nova_posicao = posicao_vazia + deslocamento
        if 0 <= nova_posicao < len(estado) and nova_posicao != posicao_vazia and abs(deslocamento) <= n:
            novo_estado = estado[:]
            novo_estado[posicao_vazia], novo_estado[nova_posicao] = novo_estado[nova_posicao], novo_estado[posicao_vazia]
            movimentos.append((novo_estado, abs(deslocamento)))
    return movimentos

def busca_largura(estado_inicial, n, exibir_movimentos=False):
    inicio = time.time()
    fila = deque([(estado_inicial, 0, [])])
    visitados = set()
    visitados.add(tuple(estado_inicial))
    nos_expandidos = 0
    memoria_maxima = 0
    total_sucessores = 0
    while fila:
        estado_atual, custo, path = fila.popleft()
        nos_expandidos += 1
        memoria_maxima = max(memoria_maxima, memoria_utilizada(fila) + memoria_utilizada(visitados))
        filhos = sucessores(estado_atual, n)
        total_sucessores += len(filhos)
        if eh_estado_meta(estado_atual, n):
            if exibir_movimentos:
                print("Movimentos realizados:")
                for movimento in path:
                    print(movimento)
            fator_ramificacao = total_sucessores / nos_expandidos if nos_expandidos > 1 else 0
            return custo, nos_expandidos, time.time() - inicio, memoria_maxima, fator_ramificacao
        for vizinho, _ in filhos:
            if tuple(vizinho) not in visitados:
                visitados.add(tuple(vizinho))
                fila.append((vizinho, custo + 1, path + [vizinho]))
    return None, nos_expandidos, time.time() - inicio, memoria_maxima, 0

def busca_profundidade_iterativa(estado_inicial, n, exibir_movimentos=False):
    inicio = time.time()
    profundidade = 0
    nos_expandidos = 0
    memoria_maxima = 0
    total_sucessores = 0

    while True:
        visitados = set()
        pilha = [(estado_inicial, 0, [])]
        profundidade_atual_sucessores = 0

        while pilha:
            estado_atual, custo, path = pilha.pop()

            if custo > profundidade:
                continue

            if tuple(estado_atual) in visitados:
                continue

            visitados.add(tuple(estado_atual))
            nos_expandidos += 1

            filhos = sucessores(estado_atual, n)
            profundidade_atual_sucessores += len(filhos)

            if eh_estado_meta(estado_atual, n):
                if exibir_movimentos:
                    print("Movimentos realizados:")
                    for movimento in path:
                        print(movimento)
                fator_ramificacao = total_sucessores / nos_expandidos if nos_expandidos > 1 else 0
                return custo, nos_expandidos, time.time() - inicio, memoria_utilizada(visitados), fator_ramificacao

            for vizinho, _ in filhos:
                if tuple(vizinho) not in visitados:
                    pilha.append((vizinho, custo + 1, path + [vizinho]))

        total_sucessores += profundidade_atual_sucessores
        profundidade += 1

def heuristica_melhor_localizacao(estado):
    penalidade = 0
    encontrou_azul = False
    for bloco in estado:
        if bloco == 'A':
            encontrou_azul = True
        elif bloco == 'B' and encontrou_azul:
            penalidade += 1
    return penalidade

def heuristica_inversoes(estado):
    inversoes = 0
    for i in range(len(estado)):
        for j in range(i + 1, len(estado)):
            if estado[i] != '-' and estado[j] != '-' and estado[i] > estado[j]:
                inversoes += 1
    return inversoes

def busca_a_estrela(estado_inicial, n, heuristica, exibir_movimentos=False):
    inicio = time.time()
    fronteira = []
    heapq.heappush(fronteira, (0, estado_inicial, 0, []))
    visitados = set()
    nos_expandidos = 0
    memoria_maxima = 0
    total_sucessores = 0
    while fronteira:
        _, estado_atual, custo, path = heapq.heappop(fronteira)

        if tuple(estado_atual) in visitados:
            continue
        visitados.add(tuple(estado_atual))

        nos_expandidos += 1
        memoria_maxima = max(memoria_maxima, memoria_utilizada(fronteira) + memoria_utilizada(visitados))
        filhos = sucessores(estado_atual, n)
        total_sucessores += len(filhos)

        if eh_estado_meta(estado_atual, n):
            if exibir_movimentos:
                print("Movimentos realizados:")
                for movimento in path:
                    print(movimento)
            fator_ramificacao = total_sucessores / nos_expandidos if nos_expandidos > 1 else 0
            return custo, nos_expandidos, time.time() - inicio, memoria_maxima, fator_ramificacao

        for vizinho, movimento_custo in filhos:
            if tuple(vizinho) not in visitados:
                heuristica_valor = heuristica(vizinho)
                novo_custo = custo + movimento_custo
                heapq.heappush(fronteira, (novo_custo + heuristica_valor, vizinho, novo_custo, path + [vizinho]))
    return None, nos_expandidos, time.time() - inicio, memoria_maxima, 0

# Exemplo de execução
N = 2
estado_inicial = ['A', 'B', '-', 'A', 'A', 'B', 'B', 'B']

# Executando as buscas com as novas heurísticas
resultado_largura = busca_largura(estado_inicial, N, exibir_movimentos=False)
resultado_profundidade = busca_profundidade_iterativa(estado_inicial, N, exibir_movimentos=True)
resultado_a_estrela_inversoes = busca_a_estrela(estado_inicial, N, heuristica_inversoes, exibir_movimentos=False)
resultado_a_estrela_melhor_localizacao = busca_a_estrela(estado_inicial, N, heuristica_melhor_localizacao, exibir_movimentos=False)

# Imprimindo o relatório de resultados
print("Relatório de Resultados:\n")
print("Busca em Largura:")
print(f"  Custo: {resultado_largura[0]}")
print(f"  Nós Expandidos: {resultado_largura[1]}")
print(f"  Tempo Gasto: {resultado_largura[2]:.6f} segundos")
print(f"  Memória Utilizada: {resultado_largura[3] / 1024:.2f} KB")
print(f"  Fator de Ramificação: {resultado_largura[4]:.2f}")

print("\nBusca em Profundidade Iterativa:")
print(f"  Custo: {resultado_profundidade[0]}")
print(f"  Nós Expandidos: {resultado_profundidade[1]}")
print(f"  Tempo Gasto: {resultado_profundidade[2]:.6f} segundos")
print(f"  Memória Utilizada: {resultado_profundidade[3] / 1024:.2f} KB")
print(f"  Fator de Ramificação: {resultado_profundidade[4]:.2f}")

print("\nBusca A* (Heurística de Inversões):")
print(f"  Custo: {resultado_a_estrela_inversoes[0]}")
print(f"  Nós Expandidos: {resultado_a_estrela_inversoes[1]}")
print(f"  Tempo Gasto: {resultado_a_estrela_inversoes[2]:.6f} segundos")
print(f"  Memória Utilizada: {resultado_a_estrela_inversoes[3] / 1024:.2f} KB")
print(f"  Fator de Ramificação: {resultado_a_estrela_inversoes[4]:.2f}")

print("\nBusca A* (Heurística de Melhor Localização):")
print(f"  Custo: {resultado_a_estrela_melhor_localizacao[0]}")
print(f"  Nós Expandidos: {resultado_a_estrela_melhor_localizacao[1]}")
print(f"  Tempo Gasto: {resultado_a_estrela_melhor_localizacao[2]:.6f} segundos")
print(f"  Memória Utilizada: {resultado_a_estrela_melhor_localizacao[3] / 1024:.2f} KB")
print(f"  Fator de Ramificação: {resultado_a_estrela_melhor_localizacao[4]:.2f}")
