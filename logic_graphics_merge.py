from random import randint

from game_graphics import *
from pathfinding import *


def add_character_to_location(character, x, y, z = 0): # Tie a character to a location in both logic and graphic space
    new_dict = {
    "base": character,
    "logic": LogicCharacter(character, x, y, z),
    "graphic": GraphicCharacter(character, x, y)
    }

    logic_character = new_dict["logic"]
    logic_character.parent_dict = new_dict  # Set the parent dictionary reference

    game_state.current_map_tiles[x, y].entities.append(new_dict["logic"])
    game_state.current_map_tiles[x, y].passable = False

    game_state.current_map_array[x][y] = 999

    return new_dict


def end_turn(state=game_state):
    enemy_sense_check(game_state)
    state.ai_turn_in_progress = True
    state.player_control = False


def start_turn(game_state, bot_left_log):
    game_state.ai_turn_in_progress = False
    game_state.player_control = True
    game_state.targeted_character = None
    game_state.accessible_tiles.clear()
    game_state.show_accessible_tiles = False
    game_state.interface_update_needed = True
    game_state.current_npc_index = 0
    game_state.turn_counter += 1
    bot_left_log.add_message(f"Turn {game_state.turn_counter} has started.")

    for character in game_state.all_characters:
        character["base"].new_turn()

    for character in game_state.player_characters:
            game_state.selected_character = character
            break


def enemy_sense_check(game_state):
    for character in game_state.non_player_characters:
        if character["base"].current_health_points <= 0:
            character["base"].active = False
            continue
        max_distance = character["base"].final_sense
        # print(f"{character["base"].name}, max distance = {max_distance}")
        char_x, char_y, char_z = get_character_coordinates(character)

        for other_character in character["base"].hostile:
            char_o_x, char_o_y, char_o_z = get_character_coordinates(other_character)
            distance = calculate_bird_distance(char_x, char_y, char_z, char_o_x, char_o_y, char_o_z)
            # print(f"{other_character["base"].name}, distance = {distance}")
            if distance <= max_distance:
                    character["base"].active = True
                    break
            if distance <= max_distance*3:
                if has_line_of_sight(char_x, char_y, char_z, char_o_x, char_o_y, char_o_z):
                    character["base"].active = True
                    break


def handle_ai_action(game_state, bot_left_log, character_ai_decision_tree):
    while True:
        game_state.selected_character = game_state.non_player_characters[game_state.current_npc_index]
        if not game_state.selected_character["base"].active:
            game_state.current_npc_index += 1

        else:
            if game_state.selected_character["base"].actions_left > 0:
                character_ai_decision_tree(game_state, bot_left_log)
                return
            else:
                game_state.current_npc_index += 1

        if game_state.current_npc_index >= len(game_state.non_player_characters):
                    start_turn(game_state, bot_left_log)
                    return


def remove_tile_entity(character):
    x, y, z = character["logic"].pos_x, character["logic"].pos_y, character["logic"].pos_z

    game_state.maps[Z_DEFAULT+z][LOGIC_TILES_INDEX][x, y].entities.remove(character["logic"]) # Remove the character from the current tile's contents
    game_state.maps[Z_DEFAULT+z][LOGIC_TILES_INDEX][x, y].passable = True

    game_state.maps[Z_DEFAULT+z][MAP_ARRAY_INDEX][x, y] = 1


def get_tile_under_cursor(game_state):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    logic_x = (mouse_x + game_state.camera_x) //TILE_SIZE
    logic_y = (mouse_y + game_state.camera_y) //TILE_SIZE
    logic_z = game_state.z_level
    return logic_x, logic_y, logic_z


def has_line_of_sight(x1, y1, z1, x2, y2, z2):
    """Makes sure there's unobstructed line of sight between the 2 points."""
    points = bresenham_line_3d(x1, y1, z1, x2, y2, z2)
    for i in range(1, len(points) - 1): # Skip the start and end points
        X, Y, Z = 0, 1, 2

        tile = game_state.maps[Z_DEFAULT + points[i][Z]][LOGIC_TILES_INDEX][(points[i][X], points[i][Y])]
        tile_previous = game_state.maps[Z_DEFAULT + points[i-1][Z]][LOGIC_TILES_INDEX][(points[i][X], points[i][Y])]
        
        if points[i][Z] != points[i-1][Z]: # When moving between different z-levels
            if tile_previous.material != "air":
                return False
        else: # When staying on the same z-level
            if not tile.passable:
                return False

    return True


