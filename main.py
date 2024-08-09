
import sys, pygame, pygame_widgets, time
from pygame_widgets.button import Button
import numpy as np
import os

# sys.path.append('/Andimarium_Arena')

# get the current working directory
current_working_directory = os.getcwd()

# print output to the console
print(f"/ / /")
print(f"/ / /")
print(f"/ / /")
print(current_working_directory)

from interface import *
from archetypes import *

if debug:
    print()
    print(f"Program by Antoine Margoloff under CC BY-NC 4.0 License")
    print(f"Character sprites modified from tools.2minutetabletop.com under CC BY-NC 4.0 License")
    print()
    print(f"Map width: {game_state.map_width} tiles")
    print(f"map height: {game_state.map_height} tiles")
    print()
    print(f"Game board width: {game_state.map_width * TILE_SIZE} pixels")
    print(f"Game board height: {game_state.map_height * TILE_SIZE} pixels")
    print()
    print(f"Screen size: {game_state.window_width}x{game_state.window_height} (pixels)")
    print()


game_state.load_level(0)


# swordsman_A = Character("Swordsman A", 12, medium, [8, 8, 7, 7], r"graphics/characters/etherealsoldier.png", True)
# swordsman_A.add_items([items["poleaxe"], items["medium_armour"]])
# swordsman_A.equip_items([items["poleaxe"], items["medium_armour"]])
# swordsman_A = add_character_to_location(swordsman_A, 12, 10)

# swordsman_A = Character("Swordsman A", 12, medium, [7, 7, 9, 6], r"graphics/characters/etherealsoldier.png", True)
# # swordsman_A.add_items([items["bow"], items["medium_armour"]])
# # swordsman_A.equip_items([items["bow"], items["medium_armour"]])
# swordsman_A.add_items([items["poleaxe"], items["medium_armour"]])
# swordsman_A.equip_items([items["poleaxe"], items["medium_armour"]])
# swordsman_A = add_character_to_location(swordsman_A, 12, 10)
# swordsman_A["base"].archetype = "paragon"

swordsman_A = Character("Swordsman A", 12, medium, [5, 6, 6, 10], r"assets/graphics/characters/etherealsoldier.png", True)
swordsman_A.add_items([items["straightsword"], items["medium_shield"], items["medium_armour"]])
swordsman_A.equip_items([items["straightsword"], items["medium_shield"], items["medium_armour"]])
swordsman_A = add_character_to_location(swordsman_A, 12, 10)
swordsman_A["base"].archetype = "mage"


swordsman_B = Character("Swordsman B", 12, medium, [8, 8, 7, 7], r"assets/graphics/characters/ashenknight1.png")
swordsman_B.add_items([items["straightsword"], items["medium_shield"], items["medium_armour"]])
swordsman_B.equip_items([items["straightsword"], items["medium_shield"], items["medium_armour"]])
swordsman_B = add_character_to_location(swordsman_B, 5, 7)
swordsman_B["base"].archetype = "mage"

# swordsman_C = Character("Swordsman C", 6, medium, [8, 8, 7, 7], r"graphics/charC.png")
# swordsman_C.add_items([items["greatsword"], items["medium_armour"]])
# swordsman_C.equip_items([items["greatsword"], items["medium_armour"]])
# swordsman_C = add_character_to_location(swordsman_C, 5, 5)

swordsman_C = Character("Swordsman C", 12, medium, [8, 8, 7, 7], r"assets/graphics/characters/ashenwarrior1.png")
swordsman_C.add_items([items["bow"], items["medium_armour"]])
swordsman_C.equip_items([items["bow"], items["medium_armour"]])
swordsman_C = add_character_to_location(swordsman_C, 5, 5)

# swordsman_A["base"].add_activity(example_power_activity)
# swordsman_A["base"].add_spell(example_spell_activity)
swordsman_B_AoO = AttackOfOpportunity(swordsman_B)
swordsman_B["base"].reactions.append(swordsman_B_AoO)

