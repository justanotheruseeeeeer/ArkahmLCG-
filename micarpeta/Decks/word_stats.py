"""
word_stats.py
=============
Frecuencia / importancia de palabras y expresiones (n-gramas) en el texto
"verbatim" de tus cartas. Es la base del "Layer 1" del motor de sinergia
que hablamos: un lexicón de expresiones frecuentes/relevantes que luego
sirve para etiquetar mecánicas (Layer 1) y medir sinergia entre cartas
(Layer 2).

QUÉ HACE
────────
1. Tokeniza el texto de cada carta:
   - Respeta los iconos entre corchetes como UN solo token: [willpower],
     [reaction], [auto_fail]...
   - Normaliza cualquier número a un token especial <n>, para que
     "move 1 space" y "move 3 spaces" cuenten como la MISMA expresión
     (si no, tendrías una entrada distinta por cada número que aparece).
   - Todo en minúsculas, sin puntuación.

2. UNIGRAMAS (palabras sueltas): cuenta frecuencia total y en cuántas
   cartas DISTINTAS aparece cada una, filtrando stopwords (the, a, of,
   you, your...). Si no las filtras, dominan el ranking y no dicen nada
   sobre mecánicas del juego.

3. N-GRAMAS (expresiones de 2+ palabras, ej. "take <n> horror",
   "you may move", "succeed by <n> or more"): aquí NO se quitan
   stopwords individuales -> "you may move" pierde sentido si le quitas
   "you". Solo se descartan los n-gramas que son PURAMENTE stopwords
   (ej. "of the", "in a") porque esos sí son ruido gramatical puro.

4. Para cada término se reportan DOS métricas que miden cosas distintas:
   - freq: nº total de apariciones en todo el corpus (una carta con
     texto largo y repetitivo puede inflar esto).
   - df (document frequency): en cuántas cartas DISTINTAS aparece al
     menos una vez. Normalmente esta es la métrica correcta para medir
     "importancia" de una mecánica -> una expresión que aparece 1 vez
     en 40 cartas distintas es una mecánica genuinamente extendida;
     una que aparece 40 veces en LA MISMA carta no lo es.

USO
───
    cards = load_library("library_mystic.json")
    uni   = unigram_stats(cards)
    bi    = ngram_stats(cards, n=2)
    tri   = ngram_stats(cards, n=3)

    print_top(uni, k=25)          # top palabras sueltas por df
    print_top(bi,  k=25, by='df') # top bigramas por df
    print_top(tri, k=25, by='freq')

    search_phrase(cards, "take horror")   # ¿en qué cartas aparece esto?
"""

import json
import re
from collections import defaultdict


# ── Stopwords ────────────────────────────────────────────────────────────
# Solo palabras funcionales/gramaticales en inglés.
STOPWORDS = {
    'a', 'an', 'the', 'of', 'to', 'in', 'on', 'at', 'for', 'and', 'or',
    'but', 'if', 'then', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'this', 'that', 'these', 'those', 'it', 'its', 'as', 'by',
    'with', 'from', 'you', 'your', 'yours', 'each', 'any', 'all', 'may',
    'can', 'will', 'shall', 'do', 'does', 'did', 'not', 'no', 'so',
    'than', 'when', 'while', 'during', 'until', 'after', 'before',
    'into', 'onto', 'per', 'out', 'up', 'own', 'other', 'same', 'such',
    'only', 'also', 'once', 'more', 'most', 'some', 'have', 'has',
    'had', 'get', 'gets', 'getting', 'who', 'whom', 'which', 'there',
    'here', 'their',
}


# ── Tokenización ──────────────────────────────────────────────────────────
_TOKEN_RE = re.compile(r'\[[a-z_]+\]|<n>|[a-z]+')


def tokenize(text: str) -> list:
    t = text.lower()
    t = re.sub(r' x ', '<n>', t)
    t = re.sub(r' \+x ', '<n>', t)
    t = re.sub(r'\d+', '<n>', t)   # "3 cards" / "5 cards" -> misma forma
    t = t.replace('\n', ' ')
    return _TOKEN_RE.findall(t)


# ── Carga de la library ───────────────────────────────────────────────────
def load_library(path) -> list:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return [c for c in data if c.get('verbatim')]


def _card_name(c: dict) -> str:
    return c.get('Id') or c.get('name') or '?'


# ── Unigramas ──────────────────────────────────────────────────────────────
def unigram_stats(cards: list) -> dict:
    """{palabra: {'freq': N, 'df': N, 'cards': set(nombres)}}"""
    stats = defaultdict(lambda: {'freq': 0, 'cards': set()})
    for c in cards:
        name = _card_name(c)
        seen = set()
        for tok in tokenize(c['verbatim']):
            if tok in STOPWORDS or tok == '<n>' or len(tok) < 2:
                continue
            stats[tok]['freq'] += 1
            if tok not in seen:
                stats[tok]['cards'].add(name)
                seen.add(tok)
    for v in stats.values():
        v['df'] = len(v['cards'])
    return dict(stats)


