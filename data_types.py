from dataclasses import dataclass


ALIGNMENT_CHAOS = 0
ALIGNMENT_NATURE = 1
ALIGNMENT_LIFE = 2
ALIGNMENT_ORDER = 3
ALIGNMENT_DEATH = 4
ALIGNMENT_MIGHT = 5

@dataclass
class Resources:
    gold = 0
    wood = 0
    ore = 0
    gems = 0
    crystal = 0
    sulfur = 0
    mercury = 0


@dataclass
class Creature:
    """Base definition of a creature"""
    name = ""
    description = ""
    data = None    # should contain sprites, animations, etc (or a reference to them?)
    level = 0
    alignment = ALIGNMENT_CHAOS     # placeholder

    cost = Resources()
    growth = 0
    experience_value = 0

    damage = [0, 0]
    hp = 0
    attack = 0
    defense = 0
    move = 0
    speed = 0
    shots = 0
    abilities = []
    spells = []
    spell_power = 0
    mana = 0
