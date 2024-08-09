from random import randint
import time

from game_graphics import *
from computer_ai import *
# from logic_graphics_merge import *


class log_interface:
    def __init__(self) -> None:
        self.log = [] # List to store log messages
        self.log_old = [] # List to store old log messages (when visible log overfills)
        self.log_new = [] # List to store new log messages (when we're currently looking at old messages)
        self.message_added = False # Used to make sure the program doesn't blit the log more than necessary

        self.message_height = 12 # Define the height for each message rectangle
        self.text_y = 184  # How far down we start blitting the messages

    def wrap_text(self, message):
        lines = []
        words = message.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word # Render the current line with the new word added
            rendered_line = font.render(test_line, True, (255, 255, 255))
            
            if rendered_line.get_width() <= LOG_WIDTH:  # We check if the line with the new word added still fits
                current_line = test_line # It does fit, so the word becomes part of the current line
            else:
                lines.append(current_line) # It doesn't fit, so the current line is finalized
                current_line = word # Start a new line with the current word
        
        if current_line: # No more words, so we add the current line as the final line
            lines.append(current_line)
        
        return lines

    def add_message(self, message):
        lines = self.wrap_text(message)
        for line in lines:
            if not self.log_new:
                self.log.append(line)

                if len(self.log) > LOG_SIZE:
                    message = self.log.pop(0)
                    if len(self.log_old) <= OLD_LOG_SIZE:
                        self.log_old.append(message)
            else:
                self.log_new.insert(0, line)

        self.message_added = True
        return
    
    def go_up_in_log(self):
        if self.log_old:
            message = self.log.pop(-1)
            self.log_new.append(message)
            message = self.log_old.pop(-1)
            self.log.insert(0, message)

    def go_down_in_log(self):
        if self.log_new:
            message = self.log.pop(0)
            self.log_old.append(message)
            message = self.log_new.pop(-1)
            self.log.append(message)

    def display_log(self, font, bottom_interface):
        for message in reversed(self.log):
            text_render = font.render(message, True, WHITE)
            
            # Create a surface of fixed height for each message
            message_surface = pygame.Surface((LOG_WIDTH, self.message_height), pygame.SRCALPHA)
            message_surface.fill((0, 0, 0, 0))  # Transparent background
            message_surface.blit(text_render, (0, (self.message_height - text_render.get_height()) // 2))
            
            bottom_interface.blit(message_surface, (10, self.text_y))
            self.text_y -= self.message_height + 4  # Space between lines cumulatively added to each later message in the log
        self.text_y = 184
        return

    def update(self, bottom_interface, game_state):
        bottom_interface = pygame.Surface((game_state.window_width, 200), pygame.SRCALPHA)
        bottom_interface.fill((BLACK[0], BLACK[1], BLACK[2], ALPHA120))
        self.display_log(font, bottom_interface)
        self.message_added = False
        return bottom_interface  # Return the modified bottom_interface

    def make_update_if_needed(self, bottom_interface, game_state):
        if self.message_added == True:
            bottom_interface = self.update(bottom_interface, game_state)
        return bottom_interface  # Return the modified bottom_interface
    
    def roll_message(self, roll_result, att_roll):
        self.add_message(f"{att_roll} has been rolled for a result of {roll_result}...")
    
    def degree_of_success_message(self, degree_of_success):
        self.add_message(f"The attack is a {'critical success!' if degree_of_success == 3 
                                    else 'success.' if degree_of_success == 2 
                                    else 'moderate failure.' if degree_of_success == 1 
                                    else 'critical failure!'}")


bot_left_log = log_interface()


class actions_in_interface:
    def __init__(self, game_state) -> None:
        self.actions = 3

        self.actions_left_text = font2.render(f"Actions left: {self.actions}", True, WHITE)
        self.actions_left_text_rect = self.actions_left_text.get_rect()
        self.actions_left_text_rect.center = (0, 0)

    def update(self, game_state):
        self.actions_left_text_rect.center = game_state.actions_left
        self.actions = game_state.selected_character["base"].actions_left
        self.actions_left_text = font2.render(f"Actions left: {self.actions}", True, WHITE)

    def blit(self, screen):
        screen.blit(self.actions_left_text, self.actions_left_text_rect)


class movement_pts_in_interface:
    def __init__(self, game_state) -> None:
        self.movement = 0

        self.movement_left_text = font2.render(f"Movement left: {self.movement}", True, WHITE)
        self.movement_left_text_rect = self.movement_left_text.get_rect()
        self.movement_left_text_rect.center = (0, 0)

    def update(self, game_state):
        self.movement = game_state.selected_character["base"].movement_points_left
        self.movement_left_text = font2.render(f"Movement left: {self.movement}", True, WHITE)
        self.movement_left_text_rect.center = game_state.movement_left

    def blit(self, screen):
        screen.blit(self.movement_left_text, self.movement_left_text_rect)


class health_in_interface:
    def __init__(self, game_state) -> None:
        self.text = font2.render(f"Health: 0/0", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (0, 0)

    def update(self, game_state):
        current_HP = game_state.selected_character["base"].current_health_points
        max_HP = game_state.selected_character["base"].max_health_points
        temp_HP = game_state.selected_character["base"].current_temp_health_points

        self.text = font2.render(f"Health: {current_HP+temp_HP}/{max_HP}", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.topleft = game_state.health

    def blit(self, screen):
        screen.blit(self.text, self.text_rect)


class vigour_in_interface:
    def __init__(self, game_state) -> None:
        self.text = font2.render(f"Vigour: ", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (0, 0)

    def update(self, game_state):
        vigour = game_state.selected_character["base"].vigour

        self.text = font2.render(f"Vigour: {vigour}", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.topleft = game_state.vigour

    def blit(self, screen):
        screen.blit(self.text, self.text_rect)


class power_points_in_interface:
    def __init__(self, game_state) -> None:
        self.text = font2.render(f"Power: ", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (0, 0)

    def update(self, game_state):
        power_current = game_state.selected_character["base"].power_pool_current
        power_max = game_state.selected_character["base"].power_pool_max

        self.text = font2.render(f"Power: {power_current}/{power_max}", True, WHITE)
        self.text_rect = self.text.get_rect()
        self.text_rect.topleft = game_state.power

    def blit(self, game_state, screen):
        if game_state.selected_character["base"].max_power_tier_available > 0:
            screen.blit(self.text, self.text_rect)


class WeaponButton:
    def __init__(self, game_state, hand, position_key):
        self.selected_character = game_state.selected_character
        self.hand = hand # "left_hand" or "right_hand"
        self.position_key = position_key

        character = game_state.selected_character["base"]
        self.image_path = getattr(character, self.hand).item.sprite
        
        self.image = pygame.image.load(self.image_path)
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))

    def draw(self, game_state, screen):
        screen.blit(self.image, self.rect)

    def update(self, game_state):
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))

    def activate_on_click(self, event, game_state, function):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                function(game_state.selected_character, self.hand)
                game_state.interface_update_needed = True

    def update_for_new_character(self, gamestate):
        character = gamestate.selected_character["base"]
        self.image_path = getattr(character, self.hand).item.sprite
        
        self.image = pygame.image.load(self.image_path)


class AttackTypeButton:
    def __init__(self, game_state, hand, attack_type, sprite, position_key):
        self.selected_character = game_state.selected_character
        self.hand = hand # "left_hand" or "right_hand"
        self.attack_type = attack_type
        self.active = False
        self.position_key = position_key
        
        self.image = pygame.image.load(sprite)
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))

    def draw(self, game_state, screen):
        screen.blit(self.image, self.rect)
        if self.active == False:
            screen.blit(fill_black_40_20x, (self.rect))

    def update(self, game_state):
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))

        self.selected_character = game_state.selected_character
        hand_weapon = getattr(self.selected_character["base"], self.hand).item
        if self.attack_type in hand_weapon.weapon_damage_types:
            self.active = True
        else:
            self.active = False

    def activate_on_click(self, event, game_state, function):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.active == True and self.rect.collidepoint(event.pos):
                function(game_state.selected_character, self.hand, self.attack_type)
                game_state.interface_update_needed = True


