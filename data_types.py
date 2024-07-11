from dataclasses import dataclass, field
from enum import Enum




class Alignment(Enum):
    CHAOS = 0
    NATURE = 1
    LIFE = 2
    ORDER = 3
    DEATH = 4
    MIGHT = 5

class UnitSize(Enum):
    SMALL = 0   #3x3
    BIG = 1     #5x5 with 3x3 edges

@dataclass
class BattleMaps:
    #Stores battlefield sprites
    data:any = None
    

    #grid location, not pixel location
    team1_positions:list[tuple[int,int]] = None
    team2_positions:list[tuple[int,int]] = None

@dataclass 
class BattleTile:
    terrain:str = ""
    occupied:bool = False

@dataclass
class Resources:
    gold:int = 0
    wood:int = 0
    ore:int = 0
    gems:int = 0
    crystal:int = 0
    sulfur:int = 0
    mercury:int = 0




@dataclass
class Creature:
    """Base definition of a creature"""
    name:str = ""
    description:str = ""
    data:any = None    # should contain sprites, animations, etc (or a reference to them?)
    level:int = 0
    alignment:Alignment = None  # placeholder

    cost:Resources = None
    growth:int = 0
    experience_value:int = 0

    size:int = 0
    damage:tuple = field(default_factory=tuple)
    hp:int = 0
    melee_attack:int = 0
    ranged_attack:int = 0
    melee_defense:int = 0
    ranged_defense:int = 0   #Added ranged and melee subdivison
    move:int = 0
    speed:int = 0
    shots:int = 0
    abilities:list = field(default_factory=list)
    spells:list = field(default_factory=list)
    spell_power:int = 0
    mana:int = 0
    luck:int = 0             #Added morale and luck
    morale:int = 0


@dataclass
class StatusModifier:
    name:str = ""
    description:str = ""

#Ability class split up into two definition, conditional abilities like the pirates or flying
#On attack abilities like curse
#How to implement abilities like charge
@dataclass
class Abilities:
    name:str = ""
    description:str = ""
    data:any = None
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


 

