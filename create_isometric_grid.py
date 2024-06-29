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

grid_height = 48
grid_width = 30



diamond_width = backdrop_width / grid_width


backdrop_adjusted = 10
adjusted_height = 80
backdrop_height -= adjusted_height

diamond_height = diamond_width / 2


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
            y = start_y +  (diamond_height * row) + (diamond_height /2)
            
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
    start_y += adjusted_height
    # Convert grid coordinates (row, col) to pixel coordinates (x, y)
    #x = start_x + col * (diamond_width / 2) - row * (diamond_width / 2)
    #y = start_y + row * (diamond_height / 2) + col * (diamond_height / 2)
   
    x = (start_x +  diamond_width/2) + ((col) * (diamond_width))
    
    y = (start_y + diamond_height/2) + ((row) * (diamond_height))
    
    #grid dimensions
    #30, 48
    #inner diamonds are 0.5 off of outer diamonds
    


    #offset for png sprite position
    circle_color = (255, 0, 0)  # Red color for the circle
    circle_radius = 7  # Example radius
    pygame.draw.circle(screen, circle_color, (x, y), circle_radius)
    print(col, row)
    print(x, y)
    offset_x = 160 # 148
    offset_y = 163  #170
    
    #print(x, y)

    

    #grid size is 64, 118, 
    return (x - offset_x, y - offset_y)
    
   

