import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Requirements
# 1. Resources linked in QtDesigner, to your folder with GUI elements
# 2. ":/towns" is the variable of your resources
# 3. Change the json path
# 4. Change the pixmap path
# 5. Change your output folder to one you want but make sure the eventual file is renamed to HOMMIVtown.ui

# Load town JSON data
json_town_file_path = r'C:\Users\Justin\Downloads\layers.town.1280.h4d.json'
with open(json_town_file_path, 'r') as file:
    town_data = json.load(file)

# Scale factor (make it 1 if you aren't going to change the resolution)
scale_factor_x = 1920 / 1280
scale_factor_y = 1080 / 1027

towns = ["Life", "Nature", "Chaos", "Death", "Order", "Might"]
biomes = ["dirt", "grass", "rough", "sand", "snow", "subterranean", "swamp", "volcanic"]

# Process each image name in the JSON
for town in towns:
    # Create the root of the XML structure
    ui = ET.Element("ui", version="4.0")
    class_element = ET.SubElement(ui, "class")
    class_element.text = "MainWindow"
    widget_main_window = ET.SubElement(ui, "widget", {"class": "QMainWindow", "name": "MainWindow"})

    # Set the main window geometry
    property_geometry = ET.SubElement(widget_main_window, "property", {"name": "geometry"})
    rect_geometry = ET.SubElement(property_geometry, "rect")
    ET.SubElement(rect_geometry, "x").text = "0"
    ET.SubElement(rect_geometry, "y").text = "0"
    ET.SubElement(rect_geometry, "width").text = "1920"
    ET.SubElement(rect_geometry, "height").text = "1080"

    # Create the central widget
    widget_central = ET.SubElement(widget_main_window, "widget", {"class": "QWidget", "name": "centralwidget"})

    backgrounds = [r'C:\Users\Justin\Downloads\Heroes_assets_pngs\layers\town\{0}\layers.town.{0}.{1}'.format(town.lower(), biome)  + r'_1920\background.png' for biome in biomes]

    for background, biome in zip(backgrounds, biomes):
        coordinates = (0,0)
        start_x = 0
        start_y = 0
        width = 1920
        height = 867

        # Create a QLabel for the image
        widget_label = ET.SubElement(widget_central, "widget", {"class": "QLabel", "name": f"label_{'background_' +  biome}"})
        
        # Set the geometry of the QLabel
        property_geometry = ET.SubElement(widget_label, "property", {"name": "geometry"})
        rect_geometry = ET.SubElement(property_geometry, "rect")
        ET.SubElement(rect_geometry, "x").text = str(start_x)
        ET.SubElement(rect_geometry, "y").text = str(start_y)
        ET.SubElement(rect_geometry, "width").text = str(width)
        ET.SubElement(rect_geometry, "height").text = str(height)

        # Set the pixmap of the QLabel
        property_pixmap = ET.SubElement(widget_label, "property", {"name": "pixmap"})
        ET.SubElement(property_pixmap, "pixmap").text = background

    # Load death town JSON data
    json_death_town_file_path = r'C:\Users\Justin\Downloads\layers.town.{0}.layout.h4d.json'.format(town.lower())
    with open(json_death_town_file_path, 'r') as file:
        alignment_town_data = json.load(file)

    dirs = [r":/towns/Users/Justin/Downloads/Heroes_assets_pngs/layers/town/layers.town.1920/", r":/towns/Users/Justin/Downloads/Heroes_assets_pngs/layers/town/{0}/layers.town.{0}.layout_1920/".format(town.lower())]
    datas = [town_data, alignment_town_data]

    for directory, data in zip(dirs, datas):
        for image_name in data['mImageNames']:
            if image_name in data['mImageMap']:
                coordinates = data['mImageMap'][image_name]
                start_x = int(coordinates['mStartX'] * scale_factor_x)
                start_y = int(coordinates['mStartY'] * scale_factor_y)
                width = int((coordinates['mEndX'] - coordinates['mStartX']) * scale_factor_x)
                height = int((coordinates['mEndY'] - coordinates['mStartY']) * scale_factor_y)

                # Create a QLabel for the image
                widget_label = ET.SubElement(widget_central, "widget", {"class": "QLabel", "name": f"label_{image_name}"})
                
                # Set the geometry of the QLabel
                property_geometry = ET.SubElement(widget_label, "property", {"name": "geometry"})
                rect_geometry = ET.SubElement(property_geometry, "rect")
                ET.SubElement(rect_geometry, "x").text = str(start_x)
                ET.SubElement(rect_geometry, "y").text = str(start_y)
                ET.SubElement(rect_geometry, "width").text = str(width)
                ET.SubElement(rect_geometry, "height").text = str(height)

                # Set the pixmap of the QLabel
                property_pixmap = ET.SubElement(widget_label, "property", {"name": "pixmap"})
                ET.SubElement(property_pixmap, "pixmap").text = directory + f"{image_name}.png"

    # Add the resources and connections tags
    ET.SubElement(ui, "resources")
    ET.SubElement(ui, "connections")

    # Convert the ElementTree to a pretty-printed XML string
    xml_str = ET.tostring(ui, encoding='utf-8', method='xml')
    parsed_xml = minidom.parseString(xml_str)
    pretty_xml_str = parsed_xml.toprettyxml(indent="  ")

    # Save the new .ui file
    new_ui_file_path = r'D:\Blender_video_music\Games\HOMMIVremake\HOMMIV{0}town.ui'.format(town)
    with open(new_ui_file_path, 'w') as file:
        file.write(pretty_xml_str)

    print(f'New .ui file saved as {new_ui_file_path}')