def update_accessible_tiles(game_state):
    game_state.accessible_tiles.clear()
    potentially_accessible_coordinates = list_accessible_tiles(game_state.selected_character)
    # print(f"Potentially accessible tiles: ")
    # print(f"{potentially_accessible_coordinates}")

    for coordinates in potentially_accessible_coordinates:
            x, y, z = coordinates
            if 0 <= x < game_state.map_width and 0 <= y < game_state.map_height:
                game_state.accessible_tiles.add((x, y, z))


def update_weapon_range(character, state=game_state):
    state.weapon_range_tiles.clear()
    character["base"].threatened_tiles.clear()
    
    min_range, max_range = character["base"].selected_hand.item.melee_range
    char_x, char_y, char_z = get_character_coordinates(character)
    
    for i in range(-max_range, max_range + 1):
        for j in range(-max_range, max_range + 1):
            if abs(i) >= min_range or abs(j) >= min_range:
                target_x, target_y = char_x + i, char_y + j
                if 0 <= target_x < state.map_width and 0 <= target_y < state.map_height:
                    if has_line_of_sight(char_x, char_y, char_z, target_x, target_y, char_z):
                        game_state.weapon_range_tiles.add((target_x, target_y, char_z))
                        character["base"].threatened_tiles.append((target_x, target_y, char_z))


def incremental_movement(character, dx, dy):
    "move a character incrementally both on the logic and the graphic board"

    remove_tile_entity(character)

    logic_char = character["logic"]
    game_state.current_map_tiles[logic_char.pos_x+dx, logic_char.pos_y+dy].entities.append(logic_char) # Add the character to the new tile's contents

    character["logic"].update_increment(dx, dy) # Move the character on the logic board
    character["graphic"].update_increment(dx, dy) # Move the character on the graphic board

    game_state.current_map_tiles[logic_char.pos_x+dx, logic_char.pos_y+dy].passable = False
    
    game_state.current_map_tiles[logic_char.pos_x+dx][logic_char.pos_y+dy] = 999


def reposition_movement(character, x, y, z, state = game_state):
    "move a character to a specific location both on the logic and the graphic board"

    remove_tile_entity(character)

    character["logic"].update_reposition(x, y, z) # Move the character on the logic board
    character["graphic"].update_reposition(x, y) # Move the character on the graphic board

    game_state.maps[Z_DEFAULT+z][LOGIC_TILES_INDEX][x, y].entities.append(character["logic"]) # Add the character to the new tile's contents
    game_state.maps[Z_DEFAULT+z][LOGIC_TILES_INDEX][x, y].passable = False
    game_state.maps[Z_DEFAULT+z][MAP_ARRAY_INDEX][x, y] = 999


def character_directional_move(dx, dy, game_state, selection_rectangle):
    x, y, z = get_character_coordinates(game_state.selected_character)
    if game_state.current_map_tiles[x+dx, y+dy].passable and game_state.selected_character["base"].movement_points_left > 0:
        game_state.selected_character["base"].movement_points_left -= 1
        incremental_movement(game_state.selected_character, dx, dy)
        selection_rectangle.update_increment(dx, dy)


def change_active_activity(selected_character, button_index, activity_or_spell):
    if activity_or_spell == "activity":
        if len(selected_character["base"].activities) > button_index:
            selected_character["base"].selected_activity = selected_character["base"].activities[button_index]
            return
    if activity_or_spell == "spell":
        if len(selected_character["base"].spells) > button_index:
            selected_character["base"].selected_activity = selected_character["base"].spells[button_index]
            return
    return


