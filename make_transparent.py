from PIL import Image, ImageDraw

def main():
    path = r"c:\Users\trahu\OneDrive\Desktop\CodeWorld\aihackathon\carepoint-clinic\frontend\public\logo.png"
    img = Image.open(path).convert("RGBA")
    
    # Flood fill from the 4 corners to replace white with transparent
    transparent = (255, 255, 255, 0)
    # Using a threshold to catch off-white anti-aliased pixels near the edge
    ImageDraw.floodfill(img, (0, 0), transparent, thresh=50)
    ImageDraw.floodfill(img, (img.width-1, 0), transparent, thresh=50)
    ImageDraw.floodfill(img, (0, img.height-1), transparent, thresh=50)
    ImageDraw.floodfill(img, (img.width-1, img.height-1), transparent, thresh=50)
    
    img.save(path)
    print("Logo background made transparent.")

if __name__ == "__main__":
    main()