class ActivityButton:
    activity_button_ID = 0

    def __init__(self, game_state, position_key):

        self.position_key = position_key
        self.image_path = r"assets/graphics/interface/activities/placeholder1.png"

        self.activity = None
        
        self.image = pygame.image.load(self.image_path)
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))

        self.activity_button_ID = ActivityButton.activity_button_ID
        ActivityButton.activity_button_ID += 1


    def draw(self, game_state, screen):
        screen.blit(self.image, self.rect)


    def update(self, game_state):
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))


    def activate_on_click(self, event, game_state, button_index, change_active_activity):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.activity and self.activity.immediate_effect == True: 
                    self.activity.perform(game_state, bot_left_log)
                    game_state.buttons_to_flash[self] = 255
                else: 
                    change_active_activity(game_state.selected_character, button_index, "activity")
                    game_state.interface_update_needed = True


    def update_for_new_character(self, gamestate):
        character = gamestate.selected_character["base"]

        activities_list_len = len(character.activities)
        if self.activity_button_ID+1 <= activities_list_len:
            self.activity = character.activities[self.activity_button_ID]

            self.image_path = self.activity.icon
            self.image = pygame.image.load(self.image_path)

        else: 
            self.image_path = r"assets/graphics/interface/activities/placeholder1.png"
            self.image = pygame.image.load(self.image_path)


