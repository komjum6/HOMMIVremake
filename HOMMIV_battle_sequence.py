import os
import pygame
from pygame.locals import *
from create_hex_grid import * 
from pathing import *         
from config import *          
import json

# Global variables, initialized to None or default values
path_radius = 0
screen_height = 1080 
screen_width = 1920
azure = None # Initialize lazily
FPS = 10
clock = None 
background_battle_sequence = None 

# Internal flag to track if pygame components are initialized within this module
_pygame_components_initialized = False

def _initialize_pygame_components_in_battle_sequence():
    """Initializes pygame components required by HOMMIV_battle_sequence.py, without creating a display."""
    global clock, azure, _pygame_components_initialized

    if _pygame_components_initialized:
        return

    # Ensure pygame is initialized if it hasn't been by the main Kivy app
    if not pygame.get_init():
        pygame.init()
        print("HOMMIV_battle_sequence: pygame.init() called internally.")
    
    # Initialize font module for text rendering
    if not pygame.font.get_init():
        pygame.font.init()
        print("HOMMIV_battle_sequence: pygame.font.init() called internally.")

    clock = pygame.time.Clock()
    azure = pygame.color.Color("azure") # MOVED HERE
    _pygame_components_initialized = True
    print("HOMMIV_battle_sequence: Internal pygame components initialized.")

def _initialize_pygame_components_in_battle_sequence():
    """Initializes pygame components required by HOMMIV_battle_sequence.py, without creating a display."""
    global clock, azure, _pygame_components_initialized

    if _pygame_components_initialized:
        return

    # Ensure pygame is initialized (should already be done by caller with dummy driver)
    if not pygame.get_init():
        # If not initialized, do NOT set SDL_VIDEODRIVER here - it's too late
        pygame.init()
        print("HOMMIV_battle_sequence: pygame.init() called (should already be in dummy mode).")
    
    # Initialize font module for text rendering
    if not pygame.font.get_init():
        pygame.font.init()
        print("HOMMIV_battle_sequence: pygame.font.init() called internally.")

    clock = pygame.time.Clock()
    azure = pygame.color.Color("azure")
    _pygame_components_initialized = True
    print("HOMMIV_battle_sequence: Internal pygame components initialized.")


# Read the JSON data from the file (this is fine at module level as it doesn't use pygame)
with open('battle_sequence_details.json', 'r') as json_file:
    battle_data = json.load(json_file)

config = load_config()

player_1_sprites = battle_data.get('player_1', {})
player_2_sprites = battle_data.get('player_2', {})

player_1_sprite_names = []
player_1_attributes = []
for sprite_name, sprite_attrs in player_1_sprites.items():
    player_1_sprite_names.append(sprite_name)
    player_1_attributes.append(sprite_attrs)

player_2_sprite_names = []
player_2_attributes = []
for sprite_name, sprite_attrs in player_2_sprites.items():
    player_2_sprite_names.append(sprite_name)
    player_2_attributes.append(sprite_attrs)

sprites_names = player_1_sprite_names + player_2_sprite_names
total_attributes = player_1_attributes + player_2_attributes

sprite_directions, sprite_actions, sprite_speeds, start_positions = \
    [a['active_sprite_direction'] for a in total_attributes], \
    [a['active_sprite_action'] for a in total_attributes], \
    [a['active_sprite_speed'] for a in total_attributes], \
    [a['start_position'] for a in total_attributes]

# Directories (fine at module level)
base_directory = config["base_directory"]
active_background_battle_sequence = "Death/battlefield_preset_map.Death.single/backdrop.png"
battlefield_preset_map_directory = os.path.join(base_directory, "battlefield_preset_map/{0}".format(active_background_battle_sequence))

# Function to load images from a given folder (uses pygame, so needs pygame.init() first)
def load_images_from_folder(folder_path):
    _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized
    frames = []
    shadows = []
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.startswith('frame') and file_name.endswith('.png'):
            frame_path = os.path.join(folder_path, file_name)
            frames.append(pygame.image.load(frame_path).convert_alpha())
        elif file_name.startswith('shadow') and file_name.endswith('.png'):
            shadow_path = os.path.join(folder_path, file_name)
            shadows.append(pygame.image.load(shadow_path).convert_alpha())
    return frames, shadows

