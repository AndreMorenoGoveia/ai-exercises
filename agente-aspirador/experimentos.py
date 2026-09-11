"""
Experimentos com o agente aspirador de pó do AIMA (aimacode/aima-python).

O código do AIMA (pasta `aima/`) é usado sem nenhuma modificação; tudo o que
está aqui é instrumentação e roteiro de testes.

Uso:
    python3 experimentos.py

Gera as tabelas em `resultados/*.csv` e imprime um resumo no terminal.
"""

import copy
import csv
import os
import random
from statistics import mean, pstdev

from aima.agents import (
    Agent, Dirt, Direction,
    ReflexVacuumAgent, TableDrivenVacuumAgent, ModelBasedVacuumAgent,
    RandomVacuumAgent,
    TrivialVacuumEnvironment, VacuumEnvironment,
    compare_agents, loc_A, loc_B,
)

SEED = 42
PASSOS = 1000            # horizonte padrão de simulação
REPETICOES_ALEATORIO = 30  # amostras para o agente aleatório (é estocástico)
DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')

AGENTES = [
    ('Reflexo simples', ReflexVacuumAgent),
    ('Tabela',          TableDrivenVacuumAgent),
    ('Baseado modelo',  ModelBasedVacuumAgent),
    ('Aleatório',       RandomVacuumAgent),
]

# Os 8 estados iniciais do mundo de dois quadrados: 4 configurações de sujeira
# x 2 posições iniciais do agente.
ESTADOS_INICIAIS = [
    ({loc_A: sa, loc_B: sb}, inicio)
    for sa in ('Dirty', 'Clean')
    for sb in ('Dirty', 'Clean')
    for inicio in (loc_A, loc_B)
]


class AmbienteInstrumentado(TrivialVacuumEnvironment):
    """TrivialVacuumEnvironment com registro do que aconteceu.

    Não altera nenhuma regra do ambiente nem a medida de desempenho: só
    guarda a sequência (t, local, status, ação) e o instante em que os dois
    quadrados ficaram limpos.
    """

    def __init__(self, sujeira):
        super().__init__()
        self.status = dict(sujeira)
        self.t = 0
        self.t_limpo = 0 if self._limpo() else None
        self.registro = []

    def _limpo(self):
        return all(s == 'Clean' for s in self.status.values())

    def execute_action(self, agent, action):
        self.registro.append((self.t, agent.location, self.status[agent.location], action))
        super().execute_action(agent, action)

    def step(self):
        super().step()
        self.t += 1
        if self.t_limpo is None and self._limpo():
            self.t_limpo = self.t


def simular(fabrica_agente, sujeira, inicio, passos=PASSOS):
    """Roda um agente num estado inicial dado e devolve as métricas da corrida."""
    amb = AmbienteInstrumentado(sujeira)
    agente = fabrica_agente()
    amb.add_thing(agente, inicio)   # posição inicial fixada (não sorteada)
    amb.run(passos)

    reg = amb.registro
    movimentos = sum(1 for _, _, _, a in reg if a in ('Left', 'Right'))
    sugadas = sum(1 for _, _, _, a in reg if a == 'Suck')
    sugadas_uteis = sum(1 for _, _, st, a in reg if a == 'Suck' and st == 'Dirty')
    ociosas = sum(1 for _, _, _, a in reg if a in ('NoOp', None))
    limpo_em = amb.t_limpo
    desperdicio = 0 if limpo_em is None else sum(
        1 for t, _, _, a in reg if t >= limpo_em and a in ('Left', 'Right'))
    return {
        'desempenho': agente.performance,
        't_limpo': limpo_em,
        'movimentos': movimentos,
        'sugadas': sugadas,
        'sugadas_uteis': sugadas_uteis,
        'ociosas': ociosas,
        'desperdicio': desperdicio,
        'registro': reg,
    }


def simular_medio(nome, fabrica, sujeira, inicio, passos=PASSOS):
    """Como simular(), mas tira média sobre várias sementes p/ o agente aleatório."""
    if nome != 'Aleatório':
        random.seed(SEED)
        return simular(fabrica, sujeira, inicio, passos), 0.0
    amostras = []
    for k in range(REPETICOES_ALEATORIO):
        random.seed(SEED + k)
        amostras.append(simular(fabrica, sujeira, inicio, passos))
    medio = {
        'desempenho': mean(a['desempenho'] for a in amostras),
        't_limpo': mean(a['t_limpo'] for a in amostras if a['t_limpo'] is not None)
                   if any(a['t_limpo'] is not None for a in amostras) else None,
        'movimentos': mean(a['movimentos'] for a in amostras),
        'sugadas': mean(a['sugadas'] for a in amostras),
        'sugadas_uteis': mean(a['sugadas_uteis'] for a in amostras),
        'ociosas': mean(a['ociosas'] for a in amostras),
        'desperdicio': mean(a['desperdicio'] for a in amostras),
        'registro': amostras[0]['registro'],
    }
    return medio, pstdev([a['desempenho'] for a in amostras])


