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
    melee_attack = 0
    ranged_attack = 0
    melee_defense = 0
    ranged_defense = 0     #Added ranged and melee subdivison
    move = 0
    speed = 0
    shots = 0
    abilities = []
    spells = []
    spell_power = 0
    mana = 0
    luck = 0              #Added morale and luck
    morale = 0


#Ability class split up into two definition, conditional abilities like the pirates or flying
#On attack abilities like curse
#How to implement abilities like charge
@dataclass
class Abilities:
    name = ""
    description = ""
    data = None
    def apply(self, attacker, defender):
        """Default apply method."""
        pass

class ConditionalAbility(Abilities):
    def check_condition(self, creature, context):
        """Check specific conditions"""
        return False
    
    def apply_condition(self, creature, context):
        """Apply effects based on condition"""
        pass

class CombatAbility(Abilities):
    def apply_on_attack(self, attacker, defender):
        """Apply during attack"""
        pass


 

