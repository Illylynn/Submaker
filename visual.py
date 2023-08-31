from PIL import Image, ImageDraw, ImageFont, ImageGrab, ImageOps
import random
from progress import printProgressBar

def in_bbox(coords, box):
    if coords[0] > box[1][0] and coords[0] < box[1][0] + box[0][0]:
        if coords[1] > box[1][1] and coords[1] < box[1][1] + box[0][1]:
            return True
    return False

def create_visual(filename, affs):
    
    if filename == "copy":
        img = ImageGrab.grabclipboard()
    else:
        img = Image.open(filename) 
    
    img.load()
    
    inverted_img = ImageOps.invert(img.convert("RGB"))
    
    text_scale = 80
    
    text_canvas = Image.new(mode="RGBA", size = (img.width, img.height))
    text_draw = ImageDraw.Draw(text_canvas)
        
    font = "Bebas-Regular.ttf"
        
    new_font = ImageFont.truetype(font, text_scale)
        
    drawn_affs = []
        
    for index, aff in enumerate(affs):
        #if (index > 1):
        #    print ("\033[A")
        printProgressBar(index, len(affs))
        
        coordinates = [[x, y] for x in range(text_canvas.width) for y in range(text_canvas.height)]
                
        non_drawn_coordinates = [i for i in coordinates if all(not in_bbox(i, bbox) for bbox in drawn_affs)]
        
        index = random.randint(0, len(non_drawn_coordinates) - 1)
            
        text_draw.text(non_drawn_coordinates[index], aff, fill = (255, 255, 255), font = new_font)
            
        size = new_font.getsize(aff)
        coordinate = non_drawn_coordinates[index]
            
        drawn_affs.append([size, coordinate])
            
        
    text_mask = text_canvas.point(lambda x: x // 20)
            
    img.paste(inverted_img, (0, 0), text_mask)
        
    
    return img