def change_active_weapon(selected_character, hand):
    # "left_hand" or "right_hand"

    if hand == "left_hand":
        selected_character["base"].selected_hand = selected_character["base"].left_hand
    else:
        selected_character["base"].selected_hand = selected_character["base"].right_hand

    selected_character["base"].selected_activity = selected_character["base"].selected_hand


def change_active_attack_type(selected_character, hand, attack_type):
    # "left_hand" or "right_hand"
    if hand == "left_hand":
        selected_character["base"].left_hand.attack_type = attack_type
    if hand == "right_hand":
        selected_character["base"].right_hand.attack_type = attack_type


def flash_for_damage(game_state, screen):
    for character, damage_taken in list(game_state.hit_characters.items()): # List apparently to avoid runtime errors due to iterating over a dict with a different len
        if damage_taken > 30:
            game_state.hit_characters[character] = 30
        if damage_taken > 0:
            damage_alpha = damage_taken * 10
            if damage_alpha > 255:
                damage_alpha = 255
            fill_with_colour_precise(character, RED, damage_alpha)
            game_state.hit_characters[character] -= 1
        else:
            del character


def flash_for_button_activation(game_state, screen):
    for button, duration in list(game_state.buttons_to_flash.items()):
        if duration > 0:
            activation_alpha = duration
            if activation_alpha > 250:
                activation_alpha = 250
            fill_with_colour_button(button, YELLOW, activation_alpha)
            game_state.buttons_to_flash[button] -= 10
        else:
            del button


def flash_for_path_taken(game_state, screen):
    for coordinates in game_state.path_tiles_to_flash:
        if game_state.time_to_flash_path_tiles > 0:
            if coordinates[2] == game_state.z_level:
                activation_alpha = game_state.time_to_flash_path_tiles
                fill_with_colour_imprecise(GREEN, activation_alpha, coordinates, 40, 40)
        else:
            game_state.path_tiles_to_flash.clear()
    game_state.time_to_flash_path_tiles -= 3


def cut_path_based_on_cost(path, max_cost):
    total_cost = 0
    last_possible_tile = None

    for n in range(1, len(path)):
        current_tile = path[n]
        previous_tile = path[n - 1]

        if current_tile[0] != previous_tile[0] and current_tile[1] != previous_tile[1]:
            step_cost = 1.5
        else:
            step_cost = 1

        if total_cost + step_cost <= max_cost:
            total_cost += step_cost
            last_possible_tile = current_tile
        else:
            break

    return last_possible_tile, total_cost


def get_cost_from_path(game_state):
    total_cost = 0
    for n in range(1, len(game_state.path_tiles)):
        if game_state.path_tiles[n][0] != game_state.path_tiles[n-1][0] and game_state.path_tiles[n][1] != game_state.path_tiles[n-1][1]:
            total_cost += 1.5
        else: 
            total_cost += 1
    return total_cost


def find_path(start_tile, end_tile, state = game_state):
    # print("find_path function initialized.")
    # print(f"Looking for path from {start_tile} to {end_tile}")
    state.path_tiles.clear()
    x1, y1, z1 = start_tile
    x2, y2, z2 = end_tile
    path = []

    # Perform 2D A* pathfinding
    array_path = pyastar2d.astar_path(state.maps[Z_DEFAULT + z1][MAP_ARRAY_INDEX], (x1, y1), (x2, y2), True)
    # print(f"Array path: {array_path}")
    for coordinates in array_path:  # type: ignore
        coordinates_tuple = tuple(map(int, coordinates))
        # If the tile we're looking at is not the origin tile and yet it's also unpassable, we clear the path and break
        if state.maps[Z_DEFAULT + z1][LOGIC_TILES_INDEX][coordinates_tuple] != state.maps[Z_DEFAULT + z1][LOGIC_TILES_INDEX][x1, y1] and not state.maps[Z_DEFAULT + z1][LOGIC_TILES_INDEX][coordinates_tuple].passable:
            state.path_tiles.clear()
            break
        path.append(coordinates_tuple + (z1,))
    state.path_tiles = path.copy()
    cost = get_cost_from_path(state)
    # print(f"Path: {path}, Cost: {cost}")
    # print("find_path function ended.")
    return path, cost


