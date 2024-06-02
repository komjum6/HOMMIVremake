import os
import pygame
from pygame.locals import *
# Note: This also loads all the variables from here in the global scope
# In case the one reading this is puzzled by where some variables come from
from HOMMIV_battle_sequence import *
from HOMMIV_campaign_ui_widgets import *
import json

# Initialize Pygame
pygame.init()

pygame.display.set_caption("HOMMIV Remake")

campaign_map = True
battle_sequence = False
haven_town = False
academy_town = False
necropolis_town = False
asylum_town = False
preserve_town = False
stronghold_town = False

grid_toggle = False
no_grid_movement_toggle = False

RPG_mode_toggle = True

################# UI #################

def haven_town_toggle():
    global campaign_map
    global haven_town
    campaign_map = False
    haven_town = True

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
    
    campaign_map = True
    battle_sequence = False
    haven_town = False
    academy_town = False
    necropolis_town = False
    asylum_town = False
    preserve_town = False
    stronghold_town = False

campaign_map_button = Button(100, 100, 300, 150, text="Campaign map", font_size=30, callback=campaign_map_toggle)

############# End of UI ##############

# Main loop
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            if battle_sequence:
                battle_sequence_keys(event, RPG_mode_toggle)
        if campaign_map:
            haven_town_button.is_clicked(event)
        elif haven_town:
            campaign_map_button.is_clicked(event)
        else:
            pass

    if battle_sequence:
        battle_sequence_scene_update(screen, background_battle_sequence, active_sprites_list, grid_toggle, no_grid_movement_toggle)
    elif haven_town:
        background = pygame.image.load("./assets_webp/Haven_city.webp")
        background = pygame.transform.smoothscale(background, screen.get_size())
        screen.blit(background, (0, 0))
        campaign_map_button.draw(screen)
    elif academy_town:
        background = pygame.image.load("./assets_webp/Academy_city.webp")
        background = pygame.transform.smoothscale(background, screen.get_size())
        screen.blit(background, (0, 0))
        campaign_map_button.draw(screen)
    elif necropolis_town:
        background = pygame.image.load("./assets_webp/Necropolis_city.webp")
        background = pygame.transform.smoothscale(background, screen.get_size())
        screen.blit(background, (0, 0))
        campaign_map_button.draw(screen)
    elif asylum_town:
        background = pygame.image.load("./assets_webp/Asylum_city.webp")
        background = pygame.transform.smoothscale(background, screen.get_size())
        screen.blit(background, (0, 0))
        campaign_map_button.draw(screen)
    elif preserve_town:
        background = pygame.image.load("./assets_webp/Preserve_city.webp")
        background = pygame.transform.smoothscale(background, screen.get_size())
        screen.blit(background, (0, 0))
        campaign_map_button.draw(screen)
    elif stronghold_town:
        background = pygame.image.load("./assets_webp/Stronghold_city.webp")
        background = pygame.transform.smoothscale(background, screen.get_size())
        screen.blit(background, (0, 0))
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