swordsman_B["base"].hostile.append(swordsman_A)
swordsman_C["base"].hostile.append(swordsman_A)

game_state.all_characters += swordsman_A, swordsman_B, swordsman_C


for character in game_state.all_characters:
    if character["base"].player:
        game_state.player_characters.append(character)
    else:
        game_state.non_player_characters.append(character)

for character in game_state.all_characters:
    game_state.selected_character = character
    character["base"].initialisation(default_activites, update_weapon_range)

if game_state.player_characters:
    game_state.selected_character = game_state.player_characters[0]
else:
    game_state.selected_character = game_state.all_characters[0]

for reaction in swordsman_B["base"].reactions:
    game_state.reaction_tracker.add(reaction)

left_hand_weapon_button = WeaponButton(game_state, "left_hand", "weapon_pos_1")
right_hand_weapon_button = WeaponButton(game_state, "right_hand", "weapon_pos_2")

left_crush_button = AttackTypeButton(game_state, "left_hand", damage_crushing, r"assets/graphics/interface/base/crush.png", "at_type_left_pos_1")
left_slash_button = AttackTypeButton(game_state, "left_hand", damage_slashing, r"assets/graphics/interface/base/slash.png", "at_type_left_pos_2")
left_pierce_button = AttackTypeButton(game_state, "left_hand", damage_piercing, r"assets/graphics/interface/base/pierce.png", "at_type_left_pos_3")

right_crush_button = AttackTypeButton(game_state, "right_hand", damage_crushing, r"assets/graphics/interface/base/crush.png", "at_type_right_pos_1")
right_slash_button = AttackTypeButton(game_state, "right_hand", damage_slashing, r"assets/graphics/interface/base/slash.png", "at_type_right_pos_2")
right_pierce_button = AttackTypeButton(game_state, "right_hand", damage_piercing, r"assets/graphics/interface/base/pierce.png", "at_type_right_pos_3")

activity_1_button = ActivityButton(game_state, "activity_1")
activity_2_button = ActivityButton(game_state, "activity_2")
activity_3_button = ActivityButton(game_state, "activity_3")
activity_4_button = ActivityButton(game_state, "activity_4")
activity_5_button = ActivityButton(game_state, "activity_5")
activity_6_button = ActivityButton(game_state, "activity_6")
activity_7_button = ActivityButton(game_state, "activity_7")
activity_8_button = ActivityButton(game_state, "activity_8")
activity_9_button = ActivityButton(game_state, "activity_9")
activity_10_button = ActivityButton(game_state, "activity_10")

power_tier_1_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_1.png", "power_tier_1", 1)
power_tier_2_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_2.png", "power_tier_2", 2)
power_tier_3_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_3.png", "power_tier_3", 3)
power_tier_4_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_4.png", "power_tier_4", 4)
power_tier_5_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_5.png", "power_tier_5", 5)
power_tier_6_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_6.png", "power_tier_6", 6)
power_tier_7_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_7.png", "power_tier_7", 7)
power_tier_8_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_8.png", "power_tier_8", 8)
power_tier_9_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_9.png", "power_tier_9", 9)
power_tier_10_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_10.png", "power_tier_10", 10)
power_tier_11_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_11.png", "power_tier_11", 11)
power_tier_12_button = PowerTierButton(game_state, r"assets/graphics/interface/base/power_tier_12.png", "power_tier_12", 12)

spell_1_button = SpellButton(game_state, "spell_1")
spell_2_button = SpellButton(game_state, "spell_2")
spell_3_button = SpellButton(game_state, "spell_3")
spell_4_button = SpellButton(game_state, "spell_4")
spell_5_button = SpellButton(game_state, "spell_5")
spell_6_button = SpellButton(game_state, "spell_6")
spell_7_button = SpellButton(game_state, "spell_7")
spell_8_button = SpellButton(game_state, "spell_8")
spell_9_button = SpellButton(game_state, "spell_9")
spell_10_button = SpellButton(game_state, "spell_10")

