from typing import Any
from data_types import Creature, Abilities, ConditionalAbility, CombatAbility
import random, math
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
        self.melee_attack = c.melee_attack
        self.melee_defense = c.melee_defense
        self.ranged_attack = c.ranged_attack
        self.ranged_defense = c.ranged_defense
        self.move = c.move
        self.speed = c.speed
        self.shots = c.shots
        self.abilities = c.abilities
        self.spells = c.spells
        self.luck = c.luck
        self.morale = c.morale
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
    #Attack x melee dmg / Defense 
   
    morale_probability = abs(source.morale * .1)
    luck_probability = abs(target.luck * .1)
    #luck is defensive
    #morale effects turn order and offensive dmg
    morale_strike = random.random() < morale_probability
    lucky_strike = random.random() < luck_probability


    attack = source.melee_attack
    if morale_strike == True:
        if source.morale > 0:
            attack = source.melee_attack * 1.25
        if source.morale < 0:
            attack = source.melee_attack * .8

    #calculate dmg range
    min_damage, max_damage = source.damage
    damage = random.randint(min_damage, max_damage)
    

    #calculating damage
    damage_dealt = attack * damage / target.melee_defense

    if lucky_strike == True:
        if target.luck > 0:
            damage_dealt *= .67
        if target.luck < 0:
            damage_dealt *= 1.5

    
    for ability in source.abilities:
        if isinstance(ability, CombatAbility):
            ability.apply_on_attack(source, target)
    for ability in target.abilities:
        if isinstance(ability, CombatAbility):
            ability.apply_on_attack(source, target)

    #Apply effective health pool change
    total = target.current_hp + (target.max_hp * target.amount - 1)
    remaining_hp = total - damage_dealt

    remaining = math.ceil(remaining_hp/ source.max_hp)
    top_health = remaining_hp % source.max_hp
    # In this case im treating current_hp as top unit on the stacks hp
    if remaining_hp <= 0:
        target.amount = 0
        target.current_hp = 0
    else:
        target.amount = remaining
        target.current_hp = top_health

    pass



def apply_range_attack(source: Unit, target: Unit):
    #Attack x ragned dmg / defense
    

    source.shots -= 1
   
   
    morale_probability = abs(source.morale * .1)
    luck_probability = abs(target.luck * .1)
    #luck is defensive
    #morale effects turn order and offensive dmg
    morale_strike = random.random() < morale_probability
    lucky_strike = random.random() < luck_probability


    attack = source.ranged_attack
    if morale_strike == True:
        if source.morale > 0:
            attack = source.ranged_attack * 1.25
        if source.morale < 0:
            attack = source.ranged_attack * .8

    #calculate dmg range
    min_damage, max_damage = source.damage
    damage = random.randint(min_damage, max_damage)
    

    #calculating damage
    damage_dealt = attack * damage / target.ranged_defense

    if lucky_strike == True:
        if target.luck > 0:
            damage_dealt *= .67
        if target.luck < 0:
            damage_dealt *= 1.5

    
    for ability in source.abilities:
        if isinstance(ability, CombatAbility):
            ability.apply_on_attack(source, target)
    for ability in target.abilities:
        if isinstance(ability, CombatAbility):
            ability.apply_on_attack(source, target)

    #Apply effective health pool change
    total = target.current_hp + (target.max_hp * target.amount - 1)
    remaining_hp = total - damage_dealt

    remaining = math.ceil(remaining_hp/ source.max_hp)
    top_health = remaining_hp % source.max_hp
    # In this case im treating current_hp as top unit on the stacks hp
    if remaining_hp <= 0:
        target.amount = 0
        target.current_hp = 0
    else:
        target.amount = remaining
        target.current_hp = top_health

    pass




def apply_spell_attack(source: Unit, target: Unit):


    pass