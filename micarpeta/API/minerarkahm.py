"""
ArkhamDB Card Miner — v3 (final)
=================================
Implements the parameter rules from the author PDF + Gemini session + corrections.

KEY DESIGN DECISIONS
────────────────────
TYPE HIERARCHY
  skill         Raw skill card.
  pseudo_skill  Fast event triggering ON a test result (Lucky!, Oops!, Dumb Luck,
                "Look what I found!", Survival Instinct-class).
                Treated as a costly skill: AcP=0, conditions assumed fulfilled.
  event         Normal event.
  asset         Normal asset.
  pseudo_asset  Event that attaches or carries a charges pool (Barricade xp3,
                Shortcut xp2) — modelled like an asset.

ACTION ECONOMY (AcP)
  +1  Playing the card is Fast (line-1 "Fast.") for ANY card type (asset or event).
      Exception: pseudo_skills always return AcP=0.
  +1  Each \n[fast] ability on an asset.
      Exhaust assets: ÷3 (fires ~once per round = once per 3 action-slots).
  +1  Connecting location / movement BONUS — only when the move is ON TOP of
      another action.  When the whole point of the card IS the move (Pathfinder,
      Cat Burglar), it is not counted separately (already in the [fast]/[action]
      economy). When the card does something else AND also grants access to a
      connecting location (Seeking Answers, Bait and Switch, Dynamite Blast,
      Survival Instinct-move-after-evade), count +1.
      Special rule for [action]+exhaust+move: the move saves 1 action but costs
      1 action → net 0, then ÷3 for exhaust = +0.333.
  +N  Explicit "may take N additional actions".  Exhaust → ÷3.

CHARGES
  Explicit uses(N …):  use that number.
  Exhaust asset, no uses():  7×3 = 21  (triple pool, effect ÷3).
  Non-exhaust asset, no uses():  7.
  Event / skill / pseudo_skill:  1.

EXHAUST DIVISION
  Exhaust assets: all per-use effect params ÷3 (fires once per ~3 actions).

MULTI-CHOICE
  Multiple \n ability blocks → weighted average by per-block charge cost.
  Discard-cost blocks are ignored (zero value — the card is consumed).
  Play-condition lines ("Fast. Play after …") treated as non-effect headers.

BLESSED/CURSED FILTERING
  Only filter if the TEXT explicitly uses the chaos-bag manipulation mechanics
  ("becomes blessed", "add a [bless] token", etc.).
  The mere presence of "Blessed." as a trait keyword does NOT filter the card.
"""

import re
import requests
import json
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
FACTION_ICON = {
    'guardian': 'skill_combat',
    'mystic':   'skill_willpower',
    'seeker':   'skill_intellect',
    'rogue':    'skill_agility',
    'survivor': 'skill_combat',
}

current_faction = 'mystic'
print(FACTION_ICON.get(current_faction))
DEFAULT_CHARGES = 7#The number of 'charges' of a 'permanent' asset

# Mechanics that make a card too complex to auto-parse.
# NOTE: 'blessed'/'cursed' removed — we now check for the MECHANIC in text,
# not just the trait name. A card with trait "Blessed." is fine.
FORBIDDEN_MECHANICS = [
    'bonded', 'myriad', 'customizable', 'resource: you get','deck only', 'permanent'
]
# Chaos-bag text patterns that indicate the blessed/cursed bag-manipulation mechanic
BLESSED_CURSED_TEXT = [
    'becomes blessed', 'add a [bless]', 'add 1 [bless]',
    'becomes cursed',  'add a [curse]', 'add 1 [curse]',
    '[bless] token', '[curse] token',
    'bless token', 'curse token',
]
# Exile is kept — most exile cards are fine (A Test of Will is handled: charges=1).
# Only filter if exile is paired with campaign-level permanence.

FORBIDDEN_PHRASES = [
    'cannot move away', 'cannot be moved',
    'cannot leave this location', 'cannot leave play',
]#just for barricade

# ─────────────────────────────────────────────────────────────────────────────
def _safe_int(val, default=0) -> int:
    return int(val) if val is not None else default

def is_too_complex(text: str, traits: str) -> bool:
    tl = text.lower()
    tr = traits.lower()
    for m in FORBIDDEN_MECHANICS:
        if m in tl or m in tr:
            return True
    for p in FORBIDDEN_PHRASES:
        if p in tl:
            return True
    # Blessed/cursed: only if the bag-manipulation MECHANIC appears in text
    for bc in BLESSED_CURSED_TEXT:
        if bc in tl:
            return True
    return False

# ─────────────────────────────────────────────────────────────────────────────
# TYPE CLASSIFIER
# ─────────────────────────────────────────────────────────────────────────────
_PSEUDO_SKILL_TRIGGERS = [
    'after you fail a skill test',   'play after you fail',
    'play when you would fail',      'when you would fail',
    'if this skill test is successful',
    'if this test is successful',
]

