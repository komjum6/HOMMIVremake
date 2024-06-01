import os
import numpy as np
from PIL import Image
#from pywfc import WFC
from perlin_noise import PerlinNoise
import json

base_dir = r"C:\Users\Justin\Downloads\Heroes_assets_pngs"
combat_obstacles_probs_json = os.path.join(base_dir, r"table\table.combat_obstacles\table.combat_obstacles.json")  # Update with your actual path
terrain_dir = os.path.join(base_dir, r"terrain") # No pngs yet
adjacent_overlap_dir = os.path.join(base_dir, r"combat_object\Obstacles")

with open(combat_obstacles_probs_json, 'r') as json_file:
    obstacles_data = json.load(json_file)

# Assigning a probability to the words
probabilities_dict = {"never":"0","rare":"0.05", "seldom":"0.15","usually":"0.35","common":"0.6"}

terrain_images = []
adjacent_overlap_images = []

# Example: Accessing data in the dictionary
for obstacle_type, obstacles in obstacles_data.items():

    # Taking only the Adjacent ones for now
    if obstacle_type == "Terrain":
        #obstacle_type
        print(f"Obstacle Type: {obstacle_type}")
        for obstacle, attributes in obstacles.items():
            print(f"  Obstacle: {obstacle}")
            for attribute, value in attributes.items():
                print(f"    {attribute}: {float(probabilities_dict[value])}")
                
water = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\water\1\terrain.water.1.1\terrain.water.1.1.h4d.34.png"
grass = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\grass\1\terrain.grass.1.2\terrain.grass.1.2.h4d.62.png"
rough = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\rough\1\terrain.rough.1.1\terrain.rough.1.1.h4d.33.png"
swamp = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\swamp\1\terrain.swamp.1.1\terrain.swamp.1.1.h4d.34.png"
#lava
volcanic = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\lava\1\terrain.lava.1.1\terrain.lava.1.1.h4d.22.png" 
snow = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\snow\1\terrain.snow.1.1\terrain.snow.1.1.h4d.34.png"
sand = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\sand\1\terrain.sand.1.1\terrain.sand.1.1.h4d.46.png"
subterranean = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\subterranean\1\terrain.subterranean.1.1\terrain.subterranean.1.1.h4d.22.png"
dirt = r"C:\Users\Justin\Downloads\Heroes_assets_pngs\terrain\dirt\1\terrain.dirt.1.1\terrain.dirt.1.1.h4d.54.png"

# Load your PNG images
image_water = Image.open(water)
image_grass = Image.open(grass)
image_rough = Image.open(rough)
image_swamp = Image.open(swamp)
image_volcanic = Image.open(volcanic)
image_snow = Image.open(snow)
image_sand = Image.open(sand)
image_subterranean = Image.open(subterranean)
image_dirt = Image.open(dirt)

def extract_opaque_region(image):
    # Create a new image with the same size and white background
    opaque_image = Image.new("RGBA", image.size, (255, 255, 255, 0))

    # Get pixel data
    pixels = image.load()
    opaque_pixels = opaque_image.load()

    # Iterate through each pixel
    for x in range(image.width):
        for y in range(image.height):
            r, g, b, a = pixels[x, y]
            if a != 0:
                # Opaque pixel: copy RGB values
                opaque_pixels[x, y] = (r, g, b, a)

    # Find the bounding box of the opaque region
    bbox = opaque_image.getbbox()
    if bbox:
        opaque_image = opaque_image.crop(bbox)

    return opaque_image

def load_and_process_image(image_path):
    image = Image.open(image_path).convert("RGBA")
    return extract_opaque_region(image)

# Process images to remove transparent regions
image_water = load_and_process_image(water)
image_grass = load_and_process_image(grass)
image_rough = load_and_process_image(rough)
image_swamp = load_and_process_image(swamp)
image_volcanic = load_and_process_image(volcanic)
image_snow = load_and_process_image(snow)
image_sand = load_and_process_image(sand)
image_subterranean = load_and_process_image(subterranean)
image_dirt = load_and_process_image(dirt)

# Convert the images to NumPy arrays
tile_water = np.array(image_water)
tile_grass = np.array(image_grass)
tile_rough = np.array(image_rough)
tile_swamp = np.array(image_swamp)
tile_volcanic = np.array(image_volcanic)
tile_snow = np.array(image_snow)
tile_sand = np.array(image_sand)
tile_subterranean = np.array(image_subterranean)
tile_dirt = np.array(image_dirt)