# Function to get all the actions from the loaded images (uses load_images_from_folder)
def get_sprite_images(active_sprite_name):
    _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized
    directions_4_files = ["ne", "nw", "se", "sw"]
    directions_8_files = ["ne", "e", "se", "s", "sw", "w", "nw", "n"]
    action_types = {
        "attack": f"attack/actor_sequence.{active_sprite_name}.attack.",
        "fidget": f"fidget/actor_sequence.{active_sprite_name}.fidget.",
        "postwalk": f"postwalk/actor_sequence.{active_sprite_name}.postwalk.",
        "prewalk": f"prewalk/actor_sequence.{active_sprite_name}.prewalk.",
        "wait": f"wait/actor_sequence.{active_sprite_name}.wait.",
        "walk": f"walk/actor_sequence.{active_sprite_name}.walk.",
        "combat_die": f"combat/die/actor_sequence.{active_sprite_name}.combat.die.",
        "combat_fidget": f"combat/fidget/actor_sequence.{active_sprite_name}.combat.fidget.",
        "combat_flinch": f"combat/flinch/actor_sequence.{active_sprite_name}.combat.flinch.",
        "combat_melee": f"combat/melee/actor_sequence.{active_sprite_name}.combat.melee.",
        "combat_melee_up": f"combat/melee_up/actor_sequence.{active_sprite_name}.combat.melee_up.",
        "combat_ranged": f"combat/ranged/actor_sequence.{active_sprite_name}.combat.ranged.",
        "combat_postwalk": f"combat/postwalk/actor_sequence.{active_sprite_name}.combat.postwalk.",
        "combat_prewalk": f"combat/prewalk/actor_sequence.{active_sprite_name}.combat.prewalk.",
        "combat_stand": f"combat/stand/actor_sequence.{active_sprite_name}.combat.stand.",
        "combat_wait": f"combat/wait/actor_sequence.{active_sprite_name}.combat.wait.",
        "combat_walk": f"combat/walk/actor_sequence.{active_sprite_name}.combat.walk.",
    }
    action_images_dict = {}
    for action_type, path in action_types.items():
        if action_type in ["combat_die", "combat_fidget", "combat_flinch", "combat_wait"]:
            directions = directions_4_files
        else:
            directions = directions_8_files
        for direction in directions:
            actor_sequence_directory = os.path.join(base_directory, f"actor_sequence/{active_sprite_name}") 
            folder_path = os.path.join(actor_sequence_directory, f"{path}{direction}") 
            if os.path.exists(folder_path):
                store_action_type = action_type + direction
                image_files = load_images_from_folder(folder_path)
                action_images_dict[store_action_type] = [image_files, directions]
            
    return action_images_dict

