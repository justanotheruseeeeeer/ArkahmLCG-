import requests
import json
import math
from typing import Optional

# ====================== CONFIG ======================


deck_id=37336
library_path = r"C:\Users\34651\OneDrive\Escritorio\AIArkham\library_mystic_22.json"
# ===================================================
class DeckId:
    def __init__(self, deck_id):
        self.deck_id=deck_id
        # 1. Descargar el decklist
        url = f"https://arkhamdb.com/api/public/decklist/{self.deck_id}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            deck_data = response.json()

            print(f"Deck cargado: {deck_data.get('name')}")
            print(f"Investigador: {deck_data.get('investigator_name')}")
            print(f"Total cartas en slots: {len(deck_data.get('slots', {}))}")
        except Exception as e:
            print(f"Error al descargar deck: {e}")
            exit()

        # 2. Extraer códigos de cartas
        slots = deck_data.get('slots', {})
        new_deck = []
        for code, qty in slots.items():
            new_deck.extend([code] * qty)

        print(f"Total cartas en el mazo: {len(new_deck)}")

        # 3. Cargar la librería
        try:
            with open(library_path, "r", encoding="utf-8") as f:
                library = json.load(f)
            
            print(f"Libreria cargada correctamente: {len(library)} cartas")
        except Exception as e:
            print(f"Error al cargar library: {e}")
            exit()

        # 4. Crear buscador por código
        buscador = {carta.get('Code'): carta for carta in library if carta.get('Code')}

        # 5. Construir el deck real
        real_deck = []
        missing = []

        for code in new_deck:
            card = buscador.get(code)
            if card:
                real_deck.append(card)
            else:
                missing.append(code)

        print(f"\nCartas encontradas: {len(real_deck)} / {len(new_deck)}")

        if missing:
            print(f"Cartas NO encontradas: {missing}")

        with open("real_deck.json", "w", encoding="utf-8") as f:
            json.dump(real_deck, f, indent=4, ensure_ascii=False)

        print(f"Guardado real_deck.json con {len(real_deck)} cartas")
        #Hace falta cambiar el formato para que coincida con el del código

        """
        Conversor: diccionario "miner" (salida de la librería JSON) -> diccionario "deck"
        (el formato plano que usa tu código de simulación / algoritmo genético).

        SUPUESTOS (revisa y ajusta si algo no cuadra con tu código):
        ──────────────────────────────────────────────────────────────
        - El "Id" del miner es en realidad el NOMBRE de la carta (confuso, pero así
        está en tu JSON). Por eso lo mapeo a 'name', y genero un 'Id' nuevo
        (índice secuencial) para el deck, como en tu ejemplo (0,1,2,3...).
        - 'Type' en tu deck es un string simple ('stre' / 'Goal_Card' / 'hel'),
        pero el miner lo da como lista en 'Goal_Type'. Cojo el más específico:
        'Goal_Card' > 'hel' > 'stre' (fallback).
        - charges (Parameters.charges) -> 'time'. Deducido de tu tabla en el
        briefing V2: Shrivelling charges=4 <-> tu deck tiene Shrivelling time:4.
        Si 'time' significa otra cosa en tu código, cambia esa línea.
        - 'num_sea' (nº de búsquedas efectivas) = Parameters.charges, pero SOLO
        para cartas que tienen 'search' > 0 (ahí se usa 'num_sea' en vez de
        'time' para representar las cargas). Confirmado por el usuario:
        num_sea ≈ charges.
        - 'time' = Parameters.charges para el resto de cartas (las que no tienen
        'search'). O sea: charges se llama 'num_sea' si hay búsqueda, y 'time'
        si no la hay — es el mismo concepto (nº de activaciones) con dos
        nombres distintos según el contexto de la carta.
        - 'perm_A' (bonus permanente tipo Holy Rosary/Peter) = Parameters/top-level
        'Perm_Add' directamente. Confirmado por el usuario.
        - 'icons' (para cartas Type 'hel', o sea skills) = suma de todos los pips
        en All_Icons. Para esas cartas, quito los parámetros de efecto (dm, inv,
        etc.) porque en tu deck las skills 'hel' solo llevan 'icons' (y a veces
        'draw' como Guts).
        - Los valores en 0 se omiten del dict de salida (igual que en tu ejemplo,
        donde no todas las cartas tienen todas las keys).
        """




    def miner_to_deck_card(self, card: dict, deck_id=None) -> dict:
        p = card.get('Parameters', {}) or {}
        goal_types = card.get('Goal_Type', []) or []
        icons = card.get('All_Icons', {}) or {}

        # ── Tipo simple para tu deck ────────────────────────────────────────
        if 'Goal_Card' in goal_types:
            card_type = 'Goal_Card'
        elif 'hel' in goal_types:
            card_type = 'hel'
        elif goal_types:
            card_type = goal_types[0]
        else:
            card_type = 'stre'

        out = {
            'Id':   str(deck_id) if deck_id is not None else card.get('Code', ''),
            'name': card.get('Id', ''),      # el "Id" del miner = nombre real
            'Type': card_type,
            'cost': card.get('Cost', 0),
        }

        # ── Parámetros de efecto directos (mismo nombre en ambos lados) ─────
        direct_keys = ('dm', 'inv', 'evade', 'draw', 'search', 'res',
                    'fix', 'heal_dmg', 'heal_hor')
        for k in direct_keys:
            val = p.get(k, 0)
            out[k] = val

        # ── hp / sp: soak pasivo del asset (vienen del nivel superior, no de
        # Parameters — el miner los duplica como 'soak_dmg'/'soak_hor' dentro
        # de Parameters, pero 'hp'/'sp' arriba son los que usa tu deck) ──────
        hp = card.get('hp', 0)
        sp = card.get('sp', 0)
        if hp:
            out['heal_dmg']+= round(hp/2)
        if sp:
            out['heal_hor']+= round(sp/2)

        # ── AcP -> 'AP+' (tu deck usa la misma etiqueta que el top-level del miner) ──
        acp = card.get('AP+', p.get('AcP', 0))
        if acp:
            out['AP+'] = acp

        # ── charges -> 'num_sea' (si hay búsqueda) o 'time' (el resto) ──────
        charges = p.get('charges', 0)
        if charges:
            if out.get('search', 0):
                out['num_sea'] = charges
            else:
                out['time'] = charges

        # ── Bonus temporales (chunk2: add/red con duración) ────────────────
        if p.get('Add_Q', 0):
            out['Add_Q'] = p['Add_Q']
        if p.get('Red_Q', 0):
            out['Red_Q'] = p['Red_Q']
        if p.get('Add_Clock', 0):
            out['Add_Clock'] = p['Add_Clock']

        # ── Bonus permanente (Holy Rosary / Peter -> 'perm_A') ─────────────
        perm = card.get('Perm_Add', p.get('Perm_Add', 0))
        if perm:
            out['perm_A'] = perm

        # ── Cartas 'hel' (skills puras): usan 'icons' en vez de dm/res/etc. ─
        if card_type == 'hel':
            out['icons'] = sum(icons.get(k, 0) for k in ('wil', 'int', 'com', 'agi', 'wld'))
            # Guts sí conserva 'draw'; el resto de efectos de test no aplican aquí.
            for k in ('dm', 'inv', 'evade', 'search', 'res', 'fix', 'heal_dmg', 'heal_hor'):
                out.pop(k, None)

        return out


    def convert_library(self, cards: list) -> list:
        """Convierte una lista completa de cartas 'miner' (ya con las copias
        duplicadas que hayas cogido de la web) en tu formato de deck, asignando
        Id secuenciales 0,1,2... como en tu ejemplo."""
        return [self.miner_to_deck_card(c, i) for i, c in enumerate(cards)]



    def final(self):
        import aiarkham   # el archivo .py donde está def simular(deck)

        with open("real_deck.json", encoding="utf-8") as f:
            cartas_miner = json.load(f)
        mi_deck = self.convert_library(cartas_miner)
        resultados = aiarkham.new_function_for_passing(mi_deck)
        


        #FIN
if __name__ == "__main__":
    example=DeckId(deck_id)
    example.final()