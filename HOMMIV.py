import os
import pygame
from pygame.locals import *
import pygame_gui
# Note: This also loads all the variables from here in the global scope
# In case the one reading this is puzzled by where some variables come from
from HOMMIV_battle_sequence2 import *
from HOMMIV_campaign_ui_widgets import *
from HOMMIV_parse_ui_town import *
import json
import time

# Set the SDL video driver to Wayland
os.environ['SDL_VIDEODRIVER'] = 'x11'

# Bypass audio issues if not using audio
os.environ['SDL_AUDIODRIVER'] = 'dummy'

towns = ["Life", "Nature", "Chaos", "Death", "Order", "Might"]
biomes = ["dirt", "grass", "rough", "sand", "snow", "subterranean", "swamp", "volcanic"]

town = towns[0]
biome = biomes[3]


# Initialize Pygame
pygame.init()

pygame.display.set_caption("HOMMIV Remake")

#screen_info = pygame.display.Info()
#screen_height = screen_info.current_h
#screen_width = screen_info.current_w
#print(screen_width)
#print(screen_height)
#screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

resolution = (1920, 1080)
#resolution = (screen_width, screen_height)
screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
manager = pygame_gui.UIManager(resolution, 'theme.json')


campaign_map = False
battle_sequence = True
haven_town = False
academy_town = False
necropolis_town = False
asylum_town = False
preserve_town = False
stronghold_town = False

grid_toggle = True
no_grid_movement_toggle = True

RPG_mode_toggle = True

# Cooldown time in seconds for mouse clicks
click_cooldown = 0.5
last_click_time = 0

################# UI #################

def haven_town_toggle():
    global campaign_map
    global haven_town
    campaign_map = False
    haven_town = False

haven_town_button = Button(100, 100, 300, 150, text="Haven Town", font_size=30, callback=haven_town_toggle)

def campaign_map_toggle():
    global campaign_map
    global battle_sequence
    global haven_town
    global academy_town
    global necropolis_town
    global asylum_town
    global preserve_town
    global stronghold_town
    global haven_town
    
    campaign_map = False
    battle_sequence = True
    haven_town = False
    academy_town = False
    necropolis_town = False
    asylum_town = False
    preserve_town = False
    stronghold_town = False

campaign_map_button = Button(100, 100, 300, 150, text="Campaign map", font_size=30, callback=campaign_map_toggle)

############# End of UI ##############

mouse_click_pos = False

# Main loop
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            #if battle_sequence:
                #battle_sequence_keys(event, RPG_mode_toggle)
        elif event.type == MOUSEBUTTONDOWN:
            current_time = time.time()
            if current_time - last_click_time > click_cooldown:
                last_click_time = current_time
                mouse_click_pos = event.pos
                
        manager.process_events(event)
        
        if campaign_map:
            haven_town_button.is_clicked(event)
        elif haven_town:
            campaign_map_button.is_clicked(event)
        else:
            pass

    manager.update(time_delta)

    if battle_sequence:
        #battle_sequence_scene_update(screen, background_battle_sequence, active_sprites_list, mouse_click_pos, grid_toggle, no_grid_movement_toggle)
        battle_sequence_run()
        mouse_click_pos = False
    elif haven_town:
        ui_file_path = r'D:\Blender_video_music\Games\HOMMIVremake\HOMMIVremake\HOMMIV{0}town.ui'.format(town)  # Replace with your .ui file path
        load_ui(ui_file_path, town, biome, manager)
        manager.draw_ui(window_surface)
        campaign_map_button.draw(screen)
    elif academy_town:
        ui_file_path = r'D:\Blender_video_music\Games\HOMMIVremake\HOMMIVremake\HOMMIV{0}town.ui'.format(town)  # Replace with your .ui file path
        load_ui(ui_file_path, town, biome, manager)
        manager.draw_ui(window_surface)
        campaign_map_button.draw(screen)
    elif necropolis_town:
        ui_file_path = r'D:\Blender_video_music\Games\HOMMIVremake\HOMMIVremake\HOMMIV{0}town.ui'.format(town)  # Replace with your .ui file path
        load_ui(ui_file_path, town, biome, manager)
        manager.draw_ui(window_surface)
        campaign_map_button.draw(screen)
    elif asylum_town:
        ui_file_path = r'D:\Blender_video_music\Games\HOMMIVremake\HOMMIVremake\HOMMIV{0}town.ui'.format(town)  # Replace with your .ui file path
        load_ui(ui_file_path, town, biome, manager)
        manager.draw_ui(window_surface)
        campaign_map_button.draw(screen)
    elif preserve_town:
        ui_file_path = r'D:\Blender_video_music\Games\HOMMIVremake\HOMMIVremake\HOMMIV{0}town.ui'.format(town)  # Replace with your .ui file path
        load_ui(ui_file_path, town, biome, manager)
        manager.draw_ui(window_surface)
        campaign_map_button.draw(screen)
    elif stronghold_town:
        ui_file_path = r'D:\Blender_video_music\Games\HOMMIVremake\HOMMIVremake\HOMMIV{0}town.ui'.format(town)  # Replace with your .ui file path
        load_ui(ui_file_path, town, biome, manager)
        manager.draw_ui(window_surface)
        campaign_map_button.draw(screen)
    else:

        # Draw Background
        background = pygame.image.load("./assets_webp/test_scene.webp")
        background = pygame.transform.smoothscale(background, screen.get_size())
        screen.blit(background, (0, 0))
        
        # Update the buttons
        #button.listen(events)
        haven_town_button.draw(screen)
        
            

    # Display the screen
    pygame.display.flip()
    
    clock.tick(FPS)  # Frame rate

# Quit Pygame
pygame.quit()
