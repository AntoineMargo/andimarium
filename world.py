from PIL import Image
import numpy as np

from config import *


game_map = Image.open(game_state.maps[Z_DEFAULT][ADDRESS_INDEX])

game_state.map_width, game_state.map_height = game_map.size


class LogicCharacter: # the character as inserted into a particular gameboard/gamespace
    def __init__(self, character, pos_x: int = 0, pos_y: int = 0, pos_z: int = 0, parent_dict: dict = {}):
        self.character = character

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z

        self.parent_dict = parent_dict

    def update_increment(self, dx, dy):
        self.pos_x += dx
        self.pos_y += dy

    def update_reposition(self, x, y, z=0):
        self.pos_x = x
        self.pos_y = y
        self.pos_z = z
    
    def __str__(self) -> str:
        return f"{self.character.name}"

    def __repr__(self) -> str:
        return f"{self.character.name})"


class Tile:
    instance_count = 0

    def __init__(self, x, y, z = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.entities = [] # characters or objects inside/on the tile
        self.material = "air"
        self.passable = True
        self.sprite = r'assets/graphics/terrain/air_empty.png'
        self.max_hp = 999
        self.current_hp = 999
        self.damage_reduction = 999
        self.water = False

        Tile.instance_count += 1
        self.tile_ID = Tile.instance_count

    def __str__(self):
        return f"{self.material}: {self.x}, {self.y}"
    
    def __repr__(self) -> str:
        return f"{self.material}: {self.x}, {self.y}"


class EarthTileEmpty(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/earth_empty.png'
        self.material = "earth"


class SandTileEmpty(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/sand_empty.png'
        self.material = "sand"


class EarthTileFull(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/earth_full.png'
        self.material = "earth"
        self.passable = False
        self.max_hp = 200
        self.current_hp = 200
        self.damage_reduction = 40


class WaterTileEmpty(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/water_empty.png'
        self.material = "water"
        self.passable = False
        self.water = True


class WaterTileFull(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/water_full.png'
        self.material = "water"
        self.passable = False
        self.water = True


class GrassTileEmpty(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/grass_empty.png'
        self.material = "grass"


class WoodTileEmpty(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/wood_empty.png'
        self.material = "wood"


class WoodTileFull(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/wood_full.png'
        self.material = "wood"
        self.passable = False
        self.max_hp = 100
        self.current_hp = 100
        self.damage_reduction = 20


class StoneTileEmpty(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/stone_empty.png'
        self.material = "stone"


class StoneTileFull(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/stone_full.png'
        self.material = "stone"
        self.passable = False
        self.max_hp = 200
        self.current_hp = 200
        self.damage_reduction = 40


class StairsUpTile(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/stairs_up.png'
        self.material = "stairs up"
        self.passable = True
        self.max_hp = 999
        self.current_hp = 999
        self.damage_reduction = 999


class StairsDownTile(Tile):
    def __init__(self, x, y, z = 0) -> None:
        super().__init__(x, y, z)
        self.sprite = r'assets/graphics/terrain/stairs_down.png'
        self.material = "stairs down"
        self.passable = True
        self.max_hp = 999
        self.current_hp = 999
        self.damage_reduction = 999


COLOR_TO_TILE_TYPE = {
    (239, 228, 176, 255): EarthTileEmpty,
    (255, 242, 0, 255): EarthTileFull,
    (255, 201, 14, 255): SandTileEmpty,
    (153, 217, 234, 255): WaterTileEmpty,
    (0, 162, 232, 255): WaterTileFull,
    (34, 177, 76, 255): GrassTileEmpty,
    (185, 122, 87, 255): WoodTileEmpty,
    (136, 0, 21, 255): WoodTileFull,
    (195, 195, 195, 255): StoneTileEmpty,
    (127, 127, 127, 255): StoneTileFull,

    (163, 73, 164, 255): StairsUpTile,
    (200, 191, 231, 255): StairsDownTile}


def map_pixels_to_tiles(image_address, z_level = 0):
    image = Image.open(image_address)

    width, height = image.size
    tiles = {}
    map_array = np.array([[0 for _ in range(width)] for _ in range(height)], dtype=np.float32)

    for y in range(height):
        for x in range(width):
            pixel_color = image.getpixel((x, y)) # Extracts RGB code as tuple from each pixel
            tile_type = COLOR_TO_TILE_TYPE.get(pixel_color, Tile)
            tiles[(x, y)] = tile_type(x, y, z_level)
            map_array[y][x] = 1 if tiles[(x, y)].passable else 999  # Sets the "cost" (weight) of passing that tile

    return tiles, map_array


def get_character_coordinates(character):
    "returns a tuple of the character's x and y coordinates"

    return character["logic"].pos_x, character["logic"].pos_y, character["logic"].pos_z


def find_stairs(state = game_state):
    # We find and build the stairs up index
    for n in range(len(maps)):
        state.stairs_up_positions.append([]) # We replicate the maps structure
        state.stairs_down_positions.append([]) # We replicate the maps structure
        if state.maps[n][ADDRESS_INDEX]:
            for x in range(len(state.maps[n][MAP_ARRAY_INDEX])):
                for y in range(len(state.maps[n][MAP_ARRAY_INDEX][0])):
                    if state.maps[n][LOGIC_TILES_INDEX][(x, y)].material == "stairs up":
                        state.stairs_up_positions[n].append((x, y))

    # We build the matching stairs down index
    for n in range(len(state.stairs_up_positions)):
        if state.stairs_up_positions[n]:
            for stairs in state.stairs_up_positions[n]:
                state.stairs_down_positions[n+1].append(stairs)


for z_level in game_state.maps:
    if z_level[ADDRESS_INDEX]:
        z_level[LOGIC_TILES_INDEX], z_level[MAP_ARRAY_INDEX] = map_pixels_to_tiles(z_level[ADDRESS_INDEX], z_level[LEVEL_INDEX])
        z_level[MAP_ARRAY_INDEX] = z_level[MAP_ARRAY_INDEX].T