def escrever_csv(nome_arquivo, cabecalho, linhas):
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    caminho = os.path.join(DIR_RESULTADOS, nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)
    return caminho


def titulo(txt):
    print('\n' + '=' * 78)
    print(txt)
    print('=' * 78)


def fmt(x):
    """Formata t_limpo (pode ser None ou média fracionária)."""
    if x is None:
        return '-'
    return '{:.4g}'.format(x)


def rotulo(sujeira, inicio):
    return 'A={:5s} B={:5s} início={}'.format(
        sujeira[loc_A], sujeira[loc_B], 'A' if inicio == loc_A else 'B')


# ---------------------------------------------------------------------------
# Teste 0: os doctests do próprio AIMA para os quatro agentes aspiradores
# ---------------------------------------------------------------------------
def teste_0():
    import doctest
    from aima import agents as mod
    titulo('TESTE 0 - Doctests do AIMA para os agentes aspiradores')
    random.seed(SEED)
    runner = doctest.DocTestRunner(verbose=False)
    alvos = [f for f in doctest.DocTestFinder().find(mod)
             if 'Vacuum' in f.name or f.name.endswith('compare_agents')]
    for teste in sorted((t for t in alvos if t.examples), key=lambda t: t.name):
        antes = runner.failures
        runner.run(teste)
        status = 'OK' if runner.failures == antes else 'FALHOU'
        print('  {:45s} {:>2d} exemplo(s)  {}'.format(teste.name, len(teste.examples), status))
    print('  total: {} exemplos, {} falhas'.format(runner.tries, runner.failures))


# ---------------------------------------------------------------------------
# Experimento 1: os 8 estados iniciais, horizonte de 1000 passos
# ---------------------------------------------------------------------------
def experimento_1():
    titulo('EXPERIMENTO 1 - Desempenho nos 8 estados iniciais (1000 passos)')
    linhas = []
    print('{:22s} {:>8s} {:>8s} {:>7s} {:>7s} {:>8s} {:>9s}'.format(
        'estado inicial', 'agente', 'desemp.', 't_limpo', 'movs', 'sugadas', 'desperd.'))
    resumo = {nome: [] for nome, _ in AGENTES}
    for sujeira, inicio in ESTADOS_INICIAIS:
        for nome, fabrica in AGENTES:
            r, _ = simular_medio(nome, fabrica, sujeira, inicio)
            resumo[nome].append(r['desempenho'])
            print('{:22s} {:>8s} {:8.1f} {:>7s} {:7.1f} {:8.1f} {:9.1f}'.format(
                rotulo(sujeira, inicio), nome[:8], r['desempenho'],
                fmt(r['t_limpo']), r['movimentos'], r['sugadas'], r['desperdicio']))
            linhas.append([rotulo(sujeira, inicio), nome, round(r['desempenho'], 2),
                           fmt(r['t_limpo']), round(r['movimentos'], 2), round(r['sugadas'], 2),
                           round(r['sugadas_uteis'], 2), round(r['ociosas'], 2),
                           round(r['desperdicio'], 2)])
    print('\nMédia sobre os 8 estados iniciais:')
    for nome, _ in AGENTES:
        print('  {:18s} {:10.2f}'.format(nome, mean(resumo[nome])))
        linhas.append(['MÉDIA (8 estados)', nome, round(mean(resumo[nome]), 2),
                       '', '', '', '', '', ''])
    escrever_csv('exp1_estados_iniciais.csv',
                 ['estado_inicial', 'agente', 'desempenho', 't_limpo', 'movimentos',
                  'sugadas', 'sugadas_uteis', 'ociosas', 'desperdicio'], linhas)
    return resumo


# ---------------------------------------------------------------------------
# Experimento 2: sensibilidade ao horizonte de tempo
# ---------------------------------------------------------------------------
def experimento_2():
    titulo('EXPERIMENTO 2 - Desempenho médio x horizonte de tempo')
    horizontes = [5, 10, 50, 100, 500, 1000]
    linhas = []
    print('{:18s}'.format('agente') + ''.join('{:>9s}'.format('t=' + str(h)) for h in horizontes))
    for nome, fabrica in AGENTES:
        medias = []
        for h in horizontes:
            vals = [simular_medio(nome, fabrica, s, i, h)[0]['desempenho']
                    for s, i in ESTADOS_INICIAIS]
            medias.append(mean(vals))
        print('{:18s}'.format(nome) + ''.join('{:9.1f}'.format(m) for m in medias))
        linhas.append([nome] + [round(m, 2) for m in medias])
    escrever_csv('exp2_horizonte.csv',
                 ['agente'] + ['t=' + str(h) for h in horizontes], linhas)


