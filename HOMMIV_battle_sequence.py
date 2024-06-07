import os
import pygame
from pygame.locals import *
from create_hex_grid import *
from pathing import *
from config import *
import json

path_radius = 0
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_height = 1080
screen_width = 1920
azure = pygame.color.Color("azure")
FPS = 10
clock = pygame.time.Clock()

#active_sprites_names = ["zombie", "Mummy"]

############################## 


# Read the JSON data from the file
with open('battle_sequence_details.json', 'r') as json_file:
    battle_data = json.load(json_file)

config = load_config()

# Create dictionaries for player 1 and player 2 sprites
player_1_sprites = battle_data.get('player_1', {})
player_2_sprites = battle_data.get('player_2', {})

# Extract sprite attributes for player 1
player_1_sprite_names = []
player_1_attributes = []
for sprite_name, sprite_attrs in player_1_sprites.items():
    player_1_sprite_names.append(sprite_name)
    player_1_attributes.append(sprite_attrs)

# Extract sprite attributes for player 2
player_2_sprite_names = []
player_2_attributes = []
for sprite_name, sprite_attrs in player_2_sprites.items():
    player_2_sprite_names.append(sprite_name)
    player_2_attributes.append(sprite_attrs)

# Combining the collective sprites for both players, the reason it was seperated at the beginning is because
# we want to make sure we can cast spells on only one group later    
sprites_names = player_1_sprite_names + player_2_sprite_names
total_attributes = player_1_attributes + player_2_attributes

sprite_directions, sprite_actions, sprite_speeds, start_positions = [a['active_sprite_direction'] for a in total_attributes], [a['active_sprite_action'] for a in total_attributes], [a['active_sprite_speed'] for a in total_attributes], [a['start_position'] for a in total_attributes]

#active_sprite_direction = "ne"
#active_sprite_action = "walk"
#active_sprite_speed = 2
#start_position = [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2]
#sprite_direction, sprite_action, sprite_speed = active_sprite_direction, active_sprite_action, active_sprite_speed

#active_sprite_direction_1 = "sw"
#active_sprite_action_1 = "walk"
#active_sprite_speed_1 = 2
#start_position_1 = [SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT * 0.25]
#sprite_direction_1, sprite_action_1, sprite_speed_1 = active_sprite_direction_1, active_sprite_action_1, active_sprite_speed_1

#active_sprite_directions = [active_sprite_direction, active_sprite_direction_1]
#active_sprite_actions = [active_sprite_action, active_sprite_action_1]
#active_sprite_speeds = [active_sprite_speed, active_sprite_speed_1]
#start_positions = [start_position, start_position_1]
#sprite_directions, sprite_actions, sprite_speeds = [sprite_direction, sprite_direction_1], [sprite_action, sprite_action_1], [sprite_speed, sprite_speed_1]

##############################

# Directories
base_directory = config["base_directory"]
active_background_battle_sequence = "Death/battlefield_preset_map.Death.single/backdrop.png"
battlefield_preset_map_directory = os.path.join(base_directory, "battlefield_preset_map/{0}".format(active_background_battle_sequence))  # Update with your actual path
    

# Function to load images from a given folder
def load_images_from_folder(folder_path):
    frames = []
    shadows = []

    # Load frame and shadow images
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.startswith('frame') and file_name.endswith('.png'):
            frame_path = os.path.join(folder_path, file_name)
            frames.append(pygame.image.load(frame_path).convert_alpha())
        elif file_name.startswith('shadow') and file_name.endswith('.png'):
            shadow_path = os.path.join(folder_path, file_name)
            shadows.append(pygame.image.load(shadow_path).convert_alpha())

    return frames, shadows

