import pygame
import math

##################################### Grid #####################################


# Colors for the grid 
#grid_color = (255, 255, 255)
grid_color = (0, 255, 0)

#Square properties

#potentially scalable
backdrop_height = 1024
backdrop_width = 1180
#common denom
#denom= 1180/1024
#battleable area is approx 944, 1180


#I wasnt quite sure the angle of battlefield
#This is adjusted to match the angle, couldnt figure a good way to mathematically ccalculate it
#grid_height = 45 # Number of squares in each row and column
#grid_width = 24

#grid_height = 45
#grid_width = 30

grid_height = 64
grid_width = 37




diamond_width = backdrop_width / grid_width


#backdrop_adjusted = 10
adjusted_height = 0
backdrop_height -= adjusted_height

diamond_height =backdrop_height/ grid_height
#diamond_height = diamond_width / 2


# angle is 30 60
# Function to draw the grid

def draw_isometric_grid(screen, backdrop_position):
    #screen_width, screen_height = screen.get_size()
    # Calculate the starting position of the grid to center it
    #center_x = screen_width // 2
    #adjusted for missing space at the top
    #center_y = (screen_height // 2) - adjusted_height
    start_x, start_y = backdrop_position
    start_y += adjusted_height
    for row in range(grid_height):
        for col in range(grid_width):
            # Calculate screen coordinates for each square
            x = start_x + (diamond_width * col)
            y = start_y + (diamond_height * row) + (diamond_height /2)
            
            # Draw each square
            pygame.draw.polygon(screen, grid_color, [
                (x, y),
                (x + diamond_width // 2, y - diamond_height // 2),
                (x + diamond_width, y),
                (x + diamond_width // 2, y + diamond_height // 2)
            ], 1)




def center_of_tile(col, row, screen, backdrop_position):

    
    #start_x = (screen.get_width() / 2) - (backdrop_width / 2)
    #start_y = (screen.get_height() / 2) - (backdrop_height / 2)
    start_x, start_y = backdrop_position
    #start_y += 9 * diamond_height
    # Condavert grid coordinates (row, col) to pixel coordinates (x, y)
    #x = start_x + col * (diamond_width / 2) - row * (diamond_width / 2)
    #y = start_y + row * (diamond_height / 2) + col * (diamond_height / 2)
   
    if (row % 2 == 0):
        x = (start_x + diamond_width/2) + ((col) * (diamond_width))
        y = (start_y + diamond_height/2) + ((row) * (diamond_height/2))
    else:
        x = (start_x  + diamond_width) + ((col) * (diamond_width))
        y = (start_y + diamond_height/2) + ((row) * (diamond_height/2))
    
    #0-36, 0- 63
    #74, 128
    #row column grid points must be on the diagonals aka col - row = 0.5
    #grid dimensions
    #37, 64
    #inner diamonds are 0.5 off of outer diamonds


    #grid size is 64, 118, 
    return (x, y)

#Diamond corners exact position
def diamond_corners(col, row, screen, backdrop_position):
    x, y = center_of_tile(col, row, screen, backdrop_position)
    left = (x - diamond_width/2, y)
    up = (x, y - diamond_height/2)
    right = (x + diamond_width/2, y)
    down = (x, y + diamond_height/2)
    return left, up, right, down


def initialize_grid_matrix():
    grid = []
    #for each row
    #
    for i in range((grid_height * 2)-1):
        #if odd add 
        if i % 2 == 0:
            grid.append([{'terrain': '', 'occupied': False} for _ in range(grid_width)])
        else:
            grid.append([{'terrain': '', 'occupied': False} for _ in range(grid_width-1)])
    print(len(grid))
    print(len(grid[0]))
    
    return grid


def is_point_in_triangle(p, a, b, c):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    # Calculate the signs of the areas
    d1 = sign(p, a, b)
    d2 = sign(p, b, c)
    d3 = sign(p, c, a)

    # Points exactly on the edges should be considered inside
    return d1 <= 0 and d2 <= 0 and d3 <= 0 or d1 >= 0 and d2 >= 0 and d3 >= 0


def is_point_in_quadrilateral(p, a, b, c, d):
    # Check if point is in either of the two triangles forming the quadrilateral
    return is_point_in_triangle(p, a, b, d) or is_point_in_triangle(p, b, c, d)


def occupy_area(grid, screen, backdrop_position,a, b, c, d=None):
    rows = len(grid)
    for row in range(rows):
        for col in range(len(grid[row])):
            x,y = center_of_tile(col, row, screen, backdrop_position)
            a1 = center_of_tile(a[0], a[1], screen, backdrop_position )
            b1 = center_of_tile(b[0], b[1], screen, backdrop_position )
            c1 = center_of_tile(c[0], c[1], screen, backdrop_position )
            left, up, right, down = diamond_corners(col, row, screen, backdrop_position)

            if d is not None:
                # For quadrilateral
                d1 = center_of_tile(d[0], d[1], screen, backdrop_position )

                if  (is_point_in_quadrilateral(left, a1, b1, c1, d1) or is_point_in_quadrilateral(up, a1, b1, c1, d1)
                or is_point_in_quadrilateral(right, a1, b1, c1, d1) or is_point_in_quadrilateral(down, a1, b1, c1, d1)):
                    grid[row][col]['occupied'] = True
            else:
                # For triangle
                if (is_point_in_triangle(left, a1, b1, c1) or is_point_in_triangle(up, a1, b1, c1) 
                or is_point_in_triangle(right, a1, b1, c1) or is_point_in_triangle(down, a1, b1, c1)):
                    grid[row][col]['occupied'] = True
    return grid


def darken_occupied(grid, screen, backdrop_position):
    rows = len(grid)
    for row in range(rows):
        for col in range(len(grid[row])):
            if(grid[row][col]['occupied'] == True):
                circle_color = (255, 0, 0)  
                circle_radius = 7  
                x, y = center_of_tile(col, row, screen, backdrop_position)
                print(col, row)
                print(x, y)
                pygame.draw.circle(screen, circle_color, (x, y), circle_radius)

def pixel_position_to_tile(x, y, screen, backdrop_position):
    start_x, start_y = backdrop_position
    
    # Adjust the starting position to shift tiles to the right
    start_x -= diamond_width
    
    # Calculate relative position from the backdrop's starting position
    relative_x = x - start_x
    relative_y = y - start_y

    # Convert the relative pixel coordinates to isometric grid coordinates
    row = int((relative_y / diamond_height) * 2)
    if row < 0 or row >= (grid_height * 2)-1:
        return None

    # Calculate initial column
    col = int(relative_x / diamond_width - (0.5 if row % 2 == 1 else 0))
    
    # Refine the column calculation based on precise position within the tile
    tile_center_x, tile_center_y = center_of_tile(col, row, screen, backdrop_position)
    if row % 2 == 1:
        tile_center_x -= diamond_width / 2
    
    # Check if the point is left or right of the tile center and adjust accordingly
    if (relative_x < tile_center_x and relative_y < tile_center_y) or (relative_x < tile_center_x and relative_y > tile_center_y):
        col -= 1
    
    # Ensure the column is within bounds after adjustment
    if row % 2 == 0:
        if col < 0 or col >= grid_width:
            return None
    else:
        if col < 0 or col >= grid_width - 1:
            return None

    return col, row

def shade_tile(col, row, screen, backdrop_position):
    #overlay_surface.fill((0, 0, 0, 0)) 
    left, up, right, down = diamond_corners(col, row, screen, backdrop_position)
    TRANSLUCENCY = 128
    COLOR_BLACK = (0, 0, 0, TRANSLUCENCY)
    pygame.draw.polygon(screen, COLOR_BLACK, [left, up, right, down])
    screen.blit(screen, (0, 0)) 


#Drawing coordinates highlighted for sake of debudding
def draw_grid_coordinates(screen, coords, backdrop_position):
    if coords:
        col, row = coords

        font = pygame.font.SysFont(None, 36)
        text = f"({col}, {row})"
        text_surface = font.render(text, True, (255, 255, 255))  
        

        offset_y = 40

        center_x, center_y = center_of_tile(col, row, screen, backdrop_position)
        text_rect = text_surface.get_rect(center=(center_x, center_y + offset_y))

    
        pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(10, 10))  # Inflate creates padding

    
        screen.blit(text_surface, text_rect)