def classify_type(raw_type: str, text: str) -> str:
    t = text.lower()
    if raw_type == 'skill':
        return 'skill'
    if raw_type == 'asset':
        return 'asset'
    # Events:
    for trigger in _PSEUDO_SKILL_TRIGGERS:
        if trigger in t:
            return 'pseudo_skill'
    has_attach  = bool(re.search(r'\battach\b|\battached to\b', t))
    has_charges = bool(re.search(
        r'uses \((\d+)', t))
    if has_attach or has_charges:
        return 'pseudo_asset'
    return 'event'

# ─────────────────────────────────────────────────────────────────────────────
# PARAGRAPH UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def split_paragraphs(text: str) -> list:
    t = text.replace('\r\n', '\n')
    return [p.strip() for p in t.split('\n') if p.strip()]
def _is_play_condition(para: str) -> bool:
    """
    Returns True for play-condition / timing lines that are NOT effect blocks.
    Examples: "Fast. Play after you defeat an enemy."
              "Fast. Play only during your turn."
              "Fast. Play when you draw a treachery."
    These appear as the first newline paragraph of many events and pseudo_skills.
    They must NOT be treated as effect paragraphs (they have zero payload).
    """
    t = para.lower().strip()
    return bool(re.match(r'^fast[\.,]\s*play\b', t))

def _is_header(para: str) -> bool:
    t = para.lower().strip()
    t_clean = re.sub(r'<[^>]+>', '', t).strip()  # quitar <b>, </b>, etc.
    return (
        t_clean.startswith('forced')
        or t_clean.startswith('uses (')
        or t_clean.startswith('exceptional.')
        or bool(re.match(r'^<b>(?:evade|fight|investigate)\.</b>', t))
        or bool(re.search(r'enters? play', t))
        or bool(re.match(r'^you get \+\d+|^while you|^limit \d+', t_clean))
        or bool(re.search(r'play only', t_clean))
        or _is_play_condition(t_clean)
    )

def _is_discard_cost(para: str) -> bool:
    """True when discarding the card itself is the COST of the ability."""
    t = para.lower()
    if ':' in t:
        cost_part = t.split(':')[0]
        if 'discard' in cost_part:
            return True
    return False