# Function to get all the actions from the loaded images
def get_sprite_images(active_sprite_name):

    # Define the directions for each action type
    directions_4_files = ["ne", "nw", "se", "sw"]
    directions_8_files = ["ne", "e", "se", "s", "sw", "w", "nw", "n"]

    # TODO make a function to load a JSON with all the action types, so it's not hardcoded anymore
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

    # Create an empty dictionary to store action types, their image files and directions
    action_images_dict = {}

    # Iterate through each action type
    for action_type, path in action_types.items():
    
        # Determine the directions based on the action type (some don't have all 8 directions)
        if action_type in ["combat_die", "combat_fidget", "combat_flinch", "combat_wait"]:
            directions = directions_4_files
        else:
            directions = directions_8_files
    
        # Store the action types with their image files and directions in a dictionary
        for direction in directions:
            folder_path = os.path.join(base_directory, f"{path}{direction}")
            if os.path.exists(folder_path):
                
                store_action_type = action_type + direction
                folder_path = os.path.join(actor_sequence_directory, store_action_type)
                image_files = load_images_from_folder(folder_path)
                action_images_dict[store_action_type] = [image_files, directions]
            
    return action_images_dict

# Create an AnimatedSprite class
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_name, position, sprite_direction, sprite_action, sprite_speed, images, hitbox_radius, movement_range, actor_sequence_directory):
        super(AnimatedSprite, self).__init__()
        self.actor_sequence_directory = actor_sequence_directory
        self.sprite_name = sprite_name
        self.images = images
        self.index = 0
        self.image = images[self.index]
        self.position = position
        self.sprite_speed = sprite_speed
        self.rect = self.image.get_rect(center=self.position)
        self.sprite_direction = sprite_direction
        self.sprite_action = sprite_action
        self.hitbox_radius = hitbox_radius
        self.movement_range = movement_range
        self.animation_time = len(self.images) / FPS
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
                
        # A path to walk to if there is one
        if self.sprite_action == "walk" and self.path:
            if self.path:
                next_pos = self.path[0]
                self.move_towards(next_pos)
                # TODO: The sprite should stop walking when reaching the next position and continue to the position after that in the next turn 
                if self.rect.center >= next_pos:
                    self.path.pop(0)  # Remove the reached position
                    #print(self.path)
                if self.path == []:
                    # TODO Temporary try except since the dwarf has only 4 wait directions for some reason
                    try:
                        change_selected_action(active_sprites_list, 0, "same direction", "wait")
                    except:
                        change_selected_action(active_sprites_list, 0, "sw", "wait")

    def move_towards(self, target):
        # Calculate the vector to the target
        direction = (target[0] - self.rect.centerx, target[1] - self.rect.centery)
        distance = (direction[0]**2 + direction[1]**2)**0.5
        #print(distance)
        if distance != 0:
            direction = (direction[0] / distance, direction[1] / distance)
        
        # Move the sprite
        self.rect.centerx += min(direction[0] * self.sprite_speed, distance)*20
        self.rect.centery += min(direction[1] * self.sprite_speed, distance)*20
        
        # When you change a path at least it won't walk back to the position the sprite gets 
        # when the sprite object is instantiated
        self.position = (self.rect.centerx, self.rect.centery)

        # Update the sprite direction based on the movement
        if direction[0] > 0 and direction[1] == 0:
            self.sprite_direction = "e"
            change_selected_action(active_sprites_list, 0, "e", "walk")
        elif direction[0] < 0 and direction[1] == 0:
            self.sprite_direction = "w"
            change_selected_action(active_sprites_list, 0, "w", "walk")
        elif direction[1] > 0 and direction[0] == 0:
            self.sprite_direction = "s"
            change_selected_action(active_sprites_list, 0, "s", "walk")
        elif direction[1] < 0 and direction[0] == 0:
            self.sprite_direction = "n"
            change_selected_action(active_sprites_list, 0, "n", "walk")
        elif direction[0] > 0 and direction[1] > 0:
            self.sprite_direction = "se"
            change_selected_action(active_sprites_list, 0, "se", "walk")
        elif direction[0] < 0 and direction[1] < 0:
            self.sprite_direction = "nw"
            change_selected_action(active_sprites_list, 0, "nw", "walk")
        elif direction[0] > 0 and direction[1] < 0:
            self.sprite_direction = "ne"
            change_selected_action(active_sprites_list, 0, "ne", "walk")
        elif direction[0] < 0 and direction[1] > 0:
            self.sprite_direction = "sw"
            change_selected_action(active_sprites_list, 0, "sw", "walk")        
                
        if self.sprite_action == "melee":
            
            # This helps with making sure the sprite attacks only once, but can attack again later
            if self.action_change:
                self.current_time = 0
                self.action_change = False
            
            # This is to make sure the sprite attacks only once
            if self.current_time >= self.animation_time and not self.played_once:
                self.played_once = True
            
            # If the melee animation played once, switch back to wait
            if self.played_once:   
                # TODO Temporary try except since the dwarf has only 4 wait directions for some reason
                try:
                    change_selected_action(active_sprites_list, 0, "same direction", "wait")
                except:
                    change_selected_action(active_sprites_list, 0, "sw", "wait")
        
        # Cycling through the images for the animation sequences
        self.index = (self.index + 1) % len(self.images)
        self.image = self.images[self.index]

