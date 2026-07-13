"""
Decisor de mulligan: Pareto-filter + desempate lexicográfico con tolerancia.

Filosofía:
  - Heurística 1 (P_mejora): cuán fiable es la mejora — robusta a que el
    score sea más ordinal que cardinal.
  - Heurística 2 (EV): magnitud esperada — útil pero más sensible a que el
    score capture mal las sinergias reales de la carta.
  - No se combinan en un número ponderado. Se filtra por Pareto-dominancia
    primero (gratis, sin asumir nada), y solo si queda un tradeoff genuino
    se aplica una regla lexicográfica con tolerancia (epsilon-lexicográfico,
    en la tradición de "satisficing" de Simon / Take-The-Best de Gigerenzer).
"""

from itertools import combinations
from collections import defaultdict


def _draw_distribution(pool_scores, k):
    """Distribución completa {suma: prob} de extraer k cartas sin reemplazo."""
    if k == 0:
        return {0: 1.0}
    dist = defaultdict(int)
    total = 0
    for combo in combinations(pool_scores, k):
        dist[sum(combo)] += 1
        total += 1
    return {s: c / total for s, c in dist.items()}


def analyze_mulligan(hand_scores, deck_pool_scores):
    """
    Calcula EV y P_mejora para cada estrategia k=0..len(hand_scores).

    hand_scores: lista de scores de la mano actual (longitud = tamaño de mano)
    deck_pool_scores: scores de TODAS las cartas restantes en el mazo
                      (antes de barajar de vuelta las mulliganeadas)

    Devuelve: dict {k: {'EV': float, 'P_mejora': float, 'dist': {valor: prob}}}
    """
    hand_size = len(hand_scores)
    original_sum = sum(hand_scores)
    sorted_hand = sorted(hand_scores, reverse=True)
    results = {}

    for k in range(0, hand_size + 1):
        kept = sorted_hand[:hand_size - k]
        kept_sum = sum(kept)
        pool = list(deck_pool_scores)
        draw_dist = _draw_distribution(pool, k)
        full_dist = {kept_sum + s: p for s, p in draw_dist.items()}

        ev = sum(v * p for v, p in full_dist.items())
        p_better = sum(p for v, p in full_dist.items() if v > original_sum)
        results[k] = {'EV': ev, 'P_mejora': p_better, 'dist': full_dist}

    return results


def pareto_frontier(results):
    """
    Devuelve la lista de k's no-dominados (frontera de Pareto) sobre
    los ejes (EV, P_mejora). Una estrategia se descarta si existe otra
    igual o mejor en ambos ejes y estrictamente mejor en al menos uno.
    """
    keys = list(results.keys())
    dominated = set()
    for a in keys:
        ev_a, p_a = results[a]['EV'], results[a]['P_mejora']
        for b in keys:
            if a == b:
                continue
            ev_b, p_b = results[b]['EV'], results[b]['P_mejora']
            if ev_b >= ev_a and p_b >= p_a and (ev_b > ev_a or p_b > p_a):
                dominated.add(a)
                break
    return sorted(k for k in keys if k not in dominated)


def choose_mulligan(hand_scores, deck_pool_scores,
                     priority='P_mejora', tolerance=0.075):
    """
    Decide la estrategia óptima de mulligan.

    priority: 'P_mejora' o 'EV' — qué heurística actúa como criterio
              primario (lexicográfico). La recomendación por defecto es
              'P_mejora' cuando el score es más ordinal que cardinal
              (refleja orden de preferencia, no impacto real medido).
    tolerance: margen relativo (epsilon-lexicográfico). Si dos estrategias
               están dentro de esta tolerancia en el criterio primario,
               se rompe el empate con el criterio secundario en vez de
               exigir una victoria estricta. Evita decisiones frágiles
               por diferencias de ruido en el criterio primario.

    Devuelve: (k_elegido, dict con resultados completos, frontera_pareto)
    """
    results = analyze_mulligan(hand_scores, deck_pool_scores)
    frontier = pareto_frontier(results)
    
    
    if len(frontier) == 1:
        return frontier[0], results, frontier

    secondary = 'EV' if priority == 'P_mejora' else 'P_mejora'

    # Mejor valor del criterio primario dentro de la frontera
    best_primary = max(results[k][priority] for k in frontier)

    # Candidatos dentro de la tolerancia del mejor valor primario
    # (tolerancia relativa si best_primary != 0, absoluta si es 0)
    if best_primary != 0:
        candidates = [k for k in frontier
                      if results[k][priority] >= best_primary * (1 - tolerance)]
    else:
        candidates = [k for k in frontier
                      if results[k][priority] >= best_primary - tolerance]

    # Desempate por el criterio secundario entre los candidatos
    chosen = max(candidates, key=lambda k: results[k][secondary])
    return chosen, results, frontier


if __name__ == "__main__":
    print("=" * 70)
    print("CASO 1 — dominancia clara")
    print("=" * 70)
    import random
    random.seed(42)
    hand1 = [5, 4, 3, 1, 0.5]
    pool1 = [round(random.uniform(0, 5), 1) for _ in range(28)]
    k, res, frontier = choose_mulligan(hand1, pool1)
    print(f"Mano: {hand1}")
    for kk in sorted(res):
        marker = " FRONTERA" if kk in frontier else ""
        print(f" k={kk}  EV={res[kk]['EV']:.3f}  P_mejora={res[kk]['P_mejora']*100:.1f}%{marker}")
    print(f"\n Estrategia elegida: mulliganear {k} carta(s)\n")

    print("=" * 70)
    print("CASO 2 — tradeoff genuino, mazo bimodal")
    print("=" * 70)
    hand2 = [3, 3, 2.5, 2, 1]
    pool2 = [0.5]*22 + [8]*3 + [4]*3
    for prio in ('P_mejora', 'EV'):
        k, res, frontier = choose_mulligan(hand2, pool2, priority=prio)
        print(f"\nPrioridad = '{prio}':")
        for kk in frontier:
            print(f"  k={kk}  EV={res[kk]['EV']:.3f}  P_mejora={res[kk]['P_mejora']*100:.1f}%")
        print(f"  Estrategia elegida: mulliganear {k} carta(s)")
        
        
#In reality we have the TOTAL pool - the full list - and then the sublist -our hand-
def substr_list(main_list,sublist):
    result = main_list.copy()

    for item in sublist:
        if item in result:
            result.remove(item)
    return result #returns the actual list of our potential new hand