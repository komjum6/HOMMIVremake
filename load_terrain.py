# File: load_terrain.py
import json
import numpy as np
from ursina import *  
from ursina import color, Vec3, Vec2, Entity, Texture, camera
import ursina
from PIL import Image
import time
import os
from perlin_noise import PerlinNoise
import random
from random import randint, uniform
from noise import pnoise2
import matplotlib.pyplot as plt
from io import BytesIO
import mmap
import math

def load_terrain_config(preset="desert_landscape"):
    """Load terrain configuration from JSON file."""
    try:
        with open('terrain_config.json', 'r') as f:
            configs = json.load(f)
            return configs.get(preset, configs['desert_landscape'])
    except FileNotFoundError:
        print("Warning: terrain_config.json not found, using default values")
        return {
            "scale": 0.9,
            "max_height": 4,
            "noise_scale": 0.08,
            "smoothing_passes": 2,
            "biome_percentages": {
                "Pablo_img": 0.6,
                "pavement": 0.2,
                "pavement2": 0.1,
                "grass": 0.1
            },
            "cactus_density": 0.3,
            "cactus_scale": 0.3
        }

def create_texture_atlas(texture_paths=None):
    """Create or load a texture atlas."""
    atlas_path = './assets/map/texture_atlas.png'
    
    if texture_paths is None:
        texture_paths = {
            'Pablo_img': './assets/map/Pablo_img.jpg',
            'pavement': './assets/map/pavement.jpg',
            'pavement2': './assets/map/pavement2.jpg',
            'grass': './assets/map/grass.jpg'
        }

    if os.path.exists(atlas_path):
        texture_atlas = Image.open(atlas_path).convert('RGBA')
        atlas_height = texture_atlas.height
        target_size = 1024
        texture_regions = {
            key: (0, i * target_size / atlas_height,
                 1, (i + 1) * target_size / atlas_height)
            for i, key in enumerate(texture_paths.keys())
        }
        return texture_atlas, texture_regions

    # Create new atlas
    textures = {
        name: Image.open(path).convert('RGBA')
        for name, path in texture_paths.items()
    }

    target_size = (1024, 1024)
    for key in textures:
        textures[key] = textures[key].resize(target_size, Image.Resampling.LANCZOS)

    atlas_width = target_size[0]
    atlas_height = target_size[1] * len(textures)
    texture_atlas = Image.new('RGBA', (atlas_width, atlas_height))

    current_y = 0
    texture_regions = {}
    for key, texture in textures.items():
        texture_atlas.paste(texture, (0, current_y))
        texture_regions[key] = (
            0, current_y / atlas_height,
            1, (current_y + target_size[1]) / atlas_height
        )
        current_y += target_size[1]

    texture_atlas.save(atlas_path)
    return texture_atlas, texture_regions

def load_terrain(positions, sizes, position, scale, texture_paths):
    """
    Basic terrain loading function with combined hover/collision entities.
    
    Args:
        positions (list): List of (x, y, z) positions for each terrain section
        sizes (list): List of (width, height, depth) sizes for each section
        position (tuple): Global position offset for the entire terrain
        scale (float): Global scale factor for the entire terrain
        texture_paths (dict): Dictionary mapping section names to texture file paths
    
    Returns:
        tuple: (floor Entity, list of hover/collision entities)
    """
    # Generate the texture atlas and UV regions
    texture_atlas_img, texture_regions = create_texture_atlas(texture_paths)
    texture_atlas = Texture(texture_atlas_img)

    # Define terrain sections
    sections = [
        {'type': 'room1', 'position': Vec3(*positions[0]), 'size': Vec3(*sizes[0])},
        {'type': 'hallway', 'position': Vec3(*positions[1]), 'size': Vec3(*sizes[1])},
        {'type': 'room2', 'position': Vec3(*positions[2]), 'size': Vec3(*sizes[2])},
    ]

    # Create main floor entity
    floor = Entity(
        model=Mesh(),
        texture=texture_atlas,
        scale=scale,
        position=position
    )

    vertices = []
    uvs = []
    triangles = []
    entities = []
    vertex_index = 0

    for section in sections:
        pos = section['position']
        size = section['size']
        uv = texture_regions[section['type']]

        # Create vertices
        new_vertices = [
            Vec3(pos.x, pos.y, pos.z),
            Vec3(pos.x + size.x, pos.y, pos.z),
            Vec3(pos.x + size.x, pos.y, pos.z + size.z),
            Vec3(pos.x, pos.y, pos.z + size.z),
        ]
        vertices.extend(new_vertices)

        new_uvs = [
            Vec2(uv[0], uv[1]),
            Vec2(uv[2], uv[1]),
            Vec2(uv[2], uv[3]),
            Vec2(uv[0], uv[3]),
        ]
        uvs.extend(new_uvs)

        triangles.extend([
            vertex_index, vertex_index + 1, vertex_index + 2,
            vertex_index, vertex_index + 2, vertex_index + 3
        ])
        vertex_index += 4

        # Create hover/collision entity
        entity = Entity(
            model=Mesh(
                vertices=[Vec3(0, 0, 0), Vec3(1, 0, 0), Vec3(1, 0, 1), Vec3(0, 0, 1)],
                triangles=[0, 1, 2, 0, 2, 3],
                uvs=[Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)]
            ),
            position=Vec3(*pos) * scale + Vec3(*position),
            scale=Vec3(*size) * scale,
            color=color.rgba(1, 1, 1, 0),
            collider='mesh',
            visible=False
        )
        entities.append(entity)

    floor.model.vertices = vertices
    floor.model.uvs = uvs
    floor.model.triangles = triangles
    floor.model.generate()

    return floor, entities

