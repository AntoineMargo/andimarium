from random import randint

from logic_graphics_merge import *
from interface import *
from characters import *


def basic_roll(attacking_character, defending_character, attacking_stat: str, defending_stat: str, attacking_bonus = 0, defending_bonus = 0):
        attack_roll = randint(1, 12)
        defence_roll = randint(1, 12)
        attack_number = attack_roll + getattr(attacking_character["base"], attacking_stat) + attacking_bonus
        defence_number = defence_roll + getattr(defending_character["base"], defending_stat) + defending_bonus
        number_difference = attack_number - defence_number
        return number_difference, attack_roll, defence_roll


def determine_degree_of_success(roll_result):
    determined_degree = 0 # the damage type's multiplier for the degree of success achieved by the attack
    difference_to_multiplier = {10: 3, 0: 2, -10: 1}

    for threshold, multiplier in difference_to_multiplier.items():
        if roll_result >= threshold:
            determined_degree = multiplier
            break
    return determined_degree


def power_points_used(state=game_state):
    character = state.selected_character["base"]
    amount = character.spellcasting_table[character.level][character.selected_power_tier-1]
    character.power_pool_current -= amount


def action_point_used(amount=1, state=game_state):
    state.selected_character["base"].actions_left -= amount


def reaction_point_used(character, amount=1, state=game_state):
    character["base"].reactions_left -= amount


def create_melee_attack_activity_for_item(item):
    activity_name = f"{item.name}_attack"
    activity_description = f"An attack with your {item.name}."
    activity = WeaponMeleeAttackActivity(activity_name, item.sprite, activity_description, 1, False, item)
    item.activity = activity


def create_ranged_attack_activity_for_item(item):
    activity_name = f"{item.name}_attack"
    activity_description = f"An attack with your {item.name}."
    activity = WeaponRangedAttackActivity(activity_name, item.sprite, activity_description, 1, False, item)
    item.activity = activity


def weapon_attack(origin_character, destination_character, increment=0, state=game_state, log=bot_left_log):
    weapon = origin_character["base"].selected_hand.item
    attack_type = origin_character["base"].selected_hand.attack_type

    if increment:
        defending_stat = "final_ranged_defence"
        bonus = increment*2
    else:
        defending_stat = "final_melee_defence"
        bonus = 2

    roll_result, att_roll, def_roll = basic_roll(origin_character, destination_character, "final_offence", defending_stat, bonus)
    damage_rolls = []
    degree_of_success = determine_degree_of_success(roll_result)
    log.roll_message(roll_result, att_roll)
    log.degree_of_success_message(degree_of_success)

    if attack_type.multiplier[degree_of_success] > 0:
        damage_rolls = [randint(1, weapon.damage_die) for _ in range(weapon.dice_number*attack_type.multiplier[degree_of_success])]
        damage_dealt = sum(damage_rolls)+origin_character["base"].base_strength_bonus
    else:
        damage_rolls = [0]
        damage_dealt = 0

    # bot_left_log.add_message(f"{damage_rolls}")

    damage_taken = destination_character["base"].take_damage(damage_dealt, "physical")

    if damage_taken < 0:
        log.add_message(f"{destination_character["base"].name} has taken no damage.")
    else:
        log.add_message(f"{destination_character["base"].name} has taken {str(damage_taken)} damage.")
        state.hit_characters[destination_character["graphic"]] = damage_taken


def spell_attack(destination_character, damage_die, defending_stat, damage_multiplier=[0, 1, 2, 3], state=game_state, log=bot_left_log):
    origin_character = state.selected_character
    roll_result, att_roll, def_roll = basic_roll(origin_character, destination_character, "final_resolve", defending_stat)
    damage_rolls = []
    degree_of_success = determine_degree_of_success(roll_result)
    log.roll_message(roll_result, att_roll)
    log.degree_of_success_message(degree_of_success)

    if degree_of_success > 0:
        damage_rolls = [randint(1, damage_die) for _ in range(origin_character["base"].selected_power_tier*damage_multiplier[degree_of_success])]
        damage_dealt = sum(damage_rolls)
    else:
        damage_rolls = [0]
        damage_dealt = 0

    # bot_left_log.add_message(f"{damage_rolls}")

    damage_taken = destination_character["base"].take_damage(damage_dealt, "physical")

    if damage_taken < 0:
        log.add_message(f"{destination_character["base"].name} has taken no damage.")
    else:
        log.add_message(f"{destination_character["base"].name} has taken {str(damage_taken)} damage.")
        state.hit_characters[destination_character["graphic"]] = damage_taken


class Reaction:
    def __init__(self, character) -> None:
        self.character = character