# ── N-gramas (frases de n palabras) ────────────────────────────────────────
def _ngrams(tokens: list, n: int):
    for i in range(len(tokens) - n + 1):
        yield tuple(tokens[i:i + n])


def ngram_stats(cards: list, n: int = 2) -> dict:
    """{n-grama (tupla): {'freq': N, 'df': N, 'cards': set(nombres)}}"""
    stats = defaultdict(lambda: {'freq': 0, 'cards': set()})
    for c in cards:
        name = _card_name(c)
        seen = set()
        for gram in _ngrams(tokenize(c['verbatim']), n):
            if all(g in STOPWORDS or g == '<n>' for g in gram):
                continue  # ej. "of the" -> ruido gramatical puro
            stats[gram]['freq'] += 1
            if gram not in seen:
                stats[gram]['cards'].add(name)
                seen.add(gram)
    for v in stats.values():
        v['df'] = len(v['cards'])
    return dict(stats)


# ── Presentación ────────────────────────────────────────────────────────────
def print_top(stats: dict, k: int = 60, by: str = 'df'):
    """
    by='df'   -> ordena por en cuántas cartas DISTINTAS aparece
                 (recomendado para medir importancia/relevancia real).
    by='freq' -> ordena por nº total de apariciones (sesgable por una
                 sola carta con texto largo y repetitivo).
    """
    ree=[]
    items = sorted(stats.items(), key=lambda kv: kv[1][by], reverse=True)[:k]
    for term, v in items:
        label = ' '.join(term) if isinstance(term, tuple) else term
        ejemplo = list(v['cards'])[:3]
        ree.append({'freq':v['freq'], 'df':v['df'],'label':label,'e.g.':ejemplo})
    return ree


def search_phrase(cards: list, phrase: str):
    """Busca una expresión literal y lista las cartas donde aparece."""
    target = tuple(tokenize(phrase))
    n = len(target)
    hits = [
        _card_name(c) for c in cards
        if any(g == target for g in _ngrams(tokenize(c['verbatim']), n))
    ]
    print(f"'{phrase}' aparece en {len(hits)} carta(s): {hits}")
    return hits


# ── Skip-grams: co-ocurrencia de palabras SIN exigir contigüidad ──────────
# Esto es lo que hace falta para detectar patrones tipo
# "if you succeed by ... this attack deals ..." -> "succeed" y "deals"
# nunca están pegadas (hay números/comas en medio), así que un n-grama
# contiguo (ngram_stats) JAMÁS los va a juntar. Un skip-gram cuenta pares
# de palabras que aparecen dentro de una ventana de N tokens, sin importar
# qué haya en medio ni cuánto varíe la distancia de una carta a otra.
def skipgram_stats(cards: list, window: int = 8) -> dict:
    """
    {(palabra1, palabra2): {'freq': N, 'df': N, 'cards': set(nombres)}}
    Solo empareja palabras de CONTENIDO (se ignoran stopwords y <n> como
    ancla, igual que en unigram_stats) para no llenar el ranking de
    pares tipo ('you', 'the'). window = cuántos tokens hacia delante se
    permite mirar para formar el par.
    """
    stats = defaultdict(lambda: {'freq': 0, 'cards': set()})
    for c in cards:
        name = _card_name(c)
        toks = tokenize(c['verbatim'])
        seen = set()
        n = len(toks)
        for i in range(n):
            if toks[i] in STOPWORDS or toks[i] == '<n>':
                continue
            for j in range(i + 1, min(i + 1 + window, n)):
                if toks[j] in STOPWORDS or toks[j] == '<n>':
                    continue
                pair = (toks[i], toks[j])
                stats[pair]['freq'] += 1
                if pair not in seen:
                    stats[pair]['cards'].add(name)
                    seen.add(pair)
    for v in stats.values():
        v['df'] = len(v['cards'])
    return dict(stats)



# ── DEMO (texto de ejemplo de tu propio proyecto, para probar el script) ───
if __name__ == "__main__":
    x= load_library('library_mystic_22.json')
    print("unigram:")
    print_top(unigram_stats(x))
    print("bigram:")
    print_top(ngram_stats(x))
    print("trigram:")
    print_top(ngram_stats(x,3),30)
    print("cuatrigram:")
    print_top(ngram_stats(x,4),30)
    with open("Unigram.json", "w", encoding="utf-8") as f:
        json.dump(print_top(unigram_stats(x)), f, indent=4, ensure_ascii=False)
    with open("Bigram.json", "w", encoding="utf-8") as f:
        json.dump(print_top(ngram_stats(x)), f, indent=4, ensure_ascii=False)
    with open("Trigram.json", "w", encoding="utf-8") as f:
        json.dump(print_top(ngram_stats(x,3),30), f, indent=4, ensure_ascii=False)
    with open("Cuartigram.json", "w", encoding="utf-8") as f:
        json.dump(print_top(ngram_stats(x,4),30), f, indent=4, ensure_ascii=False)