# Create an AnimatedSprite class (uses pygame.sprite.Sprite, so needs pygame.init())
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_name, position, sprite_direction, sprite_action, sprite_speed, images_tuple, hitbox_radius, movement_range, actor_sequence_directory):
        super(AnimatedSprite, self).__init__()
        _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized
        self.actor_sequence_directory = actor_sequence_directory
        self.sprite_name = sprite_name
        self.frames = images_tuple[0] 
        self.shadows = images_tuple[1] 
        self.index = 0
        self.image = self.frames[self.index] if self.frames else pygame.Surface((1,1)) 
        self.position = position
        self.sprite_speed = sprite_speed
        self.rect = self.image.get_rect(center=self.position)
        self.sprite_direction = sprite_direction
        self.sprite_action = sprite_action
        self.hitbox_radius = hitbox_radius
        self.movement_range = movement_range
        self.animation_time = len(self.frames) / FPS if self.frames else 0
        self.action_change = True
        self.played_once = False
        self.path = None
        self.current_time = 0

    @property
    def sprite_action(self):
        return self._sprite_action

    @sprite_action.setter
    def sprite_action(self, new_action):
        self._sprite_action = new_action

    def update(self):
        global clock 
        if clock: 
            self.current_time += clock.get_time() / 1000.0
        
        if self.sprite_action == "walk" and not self.path:
            if self.sprite_direction == "n":
                self.rect.y -= self.sprite_speed
            if self.sprite_direction == "s":
                self.rect.y += self.sprite_speed
            if self.sprite_direction == "e":
                self.rect.x += self.sprite_speed
            if self.sprite_direction == "w":
                self.rect.x -= self.sprite_speed
            if self.sprite_direction == "nw":
                self.rect.x -= self.sprite_speed
                self.rect.y -= self.sprite_speed
            if self.sprite_direction == "se":
                self.rect.x += self.sprite_speed
                self.rect.y += self.sprite_speed
            if self.sprite_direction == "ne":
                self.rect.x += self.sprite_speed
                self.rect.y -= self.sprite_speed
            if self.sprite_direction == "sw":
                self.rect.x -= self.sprite_speed
                self.rect.y += self.sprite_speed
                
        if self.sprite_action == "walk" and self.path:
            if self.path:
                next_pos = self.path[0]
                self.move_towards(next_pos)
                if self.rect.centerx >= next_pos[0] - self.sprite_speed and \
                   self.rect.centerx <= next_pos[0] + self.sprite_speed and \
                   self.rect.centery >= next_pos[1] - self.sprite_speed and \
                   self.rect.centery <= next_pos[1] + self.sprite_speed:
                    self.path.pop(0)
                if not self.path: 
                    try:
                        change_selected_action(active_sprites_list, 0, "same direction", "wait")
                    except:
                        change_selected_action(active_sprites_list, 0, "sw", "wait")

    def move_towards(self, target):
        direction = (target[0] - self.rect.centerx, target[1] - self.rect.centery)
        distance = (direction[0]**2 + direction[1]**2)**0.5
        if distance != 0:
            direction = (direction[0] / distance, direction[1] / distance)
        
        self.rect.centerx += int(direction[0] * self.sprite_speed) 
        self.rect.centery += int(direction[1] * self.sprite_speed)
        
        self.position = (self.rect.centerx, self.rect.centery)

        if direction[0] > 0 and direction[1] == 0:
            self.sprite_direction = "e"
        elif direction[0] < 0 and direction[1] == 0:
            self.sprite_direction = "w"
        elif direction[1] > 0 and direction[0] == 0:
            self.sprite_direction = "s"
        elif direction[1] < 0 and direction[0] == 0:
            self.sprite_direction = "n"
        elif direction[0] > 0 and direction[1] > 0:
            self.sprite_direction = "se"
        elif direction[0] < 0 and direction[1] < 0:
            self.sprite_direction = "nw"
        elif direction[0] > 0 and direction[1] < 0:
            self.sprite_direction = "ne"
        elif direction[0] < 0 and direction[1] > 0:
            self.sprite_direction = "sw"        
                
        if self.sprite_action == "melee":
            if self.action_change:
                self.current_time = 0
                self.action_change = False
            
            if self.current_time >= self.animation_time and not self.played_once:
                self.played_once = True
            
            if self.played_once:   
                try:
                    change_selected_action(active_sprites_list, 0, "same direction", "wait")
                except:
                    change_selected_action(active_sprites_list, 0, "sw", "wait")
        
        if self.frames: 
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
        else:
            self.image = pygame.Surface((1,1)) 

def load_all_sprites():
    global active_sprites_list
    _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized
    active_sprites_list = [] 
    for active_sprite_name, active_sprite_direction, active_sprite_action, active_sprite_speed, start_position, _, _, _ in zip(sprites_names, sprite_directions, sprite_actions, sprite_speeds, start_positions, sprite_directions, sprite_actions, sprite_speeds):
        actor_sequence_directory = os.path.join(base_directory, f"actor_sequence/{active_sprite_name}")
        action_images_dict = get_sprite_images(active_sprite_name)

        default_action_direction_key = active_sprite_action + active_sprite_direction
        
        if default_action_direction_key in action_images_dict:
            images_for_sprite = action_images_dict[default_action_direction_key][0] 
        else:
            print(f"Warning: No images found for {active_sprite_name} {default_action_direction_key}. Using empty surfaces.")
            images_for_sprite = ([], []) 

        active_sprite = AnimatedSprite(active_sprite_name, start_position, active_sprite_direction, active_sprite_action, active_sprite_speed, images_for_sprite, 2, 20, actor_sequence_directory)
        active_sprites_list.append((active_sprite, active_sprite)) 
    print("HOMMIV_battle_sequence: All sprites loaded.")

