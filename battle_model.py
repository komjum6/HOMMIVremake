from typing import Any
from data_types import Creature

class StatusEffect:
    """Very unfinished"""
    def __init__(self, name: str, effect: Any, visible: bool, is_good: bool, conflicts_with: list[str] | None = None) -> None:
        self.name = name
        self.visible = visible
        self.is_good = is_good
        if conflicts_with is not None:
            self.conflicts_with = conflicts_with
        else:
            self.conflicts_with = []
        self.effect = effect    # maybe dictionary, maybe callback function


class Unit:
    """A stack in battle"""
    def __init__(self, creature: Creature, amount: int, is_illusion: bool = False, is_summon: bool = False) -> None:
        self.creature = creature
        c = creature
        self.amount = amount
        self.is_illusion = is_illusion
        self.is_summon = is_summon
        self.damage = c.damage
        self.max_hp = c.hp
        self.current_hp = c.hp
        self.attack = c.attack
        self.defense = c.defense
        self.move = c.move
        self.speed = c.speed
        self.shots = c.shots
        self.abilities = c.abilities
        self.spells = c.spells
        self.statuses: list[StatusEffect] = []

    def add_status(self, status: StatusEffect) -> None:
        # remove conflicting effects
        statuses = [x for x in self.statuses if x.name not in status.conflicts_with]
        # actually add it
        statuses.append(status)
        self.statuses = statuses

    def update_state(self):
        """Apply effects, re-calculate all stat multipliers, etc"""
        pass


def apply_melee_attack(source: Unit, target: Unit):
    # What were the formulas for this again?
    pass


def apply_range_attack(source: Unit, target: Unit):
    source.shots -= 1
    pass
