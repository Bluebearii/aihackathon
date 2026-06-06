from PIL import Image, ImageDraw

def mask_circle():
    path = r"c:\Users\trahu\OneDrive\Desktop\CodeWorld\aihackathon\carepoint-clinic\frontend\public\logo.png"
    img = Image.open(path).convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    # We find the bounding box of the non-white/non-transparent pixels
    # Assuming the corner pixel is the background color we want to remove
    bg_color = pixels[0, 0]
    
    min_x = width
    max_x = 0
    min_y = height
    max_y = 0
    
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            # Check if it's significantly different from background and not fully transparent
            if a > 0 and (abs(r - bg_color[0]) > 15 or abs(g - bg_color[1]) > 15 or abs(b - bg_color[2]) > 15):
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
                
    # If we couldn't find a bounding box, fallback to the whole image
    if min_x >= max_x or min_y >= max_y:
        min_x, max_x, min_y, max_y = 0, width, 0, height
        
    print(f"Bounding box: {min_x}, {min_y}, {max_x}, {max_y}")
    
    # Create an anti-aliased circular mask
    scale = 4
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((min_x * scale, min_y * scale, max_x * scale, max_y * scale), fill=255)
    
    mask = mask.resize((width, height), Image.LANCZOS)
    
    # Apply the mask
    transparent_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
    transparent_img.paste(img, (0, 0), mask)
    
    # Crop it tightly
    cropped_img = transparent_img.crop((min_x, min_y, max_x, max_y))
    cropped_img.save(path)
    print("Logo circle cropped and background made fully transparent.")

if __name__ == "__main__":
    mask_circle()
