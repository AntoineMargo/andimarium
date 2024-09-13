
from game_graphics import *
from logic_graphics_merge import *


def ai_melee_attack(game_state, bot_left_log):
    x1, y1, z1 = get_character_coordinates(game_state.selected_character)
    x2, y2, z2 = get_character_coordinates(game_state.targeted_character)
    if (x2, y2, z2) in game_state.weapon_range_tiles:
        game_state.selected_character["base"].selected_hand.item.activity.perform()
        game_state.targeted_character = None
        return True
    return False


def ai_ranged_attack(game_state, bot_left_log):
    x1, y1, z1 = get_character_coordinates(game_state.selected_character)
    x2, y2, z2 = get_character_coordinates(game_state.targeted_character)
    if z1 == z2:
        distance_to_target = calculate_bird_distance(x1, y1, z1, x2, y2, z2)
        if (distance_to_target <= game_state.selected_character["base"].selected_hand.item.ranged_increment * 5) and has_line_of_sight(x1, y1, z1, x2, y2, z2):
            game_state.selected_character["base"].selected_hand.item.activity.perform((x2, y2, z2))
            game_state.targeted_character = None
            return True
    return False


def ai_move(game_state, bot_left_log, path):
    game_state.path_tiles.clear()
    for tile in path[0]:
        game_state.path_tiles.append(tile)

    game_state.selected_character["base"].activities[0].perform() # We perform the move activity that's always at index 0
    max_cost = game_state.selected_character["base"].movement_points_left
    last_possible_tile, total_cost = cut_path_based_on_cost(path[0], max_cost)

    last_possible_tile = last_possible_tile[0], last_possible_tile[1], last_possible_tile[2]
    if game_state.selected_character["base"].activities[0].move_to_location(last_possible_tile): # We actually do the movement towards the chosen tile
        return True
    else:
        return False


def target_closest_enemy(game_state):
    x1, y1, z1 = get_character_coordinates(game_state.selected_character)
    closest_enemy = [None, 999]
    for character in game_state.selected_character["base"].hostile:
        if not character["base"].current_health_points > 0:
            continue
        x2, y2, z2 = get_character_coordinates(character)
        distance = calculate_bird_distance(x1, y1, z1, x2, y2, z2)
        if distance < closest_enemy[1]:
            closest_enemy[0] = character
            closest_enemy[1] = distance
    if closest_enemy[0]:
        game_state.targeted_character = closest_enemy[0]
        return True
    else:
        return False


def character_ai_decision_tree(game_state, bot_left_log):
    update_accessible_tiles(game_state)
    update_weapon_range(game_state.selected_character)

    if target_closest_enemy(game_state):
        if attempt_weapon_attack_against_nearby_enemy(game_state, bot_left_log):
            return
        if attempt_movement_towards_nearby_enemy(game_state, bot_left_log):
            return
        
    skip_action(game_state)


def attempt_weapon_attack_against_nearby_enemy(game_state, bot_left_log):
    selected_hand = game_state.selected_character["base"].selected_hand
    attack_function = ai_ranged_attack if selected_hand.item.ranged_increment else ai_melee_attack

    return attack_function(game_state, bot_left_log)


def get_tiles_from_which_to_attack_target(game_state):
    potential_destination_tiles = []

    x, y, z = get_character_coordinates(game_state.targeted_character)

    if game_state.selected_character["base"].selected_hand.item.ranged_increment: # If a ranged weapon is selected
        potential_destination_tiles += get_tiles_at_distance(game_state, x, y, z, 1) # We check all the tiles in weapon range

    else: # If a melee weapon is selected
        for n in range(game_state.selected_character["base"].selected_hand.item.melee_range[0], game_state.selected_character["base"].selected_hand.item.melee_range[1]+1):
            potential_destination_tiles += get_tiles_at_distance(game_state, x, y, z, n) # We check all the tiles in weapon range

    return potential_destination_tiles


def attempt_movement_towards_nearby_enemy(game_state, bot_left_log):
    best_path = [(0, 0)], float('inf')
    potential_destination_tiles = get_tiles_from_which_to_attack_target(game_state)

    x, y, z = get_character_coordinates(game_state.targeted_character)

    path_found = False

    for tile in potential_destination_tiles: # We check which of said tiles would be quickest to get to
        tile = tile[0], tile[1], z
        path, cost = determine_path(tile)
        if 0 < cost < best_path[1]:
            best_path = path, cost
            path_found = True

    if path_found:
        print(f"Best path found: {best_path}")
        print(f"Attempting ai_move")
        if ai_move(game_state, bot_left_log, best_path): # best_path contains both the path list and its cost in a tuple
            return True
        
    return False


def skip_action(game_state):
    game_state.selected_character["base"].actions_left -= 1
    game_state.targeted_character = None