# ---------------------------------------------------------------------------
# Experimento 3: compare_agents() do próprio AIMA (ambientes sorteados)
# ---------------------------------------------------------------------------
def experimento_3(n=50, passos=PASSOS):
    titulo('EXPERIMENTO 3 - compare_agents() do AIMA: {} ambientes sorteados'.format(n))
    random.seed(SEED)
    resultado = compare_agents(TrivialVacuumEnvironment,
                               [f for _, f in AGENTES], n=n, steps=passos)
    linhas = []
    for (fabrica, escore), (nome, _) in zip(resultado, AGENTES):
        print('  {:18s} desempenho médio = {:8.2f}'.format(nome, escore))
        linhas.append([nome, fabrica.__name__, round(escore, 2), n, passos])
    escrever_csv('exp3_compare_agents.csv',
                 ['agente', 'funcao_aima', 'desempenho_medio', 'n_ambientes', 'passos'], linhas)


# ---------------------------------------------------------------------------
# Experimento 4: traço de execução (primeiros passos) para inspeção qualitativa
# ---------------------------------------------------------------------------
def experimento_4():
    titulo('EXPERIMENTO 4 - Traço das 8 primeiras ações (A=Dirty, B=Dirty, início em A)')
    sujeira = {loc_A: 'Dirty', loc_B: 'Dirty'}
    linhas = []
    for nome, fabrica in AGENTES:
        random.seed(SEED)
        r = simular(fabrica, sujeira, loc_A, passos=8)
        acoes = ['{}/{}'.format('A' if l == loc_A else 'B', a) for _, l, _, a in r['registro']]
        print('  {:18s} {}'.format(nome, ' -> '.join(acoes)))
        linhas.append([nome] + acoes)
    escrever_csv('exp4_tracos.csv', ['agente'] + ['passo_' + str(i) for i in range(1, 9)], linhas)


# ---------------------------------------------------------------------------
# Experimento 5: mudança de ambiente (PEAS diferente) - VacuumEnvironment 2D
# ---------------------------------------------------------------------------
def AgenteReflexo2D():
    """Agente reflexo escrito para a percepção do VacuumEnvironment: (status, bump).

    Não é código do AIMA: foi escrito para este trabalho, para mostrar que o
    programa do agente depende da especificação PEAS do ambiente.
    """
    def program(percept):
        status, bump = percept
        if status == 'Dirty':
            return 'Suck'
        if bump == 'Bump':
            return random.choice(['TurnRight', 'TurnLeft'])
        return random.choices(['Forward', 'TurnRight', 'TurnLeft'],
                              weights=[0.8, 0.1, 0.1])[0]
    return Agent(program)


def rodar_2d(fabrica, n_sujeira=10, passos=PASSOS, semente=0):
    random.seed(semente)
    amb = VacuumEnvironment(10, 10)
    colocadas = 0
    while colocadas < n_sujeira:
        loc = amb.random_location_inbounds()
        if not amb.some_things_at(loc, Dirt):
            amb.add_thing(Dirt(), loc)
            colocadas += 1
    agente = fabrica()
    agente.direction = Direction('right')   # exigido pelo XYEnvironment
    amb.add_thing(agente, amb.random_location_inbounds())
    amb.run(passos)
    restante = sum(1 for t in amb.things if isinstance(t, Dirt))
    return agente.performance, n_sujeira - restante


def experimento_5(passos=PASSOS, repeticoes=20):
    titulo('EXPERIMENTO 5 - Mesmo agente, outro PEAS: VacuumEnvironment 10x10, '
           '10 sujeiras, {} passos'.format(passos))
    casos = [('Reflexo simples (AIMA, feito p/ o mundo de 2 quadrados)', ReflexVacuumAgent),
             ('Reflexo 2D (escrito para este ambiente)', AgenteReflexo2D)]
    linhas = []
    for nome, fabrica in casos:
        res = [rodar_2d(fabrica, passos=passos, semente=SEED + k) for k in range(repeticoes)]
        desemp = mean(d for d, _ in res)
        limpas = mean(c for _, c in res)
        print('  {:56s} desempenho={:9.1f}  sujeiras limpas={:5.2f}/10'.format(
            nome, desemp, limpas))
        linhas.append([nome, round(desemp, 2), round(limpas, 2), repeticoes, passos])
    escrever_csv('exp5_ambiente_2d.csv',
                 ['agente', 'desempenho_medio', 'sujeiras_limpas', 'repeticoes', 'passos'], linhas)


if __name__ == '__main__':
    print('AIMA - agente aspirador de pó: bateria de testes')
    print('semente = {}, horizonte padrão = {} passos'.format(SEED, PASSOS))
    teste_0()
    experimento_1()
    experimento_2()
    experimento_3()
    experimento_4()
    experimento_5()
    print('\nCSVs gravados em: {}'.format(DIR_RESULTADOS))