class SpellButton:
    spell_button_ID = 0

    def __init__(self, game_state, position_key):

        self.position_key = position_key
        self.image_path = r"assets/graphics/interface/activities/placeholder1.png"

        self.spell = None
        
        self.image = pygame.image.load(self.image_path)
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))

        self.spell_button_ID = SpellButton.spell_button_ID
        SpellButton.spell_button_ID += 1


    def draw(self, game_state, screen):
        if game_state.selected_character["base"].archetype in POWER_ARCHETYPES:
            screen.blit(self.image, self.rect)
            character = game_state.selected_character["base"]
            if self.spell:
                if self.spell.base_spell_tier > character.selected_power_tier:
                    screen.blit(fill_black_40x, (self.rect))


    def update(self, game_state):
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))


    def activate_on_click(self, event, game_state, button_index, change_active_activity):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.spell and self.spell.base_spell_tier <= game_state.selected_character["base"].selected_power_tier:
                if self.spell.immediate_effect == True: 
                    self.spell.perform(game_state, bot_left_log)
                    game_state.buttons_to_flash[self] = 255
                else: 
                    change_active_activity(game_state.selected_character, button_index, "spell")
                    game_state.interface_update_needed = True


    def update_for_new_character(self, gamestate, screen=screen):
        character = gamestate.selected_character["base"]

        spells_list_len = len(character.spells)
        if self.spell_button_ID+1 <= spells_list_len:
            self.spell = character.spells[self.spell_button_ID]

            self.image_path = self.spell.icon
            self.image = pygame.image.load(self.image_path)

        else: 
            self.image_path = r"assets/graphics/interface/activities/placeholder1.png"
            self.image = pygame.image.load(self.image_path)


class PowerTierButton:
    def __init__(self, game_state, image_path, position_key, power_tier = 0):

        self.power_tier = power_tier
        self.active = False
        self.image_path = image_path
        self.position_key = position_key
        
        self.image = pygame.image.load(self.image_path)
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))

        self.activity_button_ID = ActivityButton.activity_button_ID
        ActivityButton.activity_button_ID += 1


    def draw(self, game_state, screen):
        if game_state.selected_character["base"].archetype in POWER_ARCHETYPES:
            screen.blit(self.image, self.rect)
            if self.active == False:
                screen.blit(fill_black_30x, (self.rect))


    def update(self, game_state):
        self.rect = self.image.get_rect(topleft=getattr(game_state, self.position_key))
        if game_state.selected_character["base"].max_power_tier_available >= self.power_tier:
            self.active = True
        else:
            self.active = False


    def activate_on_click(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.power_tier <= game_state.selected_character["base"].max_power_tier_available:
                    game_state.selected_character["base"].selected_power_tier = self.power_tier
                    game_state.interface_update_needed = True


class ButtonSelectorRect:
    def __init__(self, button):
        self.button = button
        self.rect = button.rect.copy()

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect, 2)

    def update(self, button):
        self.button = button
        self.rect = button.rect.copy()


