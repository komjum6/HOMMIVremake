import os
import pygame
import pygame_gui
from pygame.locals import *
import xml.etree.ElementTree as ET
from pygame_gui.core import ObjectID

class TransparentButton(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect, text, manager, object_id):
        super().__init__(relative_rect=pygame.Rect(relative_rect), text=text, manager=manager)
        self.object_id = object_id

    def draw(self, surface):
        transparent_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(transparent_surface, self.bg_color, (0, 0, *self.rect.size))
        surface.blit(transparent_surface, self.rect.topleft)

# Custom class to store label information
class CustomImageLabel:
    def __init__(self, image_path, rect, manager, object_id):
        self.label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(rect),
            text='',
            manager=manager,
        )
        self.image = pygame.image.load(image_path).convert_alpha()
        self.dimension = (rect[2], rect[3])
        self.object_id = object_id

        # Set the image for the label
        self.label.image = pygame.transform.scale(self.image, self.dimension)

# Parse the .ui file from QtDesigner and create widgets
def load_ui(file_path, town, biome, manager):
    tree = ET.parse(file_path)
    root = tree.getroot()
    label_list = list()
    button_list = list()

    for widget in root.iter('widget'):
        widget_class = widget.get('class')
        widget_name = widget.get('name')
        rect = widget.find('property[@name="geometry"]/rect')
        if rect is not None:
            x = int(rect.find('x').text)
            y = int(rect.find('y').text)
            width = int(rect.find('width').text)
            height = int(rect.find('height').text)
            geometry = (x, y, width, height)
        else:
            geometry = (0, 0, 100, 30)  # Default geometry if not specified

        if widget_class == 'QLabel':
            pixmap = widget.find('property[@name="pixmap"]/pixmap')
            if pixmap is not None:
                image_path = pixmap.text.replace(':/towns', 'C:').replace('/', os.sep).replace('C:\C:\\','C:\\')
                image_name = os.path.basename(image_path).split('.')[0]  # Use the filename without extension as object_id
                if os.path.isabs(image_path):
                    # This try except was made due to the fully black images
                    try:
                        label = CustomImageLabel(image_path, geometry, manager, f"#{image_name}")
                    except Exception as e:
                        #print(e)
                        pass
                else:
                    print(f"Warning: Path '{image_path}' is not absolute.")
            else:
                text = widget.find('property[@name="text"]/string').text
                label_text = text if text is not None else ''
                label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(geometry),
                    text=label_text,
                    manager=manager,
                    object_id=ObjectID(object_id=f"#{widget_name}")
                )
                #label = CustomImageLabel(image_path, geometry, manager, f"#{widget_name})
            label_list.append(label)
        elif widget_class == 'QPushButton':
            text = widget.find('property[@name="text"]/string').text
            button_text = text if text is not None else ''
            button = TransparentButton(geometry, button_text, manager, f"#{widget_name}")
            button_list.append(button)
    
    #print(label_list)
    #print(button_list)
    #return button_list, label_list

    #for button in button_list:
    #    print(button.object_id)
        
    #for label in label_list:
    #    print(label.object_id)