# List of terrain tiles for easy access
listofterrain = {
    "water": tile_water,
    "grass": tile_grass,
    "rough": tile_rough,
    "swamp": tile_swamp,
    "volcanic": tile_volcanic,
    "snow": tile_snow,
    "sand": tile_sand,
    "subterranean": tile_subterranean,
    "dirt": tile_dirt,
}

def generate_perlin_noise(width, height, octaves=3.5, seed=777):
    noise = PerlinNoise(octaves=octaves, seed=seed)
    heightmap = np.zeros((width, height))
    for i in range(width):
        for j in range(height):
            heightmap[i][j] = noise([i / width, j / height])
    return heightmap

def normalize(heightmap):
    return (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))

def create_biome_map(heightmap):
    biome_map = np.empty_like(heightmap, dtype=object)
    rows, cols = heightmap.shape
    for i in range(rows):
        for j in range(cols):
            elevation = heightmap[i, j]
            if elevation < 0.3:
                biome_map[i, j] = "water"
            elif elevation < 0.6:
                biome_map[i, j] = "grass"
            else:
                biome_map[i, j] = "snow"
    return biome_map

def create_output_image(biome_map, terrain_tiles, h_offset=0, v_offset=0, tile_h_offset=0, tile_v_offset=0):
    
    if h_offset or v_offset != 0:
        apply_tile_offsets = True
    else:
        apply_tile_offsets = False
    if tile_h_offset or tile_v_offset != 0:
        apply_inter_tile_offsets = True
    else:
        apply_inter_tile_offsets = False
    
    tile_size = terrain_tiles["grass"].shape[0]  # Assuming all tiles have the same size

    # Calculate output image dimensions
    if apply_inter_tile_offsets:
        output_width = biome_map.shape[1] * (tile_size + h_offset)
        output_height = biome_map.shape[0] * (tile_size + v_offset)
    else:
        output_width = biome_map.shape[1] * tile_size
        output_height = biome_map.shape[0] * tile_size

    output_image = Image.new("RGBA", (output_width, output_height), (0, 0, 0, 0))

    for i in range(biome_map.shape[0]):
        for j in range(biome_map.shape[1]):
            biome = biome_map[i, j]
            tile = terrain_tiles[biome]
            tile_image = Image.fromarray(tile, mode="RGBA")
            
            if apply_inter_tile_offsets:
                x_pos = j * (tile_size + h_offset)
                y_pos = i * (tile_size + v_offset)
            else:
                x_pos = j * tile_size
                y_pos = i * tile_size

            # Apply intra-tile offsets if enabled
            tile_width, tile_height = tile_image.size
            for x in range(tile_width):
                for y in range(tile_height):
                    if tile_image.getpixel((x, y))[3] != 0:  # If not transparent
                        if apply_tile_offsets:
                            new_x = x_pos + x + tile_h_offset
                            new_y = y_pos + y + tile_v_offset
                        else:
                            new_x = x_pos + x
                            new_y = y_pos + y
                        
                        # Check if the new position is within the output image bounds
                        if 0 <= new_x < output_width and 0 <= new_y < output_height:
                            output_image.putpixel((new_x, new_y), tile_image.getpixel((x, y)))

    return output_image

# Example usage:
width, height = 128, 128  # Smaller size for faster execution

# Generate a Perlin noise heightmap
heightmap = generate_perlin_noise(width, height, seed=69)

# Normalize the heightmap
normalized_heightmap = normalize(heightmap)

# Create the final biome map
biome_map = create_biome_map(normalized_heightmap)

# Convert biome map to an image using the selected tiles with specified offsets
horizontal_offset = 0  # Change this value for horizontal offset between tiles
vertical_offset = 0    # Change this value for vertical offset between tiles
tile_horizontal_offset = 0  # Change this value for horizontal offset within tiles
tile_vertical_offset = 0    # Change this value for vertical offset within tiles
output_image = create_output_image(biome_map, listofterrain, horizontal_offset, vertical_offset, tile_horizontal_offset, tile_vertical_offset)

# Display or save the final image
output_image.show()
output_image.save("output.png")











# Create a pattern (e.g., a checkerboard)
# You can customize this pattern based on your specific constraints
#pattern = np.array([["A", "B"], ["B", "A"]])

# Initialize the WFC model
#model = WFC(obstacle_probabilities, pattern)

# Generate the output
#output = model.run()

# Convert the output to an image (you can customize this part)
#output_image = Image.fromarray(output * 255).convert("RGB")
#output_image.show()  # Display the generated image
#output_image.save("output.png")  # Save the image to a file