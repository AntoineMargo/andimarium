import copy
import pygame

pygame.init()

running = True
fullscreen = False
debug = True


maps = [[-4, None, None, None, None],
        [-3, None, None, None, None],
        [-2, None, None, None, None],
        [-1, r"assets/maps/map_6_-1.png", None, None, None],
        [0, r"assets/maps/map_6_0.png", None, None, None],
        [1, r"assets/maps/map_6_1.png", None, None, None],
        [2, r"assets/maps/map_6_2.png", None, None, None],
        [3, None, None, None, None],
        [4, None, None, None, None]]


# Constants
TILE_SIZE = 40
SCROLL_SPEED = 8
ZOOM_SPEED = 0.1
LOG_SIZE = 12
OLD_LOG_SIZE = 100
LOG_WIDTH = 290
SPACING1 = 32
SPACING2 = 50

ALPHA90 = 90
ALPHA120 = 120
ALPHA200 = 200
ALPHA255 = 255

Z_DEFAULT = 4
LEVEL_INDEX = 0
ADDRESS_INDEX = 1
LOGIC_TILES_INDEX = 2
GRAPHIC_TILES_INDEX = 3
MAP_ARRAY_INDEX = 4

WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
FADED_YELLOW = (128, 128, 0)

# Health bars
BAR_WIDTH = 40  
BAR_HEIGHT = 4
BAR_OFFSET = 40

POWER_ARCHETYPES = ["mage", "spellsword", "trancer"]


class Data:
    def __init__(self) -> None:
        self.activities = {}
        self.talents = {}
        self.archetypes = {}

    def load_activities(self, activities):
        self.activities = activities

    def load_talents(self, talents):
        self.talents = talents

    def load_archetypes(self, archetypes):
        self.archetypes = archetypes


