from config import *
from items import *
# from archetypes import *

class SizeClass:
    def __init__(self, name: str, side_length: int):
        self.type = name
        self.side_length = side_length


class ActiveInHand:
    def __init__(self, item, attack_type = damage_crushing):
        self.item = item
        self.attack_type = attack_type

    def __str__(self):
        return f"{self.item}, {self.attack_type}"
    
    def __repr__(self):
        return f"{self.item}, {self.attack_type}"


small = SizeClass("small", 1)
medium = SizeClass("medium", 1)
large = SizeClass("large", 2)
huge = SizeClass("huge", 3)


class Character:
    def __init__(self, name: str, level: int = 1, size: SizeClass = medium, attributes: list = [5, 5, 5, 5], sprite: str = r"graphics/charB.png", player=False):

        self.name = name
        self.level = level
        self.level_mod = level//2
        self.challenge_rating = self.level

        self.sprite = sprite

        self.archetype = None
        self.discipline = None

        self._base_size = size
        self._final_size = size

        self.talents = []
        self.activities = []
        self.spells = []
        self.reactions = []
        self.conditions = []

        # attributes
        self.acuity = attributes[0]
        self.brawn = attributes[1]
        self.dexterity = attributes[2]
        self.will = attributes[3]

        # primary aptitudes
        self.base_agility = int(self.dexterity+(1*self.level_mod))
        self.base_resolve = int(self.will+(1*self.level_mod))
        self.base_sense = int(self.acuity+(1*self.level_mod))
        self.base_stamina = int(self.brawn+(1*self.level_mod))
        self.base_offence = int(self.acuity+(1*self.level_mod))
        self.base_melee_defence = int(self.dexterity+(1*self.level_mod))
        self.base_ranged_defence = int(self.dexterity+(1*self.level_mod))

        #secondary aptitudes
        # later...
        
        # primary aptitudes with all modifiers factored in
        self.final_agility = self.base_agility
        self.final_resolve = self.base_resolve
        self.final_sense = self.base_sense
        self.final_stamina = self.base_stamina
        self.final_offence = self.base_offence
        self.final_melee_defence = self.base_melee_defence
        self.final_ranged_defence = self.base_ranged_defence

        # static characteristics
        self.base_strength_bonus = self.brawn

        self.base_movement_points = self.dexterity
        self.final_movement_points = self.base_movement_points
        self.movement_points_left = 0.0

        self.base_run_cost = 1
        self.base_swim_cost = 2
        self.base_climb_cost = 2
        self.base_burrow_cost = 999
        self.base_fly_cost = 999

        # static characteristics with all modifiers factored in
        self.final_strength_bonus = self.base_strength_bonus

        self.final_run_cost = self.base_run_cost
        self.final_swim_cost = self.base_swim_cost
        self.final_climb_cost = self.base_climb_cost
        self.final_burrow_cost = self.base_burrow_cost
        self.final_fly_cost = self.base_fly_cost

        self.max_load = self.base_strength_bonus
        self.current_load = 0

        self.spellcasting_table = {}
        self.max_power_tier_available = 0
        self.selected_power_tier = 0

        self.power_pool_max = int(self.will*2+(self.will*0.2*self.level_mod))
        self.power_pool_current = self.power_pool_max

        self.max_health_points = int(self.brawn*12+(self.brawn*self.level_mod))
        self.current_health_points = self.max_health_points
        self.current_temp_health_points = 0

        self.vigour = 0

        # armour
        self.base_physical_armour = 0
        self.base_heat_armour = 0
        self.base_cold_armour = 0
        self.base_electricity_armour = 0
        self.base_corrosion_armour = 0
        self.base_poison_armour = 0
        self.base_psychic_armour = 0

        self.final_physical_armour = 0
        self.final_heat_armour = 0
        self.final_cold_armour = 0
        self.final_electricity_armour = 0
        self.final_corrosion_armour = 0
        self.final_poison_armour = 0
        self.final_psychic_armour = 0

        # all carried items
        self.equipment = []

        # equipped items
        self.body = None
        self.shoulders = None
        self.left_hand = ActiveInHand(items["fist"], damage_crushing)
        self.right_hand = ActiveInHand(items["fist"], damage_crushing)
        self.belt = None
        self.boots = None
        self.gauntlets = None
        self.necklace = None
        self.left_bracelet = None
        self.right_bracelet = None
        self.left_ring1 = None
        self.left_ring2 = None
        self.left_ring3 = None
        self.left_ring4 = None
        self.left_ring5 = None
        self.right_ring1 = None
        self.right_ring2 = None
        self.right_ring3 = None
        self.right_ring4 = None
        self.right_ring5 = None

        self.selected_hand = self.left_hand
        self.selected_activity = self.selected_hand

        self.threatened_tiles = []

        # strategic level
        # relationships
        self.relatives = []
        self.friends = []
        self.acquaintances = []
        self.partners = []
        self.superiors = []
        self.colleagues = []
        self.underlings = []
        self.clients = []
        self.enemies = []

        # tactical level
        # combat status
        self.player = player
        self.allied = []
        self.safe = []
        self.suspicious = []
        self.dangerous = []
        self.hostile = []

        self.active = False
        self.normal_number_actions = 3
        self.final_number_actions = self.normal_number_actions
        self.actions_left = self.final_number_actions

        self.normal_number_reactions = 1
        self.final_number_reactions = self.normal_number_reactions
        self.reactions_left = self.final_number_reactions


    def new_turn(self):
        self.actions_left = self.final_number_actions
        self.reactions_left = self.final_number_reactions
        self.movement_points_left = 0.0


    def take_damage(self, damage, armour_type):
        armour_dict = {"physical": self.final_physical_armour, 
                      "heat":self.final_heat_armour,
                      "cold": self.final_cold_armour,
                      "electricity": self.final_electricity_armour,
                      "corrosion": self.final_corrosion_armour,
                      "poison": self.final_poison_armour,
                      "psychic": self.final_psychic_armour}
        armour = armour_dict[armour_type]
        damage_taken = damage - armour
        if damage_taken < 0:
            damage_taken = 0
        self.current_health_points -= damage_taken
        if self.current_health_points <= 0:
            self.active = False
        if self.current_health_points - damage < -self.max_health_points:
            self.current_health_points = -self.max_health_points
        return damage_taken


    def add_items(self, item_list: list):
        for item in item_list:
            if item.load + self.current_load <= self.max_load:
                self.equipment.append(item)
                self.current_load += item.load
            else:
                print(f"{item.name} can not be picked up as you're over carrying capacity.")


    def remove_items(self, item_list: list):
        for item in item_list:
            if item in self.equipment:
                self.equipment.pop(item)
                self.current_load -= item.load


    def vigour_change(self, amount: int):
        self.vigour += amount

        self.final_agility += amount
        self.final_resolve += amount
        self.final_sense += amount
        self.final_stamina += amount

        self.final_movement_points += amount

        self.final_strength_bonus += amount

        self.final_offence += amount
        self.final_melee_defence += amount
        self.final_ranged_defence += amount


    def defence_change(self, defence_change: int):
        self.final_melee_defence += defence_change
        self.final_ranged_defence += defence_change


    def speed_change(self, speed_change: int):
        self.final_movement_points += speed_change


    def update_spellcasting(self):
        self.max_power_tier_available = len(self.spellcasting_table[self.level])
        self.selected_power_tier = 1


    def equip_items(self, items_to_equip: list):
        for item in items_to_equip:
            if item in self.equipment:
                if isinstance(item, Weapon):
                    if self.left_hand.item == items["fist"]:
                        self.left_hand = ActiveInHand(item, item.weapon_damage_types[0])
                        self.defence_change(item.defence_bonus)
                        self.speed_change(item.speed_penalty)
                    elif self.right_hand.item == items["fist"]:
                        self.right_hand = ActiveInHand(item, item.weapon_damage_types[0])
                        self.defence_change(item.defence_bonus)
                        self.speed_change(item.speed_penalty)
                elif isinstance(item, Armour) and self.body == None:
                    self.body = item
                    self.vigour_change(item.vigour_penalty)
                    self.final_physical_armour += item.damage_reduction[0]
                    self.final_heat_armour += item.damage_reduction[1]
                    self.final_cold_armour += item.damage_reduction[2]
                    self.final_electricity_armour += item.damage_reduction[3]
                    self.final_corrosion_armour += item.damage_reduction[4]
                    self.final_poison_armour += item.damage_reduction[5]
                    self.final_psychic_armour += item.damage_reduction[6]


    def apply_archetype(self, archetypes):
        if self.archetype and archetypes[self.archetype]:
            archetype = archetypes[self.archetype]

            for level, talents in archetype.talents.items():
                if level <= self.level and talents[0]:
                    for talent in talents[0]:
                        self.apply_talent(talent)


    def apply_talent(self, talent):
        if hasattr(talent, "table"):
            talent.load_table(self)
            self.update_spellcasting()

        if talent.activities:
            for activity in talent.activities:
                if activity.spell:
                    self.spells.append(activity)
                else:
                    self.activities.append(activity)

        if talent.bonuses:
            for existing_talent in self.talents:
                if existing_talent.name == talent.name:
                    if existing_talent.rank >= talent.rank:
                        return
                    else:
                        existing_talent.unapply(self)
                        self.talents.remove(existing_talent)
            talent.apply(self)

        self.talents.append(talent)


    def initialisation(self, default_activites, update_weapon_range, state=game_state):
        self.selected_hand = self.left_hand
        self.selected_activity = self.selected_hand

        for activity in default_activites:
            self.activities.append(activity)

        self.apply_archetype(data.archetypes)
        update_weapon_range(state.selected_character, state=game_state)


    def add_activity(self, activity):
        self.activities.append(activity)


    def add_spell(self, spell):
        self.spells.append(spell)


    def change_tactical_relationship(self, character, new_group):
        relationship_groups = {
        "allied": self.allied,
        "safe": self.safe,
        "suspicious": self.suspicious,
        "dangerous": self.dangerous,
        "hostile": self.hostile
        }

        if new_group not in relationship_groups:
            print("Invalid relationship group.")
            return
        
        for group in relationship_groups.values():
            if character in group:
                group.remove(character)

        relationship_groups[new_group].append(character)


    def full_rest(self):
        self.current_health_points = self.max_health_points
        self.current_temp_damage = 0


    def __str__(self):
        return f"{self.name} (level: {self.level}, power rating: {self.challenge_rating})"


