from data_types import Creature

class StatusEffect:
    """Very unfinished"""
    def __init__(self, name: str, visible: bool, is_good: bool, conflicts_with: list[str], effect) -> None:
        self.name = name
        self.visible = visible
        self.is_good = is_good
        self.conflicts_with = conflicts_with
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
        self.statuses = []

    def add_status(self, status: StatusEffect) -> None:
        # remove conflicting effects
        to_remove = []
        for i in status.conflicts_with:
            if i in self.statuses:
                to_remove.append(i)
        
        try:
            for i in to_remove:
                self.statuses.remove(i)
        except ValueError:
            print(f"Attempted to remove non-existent status effect \"{i}\" from {self.creature.name}")
        # actually add it
        self.statuses.append(status)

    def update_state(self):
        """Apply effects, re-calculate all stat multipliers, etc"""
        pass


def apply_melee_attack(source: Unit, target: Unit):
    # What were the formulas for this again?
    pass


def apply_range_attack(source: Unit, target: Unit):
    source.shots -= 1
    pass