# Loading background of the battle sequence
try:
    background_battle_sequence = pygame.image.load(battlefield_preset_map_directory)
except FileNotFoundError as e:
    print("Heroes_assets_pngs folder is empty or not found. You may want to update config.json with its location.")
    print(f"Missing file: {battlefield_preset_map_directory}")
    exit()

background_battle_sequence = pygame.transform.smoothscale(background_battle_sequence, screen.get_size())

# Function to change the action of the sprite
def change_sprite_action(actor_sequence_directory, active_sprite_action, active_sprite_name, active_sprite_direction):
    # Load images for chosen action
    active_sprite_images, active_sprite_shadow_images  = load_images_from_folder(os.path.join(actor_sequence_directory, "combat/{0}/actor_sequence.{1}.combat.{0}.{2}".format(active_sprite_action, active_sprite_name, active_sprite_direction)))
    
    return active_sprite_images, active_sprite_shadow_images

# Function to create a sprite object and its shadow object
def create_sprite(active_sprite_name, start_position, sprite_direction, sprite_action, sprite_speed, actor_sequence_directory):

    active_sprite_images, active_sprite_shadow_images = change_sprite_action(actor_sequence_directory, active_sprite_action, active_sprite_name, active_sprite_direction)
    
    # Add these attributes to the battle_sequence_details.json later
    hitbox_radius = 2
    movement_range = 20
    
    # Create an instance of AnimatedSprite for chosen action
    active_sprite = AnimatedSprite(active_sprite_name, start_position, sprite_direction, sprite_action, sprite_speed, active_sprite_images, hitbox_radius, movement_range, actor_sequence_directory)

    # Create an instance of AnimatedSprite for shadow images
    active_sprite_shadow = AnimatedSprite(active_sprite_name, start_position, sprite_direction, sprite_action, sprite_speed, active_sprite_shadow_images, hitbox_radius, movement_range, actor_sequence_directory)

    return active_sprite, active_sprite_shadow

# Create an empty dictionary to store sprite info
active_sprites_list = []

# A big loop for all the data about the sprites
for active_sprite_name, active_sprite_direction, active_sprite_action, active_sprite_speed, start_position, sprite_direction, sprite_action, sprite_speed in zip(sprites_names, sprite_directions, sprite_actions, sprite_speeds, start_positions, sprite_directions, sprite_actions, sprite_speeds):
    # Define the actor_sequence directory where your sprite files are located
    actor_sequence_directory = os.path.join(base_directory, "actor_sequence/{0}".format(active_sprite_name))  # Update with your actual path
    action_images_dict = get_sprite_images(active_sprite_name)
    active_sprite, active_sprite_shadow = create_sprite(active_sprite_name, start_position, sprite_direction, sprite_action, sprite_speed, actor_sequence_directory)
    active_sprites_list.append((active_sprite, active_sprite_shadow))

# Updating sprite and shadow
def update_sprite_and_shadow(active_sprite, active_sprite_shadow):
    active_sprite.update()
    active_sprite_shadow.update()

# Function to change the action of a given sprite (index), uses change_sprite_action() function
def change_selected_action(active_sprites_list, selected_index, sprite_direction, action):
    selected = active_sprites_list[selected_index][0]
    selected_shadow = active_sprites_list[selected_index][1]
    
    selected.action_change = True
    selected_shadow.action_change = True
    
    selected.played_once = False
    selected_shadow.played_once = False

    if sprite_direction == "same direction":
        active_sprite_images, active_sprite_shadow_images = change_sprite_action(selected.actor_sequence_directory, action, selected.sprite_name, selected.sprite_direction)
    else: 
        active_sprite_images, active_sprite_shadow_images = change_sprite_action(selected.actor_sequence_directory, action, selected.sprite_name, sprite_direction)
        selected.sprite_direction = sprite_direction
        selected_shadow.sprite_direction = sprite_direction
    
    selected.sprite_action = action
    selected_shadow.sprite_action = action
    
    selected.images = active_sprite_images
    selected_shadow.images = active_sprite_shadow_images