def update_sprite_and_shadow(active_sprite, active_sprite_shadow):
    active_sprite.update()
    active_sprite_shadow.update()

def change_selected_action(active_sprites_list, selected_index, sprite_direction, action):
    _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized
    selected = active_sprites_list[selected_index][0] 
    selected_shadow = active_sprites_list[selected_index][1] 
    
    selected.action_change = True
    selected_shadow.action_change = True
    
    selected.played_once = False
    selected_shadow.played_once = False

    target_direction = sprite_direction if sprite_direction != "same direction" else selected.sprite_direction
    
    active_sprite_images, active_sprite_shadow_images = change_sprite_action(selected.actor_sequence_directory, action, selected.sprite_name, target_direction)
    
    selected.sprite_direction = target_direction
    selected_shadow.sprite_direction = target_direction
    
    selected.sprite_action = action
    selected_shadow.sprite_action = action
    
    selected.frames = active_sprite_images
    selected.shadows = active_sprite_shadow_images
    selected.index = 0 
    selected.animation_time = len(selected.frames) / FPS if selected.frames else 0

    selected_shadow.frames = active_sprite_shadow_images 
    selected_shadow.shadows = active_sprite_shadow_images 
    selected_shadow.index = 0 
    selected_shadow.animation_time = len(selected_shadow.frames) / FPS if selected_shadow.frames else 0


def battle_sequence_keys(event, RPG_mode_toggle):
    _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized
    if RPG_mode_toggle and pygame and pygame.get_init(): 
        keys = pygame.key.get_pressed()
        if keys[K_e]: 
            change_selected_action(active_sprites_list, 0, "same direction", "combat_melee")
        elif keys[K_a] and keys[K_w]:
            change_selected_action(active_sprites_list, 0, "nw", "combat_walk")
        elif keys[K_w] and keys[K_d]:
            change_selected_action(active_sprites_list, 0, "ne", "combat_walk")
        elif keys[K_d] and keys[K_s]:
            change_selected_action(active_sprites_list, 0, "se", "combat_walk")
        elif keys[K_s] and keys[K_a]:
            change_selected_action(active_sprites_list, 0, "sw", "combat_walk")
        elif keys[K_w]:
            change_selected_action(active_sprites_list, 0, "n", "combat_walk")
        elif keys[K_a]:
            change_selected_action(active_sprites_list, 0, "w", "combat_walk")
        elif keys[K_s]:
            change_selected_action(active_sprites_list, 0, "s", "combat_walk")
        elif keys[K_d]:
            change_selected_action(active_sprites_list, 0, "e", "combat_walk")
        else: 
            change_selected_action(active_sprites_list, 0, "same direction", "combat_wait")

BE = None
sprite_movement_list = []
pathfinding_required = False
target_index = 6