def determine_path(target_tile, state = game_state):
    # print("determine_path function initialized.")
    state.path_tiles.clear()
    x1, y1, z1 = get_character_coordinates(state.selected_character)
    x2, y2, z2 = target_tile

    if not state.maps[Z_DEFAULT+z2][LOGIC_TILES_INDEX][x2, y2].passable:
        return [], 0

    if z1 == z2:
        # print("Basic path identified and dealt with.")
        # print("determine_path function ended.")
        return find_path((x1, y1, z1), (x2, y2, z2))

    path = []
    total_cost = 0
    current_tile = (x1, y1, z1)
    
    while current_tile[2] != z2:
        # print(f"Complex path identified.")
        if current_tile[2] < z2:
            # print(f"We need to go up.")
            stairs_list = state.stairs_up_positions[Z_DEFAULT+current_tile[2]]
            next_level = current_tile[2] + 1
        else:
            # print(f"We need to go down.")
            stairs_list = state.stairs_down_positions[Z_DEFAULT+current_tile[2]]
            next_level = current_tile[2] - 1

        if not stairs_list:
            return [], 0  # No stairs available

        nearest_stairs = None
        nearest_cost = float('inf')
        for stairs in stairs_list:
            stairs_tile = (stairs[0], stairs[1], current_tile[2])
            # print(f"Stairs identified: {stairs_tile}")
            partial_path, partial_cost = find_path(current_tile, stairs_tile)
            # print(f"Path to stairs: {partial_path}")
            # print(f"Cost to stairs: {partial_cost}")
            if partial_cost < nearest_cost:
                nearest_stairs = stairs_tile
                nearest_cost = partial_cost

        if nearest_stairs is None:
            # print(f"No compatible stairs found.")
            # print("determine_path function ended.")
            return [], 0  # No valid path to stairs

        path.extend(partial_path)
        total_cost += nearest_cost
        # print(f"Current cost total: {partial_cost}")
        current_tile = (nearest_stairs[0], nearest_stairs[1], next_level)
        # print(f"New current tile to start next path part from: {current_tile}")
        path.append(current_tile)  # Add transition to the next level
        total_cost += 1  # Cost for moving to the next level

    # Final segment to the target on the destination level
    # print(f"We have reached the target z-level.")
    final_path, final_cost = find_path(current_tile, target_tile)
    # print(f"Path to stairs: {final_path}")
    # print(f"Cost to stairs: {final_cost}")
    path.extend(final_path)
    total_cost += final_cost
    # print(f"Cost total: {total_cost}")
    # print(f"Complete path: {path}")
    # print("determine_path function ended.")

    state.path_tiles.clear()
    state.path_tiles = path.copy()
    return path, total_cost


def get_tiles_at_distance(game_state, x, y, z, n):
    "returns a list of all tiles at chosen distance from target tile at x, y coordinates"
    coordinates = set()
    
    for dx in range(-n, n + 1):
        dy = n - abs(dx)
        
        # Calculate potential coordinates
        coord1 = (x + dx, y + dy)
        coord2 = (x + dx, y - dy)
        
        # Add coordinates only if they are within bounds and have line of sight
        if 0 <= coord1[0] < game_state.map_width and 0 <= coord1[1] < game_state.map_height:
            if has_line_of_sight( x, y, z, coord1[0], coord1[1], z):
                coordinates.add(coord1)
        if dy != 0 and 0 <= coord2[0] < game_state.map_width and 0 <= coord2[1] < game_state.map_height:
            if has_line_of_sight(x, y, z, coord2[0], coord2[1], z):
                coordinates.add(coord2)
    
    return list(coordinates)


def activating_noise(game_state, tile, multiplier = 1):
    x1, y1, z1 = tile
    for character in game_state.all_characters:
        x2, y2, z2 = get_character_coordinates(character)
        distance = calculate_bird_distance(x1, y1, z1, x2, y2, z2)
        if distance <= (character["base"].final_sense*multiplier) and not character["base"].active:
            character["base"].active = True

