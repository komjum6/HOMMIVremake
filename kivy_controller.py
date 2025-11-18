import os
import json
import mmap
import numpy as np
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.graphics.texture import Texture as KivyTexture
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from PIL import Image
import subprocess
from pynput import mouse
import time
import sys

class KivyUrsinaApp(App):
    def build(self):
        print("=== KivyUrsinaApp Build Started ===")
        Window.show_cursor = True
        
        # Main layout - horizontal split
        self.main_layout = BoxLayout(orientation='horizontal')
        
        # Left side - game display
        self.game_layout = FloatLayout()
        self.width, self.height = 1000, 800
        self.kivy_texture = KivyTexture.create(size=(self.width, self.height), colorfmt='rgba')
        self.image = KivyImage(texture=self.kivy_texture, size_hint=(1.0, 1.0))
        self.game_layout.add_widget(self.image)
        
        # Top button on game display
        top_button = Button(text="Screenshot", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'top': 1})
        top_button.bind(on_press=self.on_button_click)
        self.game_layout.add_widget(top_button)
        
        # Game control buttons
        self.haven_town_btn = Button(text="Haven Town", size_hint=(None, None), size=(300, 150), pos=(100, 100), background_color=(0.2, 0.6, 0.2, 1))
        self.haven_town_btn.bind(on_press=self.on_haven_town_click)
        
        self.campaign_map_btn = Button(text="Campaign Map", size_hint=(None, None), size=(300, 150), pos=(100, 100), background_color=(0.6, 0.2, 0.2, 1))
        self.campaign_map_btn.bind(on_press=self.on_campaign_map_click)
        
        self.haven_town_visible = False
        self.campaign_map_visible = False
        
        # Right side panel - 300px wide
        self.right_panel = BoxLayout(orientation='vertical', size_hint=(None, 1), width=300, padding=10, spacing=10)
        
        # Minimap section at top
        minimap_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=320)
        
        # Minimap title
        minimap_title = Label(text="Minimap", size_hint=(1, None), height=30, font_size='18sp', bold=True)
        minimap_container.add_widget(minimap_title)
        
        # Minimap display area with background
        self.minimap_display = FloatLayout(size_hint=(1, 1))
        with self.minimap_display.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.minimap_bg = Rectangle(pos=self.minimap_display.pos, size=self.minimap_display.size)
        self.minimap_display.bind(pos=self.update_minimap_bg, size=self.update_minimap_bg)
        
        # Minimap texture (280x280)
        self.minimap_size = 280
        self.minimap_texture = KivyTexture.create(size=(self.minimap_size, self.minimap_size), colorfmt='rgba')
        self.minimap_image = KivyImage(
            texture=self.minimap_texture,
            size_hint=(None, None),
            size=(self.minimap_size, self.minimap_size),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.minimap_display.add_widget(self.minimap_image)
        
        minimap_container.add_widget(self.minimap_display)
        self.right_panel.add_widget(minimap_container)
        
        # Separator line
        #separator = Label(text="─" * 30, size_hint=(1, None), height=20, font_size='12sp')
        #self.right_panel.add_widget(separator)
        
        # Controls section
        controls_title = Label(text="Controls & Features", size_hint=(1, None), height=30, font_size='16sp', bold=True)
        self.right_panel.add_widget(controls_title)
        
        # Future feature buttons
        placeholder_btn1 = Button(text="Future Feature 1", size_hint=(1, None), height=60, disabled=True, background_color=(0.3, 0.3, 0.3, 1))
        placeholder_btn2 = Button(text="Future Feature 2", size_hint=(1, None), height=60, disabled=True, background_color=(0.3, 0.3, 0.3, 1))
        placeholder_btn3 = Button(text="Future Feature 3", size_hint=(1, None), height=60, disabled=True, background_color=(0.3, 0.3, 0.3, 1))
        
        self.right_panel.add_widget(placeholder_btn1)
        self.right_panel.add_widget(placeholder_btn2)
        self.right_panel.add_widget(placeholder_btn3)
        
        # Spacer to push everything to top
        self.right_panel.add_widget(Label())
        
        # Add both sides to main layout
        self.main_layout.add_widget(self.game_layout)
        self.main_layout.add_widget(self.right_panel)
        
        # Set window size
        Window.size = (1300, 800)
        
        # Initialize HOMMIV
        from HOMMIV import initialize_hommiv_offscreen
        initialize_hommiv_offscreen(0, 0)
        
        # Memory-mapped files
        self.frame_mm = mmap.mmap(-1, self.width * self.height * 4, tagname='UrsinaMMap')
        self.key_mm = mmap.mmap(-1, 2048, tagname='KeyMap')
        self.mouse_pos_mm = mmap.mmap(-1, 64, tagname='MousePosMap')
        self.mouse_clicked_mm = mmap.mmap(-1, 84, tagname='MouseClickedMap')
        self.mouse_hover_mm = mmap.mmap(-1, 84, tagname='MouseHoverMap')
        self.minimap_mm = mmap.mmap(-1, 280 * 280 * 4, tagname='MinimapMMap')
        
        initial_color = np.full((self.height, self.width, 4), [50, 50, 50, 255], dtype=np.uint8)
        self.frame_mm.write(initial_color.tobytes())
        self.frame_mm.seek(0)
        
        self.key_states = {chr(i): False for i in range(32, 127)}
        self.key_states.update({'space': False, 'tab': False, 'shift': False, 'ctrl': False, 'alt': False, 'capslock': False, 'backspace': False, 'enter': False, 'left': False, 'right': False, 'up': False, 'down': False, 'esc': False, 'del': False, 'm': False})
        self.update_keymap()
        
        self.mouse_pos_mm.write(json.dumps({'x': 0, 'y': 0, 'scroll': 0}).encode('utf-8').ljust(64, b'\x00'))
        self.mouse_pos_mm.seek(0)
        self.mouse_clicked_mm.write(json.dumps({'x_click': 0, 'y_click': 0, 'clicked': False}).encode('utf-8').ljust(84, b'\x00'))
        self.mouse_clicked_mm.seek(0)
        self.mouse_hover_mm.write(json.dumps({'x_norm': 0, 'y_norm': 0, 'hovered': False}).encode('utf-8').ljust(84, b'\x00'))
        self.mouse_hover_mm.seek(0)
        
        # Start Ursina process
        self.ursina_process = subprocess.Popen(['python', 'ursina_pics.py'])
        time.sleep(2.0)
        
        self.adventuremap_running = False
        self.pygame_screen = None
        self.pygame = None
        self.HOMMIV_module = None
        self.HOMMIV_update_frame = None
        self.shared_array = None
        self.ursina_ready = False
        self.startup_frames = 0
        
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up, mouse_pos=self.on_mouse_move, on_mouse_down=self.on_mouse_click)
        self.mouse_listener = mouse.Listener(on_scroll=self.on_mouse_wheel)
        self.mouse_listener.start()
        
        Clock.schedule_interval(self.update_ursina_texture, 1 / 60)
        Clock.schedule_interval(self.update_minimap_from_ursina, 1 / 10)
        
        print("=== KivyUrsinaApp Build Complete ===")
        return self.main_layout

    def update_minimap_bg(self, instance, value):
        """Update minimap background rectangle when size/position changes."""
        self.minimap_bg.pos = instance.pos
        self.minimap_bg.size = instance.size

    def update_minimap_from_ursina(self, dt):
        """Read minimap data from Ursina shared memory."""
        try:
            self.minimap_mm.seek(0)
            data = self.minimap_mm.read(280 * 280 * 4)
            
            if not data:
                print("Kivy Minimap Debug: No data read from minimap_mm.")
                return
            
            if len(data) != 280 * 280 * 4:
                print(f"Kivy Minimap Debug: Incorrect data length from minimap_mm. Expected {280*280*4}, got {len(data)}")
                return

            minimap_array = np.frombuffer(data, dtype=np.uint8).reshape((280, 280, 4))
            self.minimap_texture.blit_buffer(minimap_array.flatten(), colorfmt='rgba', bufferfmt='ubyte')
            self.minimap_image.texture = self.minimap_texture
            # print("Kivy Minimap Debug: Minimap texture updated successfully.") # Too chatty, keep commented unless needed

        except Exception as e:
            print(f"Kivy Minimap Error: {e}")
            import traceback
            traceback.print_exc()
            # Optionally, fill the minimap with a distinct error color
            # error_data = np.full((self.minimap_size, self.minimap_size, 4), [255, 0, 0, 255], dtype=np.uint8)
            # self.minimap_texture.blit_buffer(error_data.flatten(), colorfmt='rgba', bufferfmt='ubyte')
            # self.minimap_image.texture = self.minimap_texture

    def on_haven_town_click(self, instance):
        print("=== Kivy: Haven Town button clicked! ===")
        if self.HOMMIV_module:
            self.HOMMIV_module.haven_town_toggle()
            self.update_button_visibility()

    def on_campaign_map_click(self, instance):
        print("=== Kivy: Campaign Map button clicked! ===")
        if self.HOMMIV_module:
            self.HOMMIV_module.campaign_map_toggle()
            self.update_button_visibility()

    def update_button_visibility(self):
        if self.adventuremap_running and self.HOMMIV_module:
            campaign_map_state = self.HOMMIV_module.campaign_map
            haven_town_state = self.HOMMIV_module.haven_town
            
            if self.haven_town_visible:
                self.game_layout.remove_widget(self.haven_town_btn)
                self.haven_town_visible = False
            if self.campaign_map_visible:
                self.game_layout.remove_widget(self.campaign_map_btn)
                self.campaign_map_visible = False
            
            if campaign_map_state:
                self.game_layout.add_widget(self.haven_town_btn)
                self.haven_town_visible = True
            elif haven_town_state:
                self.game_layout.add_widget(self.campaign_map_btn)
                self.campaign_map_visible = True
        else:
            if self.haven_town_visible:
                self.game_layout.remove_widget(self.haven_town_btn)
                self.haven_town_visible = False
            if self.campaign_map_visible:
                self.game_layout.remove_widget(self.campaign_map_btn)
                self.campaign_map_visible = False

    def on_key_down(self, window, key, *args):
        key_name = Window._system_keyboard.keycode_to_string(key)
        special_key_map = {'spacebar': 'space', 'capslock': 'capslock', 'escape': 'esc', 'delete': 'del', 'enter': 'enter', 'backspace': 'backspace'}
        if key_name in special_key_map:
            key_name = special_key_map[key_name]
        if key_name and key_name in self.key_states and not self.key_states[key_name]:
            self.key_states[key_name] = True
            self.update_keymap()
            if key_name == 'p':
                self.adventuremap_running = not self.adventuremap_running
                print(f"=== Kivy: 'p' pressed - Adventure map running: {self.adventuremap_running} ===")
                if self.adventuremap_running:
                    if self.pygame is None:
                        print("Kivy: Importing pygame and HOMMIV...")
                        import pygame
                        self.pygame = pygame
                        import HOMMIV
                        self.HOMMIV_module = HOMMIV
                        self.HOMMIV_update_frame = HOMMIV.HOMMIV_update_frame
                        if not self.pygame.get_init():
                            self.pygame.init()
                        self.HOMMIV_module.initialize_hommiv_offscreen(self.width, self.height)
                        print("Kivy: Pygame and HOMMIV initialized successfully.")
                    self.pygame_screen = self.pygame.Surface((self.width, self.height))
                self.update_button_visibility()

    def on_key_up(self, window, key, *args):
        key_name = Window._system_keyboard.keycode_to_string(key)
        special_key_map = {'spacebar': 'space', 'capslock': 'capslock', 'escape': 'esc', 'delete': 'del', 'enter': 'enter', 'backspace': 'backspace'}
        if key_name in special_key_map:
            key_name = special_key_map[key_name]
        if key_name and key_name in self.key_states and self.key_states[key_name]:
            self.key_states[key_name] = False
            self.update_keymap()

    def on_mouse_move(self, window, pos):
        norm_x = pos[0] / self.image.width
        norm_y = pos[1] / self.image.height
        hovered = 0 <= norm_x <= 1 and 0 <= norm_y <= 1
        self.mouse_hover_mm.seek(0)
        self.mouse_hover_mm.write(json.dumps({'x_norm': norm_x, 'y_norm': norm_y, 'hovered': hovered}).encode('utf-8').ljust(84, b'\x00'))
        self.mouse_hover_mm.flush()
        self.mouse_pos_mm.seek(0)
        self.mouse_pos_mm.write(json.dumps({'x': pos[0], 'y': pos[1], 'scroll': 0}).encode('utf-8').ljust(64, b'\x00'))
        self.mouse_pos_mm.flush()

    def on_mouse_wheel(self, x, y, dx, dy):
        self.mouse_pos_mm.seek(0)
        self.mouse_pos_mm.write(json.dumps({'x': Window.mouse_pos[0], 'y': Window.mouse_pos[1], 'scroll_x': dx, 'scroll_y': dy}).encode('utf-8').ljust(64, b'\x00'))
        self.mouse_pos_mm.flush()

    def on_mouse_click(self, *args):
        click_x, click_y = args[1], args[2]
        norm_x = click_x / self.image.width
        norm_y = click_y / self.image.height
        self.mouse_clicked_mm.seek(0)
        self.mouse_clicked_mm.write(json.dumps({'x_click': norm_x, 'y_click': norm_y, 'clicked': True}).encode('utf-8').ljust(84, b'\x00'))
        self.mouse_clicked_mm.flush()

    def update_keymap(self):
        self.key_mm.seek(0)
        self.key_mm.write(json.dumps(self.key_states).encode('utf-8').ljust(2048, b'\x00'))
        self.key_mm.flush()

    def update_ursina_texture(self, *args):
        if self.adventuremap_running:
            self.run_adventuremap_frame()
        else:
            try:
                if self.startup_frames < 120:
                    self.startup_frames += 1
                    return
                if not self.ursina_ready:
                    self.ursina_ready = True
                self.frame_mm.seek(0)
                data = self.frame_mm.read(self.width * self.height * 4)
                if data and len(data) == self.width * self.height * 4:
                    self.shared_array = np.flipud(np.frombuffer(data, dtype=np.uint8).reshape((self.height, self.width, 4)))
                    self.kivy_texture.blit_buffer(self.shared_array.flatten(), colorfmt='rgba', bufferfmt='ubyte')
                    self.image.texture = self.kivy_texture
                    self.image.canvas.ask_update()
            except Exception as e:
                print(f"Kivy: Error updating Ursina texture: {e}")
                pass

    def run_adventuremap_frame(self):
        if self.pygame is None or self.HOMMIV_update_frame is None:
            return
        if self.pygame_screen is None:
            self.pygame_screen = self.pygame.Surface((self.width, self.height))
        self.pygame_screen = self.HOMMIV_update_frame(self.pygame_screen, 1/60.0)
        flipped_surface = self.pygame.transform.flip(self.pygame_screen, False, True)
        pygame_string = self.pygame.image.tostring(flipped_surface, 'RGBA')
        pil_image = Image.frombytes('RGBA', (self.width, self.height), pygame_string)
        self.update_kivy_texture(pil_image)

    def update_kivy_texture(self, pil_image):
        texture_data = pil_image.tobytes()
        self.kivy_texture.blit_buffer(texture_data, colorfmt='rgba', bufferfmt='ubyte')
        self.image.texture = self.kivy_texture
        self.image.canvas.ask_update()

    def on_button_click(self, instance):
        if not self.adventuremap_running and self.shared_array is not None:
            Image.fromarray(self.shared_array, 'RGBA').save('saved_image.png')
            print("Screenshot saved")

    def show_popup(self, message):
        popup_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text='Close', size_hint=(1, 0.2))
        close_button.bind(on_press=self.dismiss_popup)
        popup_layout.add_widget(close_button)
        self.popup = Popup(title='Toggle', content=popup_layout, size_hint=(0.6, 0.4))
        self.popup.open()

    def dismiss_popup(self, instance):
        self.popup.dismiss()
        self.popup.content.clear_widgets()

    def on_stop(self):
        self.ursina_process.terminate()
        self.frame_mm.close()
        self.key_mm.close()
        self.mouse_pos_mm.close()
        self.mouse_clicked_mm.close()
        self.minimap_mm.close()
        self.mouse_listener.stop()

if __name__ == '__main__':
    KivyUrsinaApp().run()