# Pygame keys for the battle sequence
def battle_sequence_keys(event, RPG_mode_toggle):
    if RPG_mode_toggle:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_e]:
            change_selected_action(active_sprites_list, 0, "same direction", "melee")
        elif keys[pygame.K_a] and keys[pygame.K_w]:
            change_selected_action(active_sprites_list, 0, "nw", "walk")
        elif keys[pygame.K_w] and keys[pygame.K_d]:
            change_selected_action(active_sprites_list, 0, "ne", "walk")
        elif keys[pygame.K_d] and keys[pygame.K_s]:
            change_selected_action(active_sprites_list, 0, "se", "walk")
        elif keys[pygame.K_s] and keys[pygame.K_a]:
            change_selected_action(active_sprites_list, 0, "sw", "walk")
        elif keys[pygame.K_w]:
            change_selected_action(active_sprites_list, 0, "n", "walk")
        elif keys[pygame.K_a]:
            change_selected_action(active_sprites_list, 0, "w", "walk")
        elif keys[pygame.K_s]:
            change_selected_action(active_sprites_list, 0, "s", "walk")
        elif keys[pygame.K_d]:
            change_selected_action(active_sprites_list, 0, "e", "walk")



##################################### Battle sequence update #####################################

# Initialize the environment once
BE = None
sprite_movement_list = []
pathfinding_required = False

target_index = 6

def battle_sequence_scene_update(screen, background_battle_sequence, active_sprites_list, mouse_click_pos, grid_toggle, no_grid_movement_toggle):
    global BE, sprite_movement_list, pathfinding_required

    # Check if pathfinding is required
    if mouse_click_pos:
        pathfinding_required = True

    # Draw background
    screen.blit(background_battle_sequence, (0, 0))

    # Draw the hexagonal grid
    if grid_toggle:
        draw_hex_grid()

    # Update the environment only when needed
    if no_grid_movement_toggle and not BE:
        sprite_movement_list = [
            SpriteMovement(sprite.position[0], sprite.position[1], sprite.hitbox_radius)
            for sprite, _ in active_sprites_list
        ]
        BE = BattleEnvironment(1920, 1080, sprite_movement_list)

    # Update sprites
    for index, (active_sprite, active_sprite_shadow) in enumerate(active_sprites_list):
        if no_grid_movement_toggle and pathfinding_required:
            # Perform pathfinding when the user requests
            target_index = 6
            movement_range = 20
            # If sprite selected
            #path = a_star_search(BE, sprite_movement_list[index], sprite_movement_list[target_index], movement_range)
            # If clicked on empty instead
            path = a_star_search(BE, SpriteMovement(active_sprite.position[0], active_sprite.position[1], path_radius),
                                     SpriteMovement(mouse_click_pos[0], mouse_click_pos[1], path_radius), movement_range)
            active_sprite.path = path  # Set the path for the sprite
            active_sprite.sprite_action = "walk"
            
            active_sprite_shadow.path = path  # Set the path for the sprite
            active_sprite_shadow.sprite_action = "walk"
            
            #print(path)
            pathfinding_required = False

        update_sprite_and_shadow(active_sprite, active_sprite_shadow)

        # temporary offset to correct apparent position
        offset_rect = active_sprite.rect.copy()
        offset_rect.x -= 144    # manually found these values
        offset_rect.y -= 136    # dwarf's final position is pretty accurate on my computer

        # draw debug path
        if grid_toggle:
            if active_sprite.path is not None:
                if len(active_sprite.path) > 1:
                    pygame.draw.lines(screen, azure, False, active_sprite.path)

        # Draw sprites and their shadows
        screen.blit(active_sprite.image, offset_rect)
        screen.blit(active_sprite_shadow.image, offset_rect)