weapon_buttons = [left_hand_weapon_button, right_hand_weapon_button]

attack_buttons = [left_crush_button, left_slash_button, left_pierce_button,
           right_crush_button, right_slash_button, right_pierce_button]

activity_buttons = [activity_1_button, activity_2_button, activity_3_button,
           activity_4_button, activity_5_button, activity_6_button,
           activity_7_button, activity_8_button, activity_9_button,
           activity_10_button]

power_tier_buttons = [power_tier_1_button, power_tier_2_button, power_tier_3_button, power_tier_4_button, power_tier_5_button, power_tier_6_button,
                      power_tier_7_button, power_tier_8_button, power_tier_9_button, power_tier_10_button, power_tier_11_button, power_tier_12_button]

spell_buttons = [spell_1_button, spell_2_button, spell_3_button, spell_4_button, spell_5_button,
                 spell_6_button, spell_7_button, spell_8_button, spell_9_button, spell_10_button]

all_buttons = weapon_buttons + attack_buttons + activity_buttons + power_tier_buttons + spell_buttons

key_mapping = {
    pygame.K_1: 0,
    pygame.K_2: 1,
    pygame.K_3: 2,
    pygame.K_4: 3,
    pygame.K_5: 4,
    pygame.K_6: 5,
    pygame.K_7: 6,
    pygame.K_8: 7,
    pygame.K_9: 8,
    pygame.K_0: 9,
    41: 10,
    61: 11
    }

for button in activity_buttons + spell_buttons:
    button.update_for_new_character(game_state)


char_selection_rectangle = CharacterSelectionRectangle(game_state)
previously_select_rectangle = OldActivitySelectorRect(all_buttons, FADED_YELLOW)
activity_select_rectangle = ActivitySelectorRect(all_buttons, YELLOW)
left_attack_type_select_rectangle = AttackTypeSelectorRect(game_state, "left", left_crush_button, left_slash_button, left_pierce_button)
right_attack_type_select_rectangle = AttackTypeSelectorRect(game_state, "right", right_crush_button, right_slash_button, right_pierce_button)
power_tier_select_rectangle = PowerTierSelectorRect(power_tier_buttons, YELLOW)