class GameState:
    def __init__(self, window_width, window_height, camera_x=0, camera_y=0, maps=maps, turn_counter=1, show_interface=True, show_healthbars=True):
        self.window_width = window_width
        self.window_height = window_height

        self.camera_x = camera_x
        self.camera_y = camera_y

        self.maps = maps

        self.z_level = 0

        self.current_map_tiles = None
        self.current_map_array = None
        self.current_map_graphics = None

        # self.stairs_up_positions = {}
        # self.stairs_down_positions = {}

        self.stairs_up_positions = []
        self.stairs_down_positions = []

        self.tick_counter = 0
        self.turn_counter = turn_counter

        self.show_interface = show_interface
        self.show_healthbars = show_healthbars

        self.map_width = 0
        self.map_height = 0

        self.all_characters = []

        self.player_characters = []
        self.non_player_characters = []

        self.hit_characters = {}

        self.accessible_tiles = set()
        self.show_accessible_tiles = False

        self.weapon_range_tiles = set()
        self.show_weapon_range = False

        self.path_tiles = []
        self.show_path = False

        self.path_tiles_to_flash = []
        self.time_to_flash_path_tiles = 0

        self.player_control = True
        self.ai_turn_in_progress = False
        self.current_npc_index = 0
        self.last_AI_action_tick = 0

        self.interface_update_needed = False

        # This is the structure of the character element throughout the program
        placeholder_char = {"base": "placeholder", "logic_character": "placeholder", "graphic": "placeholder"}

        self.selected_character = placeholder_char
        self.targeted_character = None

        self.reaction_tracker = None

        self.targeted_tile = (0, 0)

        self.buttons_to_flash = {}

        self.weapon_pos_1 = (0, 0)
        self.weapon_pos_2 = (0, 0)

        self.at_type_left_pos_1 = (0, 0)
        self.at_type_left_pos_2 = (0, 0)
        self.at_type_left_pos_3 = (0, 0)
        # self.at_type_left_pos_4 = (0, 0)
        # self.at_type_left_pos_5 = (0, 0)

        self.at_type_right_pos_1 = (0, 0)
        self.at_type_right_pos_2 = (0, 0)
        self.at_type_right_pos_3 = (0, 0)
        # self.at_type_right_pos_4 = (0, 0)
        # self.at_type_right_pos_5 = (0, 0)

        self.activity_1 = (0, 0)
        self.activity_2 = (0, 0)
        self.activity_3 = (0, 0)
        self.activity_4 = (0, 0)
        self.activity_5 = (0, 0)
        self.activity_6 = (0, 0)
        self.activity_7 = (0, 0)
        self.activity_8 = (0, 0)
        self.activity_9 = (0, 0)
        self.activity_10 = (0, 0)

        self.power_tier_1 = (0, 0)
        self.power_tier_2 = (0, 0)
        self.power_tier_3 = (0, 0)
        self.power_tier_4 = (0, 0)
        self.power_tier_5 = (0, 0)
        self.power_tier_6 = (0, 0)
        self.power_tier_7 = (0, 0)
        self.power_tier_8 = (0, 0)
        self.power_tier_9 = (0, 0)
        self.power_tier_10 = (0, 0)
        self.power_tier_11 = (0, 0)
        self.power_tier_12 = (0, 0)

        self.spell_1 = (0, 0)
        self.spell_2 = (0, 0)
        self.spell_3 = (0, 0)
        self.spell_4 = (0, 0)
        self.spell_5 = (0, 0)
        self.spell_6 = (0, 0)
        self.spell_7 = (0, 0)
        self.spell_8 = (0, 0)
        self.spell_9 = (0, 0)
        self.spell_10 = (0, 0)

        self.health = (0, 0)
        self.vigour = (0, 0)
        self.actions_left = (0, 0)
        self.movement_left = (0, 0)
        self.power = (0, 0) 


    def load_level(self, new_z_level):
        self.z_level = new_z_level

        self.current_map_tiles = self.maps[Z_DEFAULT+new_z_level][LOGIC_TILES_INDEX]
        self.current_map_array = self.maps[Z_DEFAULT+new_z_level][MAP_ARRAY_INDEX]
        self.current_map_graphics = self.maps[Z_DEFAULT+new_z_level][GRAPHIC_TILES_INDEX]


    def update_positions(self):
        self.weapon_pos_1 = (300, self.window_height - 190)
        self.weapon_pos_2 = (350, self.window_height - 190)

        self.at_type_left_pos_1 = (300, self.window_height - 145)
        self.at_type_left_pos_2 = (300, self.window_height - 120)
        self.at_type_left_pos_3 = (300, self.window_height - 95)
        # self.at_type_left_pos_4 = (300, self.window_height - 70)
        # self.at_type_left_pos_5 = (300, self.window_height - 45)

        self.at_type_right_pos_1 = (350, self.window_height - 145)
        self.at_type_right_pos_2 = (350, self.window_height - 120)
        self.at_type_right_pos_3 = (350, self.window_height - 95)
        # self.at_type_right_pos_4 = (350, self.window_height - 70)
        # self.at_type_right_pos_5 = (350, self.window_height - 45)

        self.activity_1 = (600, self.window_height - 190)
        self.activity_2 = (650, self.window_height - 190)
        self.activity_3 = (700, self.window_height - 190)
        self.activity_4 = (750, self.window_height - 190)
        self.activity_5 = (800, self.window_height - 190)
        self.activity_6 = (850, self.window_height - 190)
        self.activity_7 = (900, self.window_height - 190)
        self.activity_8 = (950, self.window_height - 190)
        self.activity_9 = (1000, self.window_height - 190)
        self.activity_10 = (1050, self.window_height - 190)

        self.power_tier_1 = (1250, self.window_height - 190)
        self.power_tier_2 = (self.power_tier_1[0]+SPACING1, self.window_height - 190)
        self.power_tier_3 = (self.power_tier_2[0]+SPACING1, self.window_height - 190)
        self.power_tier_4 = (self.power_tier_3[0]+SPACING1, self.window_height - 190)
        self.power_tier_5 = (self.power_tier_4[0]+SPACING1, self.window_height - 190)
        self.power_tier_6 = (self.power_tier_5[0]+SPACING1, self.window_height - 190)
        self.power_tier_7 = (self.power_tier_6[0]+SPACING1, self.window_height - 190)
        self.power_tier_8 = (self.power_tier_7[0]+SPACING1, self.window_height - 190)
        self.power_tier_9 = (self.power_tier_8[0]+SPACING1, self.window_height - 190)
        self.power_tier_10 = (self.power_tier_9[0]+SPACING1, self.window_height - 190)
        self.power_tier_11 = (self.power_tier_10[0]+SPACING1, self.window_height - 190)
        self.power_tier_12 = (self.power_tier_11[0]+SPACING1, self.window_height - 190)

        self.spell_1 = (1200, self.window_height - 150)
        self.spell_2 = (1250, self.window_height - 150)
        self.spell_3 = (1300, self.window_height - 150)
        self.spell_4 = (1350, self.window_height - 150)
        self.spell_5 = (1400, self.window_height - 150)
        self.spell_6 = (1450, self.window_height - 150)
        self.spell_7 = (1500, self.window_height - 150)
        self.spell_8 = (1550, self.window_height - 150)
        self.spell_9 = (1600, self.window_height - 150)
        self.spell_10 = (1650, self.window_height - 150)

        self.health = (400, self.window_height - 185)
        self.vigour = (400, self.window_height - 155)
        self.actions_left = (game_state.window_width - 80, game_state.window_height - 180)
        self.movement_left = (self.window_width - 110, self.window_height - 85)
        self.power = (1100, self.window_height - 185)


data = Data()

if fullscreen:
    game_state = GameState(window_width=1920, window_height=1200)
else:
    game_state = GameState(1366, 1000, 100, 100)