def load_terrain_warp(positions, sizes, position, scale, texture_paths, warp_points_list=None):
    """
    Enhanced terrain loading function with perspective warping for each section.
    """
    texture_atlas_img, texture_regions = create_texture_atlas(texture_paths)
    texture_atlas = Texture(texture_atlas_img)

    sections = []
    for i, (section_type, tex_path) in enumerate(texture_paths.items()):
        sections.append({
            'type': section_type,
            'position': Vec3(*positions[i]),
            'size': Vec3(*sizes[i])
        })

    floor = Entity(
        model=Mesh(),
        texture=texture_atlas,
        scale=scale,
        position=position
    )

    vertices = []
    uvs = []
    triangles = []
    entities = []
    vertex_index = 0

    if warp_points_list is None:
        warp_points_list = [[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)] for _ in sections]

    for section, warp_points in zip(sections, warp_points_list):
        pos = section['position']
        size = section['size']
        uv = texture_regions[section['type']]

        original_vertices = [
            Vec3(pos.x, pos.y, pos.z),
            Vec3(pos.x + size.x, pos.y, pos.z),
            Vec3(pos.x + size.x, pos.y, pos.z + size.z),
            Vec3(pos.x, pos.y, pos.z + size.z),
        ]

        warped_vertices = []
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

        vertices.extend(warped_vertices)

        new_uvs = [
            Vec2(uv[0], uv[1]),
            Vec2(uv[2], uv[1]),
            Vec2(uv[2], uv[3]),
            Vec2(uv[0], uv[3]),
        ]
        uvs.extend(new_uvs)

        triangles.extend([
            vertex_index, vertex_index + 1, vertex_index + 2,
            vertex_index, vertex_index + 2, vertex_index + 3
        ])
        vertex_index += 4

        collision_entity = Entity(
            model=Mesh(
                vertices=warped_vertices,
                triangles=[0, 1, 2, 0, 2, 3],
                uvs=new_uvs
            ),
            position=floor.position,
            scale=floor.scale,
            color=color.rgba(1, 1, 1, 0),
            collider='mesh',
            visible=False
        )
        entities.append(collision_entity)

    floor.model.vertices = vertices
    floor.model.uvs = uvs
    floor.model.triangles = triangles
    floor.model.generate()

    return floor, entities

def generate_smooth_heightmap(num_sections_x, num_sections_z, noise_scale, max_height, smoothing_passes):
    """Generate a smooth height map using multiple noise layers."""
    # Create two noise generators for different detail levels
    base_noise = PerlinNoise(octaves=4, seed=random.randint(0, 1000))
    detail_noise = PerlinNoise(octaves=8, seed=random.randint(0, 1000))
    
    # Generate initial height map
    height_map = [[
        (base_noise([x * noise_scale, z * noise_scale]) * 0.7 +
         detail_noise([x * noise_scale * 2, z * noise_scale * 2]) * 0.3) * max_height
        for x in range(num_sections_x + 1)
    ] for z in range(num_sections_z + 1)]
    
    # Apply smoothing
    def smooth_pass():
        smoothed = [[0 for _ in range(num_sections_x + 1)] 
                   for _ in range(num_sections_z + 1)]
        for z in range(1, num_sections_z):
            for x in range(1, num_sections_x):
                smoothed[z][x] = (
                    height_map[z-1][x] + height_map[z+1][x] +
                    height_map[z][x-1] + height_map[z][x+1] +
                    height_map[z][x] * 4
                ) / 8.0
        return smoothed
    
    # Apply multiple smoothing passes
    for _ in range(smoothing_passes):
        height_map = smooth_pass()
    
    return height_map