# ─────────────────────────────────────────────────────────────────────────────
# SINGLE-PARAGRAPH EFFECT EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────
def _extract_effect(para: str, card_type: str = 'event') -> dict:
    """
    card_type is passed in so skill/pseudo_skill adjustments can be made:
      - dm, inv: return only the BONUS amount, not base+bonus
      - evade: set to 0 (the evade IS the test the skill is committed to)
      - fix: always 0 for skill/pseudo_skill (result depends on the test)
    """
    t = para.lower()
    is_skill_type = card_type in ('skill', 'pseudo_skill')
    e = {
        'dm': 0, 'inv': 0, 'evade': 0, 'draw': 0, 'search': 0,
        'res': 0, 'heal_dmg': 0, 'heal_hor': 0, 'fix': 0,
        'is_react':   bool(re.search(r'\[reaction\]|\breaction\b', t)),
        'charge_cost': 1,
        'charges':0,'exhaust_use':False,
        'grants_move': False,
        'is_sole_move': False,
    }
    # Uses pool
    uses_m = re.search(
        r'uses \((\d+)', t)
    if uses_m:
        e['charges'] = int(uses_m.group(1))

    # Exhaust-as-cost
    if re.search(r'exhaust .{1,50}:', t):
        e['exhaust_use'] = True
    # Per-activation charge cost
    c = re.search(r'spend (\d+) (?:charge|ammo|secret|suppli|rumour|renown|doom)(?:es|s)?', t)
    if c:
        e['charge_cost'] = int(c.group(1))

    # Move detection — does this paragraph grant access to a connecting location?
    has_connecting  = bool(re.search(r'connecting location', t))
    has_any=bool(re.search(r'at any location', t))
    has_move_verb   = bool(re.search(r'\bmove to a\b|you may move\b', t))
    multi_move_m    = re.search(r'move up to (\d+)', t)
    extra_moves     = int(multi_move_m.group(1)) if multi_move_m else 0

    if has_connecting or has_move_verb or extra_moves or has_any:
        e['grants_move'] = True
        # Is the move the SOLE payload? Check for other meaningful keywords.
        other_payload = bool(re.search(
            r'\b(?:fight|attack|investigate|evade|discover|deal|draw|gain|'
            r'heal|search|disengage|cancel|ignore)\b', t))
        e['is_sole_move'] = not other_payload

    # ── DAMAGE ────────────────────────────────────────────────────────────
    # Defaults for variable-X bonus (no literal number in card text)
    DEFAULT_DM_BONUS = 2   # "+X damage where X is..." defaults to +2

    _dm_is_modifier = False   # tracks whether dm came from +N path vs fixed path

    if e['is_react']:
        # Reaction: extract from the effect portion (after the first colon)
        eff = t.split(':', 1)[-1] if ':' in t else t
        rdm = re.search(r'deal (\d+) damage', eff)
        if rdm:
            e['dm']  = int(rdm.group(1))
            e['fix'] = 1
    else:
        # Fixed damage: "deals N damage" where N is a bare digit (no + prefix).
        # "deals +1 damage" is a modifier, not a fixed value, so excluded here.
        fdm = re.search(
        r'deals?\s+(?!\+)(\d+)\s+damage'
        r'(?!\s+for\s+each)'
        r'(?!\s+to\s+(?:that\s+|each\s+|an?\s+|the\s+|another\s+)?investigator)'
        r'(?!\s+to\s+you\b)',
        t)
        if fdm:
            e['dm']  = int(fdm.group(1))
            e['fix'] = 1
        elif re.search(r'\b(?:fight)\b', t) or re.search(r'\b(?<!that\s)(?<!cancel\s)attack\b', t) or re.search(r'\b(?<!enemy\s)attack\b', t):
            e['dm'] = 1    # base fight action
            _dm_is_modifier = True
            # Literal "+N damage" modifier: "deals +1 damage" or "+2 damage"
            mod_lit = re.search(r'\+(\d+)\s+damage', t)
            if mod_lit:
                e['dm'] = 1 + int(mod_lit.group(1))
            # Variable "+X damage" (letter X, not a digit) → apply default bonus
            elif re.search(r'\+x\s+damage|deals?\s+\+x\b', t):
                e['dm'] = 1 + DEFAULT_DM_BONUS
            elif re.search(r'deals?.*damage (?!\s+for\s+each)',t):
                e['dm'] = 1+ DEFAULT_DM_BONUS
        elif re.search(r'\+x\s+damage|deals?\s+\+x\b', t):
            # "+X damage" without a fight keyword still implies an attack context
            e['dm'] = 1 + DEFAULT_DM_BONUS
            _dm_is_modifier = True
        
            

    # Skill/pseudo_skill correction for damage:
    # The base fight action is the test the card is committed to — the card
    # only contributes its BONUS amount. Subtract the base 1 if it was added.
    # fix=0 only when dm came from the modifier path (it piggybacks on the test).
    # Fixed "deals N damage" on a pseudo_skill stays fix=1 (unconditional once triggered).
    if is_skill_type and e['dm'] > 0 and _dm_is_modifier:
        e['dm'] = e['dm'] - 1
        e['fix'] = 0

    # ── CLUES / INVESTIGATE ───────────────────────────────────────────────
    DEFAULT_INV_BONUS = 3   # "discover X clues where X is..." defaults to 3

    _inv_is_additional = False  # tracks whether inv came from "additional" path

    # Priority 1: "N clues instead" construct → average of both values
    # "discover 1 clue at your location (2 clues instead if...)"
    # Author rule: take average of both, not the higher (it's a replacement,
    # not an additive bonus; board state determines which applies).
    instead_m = re.search(
        r'discover (\d+) clues?\b[^(]*\((\d+) clues? instead', t)
    if instead_m:
        base    = int(instead_m.group(1))
        instead = int(instead_m.group(2))
        e['inv'] = (base + instead) / 2   # e.g. (1+2)/2 = 1.5
        e['fix'] = 1
    
    # Priority 2: fixed "discovers N clues" (bare digit)
    elif re.search(r'discovers?\s+(\d+)\s+clues?', t):
        fi = re.search(r'discovers?\s+(\d+)\s+clues?', t)
        e['inv']  = int(fi.group(1))
        e['fix']  = 1

    # Priority 3: variable X clues
    elif re.search(r'discover\s+x\s+clues?', t):
        e['inv']  = DEFAULT_INV_BONUS
        e['fix']  = 1
        
    elif re.search(r'discover\s+x\s+additional|discover\s+\+x', t):
        e['inv']  = DEFAULT_INV_BONUS
        e['fix']  = 1
        _inv_is_additional=True
    # Priority 4: "discover N additional clue(s)"
    # For non-skill cards: base investigate (1) + N bonus = 1+N, fix depends on context.
    # For skill/pseudo_skill: the investigate IS the test being committed to,
    # so the card contributes only its N bonus. fix=0 (depends on test).
    else:
        addl = re.search(r'discover\s+(\d+)\s+additional\s+clues?', t)
        if addl:
            n = int(addl.group(1))
            if is_skill_type:
                e['inv']  = n        # skill contributes only the bonus
                e['fix']  = 0        # depends on the test
            else:
                e['inv']  = 1 + n    # event/asset: base investigate + bonus
                e['fix']  = 0 if re.search(r'\binvestigate\b', t) else 1
            _inv_is_additional = True

        # Priority 5: base investigate action (test required)
        elif re.search(r'\binvestigate\b', t):
            e['inv'] = 1    # fix stays 0 — test required
            mod = re.search(r'\+(\d+)\s+clues?', t)
            if mod:
                e['inv'] = 1 + int(mod.group(1))
    instead_m = re.search(
        r'discover \+(\d+) clues?\b[^(]*\(\+(\d+) clues? instead', t)
    if instead_m:
        base    = int(instead_m.group(1))
        instead = int(instead_m.group(2))
        e['inv'] = (base + instead) / 2   # e.g. (1+2)/2 = 1.5
        e['fix'] = 0
    instead_m = re.search(
        r'discover (\d+) additional clues?\b[^(]*\((\d+) additional clues? instead', t)
    if instead_m:
        base    = int(instead_m.group(1))
        instead = int(instead_m.group(2))
        e['inv'] = (base + instead) / 2   # e.g. (1+2)/2 = 1.5
        e['fix'] = 0
    # Skill/pseudo_skill correction for investigate:
    # fix=0 only when inv came from the "additional clue" modifier path
    # (it piggybacks on a test). Fixed discovers (priority 1/2/3) keep fix=1 —
    # once the trigger fires, the discover is unconditional.
    if is_skill_type and e['inv'] > 0 and _inv_is_additional:#LWIF is quite annoying
        e['fix'] = 0

    # ── EVADE ─────────────────────────────────────────────────────────────
    # Automatic evade: no skill test required → fix=1
    if re.search(r'automatically evades?', t):
        e['evade'] = 1
        e['fix']   = 1
    if re.search(r'evades? all enemies', t):
        e['evade'] = 2
        e['fix']   = 1
    # Regular evade action: test required → fix stays 0
    elif re.search(r'\bevade\b', t):
        e['evade'] = 1
        e['fix']   = 0

    # Skill/pseudo_skill correction for evade:
    # The evade IS the test the skill is committed to — not an extra evade granted
    # by the card. So evade=0 for skill types when it came from the bare keyword.
    # Exception: "automatically evade" is a genuine fixed effect even on a skill.
    # fix=0 only when the bare evade path fired (it rides the test).
    # Do NOT clear fix here if evade=0 (nothing happened) — other payloads
    # like fixed discovers set fix=1 correctly and must not be overridden.
    if is_skill_type and e['evade'] > 0:
        if not re.search(r'automatically evade|evade each enemy', t):
            e['evade'] = 0
            e['fix']   = 0

    # Draw
    dm = re.search(r'draws?\s+(\d+)\s+cards?', t)
    if dm:
        e['draw'] = int(dm.group(1))

    # Search — matches "search the top 3 cards", "look at the top 3 cards",
    # and also singular "look at the top card" (no number → implies 1)
    
        # ── SEARCH ─────────────────────────────────────────────────────────────
    # El cambio clave: (?:top|bottom) limpio, y manejamos los espacios con \s*
    sm = re.search(
        r'(?:search(?:es)?|look at)\s+(?:the\s+)?(?:top\s+|bottom\s+)?(\d+)\s+cards?', 
        t, re.IGNORECASE
    )
    if sm:
        e['search'] = int(sm.group(1))
    smx = re.search(
        r'(?:search|look at) the (?:top|bottom) x', 
        t, re.IGNORECASE
        )
    if smx:
        e['search'] = 3#default
    # Caso "Search the top X cards of your deck..."
    elif re.search(r'search the top (\d+) cards', t, re.IGNORECASE):
        e['search'] = int(re.search(r'search the top (\d+) cards', t, re.IGNORECASE).group(1))
    elif re.search(r'(?:search(?:es)?|look at)\s+(?:the\s+)?top|bottom\s+card\b', t, re.IGNORECASE):
        e['search'] = 1
    elif re.search(r'\bsearch (?:your|the) deck\b', t, re.IGNORECASE):
        e['search'] = 20
    # Resources — standard "gains N resources" OR "resource pool" transfer
    rm = re.search(r'gains?\s+(\d+)\s+resources?|gain\s+(\d+)\s+resources?', t)
    if rm:
        e['res'] = int(rm.group(1) or rm.group(2))
    elif re.search(r'to your resource pool|as a resource', t):
        nm = re.search(r'(?:move|place)\s+(\d+)', t)
        if nm:
            e['res'] = int(nm.group(1))
    elif re.search(r'may spend.*?to pay', t):
        
        e['res']=1
    # Heal
    hdm = re.search(r'heals?\s+(\d+)\s+damage|restores?\s+(\d+)\s+health', t)
    if hdm:
        e['heal_dmg'] = int(hdm.group(1) or hdm.group(2))
    hhr = re.search(r'heals?\s+(\d+)\s+horror|restores?\s+(\d+)\s+sanity', t)
    if hhr:
        e['heal_hor'] = int(hhr.group(1) or hhr.group(2))
    after_you_i    = re.search(r'after you.*investigate|after you.*discover.*clue', t)
    after_you_d    = re.search(r'after you.*damage', t)
    after_you_e    = re.search(r'after you.*evade', t)
    if after_you_i:
        e['inv']-=1
    if after_you_e:
        e['evade']-=1
    if after_you_d:
        e['dm']-=1
    e['dm']=max(e['dm'],0)
    e['inv']=max(e['inv'],0)
    e['evade']=max(e['evade'],0)
    return e