class AttackOfOpportunity(Reaction):
    def __init__(self, character) -> None:
        super().__init__(character)
        self.matching_triggers = ["movement"]

    def activation(self, state=game_state):
        if self.character != state.selected_character and self.character["base"].reactions_left > 0:
            for index, tile in enumerate(state.path_tiles):
                if tile in self.character["base"].threatened_tiles:
                    if index + 1 < len(state.path_tiles) and state.path_tiles[index+1] in self.character["base"].threatened_tiles:
                        weapon_attack(self.character, state.selected_character)
                        reaction_point_used(self.character)
                        return


class ReactionTracker:
    def __init__(self) -> None:
        """active_reactions by trigger category"""
        self.movement = []
        self.melee_attack =  []
        self.ranged_attack =  []
        self.cast =  []

    def add(self, reaction):
        for trigger in reaction.matching_triggers:
            if trigger == "movement":
                self.movement.append(reaction)
            if trigger == "melee_attack":
                self.melee_attack.append(reaction)
            if trigger == "ranged_attack":
                self.ranged_attack.append(reaction)
            if trigger == "cast":
                self.cast.append(reaction)

    def movement_trigger(self):
        if self.movement:
            for reaction in self.movement:
                reaction.activation()


class Activity:
    def __init__(self, name, icon, description, action_cost, immediate_effect: bool = False) -> None:
        self.name = name
        self.icon = icon
        self.description = description
        self.action_cost = action_cost
        self.immediate_effect = immediate_effect
        # self.spell = False

        self.image = pygame.image.load(icon).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = 800, 800

    def perform(self):
        pass

    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self) -> str:
        return f"{self.name}"


class Spell(Activity):
    def __init__(self, name, icon, description, action_cost, immediate_effect: bool, base_spell_tier) -> None:
        super().__init__(name, icon, description, action_cost, immediate_effect)
        self.base_spell_tier = base_spell_tier
        self.spell = True

    def perform(self):
        pass


class MoveActivity(Activity):
    def __init__(self, name, icon, description, action_cost, immediate_effect: bool) -> None:
        super().__init__(name, icon, description, action_cost, immediate_effect)

    def perform(self, state=game_state, log=bot_left_log):
        if state.selected_character["base"].movement_points_left > 1.5: # type: ignore
            log.add_message(f"You must exhaust your existing movement points before you can start another move activity.")
        elif state.selected_character["base"].actions_left == 0:
            log.add_message(f"You do not have enough actions left to use this activity.")
        else:
            state.accessible_tiles.clear()
            if state.selected_character["base"].actions_left > 0:
                state.selected_character["base"].actions_left -= 1
                state.selected_character["base"].movement_points_left += state.selected_character["base"].final_movement_points
                interface_actions.update(state)
                interface_movement_pts.update(state)

                potentially_accessible_coordinates = list_accessible_tiles(state.selected_character)

                for coordinates in potentially_accessible_coordinates:
                        x, y, z = coordinates
                        if 0 <= x < state.map_width and 0 <= y < state.map_height:
                            state.accessible_tiles.add(coordinates)
                state.show_accessible_tiles = True

    def move_to_location(self, target_tile, state=game_state, log=bot_left_log):
        
        path, cost = determine_path(target_tile)
        if len(path) > 0:
            if cost <= state.selected_character["base"].movement_points_left:
                state.selected_character["base"].movement_points_left -= cost
                state.path_tiles_to_flash.clear()
                state.path_tiles_to_flash = path.copy()
                state.time_to_flash_path_tiles = 160
                state.reaction_tracker.movement_trigger()
                reposition_movement(state.selected_character, target_tile[0], target_tile[1], target_tile[2])
                state.interface_update_needed = True
                return True
            else:
                print(f"Cannot reach location.")
                if not state.ai_turn_in_progress:
                    log.add_message("Cannot reach location.")
                return False


class WeaponMeleeAttackActivity(Activity):
    def __init__(self, name, icon, description, action_cost, immediate_effect: bool, item=None) -> None:
        super().__init__(name, icon, description, action_cost, immediate_effect)

    def perform(self, state=game_state, log=bot_left_log):
        targeted_character = state.targeted_character

        if targeted_character:
            if state.selected_character["base"].actions_left > 0:
                (x, y, z) = targeted_character["logic"].pos_x, targeted_character["logic"].pos_y, targeted_character["logic"].pos_z
                if (x, y, z) in state.weapon_range_tiles:
                    weapon_attack(state.selected_character, targeted_character)
                    action_point_used()
                    interface_actions.update(state)
                    update_weapon_range(game_state.selected_character)
                    return
                
                else:
                    log.add_message("Target not in range.")
                    return
            else:
                log.add_message("You have no action points left.")
                return
        else:
            log.add_message("No valid target.")
            return