def calculate_slope(heights):
    """Calculate the slope at a point based on surrounding heights."""
    max_diff = max(heights) - min(heights)
    return max_diff

def generate_section_type_map(num_sections_x, num_sections_z, texture_paths, biome_percentages):
    """Generate biome distribution with proper percentages and transitions."""
    seed = random.randint(0, 1000)
    noise = PerlinNoise(octaves=4, seed=seed)
    noise_scale = 0.1
    section_type_map = {}
    total_sections = num_sections_x * num_sections_z

    # Generate base noise map
    noise_values = []
    for z in range(num_sections_z):
        for x in range(num_sections_x):
            # Use multiple noise frequencies for more natural transitions
            noise_value = (
                noise([x * noise_scale, z * noise_scale]) * 0.6 +
                noise([x * noise_scale * 2, z * noise_scale * 2]) * 0.4
            )
            noise_values.append((noise_value, (x, z)))

    # Sort by noise value
    noise_values.sort(key=lambda x: x[0])
    
    # Calculate exact number of tiles for each biome
    biome_counts = {}
    remaining = total_sections
    for biome, percentage in biome_percentages.items():
        count = int(total_sections * percentage)
        biome_counts[biome] = count
        remaining -= count
    
    # Distribute any remaining tiles
    while remaining > 0:
        for biome in biome_counts.keys():
            if remaining > 0:
                biome_counts[biome] += 1
                remaining -= 1

    # Assign biomes based on noise values
    current_index = 0
    for biome, count in biome_counts.items():
        for _ in range(count):
            if current_index < len(noise_values):
                _, coord = noise_values[current_index]
                section_type_map[coord] = biome
                current_index += 1

    # Smooth transitions between biomes
    smoothed_map = section_type_map.copy()
    for z in range(1, num_sections_z - 1):
        for x in range(1, num_sections_x - 1):
            # Count neighboring biomes
            neighbors = [
                section_type_map.get((x+dx, z+dz))
                for dx, dz in [(-1,0), (1,0), (0,-1), (0,1)]
            ]
            # If surrounded by different biome, consider changing
            most_common = max(set(neighbors), key=neighbors.count)
            if neighbors.count(most_common) >= 3:  # If 3 or more neighbors are the same
                smoothed_map[(x, z)] = most_common

    return smoothed_map

def apply_warp(point, warp_pts):
    """Apply perspective warp to a point."""
    x, y = point
    p1, p2, p3, p4 = warp_pts
    
    # Bilinear interpolation weights
    f1 = (1 - x) * (1 - y)
    f2 = x * (1 - y)
    f3 = x * y
    f4 = (1 - x) * y
    
    # Calculate warped coordinates
    warped_x = f1 * p1[0] + f2 * p2[0] + f3 * p3[0] + f4 * p4[0]
    warped_y = f1 * p1[1] + f2 * p2[1] + f3 * p3[1] + f4 * p4[1]
    warped_z = f1 * p1[2] + f2 * p2[2] + f3 * p3[2] + f4 * p4[2]
    
    return warped_x, warped_y, warped_z