# ─────────────────────────────────────────────────────────────────────────────
# STAT EXTRACTOR.
# ─────────────────────────────────────────────────────────────────────────────
def _extract_stats(text: str) -> dict:
    t = text.lower()
    stats = {'wil': 0, 'int': 0, 'com': 0, 'agi': 0}
    for key, pat in [
        ('wil', r'\+(\d+)\s*\[?willpower\]?'),
        ('int', r'\+(\d+)\s*\[?intellect\]?'),
        ('com', r'\+(\d+)\s*\[?combat\]?'),
        ('agi', r'\+(\d+)\s*\[?agility\]?')
        
    ]:
        m = re.search(pat, t)
        if m:
            stats[key] = int(m.group(1))
    return stats
#




"""
CHUNK 2: add / add_stat / red / duration

Parameters returned:
  add      — literal +N numeric bonus to skill value or stat
             e.g. Encyclopedia "+2 to a skill" → add=2
  add_stat — which stat is being added to another stat (no literal number)
             e.g. MoM xp2 "add your [intellect] to [combat] and [agility]" → add_stat='int'
             The simulator must look up the investigator's actual stat value.
  red      — numeric reduction to shroud or difficulty
  duration — scope in actions/tests

Distinction between the two Mind over Matter versions:
  xp0: "use your [intellect] in place of your [combat] and [agility]"
       → stat SUBSTITUTION (you swap one stat for another).
       → add=0, add_stat=None, duration=0.
       → Chunk2 correctly returns nothing; stat substitution handled by chunk3.

  xp2: "add your [intellect] to your [combat] and [agility]"
       → stat ADDITION (intellect stacks on top of combat and agility).
       → add=0, add_stat='int', duration=3.
       → Captured here because it has a quantifiable (if variable) effect.

Duration rules:
  "for this test/attack/investigation/evasion"  → 1
  "for your next skill test"                     → 1
  "for X tests / turns"                          → X
  "for the rest of your turn"                    → 3
  "until the end of the phase"                   → 3
  "until the end of the round"                   → 3
  unstated / fallback                            → 2
"""

