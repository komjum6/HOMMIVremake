# currently requires Pillow (python image library). Probably temporary
# code based off H4ResourceEditor


from io import BytesIO
from PIL import Image
from time import time

TRANSPARENCY_WITH_ALPHA = 4
FASTMASK_STEP = 131

def get_byte(b: BytesIO):
    return int.from_bytes(b.read(1), "little")

def get_short(b: BytesIO):
    return int.from_bytes(b.read(2), "little")

def get_int(b: BytesIO):
    return int.from_bytes(b.read(4), "little")


def color_parser(b: BytesIO):
    num_colors = get_short(b)
    first_opaque_color = get_short(b)

    print(f"numColors: {num_colors}") ####
    print(f"{first_opaque_color=}") ####

    colors = []
    for i in range(num_colors):
        blue = get_byte(b)
        green = get_byte(b)
        red = get_byte(b)
        colors.append((red, green, blue))
    return colors, first_opaque_color


def color_parser_int(b: BytesIO):
    num_colors = get_short(b)
    print(f"numColors: {num_colors}") ####
    colors = []
    for i in range(num_colors):
        colors.append(get_int(b))


def image_parser(b: BytesIO):
    print("")
    colors = color_parser(b)
    image_name_len = get_short(b)

    print(f"{image_name_len=}") ####

    name = b.read(image_name_len).decode("ascii")
    print(f"{name=}") ####

    blend_mode = get_byte(b)
    print(f"{blend_mode=}")

    startX = get_int(b)
    startY = get_int(b)
    endX = get_int(b)
    endY = get_int(b)
    line_pos = b.tell()

    print(f"{startX=} {startY=} {endX=} {endY=}") #####
    print(f"{line_pos=}") ####

    height = endY - startY
    width = endX - startX

    print(f"{width=} {height=}") ####

    line_offsets = []
    for i in range(height):
        line_start_x = get_short(b)
        line_end_x = get_short(b)
        data_offset = get_int(b)
        # print(f"{line_start_x=} {line_end_x=} {data_offset=}")
        line_offsets.append((line_start_x, line_end_x, data_offset))
    
    pixel_data_offset = b.tell()
    pixel_data_len = 0

    print(f"{pixel_data_offset=}") ####

    pixels_data_block = []

    for i in line_offsets:
        arr = [0]*(i[1] - i[0])
        if len(arr) > 0:
            for k in range(len(arr)):
                arr[k] = get_byte(b)
            pixel_data_len += len(arr)
            pixels_data_block.append(arr)
    
    alpha = None
    acceleration_mask = None
    if blend_mode == TRANSPARENCY_WITH_ALPHA:
        alpha_offset = b.tell()
        alpha_data_len = (pixel_data_len + 1)//2
        alpha = []
        for i in range(alpha_data_len):
            x = get_byte(b)
            lower = (0x0F & x) * 17
            upper = ((0xF0 & x) >> 4) * 17
            alpha += [lower, upper]

        if colors[1] != 0:
            acceleration_mask_offset = b.tell()
            fast_mask_len = (pixel_data_len + FASTMASK_STEP) // 128
            acceleration_mask = []
            for i in range(fast_mask_len):
                acceleration_mask.append(get_byte(b))
    print(pixel_data_len)
    print("")
    print(len(alpha))
    return ((width, height), pixels_data_block, line_offsets, colors, alpha, acceleration_mask, name)



def paint_image(x):
    width = x[0][0]
    height = x[0][1]
    colors = x[3][0]
    alpha = x[4]
    index = 0
    if alpha is not None:
        img = Image.new("RGBA", (width, height))
    else:
        img = Image.new("RGB", (width, height))
    
    for i in range(height):
        pixels = x[1][i]
        if len(pixels) == 0:
            continue

        line = x[2][i]
        if alpha is not None:
            for k in range(line[0], line[1]):
                clr = colors[pixels[k - line[0]]] + (alpha[index],)
                img.putpixel((k, i), clr)
                index += 1
        else:
            for k in range(line[0], line[1]):
                img.putpixel((k, i), colors[pixels[k - line[0]]])
                index += 1

    print("fnish line")
    img.save("out.png")


def sprite_parser(b: BytesIO):
    # TODO handle more than first frame
    frame_count = get_short(b)
    print(f"frameCount: {frame_count}") ####
    x = image_parser(b)

    paint_image(x)



def parse_actor_sequence(filename: str):
    """Takes in an actor_sequence .h4d file.
    Currently only processes the first frame.
    Currently just uses Pillow to save it as an image.
    """
    print("")
    print("debug info: ")
    print("")
    t0 = time()

    with open(filename, "rb") as fp:
        data = fp.read()
        buffer = BytesIO(data)

    file_type = get_short(buffer)
    file_format = get_short(buffer)

    print(f"{file_type=}")
    print(f"{file_format=}")

    if file_format >= 3:
        print("file format !!!")
        extra_header_len = get_short(buffer)
        extra_header_info = []
        for i in range(extra_header_len):
            extra_header_info.append(get_int(buffer))

    # start sprite parser


    sprite_parser(buffer)

    t1 = time()
    print(f"total time: {t1-t0}")


# probably temporary
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print("Got more command line arguments than expected")

    if len(sys.argv) > 1:
        if sys.argv[1].strip() in ["--help", "-h", "\\?"]:
            print("usage: python parse_sprites.py filename")
            print("Takes in an actor_sequence .h4d file")
            quit()
        if not ".h4d" in sys.argv[1]:
            print(f"{sys.argv[1]} is probably not a valid .h4d file")
            quit()
        try:
            parse_actor_sequence(sys.argv[1])
        except FileNotFoundError:
            print(f"Could not open file \"{sys.argv[1]}\"")
            quit()
        print(f"Saved {sys.argv[1]} as out.png")
    else:
        print("Trying to parse default file \"actor_sequence.this.h4d\"")
        print("Otherwise, see --help")
        try:
            parse_actor_sequence("actor_sequence.this.h4d")
        except FileNotFoundError:
            print(f"Could not open file \"actor_sequence.this.h4d\"")
            quit()
    
        
    