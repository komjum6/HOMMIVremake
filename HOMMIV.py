import os
import json
import time

towns = ["Life", "Nature", "Chaos", "Death", "Order", "Might"]
biomes = ["dirt", "grass", "rough", "sand", "snow", "subterranean", "swamp", "volcanic"]

town = towns[0]
biome = biomes[3]

campaign_map = True
battle_sequence = False 
haven_town = False
academy_town = False
necropolis_town = False
asylum_town = False
preserve_town = False
stronghold_town = False

grid_toggle = True
no_grid_movement_toggle = True
RPG_mode_toggle = True

mouse_click_pos = False
click_cooldown = 0.5
last_click_time = 0

window_surface = None 
manager = None
_initialized = False 
_hidden_display = None

pygame = None
pygame_gui = None
_battle_sequence_module = None 
_parse_ui_town_module = None 

battle_sequence_keys = None
battle_sequence_scene_update = None
load_ui = None
clock = None 
FPS = 60

def haven_town_toggle():
    global campaign_map, haven_town, battle_sequence
    campaign_map = False
    haven_town = True
    battle_sequence = False 
    print("HOMMIV: Switched to Haven Town")

def campaign_map_toggle():
    global campaign_map, battle_sequence, haven_town, academy_town
    global necropolis_town, asylum_town, preserve_town, stronghold_town
    
    campaign_map = True
    battle_sequence = False 
    haven_town = False
    academy_town = False
    necropolis_town = False
    asylum_town = False
    preserve_town = False
    stronghold_town = False
    print("HOMMIV: Switched to Campaign Map")

def battle_sequence_activate():
    global campaign_map, battle_sequence, haven_town
    campaign_map = False
    haven_town = False
    battle_sequence = True
    print("HOMMIV: Battle sequence activated!")

def _import_pygame_modules():
    global pygame, pygame_gui, _battle_sequence_module, _parse_ui_town_module
    global battle_sequence_keys, battle_sequence_scene_update
    global load_ui, clock, FPS
    
    if pygame is not None:
        return  
    
    print("HOMMIV: Importing pygame modules...")
    
    import pygame as pg
    import pygame_gui as pg_gui
    
    pygame = pg
    pygame_gui = pg_gui
    
    # Initialize pygame
    if not pygame.get_init():
        pygame.init()
        print("HOMMIV: pygame.init() called.")
    
    if not pygame.font.get_init():
        pygame.font.init()
        print("HOMMIV: pygame.font.init() called.")

    # Import battle sequence module
    try:
        import HOMMIV_battle_sequence as battle_seq_mod
        _battle_sequence_module = battle_seq_mod
        battle_sequence_keys = _battle_sequence_module.battle_sequence_keys
        battle_sequence_scene_update = _battle_sequence_module.battle_sequence_scene_update
        print("HOMMIV: Imported HOMMIV_battle_sequence.")
    except Exception as e:
        print(f"HOMMIV: Could not import battle sequence module: {e}")
        import traceback
        traceback.print_exc()
        _battle_sequence_module = None
        battle_sequence_keys = None
        battle_sequence_scene_update = None

    # Import UI module
    try:
        import HOMMIV_parse_ui_town as parse_ui_mod
        _parse_ui_town_module = parse_ui_mod
        load_ui = _parse_ui_town_module.load_ui
        print("HOMMIV: Imported HOMMIV_parse_ui_town.")
    except Exception as e:
        print(f"HOMMIV: Could not import parse_ui module: {e}")
        import traceback
        traceback.print_exc()
        _parse_ui_town_module = None
        load_ui = None
    
    clock = pygame.time.Clock() 
    
    # Update globals
    globals().update({
        'pygame': pygame,
        'pygame_gui': pygame_gui,
        'battle_sequence_keys': battle_sequence_keys,
        'battle_sequence_scene_update': battle_sequence_scene_update,
        'load_ui': load_ui,
        'clock': clock
    })
    
    print("HOMMIV: Pygame modules imported successfully.")

def initialize_hommiv(resolution=(1920, 1080)):
    """Initialize for standalone mode with actual window."""
    global window_surface, manager, _initialized
    
    if _initialized:
        return  
    
    _import_pygame_modules()
    
    pygame.display.set_caption("HOMMIV Remake")
    window_surface = pygame.display.set_mode(resolution) 
    manager = pygame_gui.UIManager(resolution, 'theme.json')
    
    _initialized = True
    print("HOMMIV: Initialized for standalone mode with window.")