class WeaponRangedAttackActivity(Activity):
    def __init__(self, name, icon, description, action_cost, immediate_effect: bool, item=None) -> None:
        super().__init__(name, icon, description, action_cost, immediate_effect)
        self.item = item

    def perform(self, target_coordinates=(0, 0, 0), state=game_state, log=bot_left_log):
        x1, y1, z1 = get_character_coordinates(state.selected_character)
        if state.ai_turn_in_progress:
            x2, y2, z2 = target_coordinates
        else:
            x2, y2, z2 = get_tile_under_cursor(state)

        distance = calculate_bird_distance(x1, y1, z1, x2, y2, z2)
        increment = int(distance/state.selected_character["base"].selected_hand.item.ranged_increment)

        for entity in game_state.current_map_tiles[x2, y2].entities:
            if isinstance(entity, LogicCharacter):
                targeted_character = entity.parent_dict
                break

        if targeted_character:
            if state.selected_character["base"].actions_left > 0:
                if has_line_of_sight(x1, y1, z1, x2, y2, z2):
                    if increment <= 5:
                        weapon_attack(state.selected_character, targeted_character, increment)
                        if self.item:
                            graphic_projectile((x1, y1), (x2, y2), self.item.projectile_speed, self.item.projectile_image)
                        activating_noise(state, (x2, y2, z2))
                        action_point_used()
                        interface_actions.update(state)
                        update_weapon_range(game_state.selected_character)
                        return
                    else:
                        log.add_message("Target not in range.")
                        return
                else:
                    log.add_message("You don't have line of sight to the target.")
                    return
            else:
                log.add_message("You have no action points left.")
                return
        else:
            log.add_message("No valid target.")
            return
        
    def add_graphic_projectile(self, image, speed):
        self.image = image
        self.speed = speed


class WeaponThrowActivity(Activity):
    def __init__(self, name, icon, description, action_cost, immediate_effect: bool, item=None) -> None:
        super().__init__(name, icon, description, action_cost, immediate_effect)
        self.item = item

    def perform(self, target_coordinates=(0, 0, 0), state=game_state, log=bot_left_log):
        x1, y1, z1 = get_character_coordinates(state.selected_character)
        if state.ai_turn_in_progress:
            x2, y2, z2 = target_coordinates
        else:
            x2, y2, z2 = get_tile_under_cursor(state)

        distance = calculate_bird_distance(x1, y1, z1, x2, y2, z2)
        increment = int(distance/state.selected_character["base"].selected_hand.item.throw_increment)

        for entity in game_state.current_map_tiles[x2, y2].entities:
            if isinstance(entity, LogicCharacter):
                targeted_character = entity.parent_dict
                break

        if targeted_character:
            if state.selected_character["base"].actions_left > 0:
                if has_line_of_sight(x1, y1, z1, x2, y2, z2):
                    if increment <= 5:
                        weapon_attack(state.selected_character, targeted_character, increment)
                        graphic_projectile((x1, y1), (x2, y2), 60, r"assets/graphics/objects/big_bolt.png")
                        activating_noise(state, (x2, y2, z2))
                        action_point_used()
                        interface_actions.update(state)
                        update_weapon_range(game_state.selected_character)
                        return
                    else:
                        log.add_message("Target not in range.")
                        return
                else:
                    log.add_message("You don't have line of sight to the target.")
                    return
            else:
                log.add_message("You have no action points left.")
                return
        else:
            log.add_message("No valid target.")
            return