def battle_sequence_scene_update(screen_surface, mouse_click_pos, grid_toggle, no_grid_movement_toggle):
    """
    Updates and renders one frame of the battle sequence to the provided screen_surface.
    This function ensures pygame components are initialized internally.
    """
    global BE, sprite_movement_list, pathfinding_required, clock, background_battle_sequence, azure

    _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized

    # Load background if not already loaded
    if background_battle_sequence is None:
        try:
            background_battle_sequence = pygame.image.load(battlefield_preset_map_directory)
            background_battle_sequence = pygame.transform.smoothscale(background_battle_sequence, screen_surface.get_size())
            print("HOMMIV_battle_sequence: Background loaded for offscreen rendering.")
        except FileNotFoundError as e:
            print(f"HOMMIV_battle_sequence: Heroes_assets_pngs folder is empty or not found. Missing file: {battlefield_preset_map_directory}")
            background_battle_sequence = pygame.Surface(screen_surface.get_size())
            background_battle_sequence.fill((0, 0, 0)) # Black fallback
        except Exception as e:
            print(f"HOMMIV_battle_sequence: Error loading background: {e}")
            background_battle_sequence = pygame.Surface(screen_surface.get_size())
            background_battle_sequence.fill((0, 0, 0)) # Black fallback

    # Ensure sprites are loaded only once
    if not active_sprites_list:
        load_all_sprites()
    
    # Draw background
    if background_battle_sequence:
        screen_surface.blit(background_battle_sequence, (0, 0))
    else:
        screen_surface.fill((0, 0, 0)) 

    # Draw the hexagonal grid (assuming draw_hex_grid uses the passed screen_surface)
    if grid_toggle:
        draw_hex_grid(screen_surface) 

    # Update the environment only when needed
    if no_grid_movement_toggle and not BE and active_sprites_list:
        sprite_movement_list = [
            SpriteMovement(sprite.position[0], sprite.position[1], sprite.hitbox_radius)
            for sprite, _ in active_sprites_list
        ]
        BE = BattleEnvironment(screen_width, screen_height, sprite_movement_list) 

    if mouse_click_pos:
        pathfinding_required = True

    # Update sprites
    for index, (active_sprite, active_sprite_shadow) in enumerate(active_sprites_list):
        if no_grid_movement_toggle and pathfinding_required:
            movement_range = 20
            path = a_star_search(BE, SpriteMovement(active_sprite.position[0], active_sprite.position[1], path_radius),
                                     SpriteMovement(mouse_click_pos[0], mouse_click_pos[1], path_radius), movement_range)
            active_sprite.path = path
            active_sprite.sprite_action = "walk"
            active_sprite_shadow.path = path
            active_sprite_shadow.sprite_action = "walk"
            pathfinding_required = False

        update_sprite_and_shadow(active_sprite, active_sprite_shadow)

        offset_rect = active_sprite.rect.copy()
        offset_rect.x -= 144
        offset_rect.y -= 136

        if grid_toggle and azure: 
            if active_sprite.path is not None:
                if len(active_sprite.path) > 1:
                    pygame.draw.lines(screen_surface, azure, False, active_sprite.path)

        if active_sprite.image:
            screen_surface.blit(active_sprite.image, offset_rect)
        
        if active_sprite_shadow.frames and active_sprite_shadow.frames[active_sprite_shadow.index]: 
            screen_surface.blit(active_sprite_shadow.frames[active_sprite_shadow.index], offset_rect)
        else:
            pass 

    return screen_surface 

# This function is ONLY for standalone execution of HOMMIV_battle_sequence.py
def run_standalone_battle_sequence():
    global clock, background_battle_sequence, azure, _pygame_components_initialized

    _initialize_pygame_components_in_battle_sequence() # Ensure pygame is initialized for standalone

    screen = pygame.display.set_mode((screen_width, screen_height)) # Create actual window
    pygame.display.set_caption("HOMMIV Battle Sequence Standalone")
    
    # Load background once for standalone
    try:
        background_battle_sequence = pygame.image.load(battlefield_preset_map_directory)
        background_battle_sequence = pygame.transform.smoothscale(background_battle_sequence, screen.get_size())
        print("HOMMIV_battle_sequence: Background loaded for standalone rendering.")
    except FileNotFoundError as e:
        print(f"HOMMIV_battle_sequence: Heroes_assets_pngs folder is empty or not found. Missing file: {battlefield_preset_map_directory}")
        background_battle_sequence = pygame.Surface(screen.get_size())
        background_battle_sequence.fill((0, 0, 0)) 
    except Exception as e:
        print(f"HOMMIV_battle_sequence: Error loading background: {e}")
        background_battle_sequence = pygame.Surface(screen.get_size())
        background_battle_sequence.fill((0, 0, 0)) 

    load_all_sprites() 
        
    running = True
    while running:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == QUIT: 
                running = False
            battle_sequence_keys(event, True) 
            
        battle_sequence_scene_update(screen, (0,0), True, True) 
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    run_standalone_battle_sequence()