def generate_and_load_terrain(self, num_sections_x, num_sections_z, biome_percentages, tile_size=(4, 1, 4),
                            position=(0, 0, 0), scale=1.0, texture_paths=None, max_height=10, towns=3,
                            gold_mine_chance=0.02, minimap_path="./output/terrain_visualization.png", debug=True):
    """
    Generate and load terrain with improved height mapping and cactus placement.
    """
    # Load terrain configuration
    config = load_terrain_config()
    
    # Store terrain boundaries for minimap
    self.terrain_start_x = position[0]
    self.terrain_start_z = position[2]

    # Apply configuration values
    scale = config["scale"] if isinstance(scale, (int, float)) else scale
    max_height = config["max_height"]
    noise_scale = config["noise_scale"]
    smoothing_passes = config["smoothing_passes"]
    cactus_density = config["cactus_density"]
    cactus_scale = config["cactus_scale"]

    # Generate smooth height map
    height_map = generate_smooth_heightmap(
        num_sections_x, num_sections_z,
        noise_scale, max_height,
        smoothing_passes
    )

    # Generate biome distribution
    section_type_map = generate_section_type_map(
        num_sections_x, num_sections_z,
        texture_paths, config["biome_percentages"]
    )

    # Create texture atlas
    texture_atlas_img, texture_regions = create_texture_atlas(texture_paths)
    texture_atlas = Texture(texture_atlas_img)

    # Initialize storage lists
    positions_list = []
    hover_entities = []
    cacti_positions = []

    # Create floor entity
    #floor = Entity(
    #    model=Mesh(),
    #    texture=texture_atlas,
    #    scale=scale,
    #    position=Vec3(*position)
    #)
    
    floor = Entity(
        model=Mesh(),
        texture=texture_atlas,
        scale=(1,1,1), # Set scale to (1,1,1) to avoid double transformation
        position=(0,0,0) # Set position to (0,0,0) to avoid double transformation
    )

    # Initialize mesh data
    vertices = []
    uvs = []
    triangles = []
    vertex_index = 0

    # Process each terrain section
    for z in range(num_sections_z):
        for x in range(num_sections_x):
            # Calculate base position
            pos_x = x * tile_size[0] * scale + position[0]
            pos_z = z * tile_size[2] * scale + position[2]
            
            # Get corner heights
            vert_heights = [
                height_map[z][x],
                height_map[z][x + 1],
                height_map[z + 1][x + 1],
                height_map[z + 1][x]
            ]
            
            # Calculate center height for tile
            center_height = sum(vert_heights) / 4
            pos_y = center_height * scale

            # Store position
            positions_list.append((pos_x, pos_y, pos_z))

            # Create vertices with proper height interpolation
            warped_vertices = [
                Vec3(pos_x, vert_heights[0] * scale, pos_z),
                Vec3(pos_x + tile_size[0] * scale, vert_heights[1] * scale, pos_z),
                Vec3(pos_x + tile_size[0] * scale, vert_heights[2] * scale, pos_z + tile_size[2] * scale),
                Vec3(pos_x, vert_heights[3] * scale, pos_z + tile_size[2] * scale),
            ]
            vertices.extend(warped_vertices)

            # Get correct texture region based on biome
            biome_type = section_type_map.get((x, z), 'default')
            uv = texture_regions.get(biome_type, (0,0,1,1))
            
            # Create UVs
            new_uvs = [
                Vec2(uv[0], uv[1]),
                Vec2(uv[2], uv[1]),
                Vec2(uv[2], uv[3]),
                Vec2(uv[0], uv[3]),
            ]

            uvs.extend(new_uvs)

            # Create triangles
            triangles.extend([
                vertex_index, vertex_index + 1, vertex_index + 2,
                vertex_index, vertex_index + 2, vertex_index + 3
            ])
            vertex_index += 4

            # Create collision entity
            hover_entity = Entity(
                model=Mesh(
                    vertices=warped_vertices,
                    triangles=[0, 1, 2, 0, 2, 3],
                    uvs=new_uvs
                ),
                position=floor.position,
                scale=floor.scale,
                color=ursina.color.rgba(1, 1, 1, 0),
                collider='mesh',
                visible=False
            )
            hover_entities.append(hover_entity)

            # Handle cactus placement
            if biome_type == 'Pablo_img':  # Only place on desert tiles
                # Calculate exact ground height using bilinear interpolation
                x_local = (pos_x - position[0]) / (tile_size[0] * scale)
                z_local = (pos_z - position[2]) / (tile_size[2] * scale)
                
                # Get the exact tile coordinates
                tile_x = int(x_local)
                tile_z = int(z_local)
                
                # Only proceed if we're actually in a desert tile
                if section_type_map.get((tile_x, tile_z)) == 'Pablo_img':
                    # Calculate slope
                    max_height_diff = max(vert_heights) - min(vert_heights)
                    if max_height_diff < 0.5:  # Only place on relatively flat ground
                        # Calculate center position with proper height
                        center_x = pos_x + (tile_size[0] * scale / 2)
                        center_z = pos_z + (tile_size[2] * scale / 2)
                        
                        # Add small random offset to prevent grid pattern
                        offset_x = random.uniform(-0.2, 0.2) * tile_size[0] * scale
                        offset_z = random.uniform(-0.2, 0.2) * tile_size[2] * scale
                        
                        final_x = center_x + offset_x
                        final_z = center_z + offset_z
                        
                        # Calculate normalized coordinates of final_x, final_z within the current tile
                        norm_x_in_tile = (final_x - pos_x) / (tile_size[0] * scale)
                        norm_z_in_tile = (final_z - pos_z) / (tile_size[2] * scale)

                        # Bilinearly interpolate the height at (final_x, final_z)
                        h00 = vert_heights[0] # (x,z)
                        h10 = vert_heights[1] # (x+1,z)
                        h11 = vert_heights[2] # (x+1,z+1)
                        h01 = vert_heights[3] # (x,z+1)

                        interpolated_height = (
                            h00 * (1 - norm_x_in_tile) * (1 - norm_z_in_tile) +
                            h10 * norm_x_in_tile * (1 - norm_z_in_tile) +
                            h01 * (1 - norm_x_in_tile) * norm_z_in_tile +
                            h11 * norm_x_in_tile * norm_z_in_tile
                        )
                        
                        # Use the interpolated height, scaled
                        cactus_y = interpolated_height * scale

                        # Place cactus exactly on the ground
                        cactus_entity = Entity(
                            model=load_model('assets/map/Tall_cactus_no_flo_obj/0dddc35f4b62_Tall_cactus__no_flo.obj'),
                            texture=load_texture('assets/map/Tall_cactus_no_flo_obj/0dddc35f4b62_Tall_cactus__no_flo_texture_kd.jpg'),
                            position=Vec3(final_x, cactus_y, final_z),
                            scale=Vec3(1.0, 1.0, 1.0),
                            rotation_y=random.uniform(0, 360)
                        )
                        cacti_positions.append((final_x, cactus_y, final_z)) # Add cactus position to list
                        
                        if debug:
                            with open("./output/cactus_log.txt", "a") as f:
                                f.write(f"Cactus: Biome '{biome_type}', Tile ({tile_x}, {tile_z}), Pos ({final_x:.2f}, {cactus_y:.2f}, {final_z:.2f})\n")

    # Update floor mesh
    floor.model.vertices = vertices
    floor.model.uvs = uvs
    floor.model.triangles = triangles
    floor.model.generate()

    # Always create minimap and dot, regardless of debug status
    # Create a figure with no padding
    fig = plt.figure(figsize=(num_sections_x, num_sections_z), dpi=1) # Set figure size to match grid dimensions, dpi=1 for exact pixel control
    ax = fig.add_axes([0, 0, 1, 1]) # Make the axes take up the entire figure area
    
    # Define biome colors
    biome_colors = {
        'Pablo_img': 'yellow',
        'grass': 'green',
        'pavement': 'gray',
        'pavement2': 'lightgray'
    }
    
    # Plot biome distribution
    for z in range(num_sections_z):
        for x in range(num_sections_x):
            biome = section_type_map.get((x, z), 'grass')  # Default to grass if undefined
            color = biome_colors.get(biome, 'white')  # Default to white if biome not in colors
            ax.add_patch(plt.Rectangle(
                (x, z), 1, 1,
                color=color,
                edgecolor='black',
                alpha=0.7
            ))
    
    # Plot cactus positions if any exist
    if cacti_positions:
        # Correctly normalize cactus world positions to plot coordinates
        cactus_plot_x = [(cx - position[0]) / (tile_size[0] * scale) for cx, _, _ in cacti_positions]
        cactus_plot_z = [(cz - position[2]) / (tile_size[2] * scale) for _, _, cz in cacti_positions]
        ax.scatter(cactus_plot_x, cactus_plot_z, color='red', marker='^', label='Cactus', s=50)
    
    # Set plot properties
    ax.set_xlim(0, num_sections_x) # Explicitly set x-limits
    ax.set_ylim(0, num_sections_z) # Explicitly set y-limits
    ax.set_aspect('equal') # Ensure aspect ratio is equal
    ax.axis('off') # Turn off axes and labels to remove any remaining whitespace/borders
    
    # Save visualization to a buffer with no padding
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig) # Close the figure to free memory
    
    '''
    # Convert buffer to PIL Image and then to Ursina texture
    pil_image = Image.open(buf).convert('RGBA')
    minimap_texture = Texture(pil_image)
    
    # Create minimap and dot entities
    self.minimap = Entity(
        parent=camera.ui,
        model='quad',
        texture=minimap_texture,
        scale=(0.4, 0.4),
        position=(0.3, 0.3)
    )
    
    self.dot = Entity(
        parent=self.minimap,
        model='quad',
        color=ursina.color.white,
        scale=(0.02, 0.02),
        position=(-0.5, -0.5)
    )

    return floor, hover_entities, positions_list
    '''
    
    # Convert buffer to PIL Image
    raw_minimap_pil_image = Image.open(buf).convert('RGBA')

    # Resize the minimap to the target Kivy display size (280x280)
    target_minimap_size = (280, 280)
    resized_minimap_pil_image = raw_minimap_pil_image.resize(target_minimap_size, Image.Resampling.NEAREST) # Use NEAREST for pixelated look

    # Store minimap data for export to Kivy (don't create Ursina entity)
    self.minimap_pil_image = resized_minimap_pil_image
    
    return floor, hover_entities, positions_list