import re
from typing import Optional
STAT_CLEAN = {
    '[willpower]': 'wil', 'willpower': 'wil',
    '[intellect]': 'int', 'intellect': 'int',
    '[combat]':    'com', 'combat':    'com',
    '[agility]':   'agi', 'agility':   'agi',
}

def _clean_stat(raw: str) -> Optional[str]:
    return STAT_CLEAN.get(raw.lower().strip())


def _extract_duration(t: str) -> int:
    if re.search(
        r'for this (?:skill )?test'
        r'|for this attack'
        r'|for this investigation'
        r'|for this evasion'
        r'|for that (?:skill )?test'
        r'|for that attack', t):
        return 1.1
    if re.search(r'for (?:the )?(?:your )?next (?:skill )?test', t):
        return 1
    m = re.search(
        r'for (?:the )?next (\d+) (?:skill )?tests?'
        r'|for (?:the )?next (\d+) (?:action|turn|round)s?', t)
    if m:
        return int(next(g for g in m.groups() if g is not None))
    if re.search(r'for the rest of (?:your )?(?:this )?turn', t):
        return 3
    # "until the end of this/the/active investigator's turn"
    if re.search(r'until (?:the )?end of .{0,30}?turn\b', t):
        return 3
    if re.search(r'until (?:the )?end of (?:the )?(?:phase|round)', t):
        return 3
    return 2
###########Add and Red extraction

def _extract_add_red(t: str) -> list:
    """
    Returns (add, add_stat, red, duration).
    """
    add = red = 0
    add_stat = None

    # ── ADD: literal +N numeric bonus ─────────────────────────────────────
    add_m = re.search(
        r'(?:get|gets)\s+\+(\d+)\s+'
        r'(?:'
            r'(?:\[(?:willpower|intellect|combat|agility)\])'
            r'|skill value'
            r'|(?:willpower|intellect|combat|agility)'
            r'|to a skill'
        r')', t)
    if add_m:
        add = int(add_m.group(1))

    if not add:
        add_m2 = re.search(r'investigator(?:s)? gets?\s+\+(\d+)', t)
        if add_m2:
            add = int(add_m2.group(1))

    # ── ADD_STAT: "add your [stat] to your [other stat]" ──────────────────
    # MoM xp2: "add your [intellect] to your [combat] and [agility]"
    # The stat immediately after "add your" is the one being injected.
    # "in place of" (MoM xp0 substitution) does NOT match this pattern.
    if not add:
        addstat_m = re.search(
            r'add\s+(?:your\s+)?'
            r'(\[(?:willpower|intellect|combat|agility)\]'
            r'|\b(?:willpower|intellect|combat|agility)\b)'
            r'\s+to\s+(?:your\s+)?'
            r'(?:\[(?:willpower|intellect|combat|agility)\]'
            r'|\b(?:willpower|intellect|combat|agility)\b)',
            t)
        if addstat_m:
            add_stat = _clean_stat(addstat_m.group(1))

    # ── RED: shroud or difficulty reduction ───────────────────────────────
    red_m = re.search(
        r'(?:gets?\s+)?-(\d+)\s+(?:shroud|difficulty)'
        r'|shroud\s+(?:is\s+)?reduced\s+by\s+(\d+)'
        r'|reduce\s+(?:the\s+)?(?:shroud|difficulty)\s+by\s+(\d+)', t)
    if red_m:
        red = int(next(g for g in red_m.groups() if g is not None))

    has_effect = add or add_stat or red
    duration = _extract_duration(t) if has_effect else 0
    return [add, red, duration]
