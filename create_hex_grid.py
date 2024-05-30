import pygame
import math

##################################### Hex grid #####################################
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_height = 1080
screen_width = 1920

# Colors for the grid and hex
#grid_color = (255, 255, 255)
hex_color = (0, 255, 0)

# Hexagon properties
hex_radius = 30  # Radius of the hexagon
hex_height = math.sqrt(3) * hex_radius  # Height of the hexagon
hex_width = 2 * hex_radius  # Width of the hexagon
horizontal_spacing = 1.75 * hex_radius  # Horizontal spacing between hexagon centers
vertical_spacing = hex_height * 0.86 # Vertical spacing between hexagon centers

# Predefined hexagon to be enlarged (row, col) tuple
enlarged_hex = (4, 5)  # This is an example; you can change these values as needed

# Calculate the vertices of a hexagon
def calculate_hex_vertices(hex_center, radius):
    vertices = []
    for i in range(6):
        angle = math.radians(i * 60 + 30)
        x = hex_center[0] + radius * math.cos(angle)
        y = hex_center[1] + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

#def draw_enlarged_hex(hex_center):
#    enlarged_radius = hex_radius * 2
#    enlarged_vertices = calculate_hex_vertices(hex_center, enlarged_radius)
#    pygame.draw.polygon(screen, hex_color, enlarged_vertices, 3)
#    #print(hex_center)
    
# Get the centers of the central hexagon and its six adjacent hexagons
def get_hex_cluster_centers(hex_center):
    hex_centers = [hex_center]
    angles = [0, 60, 120, 180, 240, 300]
    for angle in angles:
        x = hex_center[0] + hex_width * 0.75 * math.cos(math.radians(angle))
        y = hex_center[1] + hex_height * math.sin(math.radians(angle))
        hex_centers.append((x, y))
    return hex_centers

# Determine the outer boundary vertices of the enlarged hexagon cluster
def get_outer_boundary_vertices(cluster_hex_centers):
    all_vertices = []
    for hex_center in cluster_hex_centers:
        vertices = calculate_hex_vertices(hex_center, hex_radius)
        all_vertices.extend(vertices)

    # Sort vertices by angle relative to the center to get the outer boundary
    cluster_hex_center = cluster_hex_centers[0]  # Use the central hexagon's center
    all_vertices.sort(key=lambda vertex: math.atan2(vertex[1] - cluster_hex_center[1], vertex[0] - cluster_hex_center[0]))

    # Remove duplicates while maintaining order
    outer_boundary = []
    [outer_boundary.append(vertex) for vertex in all_vertices if vertex not in outer_boundary]

    return outer_boundary    
    
# Draw an enlarged hexagon by combining a central hexagon and its six adjacent hexagons
def draw_enlarged_hex(hex_center):
    cluster_hex_centers = get_hex_cluster_centers(hex_center)
    outer_boundary_vertices = get_outer_boundary_vertices(cluster_hex_centers)
    pygame.draw.polygon(screen, hex_color, outer_boundary_vertices, 3)

# Draw the hexagonal grid
def draw_hex_grid():
    for row in range(2, screen_height // int(vertical_spacing) - 2):
        for col in range(2, screen_width // int(horizontal_spacing) - 2):
            x = col * horizontal_spacing
            y = row * vertical_spacing

            # Calculate the offset for even/odd rows
            offset = 0 if row % 2 == 0 else horizontal_spacing // 2
            hex_center = (x + offset, y)
            
            #hex_vertices = calculate_hex_vertices(hex_center, hex_radius)
            
            #if (row, col) == enlarged_hex:
            #    draw_enlarged_hex(hex_center)
            #else:
                #hex_vertices = calculate_hex_vertices(hex_center, hex_radius)
                #pygame.draw.polygon(screen, hex_color, hex_vertices, 1)
            #    pass
            
            hex_vertices = calculate_hex_vertices(hex_center, hex_radius)
            pygame.draw.polygon(screen, hex_color, hex_vertices, 1)