class SingleEntityDamageActivity(Activity):
    def __init__(self, name, icon, description, action_cost, immediate_effect, range, damage_die, damage_multiplier, attack_stat, defend_stat, armour_type = None) -> None:
        super().__init__(name, icon, description, action_cost, immediate_effect)
        self.immediate_effect = False
        self.range = range
        self.damage_die = damage_die
        self.damage_multiplier = damage_multiplier # ex: [0, 1, 2, 3]
        self.attack_stat = attack_stat
        self.defend_stat = defend_stat
        self.armour_type = armour_type

    def perform(self, target_coordinates=(0, 0, 0), state=game_state, log=bot_left_log):
        x1, y1, z1 = get_character_coordinates(game_state.selected_character)
        if state.ai_turn_in_progress:
            x2, y2, z2 = target_coordinates
        else:
            x2, y2, z2 = get_tile_under_cursor(state)

        distance = calculate_bird_distance(x1, y1, z1, x2, y2, z2)
        
        for entity in game_state.current_map_tiles[x2, y2].entities:
            if isinstance(entity, LogicCharacter):
                targeted_character = entity.parent_dict
                break
        
        if targeted_character:
            if state.selected_character["base"].actions_left > 0:
                if distance <= self.range and has_line_of_sight(x1, y1, z1, x2, y2, z2):
                    roll_result, att_roll, def_roll = basic_roll(state.selected_character, targeted_character, self.attack_stat, self.defend_stat, 2)
                    damage_rolls = []
                    degree_of_success = determine_degree_of_success(roll_result)
                    log.roll_message(roll_result, att_roll)
                    log.degree_of_success_message(degree_of_success)

                    if degree_of_success > 0:
                        damage_rolls = [randint(1, self.damage_die) for _ in range(state.selected_character["base"].level_mod*self.damage_multiplier[degree_of_success])]
                        damage_dealt = sum(damage_rolls)
                    else:
                        damage_rolls = [0]
                        damage_dealt = 0

                    # log.add_message(f"{damage_rolls}")
                    
                    damage_taken = targeted_character["base"].take_damage(damage_dealt, "physical")

                    if damage_taken < 0:
                        log.add_message(f"{targeted_character["base"].name} has taken no damage.")
                    else:
                        log.add_message(f"{targeted_character["base"].name} has taken {str(damage_taken)} damage.")
                        state.hit_characters[targeted_character["graphic"]] = damage_taken

                    activating_noise(state, (x2, y2))
                    action_point_used(2)
                    interface_actions.update(state)
                    update_weapon_range(game_state.selected_character)
                    state.interface_update_needed = True
                    return
                else:
                    log.add_message("Target not in range.")
                    return
            else:
                log.add_message("You have no action points left.")
                return
        else:
            log.add_message("No valid target.")
            return


class SingleEntityDamageSpell(Spell):
    def __init__(self, name, icon, description, action_cost, immediate_effect, base_spell_tier, range, damage_die, damage_multiplier, defending_stat, armour_type, speed, image) -> None:
        super().__init__(name, icon, description, action_cost, immediate_effect, base_spell_tier)
        self.immediate_effect = False
        self.range = range
        self.damage_die = damage_die
        self.damage_multiplier = damage_multiplier # ex: [0, 1, 2, 3]
        self.defending_stat = defending_stat
        self.armour_type = armour_type
        self.action_cost = action_cost
        self.speed = speed
        self.image = image

    def perform(self, target_coordinates=(0, 0, 0), state=game_state, log=bot_left_log,):
        if self.base_spell_tier > state.selected_character["base"].selected_power_tier:
            log.add_message(f"This spell cannot be cast at this low a tier.")
            return
        if state.selected_character["base"].power_pool_current < state.selected_character["base"].spellcasting_table[state.selected_character["base"].level][state.selected_character["base"].selected_power_tier-1]:
            log.add_message(f"You do not have enough power points to perform this activity.")
            return

        x1, y1, z1 = get_character_coordinates(state.selected_character)
        if state.ai_turn_in_progress:
            x2, y2, z2 = target_coordinates
        else:
            x2, y2, z2 = get_tile_under_cursor(state)

        distance = calculate_bird_distance(x1, y1, z1, x2, y2, z2)
        
        for entity in game_state.current_map_tiles[x2, y2].entities:
            if isinstance(entity, LogicCharacter):
                targeted_character = entity.parent_dict
                break
        
        if targeted_character:
            if state.selected_character["base"].actions_left >= self.action_cost:
                if distance <= self.range and has_line_of_sight(x1, y1, z1, x2, y2, z2):
                    spell_attack(targeted_character, self.damage_die,  self.defending_stat)
                    graphic_projectile((x1, y1), (x2, y2), self.speed, self.image)
                    activating_noise(state, (x2, y2, z2))
                    action_point_used(self.action_cost)
                    power_points_used()
                    interface_actions.update(state)
                    update_weapon_range(game_state.selected_character)
                    state.interface_update_needed = True
                    return
                else:
                    log.add_message("You cannot hit this target.")
                    return
            else:
                log.add_message("You have no action points left.")
                return
        else:
            log.add_message("No valid target.")
            return


for name, item in list(items.items()):
    if isinstance(item, Weapon):
        if item.ranged_increment:
            create_ranged_attack_activity_for_item(item)
        else:
            create_melee_attack_activity_for_item(item)


move_activity = MoveActivity("move", r"assets/graphics/interface/activities/move_activity2.png", "Your basic ability to move around the world.", 1, True)
throw_activity = WeaponThrowActivity("throw_weapon", r"assets/graphics/interface/activities/throw2.png", "Throw your weapon at an enemy.", 1, False)

default_activites = [move_activity, throw_activity]

activities = {"example_spell": SingleEntityDamageSpell("damage_spell", r"assets/graphics/interface/activities/placeholder3.png", "A basic single target damage spell.", 2, False, 1, 12, 10, [0, 1, 2, 3], "final_agility", "bullshit", 70, r"assets/graphics/objects/mbolt.png"),}

data.load_activities(activities)

game_state.reaction_tracker = ReactionTracker()