# ─────────────────────────────────────────────────────────────────────────────
# ACP CALCULATOR. SEEMS TO WORK FINE
# ─────────────────────────────────────────────────────────────────────────────
def compute_acp(text: str, card_type: str, params: dict) -> float:
    """
    The central subtlety around connecting location:
      · Sole-move card (Pathfinder, Cat Burglar): the economy is already
        captured in the [fast]/[action] cost → don't add connecting +1.
        Exception for [action]+exhaust+sole-move: you spend 1 action to get
        ~2 actions worth of effect (move + disengage/something else) → net +1 before exhaust,
        then ÷3 = +0.333.
      · Bonus-move card (Seeking Answers, Survival Instinct, Bait and Switch):
        the card has a primary effect AND gives a free connecting access → +1.
      · Targeting-range reference ('"You've had worse...", Dynamite Blast):
        "connecting location" describes where the card CAN reach, not a granted
        move → 0 bonus.  Detected by: 'connecting location' appears in a
        play-condition line or in a "deal damage to" / "investigator at" context.
    """
    
    t = text.lower()
    acp = 0.0
    has_connecting  = bool(re.search(r'connecting location|at any location', t))
    has_move_verb   = bool(re.search(r'\bmove to a\b|you may move\b', t))
    has_may_Action  = bool(re.search(r'you may immediately take|you may take|you may .* again', t))
    multi_move_m    = re.search(r'move up to (\d+)', t)
    extra_moves     = int(multi_move_m.group(1)) if multi_move_m else 0

    
    

    # ── Fast-on-play (ALL OTHER card types per PDF rule) ─────────────────────────

    # ── [fast] ability tags on assets (only from non-discard-cost paragraphs) ─
    # Discard-cost paragraphs (Beat Cop, Police Badge) are ignored entirely.
    # [reaction]+exhaust on an asset is treated identically to [fast]+exhaust:
    # it fires ~once per round automatically → AcP = 1/3.
    
    if not _is_discard_cost(text) and not _is_header(text):#the header is treated in the next chunk
        non_discard_text=text.lower()
    else:
        return 0.0
    #really interesting approach
    #fast_tag_count = len(re.findall(r'\[fast\]', non_discard_text)) #why??????!!!!! WRONG
    
    react_exhaust  = (bool(re.search(r'\[reaction|fast|\-\]', non_discard_text))
                      and params.get('exhaust_use')
                      and card_type in ('asset', 'pseudo_asset'))
    react_non_exhaust  = (bool(re.search(r'\[reaction|fast|\-\]', non_discard_text))
                      and not params.get('exhaust_use')
                      and card_type in ('asset', 'pseudo_asset'))
    #if card_type in ('asset', 'pseudo_asset') and fast_tag_count > 0:
        #divisor = 3.0 if params.get('exhaust_use') else 1.0
        #acp += fast_tag_count / divisor
    if react_exhaust:
        # [reaction]+exhaust = fires once per round automatically
        acp += 1.0 / 3.0 #debatable but alright
    if react_non_exhaust:
        # [reaction] but no exhaust = fires once per action automatically
        acp += 1.0 #debatable but alright
    # ── Move / connecting-location economy ────────────────────────────────
    # Rules:
    #   is_sole_move=True  → move IS the card's only purpose.
    #                        For [fast]+exhaust (Pathfinder): economy already
    #                        captured by [fast]/3. Don't add separately.
    #                        For [action]+exhaust+sole-move (pure move-only action):
    #                        net economy = 0 (spend 1, save 1). Skip.
    #   is_sole_move=False → move is a BONUS on top of another effect.
    #                        Add +1 (÷3 if exhaust).
    #   Skills: any connecting move is always a pure bonus → handled separately below.
    paras = split_paragraphs(text)
    ability_paras = [p for p in paras
                     if not _is_header(p) and not _is_discard_cost(p)]
    if not ability_paras:
        ability_paras = paras

    is_exhaust_asset = (params.get('exhaust_use') and card_type in ('asset', 'pseudo_asset'))

    
        

    # ── [action]+exhaust+sole-move+disengage: Cat Burglar pattern ─────────
    # The ability does ONLY move+disengage (is_sole_move=False because of 'disengage').
    # Handled above as a bonus move with ÷3 divisor. ✓

    # ── Skills with a bonus move ───────────────────────────────────────────
    
    if card_type == 'pseudo_skill' or card_type == 'skill':#a pseudo skill must be a fast event so usually AcP total=0
        for para in ability_paras:
            e = _extract_effect(para, card_type)
            if has_connecting or has_move_verb or extra_moves or has_may_Action or e['grants_move']:
                if  bool(re.search(r'\bfail\b', t)):
                    acp+=0
                else:
                    acp += 1.0
    else:
        for para in ability_paras:
            e = _extract_effect(para, card_type)
            skip = e['is_sole_move'] and is_exhaust_asset
            if not skip:
                if has_connecting or has_move_verb or extra_moves or has_may_Action or e['grants_move']:
                    if  bool(re.search(r'\bfail\b', t)):
                        acp +=0
                    else:
                        acp +=1.0
        # Bonus move on top of another effect
                
            # is_sole_move=True: skipped (economy already in [fast] or net-zero [action])
    # ── Explicit additional actions ────────────────────────────────────────
    # Only count from non-discard-cost text to avoid Police Badge double-count
    for m in re.finditer(
            r'(?:may take|take)\s+(?:an\s+)?additional\s+(\d+)?\s*actions?',
            non_discard_text):
        n = int(m.group(1)) if m.group(1) else 1
        acp += n-1
    
    
    return round(acp, 3) 

