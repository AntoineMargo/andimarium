import pygame
from PIL import Image
import math

from world import *


# pygame.init()

pygame.display.set_caption("Andimarium Arena Prototype")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 18)
font2 = pygame.font.Font(None, 30)


if fullscreen:
    info = pygame.display.Info()
    window_width, window_height = info.current_w, info.current_h
    screen = pygame.display.set_mode((game_state.window_width, game_state.window_height), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((game_state.window_width, game_state.window_height), pygame.RESIZABLE)


class GraphicTile(pygame.sprite.Sprite):
    def __init__(self, tile: Tile):
        super().__init__()
        self.tile = tile
        self.image = pygame.image.load(self.tile.sprite).convert_alpha()
        self.rect = self.image.get_rect(topleft=(self.tile.x * 40, self.tile.y * 40))

    def update(self, dx, dy):
        self.rect.x += dx * SCROLL_SPEED
        self.rect.y += dy * SCROLL_SPEED

    def copy(self):
        new_sprite = GraphicTile(self.tile)
        new_sprite.image = self.image.copy()
        new_sprite.rect = self.rect.copy()
        return new_sprite


class GraphicCharacter(pygame.sprite.Sprite):
    def __init__(self, character, pos_x: int = 0,  pos_y: int = 0):
        super().__init__()
        self.character = character
        self.image = pygame.image.load(self.character.sprite).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.rect.x = pos_x * TILE_SIZE
        self.rect.y = pos_y * TILE_SIZE

    def update(self, dx, dy):
        self.rect.x += dx * SCROLL_SPEED
        self.rect.y += dy * SCROLL_SPEED

    def update_increment(self, dx, dy):
        self.rect.x += dx * TILE_SIZE
        self.rect.y += dy * TILE_SIZE

    def update_reposition(self, x, y):
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE


class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, end_pos, speed, image_address, state=game_state):
        super().__init__()
        self.image_address = image_address
        self.image = pygame.image.load(image_address).convert_alpha()
        self.original_image = self.image  # Keep a copy of the original image for rotations
        self.rect = self.image.get_rect(center=start_pos)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.speed = speed

        # Calculate the direction vector (end_pos - start_pos)
        direction_x = end_pos[0] - start_pos[0]
        direction_y = end_pos[1] - start_pos[1]
        
        # Calculate the distance between start and end
        distance = math.hypot(direction_x, direction_y)
        
        # Normalize the direction vector to get the unit vector
        self.direction = (direction_x / distance, direction_y / distance)
        
        # Calculate the angle to rotate the projectile image
        angle = math.degrees(math.atan2(-direction_y, direction_x))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=start_pos)

    def update(self):
        # Move the projectile
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Check if the projectile has reached the target
        if math.hypot(self.rect.centerx - self.end_pos[0], self.rect.centery - self.end_pos[1]) < self.speed:
            self.kill()  # Remove the projectile from all sprite groups


class CharacterSelectionRectangle:
    def __init__(self, game_state):
        self.selected_character = game_state.selected_character
        self.rect = pygame.Rect(game_state.selected_character["graphic"].rect.x - game_state.camera_x,
                                game_state.selected_character["graphic"].rect.y - game_state.camera_y,
                                TILE_SIZE, TILE_SIZE)
        self.camera_x = game_state.camera_x
        self.camera_y = game_state.camera_y

    def draw_rect(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect, 2)

    def camera_update(self, dx, dy):
        self.rect.x += dx * SCROLL_SPEED
        self.rect.y += dy * SCROLL_SPEED

    def update_increment(self, dx, dy):
        self.rect.x += dx * TILE_SIZE
        self.rect.y += dy * TILE_SIZE

    def update(self, game_state):
        self.selected_character = game_state.selected_character
        self.rect = pygame.Rect(game_state.selected_character["graphic"].rect.x - game_state.camera_x,
                                game_state.selected_character["graphic"].rect.y - game_state.camera_y,
                                TILE_SIZE, TILE_SIZE)


def draw_health_bar(screen, character, game_state):
    health_ratio = character["base"].current_health_points/character["base"].max_health_points

    health_width = abs(int(BAR_WIDTH * health_ratio))

    x, y, z = get_character_coordinates(character)

    if z == game_state.z_level:
        # Draw black outline rectangle
        pygame.draw.rect(screen, (0, 0, 0), (x*TILE_SIZE- game_state.camera_x, y*TILE_SIZE- game_state.camera_y + BAR_OFFSET, BAR_WIDTH, BAR_HEIGHT))

        # Draw green filled rectangle representing health
        if health_ratio > 0:
            pygame.draw.rect(screen, (GREEN[0], GREEN[1], GREEN[2]), (x*TILE_SIZE- game_state.camera_x, y*TILE_SIZE- game_state.camera_y + BAR_OFFSET, health_width, BAR_HEIGHT))
        else:
            red_bar_start_x = (x * TILE_SIZE - game_state.camera_x + BAR_WIDTH) - health_width
            pygame.draw.rect(screen, (RED[0], RED[1], RED[2]), (red_bar_start_x, y*TILE_SIZE- game_state.camera_y + BAR_OFFSET, health_width, BAR_HEIGHT))


class FlashSprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()


def fill_with_colour_imprecise(colour, alpha, coordinates, width, height, game_state = game_state, screen = screen):
    surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    surface.fill((colour[0], colour[1], colour[2], alpha))

    flash_sprite = FlashSprite(surface)
    flash_sprite.rect.topleft = ((coordinates[0]*width) - game_state.camera_x, (coordinates[1]*height) - game_state.camera_y)

    screen.blit(flash_sprite.image, flash_sprite.rect)


def fill_with_colour_precise(character, colour, alpha, game_state = game_state, screen = screen):
    surface = pygame.Surface(character.image.get_size(), pygame.SRCALPHA)
    
    surface.fill((colour[0], colour[1], colour[2], alpha))
    
    character_mask = pygame.mask.from_surface(character.image)
    mask_surface = pygame.Surface(character.image.get_size(), pygame.SRCALPHA)
    
    mask_width, mask_height = character_mask.get_size()
    
    mask_surface.fill((0, 0, 0, 0))  # Ensure the mask surface is initially fully transparent 
    for x in range(mask_width):
        for y in range(mask_height):
            if character_mask.get_at((x, y)):
                mask_surface.set_at((x, y), surface.get_at((x, y)))

    flash_sprite = FlashSprite(mask_surface) # Create the flash sprite with the masked red surface
    flash_sprite.rect.center = (character.rect.centerx - game_state.camera_x, character.rect.centery - game_state.camera_y)
    
    screen.blit(flash_sprite.image, flash_sprite.rect)


def fill_with_colour_button(button, colour, alpha, game_state = game_state, screen = screen):
    surface = pygame.Surface(button.image.get_size(), pygame.SRCALPHA)
    surface.fill((colour[0], colour[1], colour[2], alpha))

    flash_sprite = FlashSprite(surface)
    flash_sprite.rect.center = (button.rect.centerx, button.rect.centery)

    screen.blit(flash_sprite.image, flash_sprite.rect)


def graphic_projectile(start_pos, end_pos, speed, image_address):
    x1, y1 = start_pos
    x2, y2 = end_pos

    x1 = x1 * 40 + 20
    y1 = y1 * 40 + 20
    x2 = x2 * 40 + 20
    y2 = y2 * 40 + 20

    projectile = Projectile((x1, y1), (x2, y2), speed, image_address)
    graphic_effects.add(projectile)


bottom_interface = pygame.Surface((game_state.window_width, 200), pygame.SRCALPHA)
bottom_interface.fill((BLACK[0], BLACK[1], BLACK[2], ALPHA120))

fill_black_40_20x = pygame.Surface((40, 20), pygame.SRCALPHA)
fill_black_40_20x.fill((BLACK[0], BLACK[1], BLACK[2], ALPHA120))

fill_black_30x = pygame.Surface((30, 30), pygame.SRCALPHA)
fill_black_30x.fill((BLACK[0], BLACK[1], BLACK[2], ALPHA120))

fill_black_40x = pygame.Surface((40, 40), pygame.SRCALPHA)
fill_black_40x.fill((BLACK[0], BLACK[1], BLACK[2], ALPHA120))

accessible_tile_graphic = pygame.Surface((40, 40), pygame.SRCALPHA)
accessible_tile_graphic.fill((GREEN[0], GREEN[1], GREEN[2], ALPHA120))

path_tile_graphic = pygame.Surface((40, 40), pygame.SRCALPHA)
path_tile_graphic.fill((BLUE[0], BLUE[1], BLUE[2], ALPHA120))

weapon_range_graphic = pygame.Surface((40, 40), pygame.SRCALPHA)
weapon_range_graphic.fill((RED[0], RED[1], RED[2], ALPHA120))

graphic_effects = pygame.sprite.Group()


def preprocess_graphic_tiles(game_state):
    for z_level in game_state.maps:
        if z_level[ADDRESS_INDEX]:
            z_level[GRAPHIC_TILES_INDEX] = pygame.sprite.Group()
            for coordinates, tile in z_level[LOGIC_TILES_INDEX].items(): 
                sprite = GraphicTile(tile)
                z_level[GRAPHIC_TILES_INDEX].add(sprite)


preprocess_graphic_tiles(game_state)


