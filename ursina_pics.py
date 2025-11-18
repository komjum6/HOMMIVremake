# File: ursina_pics.py
import json
import mmap
import numpy as np
from ursina import *
from OpenGL.GL import glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE
import time
from load_terrain import load_terrain, load_terrain_warp, apply_warp, generate_and_load_terrain

class CustomController(Entity):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app  # Store the Ursina app instance
        
        # Very important, the scale has a will of its own so you have to carry a stick and speak softly
        camera.ui.scale = (1, 1, 1)
        
        # Game state
        self.edit_mode = False
        self.selected_entity = None
        self.render_distance = 30
        self.gravity_enabled = False#True
        self.warp = False

        # Create UI elements with desired dimensions 
        desired_width = 280 
        desired_height = 40 
        scale_x = desired_width / window.size[0]
        scale_y = desired_height / window.size[1]
        
        # Create input fields with the calculated scale
        self.position_input = InputField(
            default_value='0,0,0',
            visible=False,
            parent=camera.ui,
            scale=(scale_x, scale_y),
            position=(0, 0)
        )
        self.size_input = InputField(
            default_value='1,1,1',
            visible=False,
            parent=camera.ui,
            scale=(scale_x, scale_y),
            position=(0, -0.05)
        )
      
        # Ground position and scale
        self.ground_position = (6, 0, 6)
        self.ground_scale = 3
        
        self.texture_paths = {
            'Pablo_img': './assets/map/Pablo_img.jpg',
            'pavement': './assets/map/pavement.jpg',
            'pavement2': './assets/map/pavement2.jpg',
            'grass': './assets/map/grass.jpg'
        }
        self.biome_percentages = { 
            'grass': 0.3, 
            'Pablo_img': 0.3, 
            'pavement': 0.2, 
            'pavement2': 0.2 
        }
        
        # Initialize terrain
        self.positions = [(-4, 0, -4), (0, 0, -3), (4, 0, -4)]
        self.sizes = [(4, 1, 4), (4, 1, 2), (4, 1, 4)]
        
        self.num_sections = len(self.texture_paths.keys())

        '''
        # Parameters
        self.num_sections_x = 30
        self.num_sections_z = 30
        self.tile_size = (4, 1, 4)
        position = (0, 0, 0)
        scale = 0.9
        max_height = 5
        texture_paths = self.texture_paths

        self.generate_and_load_terrain = generate_and_load_terrain

        # Generate and load terrain
        self.ground, self.ground_entities, self.positions = self.generate_and_load_terrain(
            self=self,
            num_sections_x=self.num_sections_x,
            num_sections_z=self.num_sections_z,
            tile_size=self.tile_size,
            position=position,
            scale=scale,
            texture_paths=texture_paths,
            max_height=max_height,
            biome_percentages=self.biome_percentages
        )
        '''
        
        # Parameters
        self.num_sections_x = 30
        self.num_sections_z = 30
        self.tile_size = (4, 1, 4)
        self.terrain_initial_position = Vec3(0, 0, 0) # Store as an attribute
        self.terrain_initial_scale = 0.9 # Store as an attribute
        max_height = 5
        texture_paths = self.texture_paths

        self.generate_and_load_terrain = generate_and_load_terrain

        # Generate and load terrain
        self.ground, self.ground_entities, self.positions = self.generate_and_load_terrain(
            self=self,
            num_sections_x=self.num_sections_x,
            num_sections_z=self.num_sections_z,
            tile_size=self.tile_size,
            position=self.terrain_initial_position, # Use the stored attribute
            scale=self.terrain_initial_scale,       # Use the stored attribute
            texture_paths=texture_paths,
            max_height=max_height,
            biome_percentages=self.biome_percentages
        )

        # Set up entity click handlers
        for entity in self.ground_entities:
            entity.on_click = lambda e=entity: self.on_entity_click(e)
            entity.hovered_color = color.green
        
        # Add decorative cubes
        self.decoration_positions = [(2, 0, 2), (6, 0, 6), (2, 0, 6), (6, 0, 2)]
        for pos in self.decoration_positions:
            Entity(position=Vec3(*pos), model='cube', color=color.green)
        
        # Load the skull model
        self.skull_entity = Entity(
            model=load_model('assets/map/skull_me_no_eyes_retopo_colored.obj'),
            texture=load_texture('assets/map/texture273.png'),
            position=Vec3(4, 2, 4),
            scale=(1,1,1)
        )
        
        # Set up lighting
        self.ambient_light = AmbientLight()
        self.ambient_light.color = color.rgb(150, 150, 150)
        self.directional_light = DirectionalLight()
        self.directional_light.look_at(Vec3(-1, -1, -1))
        
        # Memory-mapped files
        self.frame_mm = mmap.mmap(-1, 1000 * 800 * 4, access=mmap.ACCESS_WRITE, tagname='UrsinaMMap')
        self.key_mm = mmap.mmap(-1, 2048, access=mmap.ACCESS_READ, tagname='KeyMap')
        self.mouse_pos_mm = mmap.mmap(-1, 64, access=mmap.ACCESS_READ, tagname='MousePosMap')
        self.mouse_clicked_mm = mmap.mmap(-1, 84, access=mmap.ACCESS_WRITE, tagname='MouseClickedMap')
        self.mouse_hover_mm = mmap.mmap(-1, 84, access=mmap.ACCESS_READ, tagname='MouseHoverMap')
        self.minimap_mm = mmap.mmap(-1, 280 * 280 * 4, access=mmap.ACCESS_WRITE, tagname='MinimapMMap')
        
        # Controller settings
        self.speed = 5
        self.height = 1.1
        self.mouse_sensitivity = Vec2(0.2, 0.2)
        self.zoom_level = 10
        self.zoom_speed = 2.5
        self.mouse_pos = {'x': 0, 'y': 0, 'scroll_x': 0, 'scroll_y': 0}
        self.mouse_click = {'x_click': 0, 'y_click': 0, 'clicked': 0}
        self.mouse_hover = {'x_norm': 0, 'y_norm': 0, 'hovered': False}
        self.prev_mouse_pos = {'x': 0, 'y': 0}
        
        # State tracking
        self.v_pressed = False
        self.e_pressed = False
        self.m_pressed = False
        self.last_toggle_time_e = 0
        self.last_toggle_time_typing = 0
        self.toggle_delay_e = 1
        self.toggle_delay_typing = 0.1
        self.camera_angle = 0
        
        # Info text setup
        Text.default_resolution = 800 * Text.size
        self.info_text = Text(
            text='',
            position=(0, 0.1),
            origin=(0, 0),
            scale=1.0,
            color=color.white,
            visible=False
        )
        
        # Physics settings
        self.gravity = 0.5
        self.grounded = False
        self.jump_velocity = 0.2
        self.vertical_velocity = 0
        
        # Set up input handlers
        self.position_input.on_submit = self.update_entity_position
        self.size_input.on_submit = self.update_entity_size
        
        # Set up camera
        camera.position = self.skull_entity.position - self.skull_entity.forward * self.zoom_level + Vec3(0, self.height + 2, 0)
        
        # Initialize key states
        self.key_states = {chr(i): False for i in range(32, 127)}
        self.key_states.update({
            'tab': False, 'shift': False, 'ctrl': False, 'alt': False,
            'capslock': False, 'backspace': False, 'enter': False,
            'space': False, 'left': False, 'right': False, 'up': False, 'down': False,
            'esc': False, 'del': False
        })
        
        # Screenshot timing
        self.last_screenshot_time = time.time()
        self.screenshot_interval = 1/60
        
        # Apply any additional kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def set_ui_element_size(ui_element, desired_width, desired_height):
        """Set the scale of the UI element based on desired pixel dimensions."""
        screen_size = window.size

        # Calculate the required scale based on desired pixel dimensions
        scale_x = desired_width / screen_size[0]
        scale_y = desired_height / screen_size[1]

        # Set the scale
        ui_element.scale = (scale_x, scale_y)

        # Print debug information
        #print(f"Calculated scale: x={scale_x}, y={scale_y}")
        #print(f"Screen Size: {screen_size}")
        
    def get_pixel_position_and_size(self, ui_element):
        """Calculate the exact pixel position of a UI element."""
        screen_size = window.size

        # Get the world position of the UI element
        world_pos = ui_element.world_position

        # Convert the normalized world position to pixel coordinates
        pixel_x = int((world_pos[0] + 0.5) * screen_size[0])
        pixel_y = int((0.5 - world_pos[1]) * screen_size[1])
        
        # Calculate the width and height in pixels 
        width = int(ui_element.scale_x * screen_size[0]) 
        height = int(ui_element.scale_y * screen_size[1])
        
        # Debug information
        #print(f"Element Scale: (scale_x={ui_element.scale_x}, scale_y={ui_element.scale_y})")
        #print(f"Screen Size: {screen_size}")
        #print(f"Pixel Position: ({pixel_x}, {pixel_y}), Size: ({width}, {height})")

        return pixel_x, pixel_y, width, height
        
    def update_entity_fields(self, entity):
        """Update input fields to display the selected entity's current position and scale."""
        self.position_input.text = f"{round(self.positions[self.ground_entities.index(entity)][0], 1)},{round(self.positions[self.ground_entities.index(entity)][1], 1)},{round(self.positions[self.ground_entities.index(entity)][2], 1)}"
        self.size_input.text = f"{round(self.sizes[self.ground_entities.index(entity)][0], 1)},{round(self.sizes[self.ground_entities.index(entity)][1], 1)},{round(self.sizes[self.ground_entities.index(entity)][2], 1)}"
        self.position_input.visible = True
        self.size_input.visible = True

    def on_entity_click(self, entity):
        """Handle entity selection for editing."""
        if self.edit_mode:
            self.selected_entity = entity
            self.update_entity_fields(entity)

    def update_entity_position(self, value):
        """Update the selected entity's position from the input field."""
        if self.selected_entity and self.edit_mode:
            try:
                x, y, z = map(float, value.split(','))
                self.selected_entity.position = Vec3(x, y, z)
                self.update_entity_fields(self.selected_entity)
            except ValueError:
                print("Invalid position input")

    def update_entity_size(self, value):
        """Update the selected entity's scale from the input field."""
        if self.selected_entity and self.edit_mode:
            try:
                sx, sy, sz = map(float, value.split(','))
                self.selected_entity.scale = Vec3(sx, sy, sz)
                self.update_entity_fields(self.selected_entity)
            except ValueError:
                print("Invalid size input")

    def toggle_edit_mode(self):
        """Toggle edit mode and update UI visibility."""
        self.edit_mode = not self.edit_mode
        self.gravity_enabled = not self.edit_mode
        self.info_text.visible = self.edit_mode
        self.position_input.visible = self.edit_mode
        self.size_input.visible = self.edit_mode
        self.refresh_ground_entities()

    def refresh_ground_entities(self):
        """Refresh ground entity visibility based on render distance in edit mode."""
        for entity in self.ground_entities:
            entity.visible = self.edit_mode and distance(self.skull_entity.position, entity.position) < self.render_distance
            entity.color = color.green if entity.hovered else color.white

    def save_screenshot(self):
        """Save the current frame to memory-mapped file."""
        self.app.graphicsEngine.renderFrame()
        pixels = np.zeros((800, 1000, 4), dtype=np.uint8)
        glReadPixels(0, 0, 1000, 800, GL_RGBA, GL_UNSIGNED_BYTE, pixels)
        pixels = np.flipud(pixels)
        self.frame_mm.seek(0)
        self.frame_mm.write(pixels.flatten())

    def is_valid_json(self, data):
        """Validate and parse JSON data."""
        try:
            parsed = json.loads(data)
            if all(k in parsed for k in self.key_states.keys()):
                return parsed
        except ValueError:
            pass
        return None

    def handle_input(self):
        """Handle keyboard input."""
        current_time = time.time()
        
        # Read key states from memory map
        self.key_mm.seek(0)
        key_data = self.key_mm.read(2048).decode('utf-8').strip('\x00')
        new_key_states = self.is_valid_json(key_data)
        
        if new_key_states:
            self.key_states = new_key_states

        # Handle edit mode toggle
        if self.key_states.get('i', False) and ((current_time - self.last_toggle_time_e) > self.toggle_delay_e):
            self.last_toggle_time_e = current_time
            self.toggle_edit_mode()

        # Handle movement
        direction = Vec3(0, 0, 0)
        if self.key_states.get('e'):
            direction += self.skull_entity.forward
        if self.key_states.get('d'):
            direction -= self.skull_entity.forward
        if self.key_states.get('s'):
            direction -= self.skull_entity.right
        if self.key_states.get('f'):
            direction += self.skull_entity.right

        self.skull_entity.position += direction * self.speed * time.dt

        # Handle jump
        if self.key_states.get('space') and self.grounded:
            self.vertical_velocity = self.jump_velocity
            self.grounded = False

        # Handle V key for camera rotation
        v = self.key_states.get('v')
        if v and not self.v_pressed:
            self.v_pressed = True
        elif not v and self.v_pressed:
            self.v_pressed = False

    def process_mouse(self):
        """Handle mouse input and camera updates."""
        # Read mouse position
        self.mouse_pos_mm.seek(0)
        mouse_data = self.mouse_pos_mm.read(64).decode('utf-8').strip('\x00')
        try:
            self.mouse_pos = json.loads(mouse_data)
        except json.JSONDecodeError:
            return

        # Handle mouse movement
        mouse_dx = self.mouse_pos['x'] - self.prev_mouse_pos['x']
        mouse_dy = self.mouse_pos['y'] - self.prev_mouse_pos['y']
        self.prev_mouse_pos = self.mouse_pos

        # Update entity rotation based on mouse movement
        self.skull_entity.rotation_y += mouse_dx * self.mouse_sensitivity[0]
        self.skull_entity.rotation_x = clamp(
            self.skull_entity.rotation_x - mouse_dy * self.mouse_sensitivity[1],
            -45,
            45
        )
        
        # Check if the mouse is at the screen's edges 
        if self.mouse_pos['x'] <= 0: # Left edge 
            self.skull_entity.rotation_y -= self.mouse_sensitivity[0]*2.5
        elif self.mouse_pos['x']/800 >= 0.99: # Right edge 
            self.skull_entity.rotation_y += self.mouse_sensitivity[0]*2.5

        # Handle zoom with scroll wheel
        scroll_y = self.mouse_pos.get('scroll_y', 0)
        if scroll_y != 0:
            self.zoom_level = max(5, min(15, self.zoom_level - scroll_y * (self.zoom_speed / 100)))

        # Update camera position
        self.update_camera_position()

        # Process clicks
        self.process_click()
        
        # Process hover
        self.process_hover()

    def process_click(self):
        """Handle mouse click detection and entity selection."""
        self.mouse_clicked_mm.seek(0)
        click_data = self.mouse_clicked_mm.read(84).decode('utf-8').strip('\x00')

        try:
            click_info = json.loads(click_data)
            if click_info.get('clicked'):
                if self.edit_mode:
                
                    x_click = click_info.get('x_click', 0.5)
                    y_click = click_info.get('y_click', 0.5)

                    screen_x = (x_click * 2) - 1
                    screen_y = (y_click * 2) - 1

                    # Convert screen coordinates to window coordinates 
                    window_x = (screen_x + 1) * window.fullscreen_size[0] / 2 
                    window_y = (screen_y + 1) * window.fullscreen_size[1] / 2 
                    
                    # Deactivate both input fields initially 
                    self.position_input.active = False 
                    self.size_input.active = False 
                    
                    # Check if click is within position_input bounds 
                    if self.is_within_bounds(self.position_input, window_x, window_y): 
                        self.position_input.active = True 
                        #print('pos')
                    # Check if click is within size_input bounds 
                    elif self.is_within_bounds(self.size_input, window_x, window_y) and not self.position_input.active: 
                        self.size_input.active = True
                        #print('size')
                    else:
                        ray_origin = camera.position
                        
                        fov_factor = math.tan(math.radians(camera.fov) * 0.5)
                        aspect_ratio = window.aspect_ratio
                        cursor_offset = Vec3(screen_x * aspect_ratio * fov_factor, -screen_y * fov_factor, 0)
                        ray_direction = (
                            camera.forward * self.zoom_level + cursor_offset +
                            camera.right * screen_x * aspect_ratio * fov_factor +
                            camera.up * screen_y * fov_factor
                        ).normalized()

                        if ray_origin is not None and ray_direction is not None:
                            hit_info = raycast(
                                origin=ray_origin,
                                direction=ray_direction,
                                distance=self.render_distance,
                                traverse_target=scene
                            )
                            if hit_info.hit:
                                self.selected_entity = hit_info.entity
                                self.update_entity_fields(self.selected_entity)

                self.mouse_clicked_mm.seek(0)
                self.mouse_clicked_mm.write(
                    json.dumps({'clicked': False}).ljust(84, '\x00').encode('utf-8')
                )
        except json.JSONDecodeError:
            pass

    def update_ground_entities(self): 
        """Update the ground entities based on the input fields.""" 
        position_values = [float(x) for x in self.position_input.text.split(',')] 
        size_values = [float(x) for x in self.size_input.text.split(',')] 
        
        self.selected_entity.position = Vec3(*position_values) * self.ground_scale + self.ground_position 
        self.selected_entity.scale = Vec3(*size_values) * self.ground_scale
        
        #print(f'{self.selected_entity.position}')
        #print(f'{self.selected_entity.scale}')
        
        # Update corresponding part of the ground entity
        for entity in self.ground_entities: 
            if entity == self.selected_entity: 
                entity_index = self.ground_entities.index(entity) 
                pos = Vec3(*position_values)
                size = Vec3(*size_values)
                uv = self.ground.model.uvs[entity_index * 4] # Assuming uv coordinates are correctly mapped 
                
                # Update ground vertices for the selected entity 
                self.ground.model.vertices[entity_index * 4] = pos 
                self.ground.model.vertices[entity_index * 4 + 1] = pos + Vec3(size.x, 0, 0) 
                self.ground.model.vertices[entity_index * 4 + 2] = pos + Vec3(size.x, 0, size.z) 
                self.ground.model.vertices[entity_index * 4 + 3] = pos + Vec3(0, 0, size.z) 
                self.ground.model.generate()

    def update_ground_entities_warp(self):
        """Update the ground entities based on the input fields."""
        position_values = [float(x) for x in self.position_input.text.split(',')]
        size_values = [float(x) for x in self.size_input.text.split(',')]

        # Update selected entity's position and scale
        self.selected_entity.position = Vec3(*position_values) * self.ground_scale + self.ground_position
        self.selected_entity.scale = Vec3(*size_values) * self.ground_scale

        # Update corresponding part of the ground entity
        for entity in self.ground_entities:
            if entity == self.selected_entity:
                entity_index = self.ground_entities.index(entity)
                pos = Vec3(*position_values)
                size = Vec3(*size_values)
                uv = self.ground.model.uvs[entity_index * 4]  # Assuming uv coordinates are correctly mapped

                # Warp vertices based on the corresponding warp points from the list
                warped_vertices = []
                original_vertices = [
                    Vec3(pos.x, pos.y, pos.z),
                    Vec3(pos.x + size.x, pos.y, pos.z),
                    Vec3(pos.x + size.x, pos.y, pos.z + size.z),
                    Vec3(pos.x, pos.y, pos.z + size.z),
                ]

                warp_points = self.warp_points_list[entity_index]  # Get the warp points for this entity

                for vert in original_vertices:
                    norm_x = (vert.x - pos.x) / size.x
                    norm_y = (vert.z - pos.z) / size.z
                    warped_x, warped_y, warped_z = apply_warp((norm_x, norm_y), warp_points)
                    warped_vert = Vec3(
                        pos.x + warped_x * size.x,
                        vert.y + warped_z * size.y,
                        pos.z + warped_y * size.z
                    )
                    warped_vertices.append(warped_vert)

                # Update ground vertices for the selected entity with warped vertices
                self.ground.model.vertices[entity_index * 4] = warped_vertices[0]
                self.ground.model.vertices[entity_index * 4 + 1] = warped_vertices[1]
                self.ground.model.vertices[entity_index * 4 + 2] = warped_vertices[2]
                self.ground.model.vertices[entity_index * 4 + 3] = warped_vertices[3]
                self.ground.model.generate()

    def is_within_bounds(self, input_field, x, y):
        """Check if the given coordinates (x, y) are within the bounds of the input field."""
        # Convert input field's screen position to pixel coordinates   
        field_center_x, field_center_y, field_width, field_height = self.get_pixel_position_and_size(input_field) 

        # Adjust dimensions based on actual scale in pixels
        #field_width = 280 
        #field_height = 40 

        # Calculate bounds in absolute pixel coordinates
        x_min = field_center_x - field_width / 2
        x_max = field_center_x + field_width / 2
        y_min = field_center_y - field_height / 2
        y_max = field_center_y + field_height / 2

        # Debugging boundary values
        #print(f"Field Center: ({field_center_x:.2f}, {field_center_y:.2f})")
        #print(f"Field Dimensions: {field_width:.2f} x {field_height:.2f}")
        #print(f"Bounds X: {x_min:.2f} to {x_max:.2f}")
        #print(f"Bounds Y: {y_min:.2f} to {y_max:.2f}")
        #print(f"Click Coordinates: ({x:.2f}, {y:.2f})")

        # Check if the click is within bounds
        return x_min <= x <= x_max and y_min <= y <= y_max

    def process_hover(self):
        """Handle hover detection and effects."""
        self.mouse_hover_mm.seek(0)
        hover_data = self.mouse_hover_mm.read(84).decode('utf-8').strip('\x00')

        try:
            hover_info = json.loads(hover_data)
            if hover_info.get('hovered'):
                norm_x = hover_info.get('x_norm', 0.5)
                norm_y = hover_info.get('y_norm', 0.5)

                screen_x = (norm_x * 2.0) - 1.0
                screen_y = 1.0 - (norm_y * 2.0)

                ray_origin = camera.world_position

                fov_factor = math.tan(math.radians(camera.fov) * 0.5)
                aspect_ratio = window.aspect_ratio
                cursor_offset = Vec3(screen_x * aspect_ratio * fov_factor, -screen_y * fov_factor, 0)
                ray_direction = (
                    camera.forward * self.zoom_level + cursor_offset +
                    camera.right * screen_x * aspect_ratio * fov_factor +
                    camera.up * screen_y * fov_factor
                ).normalized()

                hit_info = raycast(
                    origin=ray_origin,
                    direction=ray_direction,
                    distance=self.render_distance,
                    traverse_target=scene,
                    debug=False
                )

                for entity in self.ground_entities:
                    if hit_info.hit and hit_info.entity == entity:
                        entity.color = color.yellow
                        if not hasattr(entity, 'original_y'):
                            entity.original_y = entity.y
                        entity.y = entity.original_y + 0.1
                    else:
                        entity.color = color.white
                        if hasattr(entity, 'original_y'):
                            entity.y = entity.original_y
            else:
                for entity in self.ground_entities:
                    entity.color = color.white
                    if hasattr(entity, 'original_y'):
                        entity.y = entity.original_y
        except json.JSONDecodeError:
            pass

    def update_camera_position(self):
        """Update the camera position based on player movement and view mode."""
        if self.v_pressed:
            scroll_x = self.mouse_pos.get('scroll_x', 0)
            self.camera_angle += scroll_x * 0.01
            x_offset = self.zoom_level * math.cos(self.camera_angle)
            z_offset = self.zoom_level * math.sin(self.camera_angle)
            target_position = self.skull_entity.position + Vec3(x_offset, self.height + 2, z_offset)
            if scroll_x != 0:
                camera.position = lerp(camera.position, target_position, 0.1)
                camera.position = Vec3(
                    camera.position.x - self.skull_entity.forward.x / self.zoom_level,
                    camera.position.y,
                    camera.position.z
                )
        else:
            camera.position = (
                self.skull_entity.position -
                self.skull_entity.forward * self.zoom_level +
                Vec3(0, self.height + 2, 0)
            )
        camera.rotation = Vec3(0, 0, 0)
        camera.look_at(self.skull_entity.position)

    def check_ground(self):
        """Check if the player is grounded."""
        ray = raycast(
            self.skull_entity.world_position + Vec3(0, self.height, 0),
            Vec3(0, -1, 0),
            traverse_target=scene,
            ignore=[self]
        )
        if ray.hit:
            self.skull_entity.y = max(ray.world_point.y + self.height, self.skull_entity.y)
            self.grounded = ray.distance <= self.height + 0.1
        else:
            self.grounded = False

    def update_physics(self):
        """Update physics simulation."""
        if self.gravity_enabled:
            self.vertical_velocity -= self.gravity * time.dt
            self.skull_entity.y += self.vertical_velocity
            self.check_ground()
            if self.grounded and self.vertical_velocity < 0:
                self.vertical_velocity = 0

    def type_in_active_input(self):
        """Type the active keys into the active input field."""
        active_input = None
        if self.position_input.active:
            active_input = self.position_input
        elif self.size_input.active:
            active_input = self.size_input

        if active_input:
            for key, state in self.key_states.items():
                if state:
                    if key == 'backspace':
                        active_input.text = active_input.text[:-1]
                    elif key == 'enter':
                        active_input.active = False
                        self.positions
                        self.sizes
                        if self.warp:
                            self.update_ground_entities_warp() # Call to update ground entities
                        else:
                            self.update_ground_entities()
                    else:
                        active_input.text += key
                    # Reset the key state after typing
                    self.key_states[key] = False
    '''
    def update_minimap(self):
        # Calculate skull's position in terms of grid coordinates
        # These can be outside the [0, num_sections-1] range if the skull goes off-terrain
        grid_x = (self.skull_entity.position.x - self.terrain_initial_position.x) / (self.tile_size[0] * self.terrain_initial_scale)
        grid_z = (self.skull_entity.position.z - self.terrain_initial_position.z) / (self.tile_size[2] * self.terrain_initial_scale)

        # Calculate normalized position, centering the dot within the tile representation
        # Add 0.5 to grid_x and grid_z to get the center of the current tile
        # Then divide by the total number of sections to get a normalized value from 0 to 1
        normalized_x_centered = (grid_x + 0.5) / self.num_sections_x
        normalized_z_centered = (grid_z + 0.5) / self.num_sections_z

        # Clamp the normalized position to ensure the dot stays within the minimap's logical bounds [0, 1]
        normalized_grid_x = clamp(normalized_x_centered, 0, 1)
        normalized_grid_z = clamp(normalized_z_centered, 0, 1)

        # The dot's position is relative to its parent (self.minimap),
        # where the parent's local coordinates range from -0.5 to 0.5.
        # So, map normalized_grid_x/z (0 to 1) to (-0.5 to 0.5).
        dot_pos_x = (normalized_grid_x - 0.5)
        dot_pos_y = (normalized_grid_z - 0.5)

        # Update the dot's position on the minimap
        self.dot.position = Vec2(dot_pos_x, dot_pos_y)
    '''
    
    def update_minimap(self):
        # Calculate skull's position in terms of grid coordinates
        grid_x = (self.skull_entity.position.x - self.terrain_initial_position.x) / (self.tile_size[0] * self.terrain_initial_scale)
        grid_z = (self.skull_entity.position.z - self.terrain_initial_position.z) / (self.tile_size[2] * self.terrain_initial_scale)

        # Calculate normalized position
        normalized_x_centered = (grid_x + 0.5) / self.num_sections_x
        normalized_z_centered = (grid_z + 0.5) / self.num_sections_z

        # Clamp the normalized position
        normalized_grid_x = clamp(normalized_x_centered, 0, 1)
        normalized_grid_z = clamp(normalized_z_centered, 0, 1)

        # Export minimap with player dot to Kivy
        if hasattr(self, 'minimap_pil_image'):
            from PIL import Image as PILImage, ImageDraw
            
            # Create a copy of the minimap
            minimap_with_dot = self.minimap_pil_image.copy()
            draw = ImageDraw.Draw(minimap_with_dot)
            
            # Calculate dot position in pixels
            dot_x = int(normalized_grid_x * 280)
            #dot_y = int(normalized_grid_z * 280)
            dot_y = 280 - int(normalized_grid_z * 280)
            
            # Draw white dot (5 pixel radius)
            dot_radius = 5
            draw.ellipse(
                [(dot_x - dot_radius, dot_y - dot_radius), 
                 (dot_x + dot_radius, dot_y + dot_radius)],
                fill=(255, 255, 255, 255)
            )
            
            # Convert to numpy and write to shared memory
            minimap_array = np.array(minimap_with_dot)
            self.minimap_mm.seek(0)
            self.minimap_mm.write(minimap_array.flatten().tobytes())

    def update(self):
        """Main update loop."""
        current_time = time.time()
        
        # Update info text
        self.info_text.text = str(self.skull_entity.position)
        
        # Handle input
        self.handle_input()
        self.process_mouse()
        
        # Update physics
        self.update_physics()
        
        # Update minimap
        self.update_minimap()
        
        # Type when an input screen is active
        if ((current_time - self.last_toggle_time_typing) > self.toggle_delay_typing):
            self.last_toggle_time_typing = current_time
            self.type_in_active_input()
        
        # Take screenshot if needed
        if current_time - self.last_screenshot_time >= self.screenshot_interval:
            self.save_screenshot()
            self.last_screenshot_time = current_time

    def cleanup(self):
        """Clean up memory-mapped files."""
        self.frame_mm.close()
        self.key_mm.close()
        self.mouse_pos_mm.close()
        self.mouse_clicked_mm.close()
        self.mouse_hover_mm.close()
        self.minimap_mm.close() # ADDED

# Main app setup
app = Ursina(window_type='offscreen', size=(1000, 800))
controller = CustomController(app)

# Set up application update and run
def update():
    controller.update()

controller.app.update = update
controller.app.run()

# Clean up
controller.cleanup()