# ─────────────────────────────────────────────────────────────────────────────
# MASTER PARAMETER EXTRACTOR. SURPRISINGLY WORKS
# ─────────────────────────────────────────────────────────────────────────────
def extract_parameters(text: str, card_type: str,
                       health: Optional[int], sanity: Optional[int]) -> dict:
    t_full = text.lower()
    paras  = split_paragraphs(text)
    
    params = {
        'dm': 0,'dm_react':0, 'inv': 0, 'evade': 0, 'draw': 0, 'search': 0,
        'res': 0, 'heal_dmg': 0, 'heal_hor': 0, 'fix': 0, 'AcP':0,
        'is_react':   bool(re.search(r'\[reaction\]|\breaction\b', t_full)),
        'charge_cost': 1,
        'charges':0,'exhaust_use':False,
        'grants_move': False,
        'is_sole_move': False,
        'soak_dmg': _safe_int(health), 'soak_hor': _safe_int(sanity),
        'multi_act': False,
        'stat_wil': 0, 'stat_int': 0, 'stat_com': 0, 'stat_agi': 0
    }
    
    uses_m = re.search(
        r'uses \((\d+)', t_full)
    if uses_m:
        params['charges'] = int(uses_m.group(1))
    
    # Exhaust-as-cost
    if re.search(r'exhaust .{1,50}:', t_full):
        params['exhaust_use'] = True
    

    # Stat bonuses
    for k, v in _extract_stats(text).items():
        params[f'stat_{k}'] = v
    
    # Ability paragraphs — skip headers, play-conditions, and discard-cost blocks
    ability_paras = [
        p for p in paras
        if not _is_header(p) and not _is_discard_cost(p)
    ]
    
    # If filtering left nothing, fall back to just the non-header paragraphs —
    # BUT preserve the discard-cost exclusion: a card whose ONLY ability is a
    # discard-cost ability (Beat Cop) should have zero effect params.
    # Only fall back to all-paras if there were no discard-cost paragraphs to blame.
    has_discard_cost_para = any(_is_discard_cost(p) for p in paras)
    if not ability_paras and not has_discard_cost_para:
        ability_paras = [p for p in paras if not _is_header(p)]
    
    params['multi_act'] = len(ability_paras) > 1

    effects = [_extract_effect(p, card_type) for p in ability_paras]
    total_cost = max(sum(e['charge_cost'] for e in effects), 1)
    
    def _wavg(key):
        return round(sum(e[key] * e['charge_cost'] for e in effects) / total_cost,2)

    

    params['is_react']    = any(e['is_react'] for e in effects)
    params['charge_cost'] = total_cost / max(len(effects), 1)
    
    
    # Charge accounting
    if params['charges'] == 0:
        if health or sanity:
            params['charges'] = 1#ally so yeah only only one round of firing its what im going for, otherwise laboratory assitant vs witton greene is a nightmare and whittons isnt even that easy to fire
        elif card_type in ('asset', 'pseudo_asset'):
            params['charges'] = DEFAULT_CHARGES * 3 if params['exhaust_use'] \
                                 else DEFAULT_CHARGES
        else:
            params['charges'] = 1
    for key in ('dm', 'inv', 'evade', 'draw', 'search', 'res',
                'heal_dmg', 'heal_hor', 'fix'):
        params[key] += _wavg(key)/params['charge_cost']
    params['charge_cost']=1
    if params['is_react']:
        params['dm_react'] = params['dm']
        params['dm']       = 0
    # Exhaust division
    
    # "Fast." as the first line = playing the card is fast.
    # Also catches "Exceptional. Fast." where Fast. follows a sentence.
    
    for p in paras:
        if _is_header(p):
            is_fast_play = bool(re.search(r'(?:^|\n|(?<=\. ))fast[\.,]', text.lower())) or bool(re.search(r'^fast[\.,]', text.lower())) 
            if is_fast_play and not card_type=='pseudo_skill':
                params['AcP']+=1/params['charges']#if fast is in header but there are charges we must normalize
            for key in ('dm', 'inv', 'evade', 'draw', 'search', 'res',
                'heal_dmg', 'heal_hor', 'fix'):
                params[key]+=_extract_effect(p, card_type)[key]/params['charges']
        elif not _is_discard_cost(p):
            params['AcP']+=_extract_effect(p, card_type)['charge_cost']*compute_acp(p,card_type,params)/ total_cost
    divisor=3 if params['exhaust_use'] else 1
    params['AcP']=round(params['AcP'],3)
    if params['fix']>0:
        params['fix']=1
    if params['dm_react']>=1:
        params['charges']=max(params.get('soak_dmg',0),1)
    if params['exhaust_use'] and card_type in ('asset', 'pseudo_asset'):
        for key in ('dm', 'dm_react', 'inv', 'evade', 'draw',
                    'search', 'res', 'heal_dmg', 'heal_hor'):
            params[key] = params[key] / 3.0
    params['search']=round(round(params['search']+0.1))#a kinda ceiling from 0.25
    return params