def initialize_hommiv_offscreen(width=1000, height=800):
    """Initialize for offscreen/headless rendering."""
    global manager, _initialized, _hidden_display
    
    if _initialized:
        print("HOMMIV: Already initialized, skipping.")
        return
    
    print("HOMMIV: Starting offscreen initialization...")
    
    _import_pygame_modules()
    
    # Create a minimal hidden display (0x0 pixel, hidden flag)
    try:
        # Set window position off-screen before creating it
        os.environ['SDL_VIDEO_WINDOW_POS'] = "-10000,-10000"
        
        # Create minimal display (required for pygame to work properly)
        _hidden_display = pygame.display.set_mode((0, 0), pygame.HIDDEN)
        print("HOMMIV: Created hidden 0x0 display window.")
        
        # Create UI manager with actual render size
        manager = pygame_gui.UIManager((width, height), 'theme.json')
        _initialized = True
        print("HOMMIV: Successfully initialized for offscreen rendering.")
    except Exception as e:
        print(f"HOMMIV: Error initializing: {e}")
        import traceback
        traceback.print_exc()
        _initialized = False

def HOMMIV_update_frame(screen_surface, time_delta):
    """Update and render one frame to the provided surface."""
    global mouse_click_pos, last_click_time, manager
    
    if not _initialized:
        initialize_hommiv_offscreen(screen_surface.get_width(), screen_surface.get_height())
    
    if not pygame:
        print("HOMMIV: ERROR - pygame not initialized!")
        screen_surface.fill((255, 0, 0))
        return screen_surface
    
    # Process events
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if battle_sequence and battle_sequence_keys:
                battle_sequence_keys(event, RPG_mode_toggle)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            current_time = time.time()
            if current_time - last_click_time > click_cooldown:
                last_click_time = current_time
                mouse_click_pos = event.pos
                
        if manager:
            manager.process_events(event)

    if manager:
        manager.update(time_delta)
    
    town_ui_path = r"D:\Blender_video_music\highlight_accessable_dirs\HOMMIVremake\HOMMIVremake"

    # Render based on current state
    if battle_sequence:
        if battle_sequence_scene_update and _battle_sequence_module:
            try:
                screen_surface = _battle_sequence_module.battle_sequence_scene_update(
                    screen_surface, mouse_click_pos, grid_toggle, no_grid_movement_toggle
                )
                mouse_click_pos = False
            except Exception as e:
                print(f"HOMMIV: Error in battle_sequence_scene_update: {e}")
                import traceback
                traceback.print_exc()
                screen_surface.fill((200, 50, 50))
        else:
            screen_surface.fill((200, 50, 50))
            if pygame.font.get_init():
                font = pygame.font.Font(None, 74)
                text = font.render('Battle Sequence (Module Error)', True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_surface.get_width()//2, screen_surface.get_height()//2))
                screen_surface.blit(text, text_rect)

    elif haven_town:
        screen_surface.fill((50, 100, 150))
        if load_ui and manager: 
            try:
                ui_file_path = os.path.join(town_ui_path, f'HOMMIV{town}town.ui')
                load_ui(ui_file_path, town, biome, manager)
                manager.draw_ui(screen_surface) 
            except Exception as e:
                print(f"HOMMIV: Error loading UI in Haven Town: {e}")
                if pygame.font.get_init():
                    font = pygame.font.Font(None, 74)
                    text = font.render('Haven Town (UI Error)', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(screen_surface.get_width()//2, screen_surface.get_height()//2))
                    screen_surface.blit(text, text_rect)

    elif academy_town:
        screen_surface.fill((100, 50, 150))
        if pygame.font.get_init():
            font = pygame.font.Font(None, 74)
            text = font.render('Academy Town', True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_surface.get_width()//2, screen_surface.get_height()//2))
            screen_surface.blit(text, text_rect)
    
    else:  # Campaign Map
        try:
            background = pygame.image.load("./assets_webp/test_scene.webp")
            background = pygame.transform.smoothscale(background, screen_surface.get_size())
            screen_surface.blit(background, (0, 0))
        except Exception as e:
            screen_surface.fill((100, 150, 100))
            if pygame.font.get_init():
                font = pygame.font.Font(None, 74)
                text = font.render('Campaign Map', True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_surface.get_width()//2, screen_surface.get_height()//2))
                screen_surface.blit(text, text_rect)
    
    return screen_surface

def HOMMIV_main_loop():
    """Standalone execution loop with actual window."""
    global mouse_click_pos, last_click_time, window_surface
    
    initialize_hommiv() 
    
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if battle_sequence and battle_sequence_keys:
                    battle_sequence_keys(event, RPG_mode_toggle)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                current_time = time.time()
                if current_time - last_click_time > click_cooldown:
                    last_click_time = current_time
                    mouse_click_pos = event.pos
            
            if manager:
                manager.process_events(event)
        
        if manager:
            manager.update(time_delta)
        
        HOMMIV_update_frame(window_surface, time_delta)
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__':
    HOMMIV_main_loop()