class ActivitySelectorRect:
    def __init__(self, buttons, colour):
        self.left_weapon_button = buttons[0]
        self.right_weapon_button = buttons[1]

        self.button = buttons[0]
        self.rect = buttons[0].rect.copy()

        self.colour = colour

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect, 2)

    def update(self, game_state, weapon_buttons, activity_buttons, spell_buttons):
        selected_character = game_state.selected_character["base"]
        selected_activity = selected_character.selected_activity

        if selected_activity == selected_character.left_hand:
            self.rect = weapon_buttons[0].rect.copy()
            self.button = weapon_buttons[0]
        elif selected_activity == selected_character.right_hand:
            self.rect = weapon_buttons[1].rect.copy()
            self.button = weapon_buttons[1]
        elif selected_activity in selected_character.activities:
            self.rect = activity_buttons[selected_character.activities.index(selected_activity)].rect.copy()
            self.button = activity_buttons[selected_character.activities.index(selected_activity)]
        elif selected_activity in selected_character.spells:
            self.rect = spell_buttons[selected_character.spells.index(selected_activity)].rect.copy()
            self.button = spell_buttons[selected_character.spells.index(selected_activity)]


class OldActivitySelectorRect:
    def __init__(self, buttons, colour):
        self.left_weapon_button = buttons[0]
        self.right_weapon_button = buttons[1]

        self.button = buttons[0]
        self.rect = buttons[0].rect.copy()

        self.colour = colour

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect, 2)

    def update(self, game_state, buttons):
        selected_character = game_state.selected_character["base"]
        selected_hand = selected_character.selected_hand

        if selected_hand == selected_character.left_hand:
            self.rect = buttons[0].rect.copy()
            self.button = buttons[0]
        elif selected_hand == selected_character.right_hand:
            self.rect = buttons[1].rect.copy()
            self.button = buttons[1]
        elif selected_hand in selected_character.activities:
            self.rect = buttons[8+selected_character.activities.index(selected_hand)].rect.copy()
            self.button = buttons[8+selected_character.activities.index(selected_hand)]
        else:
            pass


class AttackTypeSelectorRect:
    def __init__(self, game_state, side, crush_button, slash_button, stab_button):
        self.crush_button = crush_button
        self.slash_button = slash_button
        self.stab_button = stab_button
        self.side = side # "left" or "right"
        self.button_list = [crush_button, slash_button, stab_button]
        self.button = crush_button

        self.rect = self.button.rect.copy()

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect, 2)

    def update(self, game_state, crush_button, slash_button, stab_button):
        from items import damage_crushing, damage_slashing, damage_piercing
        selected_character = game_state.selected_character
        left_selected_hand_attack_type = selected_character["base"].left_hand.attack_type
        right_selected_hand_attack_type = selected_character["base"].right_hand.attack_type

        selected_attack_type = None

        if self.side == "right":
            selected_attack_type = right_selected_hand_attack_type
        else:
            selected_attack_type = left_selected_hand_attack_type


        if selected_attack_type == damage_crushing:
            self.button = crush_button
        elif selected_attack_type == damage_slashing:
            self.button = slash_button
        elif selected_attack_type == damage_piercing:
            self.button = stab_button

        self.rect = self.button.rect.copy()


class PowerTierSelectorRect:
    def __init__(self, buttons, colour):
    
        self.button = buttons[0]
        self.rect = buttons[0].rect.copy()

        self.colour = colour

    def draw(self, game_state, screen):
        if game_state.selected_character["base"].archetype in POWER_ARCHETYPES:
            pygame.draw.rect(screen, self.colour, self.rect, 2)

    def update(self, game_state, buttons):
        selected_power_tier = game_state.selected_character["base"].selected_power_tier
        self.rect = buttons[selected_power_tier-1].rect.copy()
        self.button = buttons[selected_power_tier-1]


interface_actions = actions_in_interface(game_state)
interface_movement_pts = movement_pts_in_interface(game_state)
interface_health = health_in_interface(game_state)
interface_vigour = vigour_in_interface(game_state)
interface_power = power_points_in_interface(game_state)