##############TODO DYNAMIC CHARGES AND ALLIES CHARGES (separate de header too)....
# ─────────────────────────────────────────────────────────────────────────────
# ADDS OR REDS CALCULATOR NEED TO DO. -1 SHROUD OR +1 INTELLECT FOR EXAMPLE
# ─────────────────────────────────────────────────────────────────────────────
#################TODO
###############TODO
# ─────────────────────────────────────────────────────────────────────────────
# MULTI ICONS CARDS WILL+AGI TEST. NEED TO DO
# ─────────────────────────────────────────────────────────────────────────────
#################TODO
###############TODO
# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFY AS HELP GOAL ETC, NAMELY GOAL AS WEAPONS, ILLEGAL, TOMES RELICS, AND SPELLS 
# ─────────────────────────────────────────────────────────────────────────────
def clas_type(card_type: str, traits: str)-> list:
    result=[]
    if card_type=='skill':
        result.append('hel')
    keywords = ['illegal', 'tome', 'relic', 'weapon', 'spell']

    if any(word in traits.lower() for word in keywords):
        result.append('Goal_Card') 
    elif card_type!='skill':
        result.append('stre')
    return result
# ─────────────────────────────────────────────────────────────────────────────
# CARD TRANSFORMER
# ─────────────────────────────────────────────────────────────────────────────
def transform_card(raw_card: dict, faction: str) -> Optional[dict]:
    if raw_card.get('subtype_code', '') in ('weakness', 'basicweakness'):
        return None
    if raw_card.get('type_code') not in ('asset', 'event', 'skill'):
        return None

    raw_type = raw_card['type_code']
    text     = raw_card.get('real_text', '') or ''
    traits   = (raw_card.get('real_traits') or raw_card.get('traits') or '')#SEE IF GOAL

    if is_too_complex(text, traits):
        return None

    card_type = classify_type(raw_type, text)
    
    params    = extract_parameters(text, card_type,
                                    raw_card.get('health'), raw_card.get('sanity'))
    
    
    acp       = compute_acp(text, card_type, params)

    icon_keys = {'wil': 'skill_willpower', 'int': 'skill_intellect',
                 'com': 'skill_combat',    'agi': 'skill_agility', 'wld': 'skill_wild'}
    all_icons = {k: _safe_int(raw_card.get(v)) for k, v in icon_keys.items()}
    #faction_icons = (
       # _safe_int(raw_card.get(FACTION_ICON.get(faction)))
      #  + all_icons['wld']
    #)

    return {
        'Id':          raw_card.get('name'),
        'Unique':      bool(raw_card.get('is_unique', False)),
        'Type':        card_type,
        'Type_Code':   raw_type,
        'Cost':        _safe_int(raw_card.get('cost')),
        'Parameters':  params,
        'Goal_Type':clas_type(card_type,traits),
        #'Icons':       faction_icons,
        'All_Icons':   all_icons,
        'hp':          params['soak_dmg'],
        'sp':          params['soak_hor'],
        'Faction':     raw_card.get('faction_code'),
        'Code':        raw_card.get('code'),
        'level':       raw_card.get('xp'),
        'permanent':   raw_card.get('permanent'),
        'exceptional': raw_card.get('exceptional'),
        'pack_name':   raw_card.get('pack_name'),
        'deck_limit':  raw_card.get('deck_limit'),
        'AP+':         params.get('AcP',0)
    }

# ─────────────────────────────────────────────────────────────────────────────
class ArkhamMiner:
    def __init__(self, faction: str = current_faction):
        self.api_url = "https://arkhamdb.com/api/public/cards/"
        self.faction  = faction
        self.library: list = []

    def fetch_raw_data(self):
        print("Connecting to ArkhamDB...")
        r = requests.get(self.api_url, timeout=30)
        if r.status_code == 200:
            return r.json()
        raise Exception(f"API Error: {r.status_code}")

    def build_library(self):
        raw_data = self.fetch_raw_data()
        for c in raw_data:
            card = transform_card(c, faction=self.faction)
            if card:
                self.library.append(card)
        outfile = f'library_{self.faction}_22.json'
        with open(outfile, 'w') as f:
            json.dump(self.library, f, indent=4)
        print(f"Saved {len(self.library)} cards -> {outfile}")

if __name__ == "__main__":
    miner = ArkhamMiner(faction='mystic')
    miner.build_library()