while running:

    events = pygame.event.get()
    screen.fill(BLACK)

    if game_state.tick_counter == 0:
        # game_state.load_level(0)
        find_stairs()
        game_state.interface_update_needed = True
        game_state.update_positions()

    # graphic_tiles.draw(screen)

    for tile in game_state.current_map_graphics:
        adjusted_rect = tile.rect.move(-game_state.camera_x, -game_state.camera_y)
        if screen.get_rect().colliderect(adjusted_rect):
            screen.blit(tile.image, adjusted_rect)

    if graphic_effects:
        for sprite in graphic_effects:
            adjusted_rect = sprite.rect.move(-game_state.camera_x, -game_state.camera_y)
            if screen.get_rect().colliderect(adjusted_rect):
                screen.blit(sprite.image, adjusted_rect)

    for character in game_state.all_characters:
        if character["logic"].pos_z == game_state.z_level:
            adjusted_char_rect = character["graphic"].rect.move(-game_state.camera_x, -game_state.camera_y)
            screen.blit(character["graphic"].image, adjusted_char_rect)
        if character["base"].current_health_points <= 0:
            fill_with_colour_precise(character["graphic"], RED, ALPHA120)

    if game_state.show_accessible_tiles and (game_state.selected_character["base"].player or debug):
        for tile in game_state.accessible_tiles:
            if tile[2] == game_state.z_level: # Making sure we're on the same z level
                screen.blit(accessible_tile_graphic, ((tile[0]*TILE_SIZE) - game_state.camera_x, (tile[1]*TILE_SIZE) - game_state.camera_y))

    if game_state.show_weapon_range and (game_state.selected_character["base"].player or debug):
        for tile in game_state.weapon_range_tiles:
            if tile[2] == game_state.z_level: # Making sure we're on the same z level
                screen.blit(weapon_range_graphic, ((tile[0]*TILE_SIZE) - game_state.camera_x, (tile[1]*TILE_SIZE) - game_state.camera_y))

    if game_state.show_path:
        for tile in game_state.path_tiles:
            if tile[2] == game_state.z_level: # Making sure we're on the same z level
                screen.blit(path_tile_graphic, ((tile[0]*TILE_SIZE) - game_state.camera_x, (tile[1]*TILE_SIZE) - game_state.camera_y))

    if game_state.show_healthbars:
        for character in game_state.all_characters:
            draw_health_bar(screen, character, game_state)
        
    if game_state.show_interface:
        screen.blit(bottom_interface, (0, game_state.window_height-200))
        if game_state.selected_character["logic"].pos_z == game_state.z_level:
            char_selection_rectangle.draw_rect(screen)

        # Making it so we can see health & vigour of characters even if they don't belong to us
        interface_health.blit(screen)
        interface_vigour.blit(screen)

        if game_state.ai_turn_in_progress == False:
            end_turn_button = Button(
                screen, game_state.window_width-120, game_state.window_height-160, 110, 50, text='End turn',
                fontSize=15, margin=10,
                inactiveColour=(220, 220, 220),
                pressedColour=(255, 255, 255), radius=10,
                onClick=lambda: end_turn(game_state))

            pygame_widgets.update(events)

            if (game_state.selected_character and game_state.selected_character["base"].player) or debug:
                interface_actions.blit(screen)
                interface_movement_pts.blit(screen)
                # interface_health.blit(screen)
                # interface_vigour.blit(screen)
                interface_power.blit(game_state, screen)
                for button in all_buttons:
                    button.draw(game_state, screen)
                previously_select_rectangle.draw(screen)
                activity_select_rectangle.draw(screen)
                left_attack_type_select_rectangle.draw(screen)
                right_attack_type_select_rectangle.draw(screen)
                power_tier_select_rectangle.draw(game_state, screen)

    if game_state.ai_turn_in_progress and game_state.last_AI_action_tick >= 30:
        handle_ai_action(game_state, bot_left_log, character_ai_decision_tree)
        game_state.interface_update_needed = True
        game_state.last_AI_action_tick = 0

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            game_state.window_width, game_state.window_height = event.size
            screen = pygame.display.set_mode((game_state.window_width, game_state.window_height), pygame.RESIZABLE)
            game_state.update_positions()
            game_state.interface_update_needed = True
            
        if game_state.show_interface:
            left_hand_weapon_button.activate_on_click(event, game_state, change_active_weapon)
            right_hand_weapon_button.activate_on_click(event, game_state, change_active_weapon)

            for button in attack_buttons:
                if button.hand == "left_hand":
                    button.activate_on_click(event, game_state, change_active_attack_type)
                elif button.hand == "right_hand":
                    button.activate_on_click(event, game_state, change_active_attack_type)
            for button in activity_buttons: 
                button.activate_on_click(event, game_state, activity_buttons.index(button), change_active_activity)
            for button in power_tier_buttons:
                button.activate_on_click(event, game_state)
            for button in spell_buttons:
                button.activate_on_click(event, game_state, spell_buttons.index(button), change_active_activity)

        # Gameplay shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                end_turn()
            if event.key == pygame.K_F1:
                if game_state.show_accessible_tiles == False:
                    game_state.show_accessible_tiles = True
                else:
                    game_state.show_accessible_tiles = False

            if event.key == pygame.K_F2:
                if game_state.show_weapon_range == False:
                    update_weapon_range(game_state.selected_character)
                    game_state.show_weapon_range = True
                else:
                    game_state.show_weapon_range = False

            if event.key == pygame.K_F4:
                if game_state.show_interface == True:
                    game_state.show_interface = False
                else:
                    game_state.show_interface = True

            if event.key == pygame.K_PAGEUP:
                new_z_level = game_state.z_level + 1
                if game_state.maps[Z_DEFAULT+new_z_level][ADDRESS_INDEX]:
                    game_state.load_level(new_z_level)

            if event.key == pygame.K_PAGEDOWN:
                new_z_level = game_state.z_level - 1
                if game_state.maps[Z_DEFAULT+new_z_level][ADDRESS_INDEX]:
                    game_state.load_level(new_z_level)

            if event.key == 178:
                if game_state.selected_character["base"].selected_hand == game_state.selected_character["base"].right_hand:
                    game_state.selected_character["base"].selected_hand = game_state.selected_character["base"].left_hand
                    game_state.selected_character["base"].selected_activity = game_state.selected_character["base"].left_hand
                else:
                    game_state.selected_character["base"].selected_hand = game_state.selected_character["base"].right_hand
                    game_state.selected_character["base"].selected_activity = game_state.selected_character["base"].right_hand
                game_state.interface_update_needed = True

            if event.key in key_mapping: # Activity hotkeys
                n = key_mapping[event.key]
                if len(game_state.selected_character["base"].activities) > n:
                    if game_state.selected_character["base"].activities[n].immediate_effect == True:
                        game_state.selected_character["base"].activities[n].perform(game_state, bot_left_log)
                        game_state.buttons_to_flash[activity_buttons[n]] = 255
                    else:
                        game_state.selected_character["base"].selected_activity = game_state.selected_character["base"].activities[n]
                    game_state.interface_update_needed = True

        # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state.player_control == True:
        #         mouse_x, mouse_y = pygame.mouse.get_pos()
        #         if (mouse_y < (game_state.window_height-200) and game_state.show_interface) or (not game_state.show_interface):
        #             x, y, z = get_tile_under_cursor(game_state)
        #             for element in game_state.current_map_tiles[x, y].entities:
        #                 if isinstance(element, LogicCharacter):
        #                     if element.parent_dict["base"].player or debug:
        #                         game_state.selected_character = element.parent_dict
        #                         game_state.interface_update_needed = True


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (game_state.player_control or debug):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (mouse_y < (game_state.window_height-200) and game_state.show_interface) or (not game_state.show_interface):
                    x, y, z = get_tile_under_cursor(game_state)
                    for element in game_state.current_map_tiles[x, y].entities:
                        if isinstance(element, LogicCharacter):
                            game_state.selected_character = element.parent_dict
                            game_state.interface_update_needed = True


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and (game_state.player_control or debug):
                if game_state.selected_character["base"].current_health_points > 0:
                    x2, y2, z2 = get_tile_under_cursor(game_state)
                    game_state.targeted_tile = (x2, y2, z2) 
                    for entity in game_state.current_map_tiles[x2, y2].entities:
                        if isinstance(entity, LogicCharacter):
                            game_state.targeted_character = entity.parent_dict
                    
                    if game_state.targeted_character:
                        if isinstance(game_state.selected_character["base"].selected_activity, ActiveInHand): # Weapon activity selected
                            game_state.selected_character["base"].selected_activity.item.activity.perform()
                        else: # Any other activity selected
                            game_state.selected_character["base"].selected_activity.perform()

                        game_state.targeted_character = None
                    else:
                        move_activity.move_to_location((x2, y2, game_state.z_level))
                else: 
                    bot_left_log.add_message(f"You are unconscious and therefore unable to act!")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if game_state.show_interface and 0 <= mouse_x <= LOG_WIDTH and game_state.window_height-200 <= mouse_y <= game_state.window_height:
                bot_left_log.go_up_in_log()
                bottom_interface = bot_left_log.update(bottom_interface, game_state)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if game_state.show_interface and 0 <= mouse_x <= LOG_WIDTH and game_state.window_height-200 <= mouse_y <= game_state.window_height:
                bot_left_log.go_down_in_log()
                bottom_interface = bot_left_log.update(bottom_interface, game_state)

        # Debug commands
        if debug:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    breakpoint()

                if event.key == pygame.K_t:
                    print(f"{game_state.camera_x}, {game_state.camera_y}")

                if event.key == pygame.K_y:
                    print(f"{game_state.window_width} x {game_state.window_height}")

                if event.key == pygame.K_w:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    logic_x = (mouse_x + game_state.camera_x) //TILE_SIZE
                    logic_y = (mouse_y + game_state.camera_y) //TILE_SIZE

                    if game_state.current_map_tiles[logic_x, logic_y].passable:
                        reposition_movement(game_state.selected_character, logic_x, logic_y, game_state.z_level)
                        game_state.interface_update_needed = True

                if event.key == pygame.K_o:
                    bot_left_log.add_message(f"All that is gold does not glitter, not all those who wander are lost; the old that is strong does not wither, deep roots are not reached by the frost.")

                if event.key == pygame.K_p:
                    bot_left_log.add_message(f"{game_state.accessible_tiles}")

                if event.key == pygame.K_u:
                    bot_left_log.add_message(f"{game_state.selected_character["base"].body}")

                if event.key == pygame.K_m:
                    bot_left_log.add_message(f"Stairs up:")
                    bot_left_log.add_message(f"{game_state.stairs_up_positions}")
                    bot_left_log.add_message(f"Stairs down:")
                    bot_left_log.add_message(f"{game_state.stairs_down_positions}")

                if event.key == pygame.K_n:
                    # bot_left_log.add_message(f"Currently selected power tier: {game_state.selected_character["base"].selected_power_tier}")
                    bot_left_log.add_message(f"{game_state.selected_character["base"].left_hand}")
                    bot_left_log.add_message(f"{game_state.selected_character["base"].right_hand}")

                if event.key == pygame.K_i:
                    bot_left_log.add_message(f"{game_state.selected_character["base"].name} HP:{game_state.selected_character["base"].current_health_points} Defence: {game_state.selected_character["base"].final_melee_defence}, {game_state.selected_character["base"].final_ranged_defence}") 

                if event.key == pygame.K_j:
                    bot_left_log.add_message(f"Character's board tile position: {swordsman_A["logic"].pos_x}, {swordsman_A["logic"].pos_y}") 

                if event.key == pygame.K_h:
                    bot_left_log.add_message(f"camera_x: {game_state.camera_x}, camera_y: {game_state.camera_y}") 

                if event.key == pygame.K_c:
                    bot_left_log.log.clear()
                    bot_left_log.log_new.clear()
                    bot_left_log.log_old.clear()
                    bot_left_log.message_added = True

                if event.key == pygame.K_k:
                    bot_left_log.add_message(f"Character's board pixel position: {swordsman_A["graphic"].rect.x}, {swordsman_A["graphic"].rect.y}") 

                if event.key == pygame.K_l:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    board_x = (mouse_x + game_state.camera_x)
                    board_y = (mouse_y + game_state.camera_y)
                    bot_left_log.add_message(f"screen_x: {mouse_x}, screen_y: {mouse_y}     board_x: {board_x}, board_y: {board_y}") 
                    
                if event.key == pygame.K_x:
                    x, y, z = get_tile_under_cursor(game_state)
                    bot_left_log.add_message(f"{game_state.current_map_tiles[x, y]}") 

                if event.key == pygame.K_g:
                    x, y, z = get_tile_under_cursor(game_state)
                    coordinates_n = ""
                    
                    if not os.path.exists("coordinates.txt"):
                        open("coordinates.txt", 'w').close()
                    
                    with open("coordinates.txt", 'r+') as f:
                        lines = f.readlines()
                        
                        if lines:
                            last_line = lines[-1]
                            for char in last_line[::-1]:
                                if char.isdigit():
                                    coordinates_n += char
                                if char == "-":
                                    break
                            coordinates_n = int(coordinates_n[::-1]) + 1
                        else: coordinates_n = 1
                        
                        f.write(f"({x}, {y}, {z}) - {coordinates_n}\n")
                        bot_left_log.add_message(f"Coordinates logged (n°{coordinates_n}).") 

                if event.key == pygame.K_v:
                    x, y, z = get_tile_under_cursor(game_state)
                    if game_state.path_tiles and game_state.path_tiles[-1] == (x, y, z):
                        game_state.path_tiles.clear()
                        game_state.show_path = False
                    else:
                        path, cost = determine_path((x, y, z))
                        bot_left_log.add_message(f"Path found. Cost: {cost}")
                        game_state.show_path = True


    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        exit()

    # Camera movement
    if keys[pygame.K_LEFT]:
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if game_state.camera_x - SCROLL_SPEED*2 >= 0:
                game_state.camera_x -= SCROLL_SPEED*2
        else:
            if game_state.camera_x - SCROLL_SPEED >= 0:
                game_state.camera_x -= SCROLL_SPEED
    if keys[pygame.K_RIGHT]:
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if game_state.camera_x + SCROLL_SPEED*2 <= (TILE_SIZE * game_state.map_width)-game_state.window_width:
                game_state.camera_x += SCROLL_SPEED*2
        else:
            if game_state.camera_x + SCROLL_SPEED <= (TILE_SIZE * game_state.map_width)-game_state.window_width:
                game_state.camera_x += SCROLL_SPEED
    if keys[pygame.K_UP]:
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if game_state.camera_y - SCROLL_SPEED*2 >= 0:
                game_state.camera_y -= SCROLL_SPEED*2
        else:
            if game_state.camera_y - SCROLL_SPEED >= 0:
                game_state.camera_y -= SCROLL_SPEED
    if keys[pygame.K_DOWN]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if game_state.camera_y + SCROLL_SPEED*2 <= (TILE_SIZE * game_state.map_height)-game_state.window_height:
                    game_state.camera_y += SCROLL_SPEED*2
            else:
                if game_state.camera_y + SCROLL_SPEED <= (TILE_SIZE * game_state.map_height)-game_state.window_height:
                    game_state.camera_y += SCROLL_SPEED


    if game_state.hit_characters:
        flash_for_damage(game_state, screen)

    if game_state.path_tiles_to_flash:
        flash_for_path_taken(game_state, screen)

    if game_state.buttons_to_flash:
        flash_for_button_activation(game_state, screen)
    
    char_selection_rectangle.update(game_state)
    bottom_interface = bot_left_log.make_update_if_needed(bottom_interface, game_state)

    if graphic_effects:
        graphic_effects.update()

    if game_state.interface_update_needed:
        # Re-build the interface (potentially according to the new window size)
        bottom_interface = bot_left_log.update(bottom_interface, game_state)
        bot_left_log.display_log(font, bottom_interface)

        interface_actions.update(game_state)
        interface_movement_pts.update(game_state)
        interface_health.update(game_state)
        interface_vigour.update(game_state)
        interface_power.update(game_state)

        update_accessible_tiles(game_state)
        update_weapon_range(game_state.selected_character)

        for button in all_buttons:
            button.update(game_state)

        char_selection_rectangle.update(game_state)
        activity_select_rectangle.update(game_state, weapon_buttons, activity_buttons, spell_buttons)
        previously_select_rectangle.update(game_state, all_buttons)
        left_attack_type_select_rectangle.update(game_state, left_crush_button, left_slash_button, left_pierce_button)
        right_attack_type_select_rectangle.update(game_state, right_crush_button, right_slash_button, right_pierce_button)
        power_tier_select_rectangle.update(game_state, power_tier_buttons)

        bottom_interface = bot_left_log.update(bottom_interface, game_state)
        previously_select_rectangle.update(game_state, all_buttons)

        for button in weapon_buttons:
            button.update_for_new_character(game_state)

        for button in activity_buttons:
            button.update_for_new_character(game_state)

        for button in spell_buttons:
            button.update_for_new_character(game_state)

        game_state.interface_update_needed = False

    pygame.display.flip()
    game_state.tick_counter += 1
    game_state.last_AI_action_tick += 1
    clock.tick(60)

pygame.quit()

