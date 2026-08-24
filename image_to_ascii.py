import sys
import os
from PIL import Image

# ASCII characters ordered by density
ASCII_CHARS = "MND8OZ$7I?+=~:,.. "

def scale_image(image, new_width=42, new_height=25):
    """Resizes the image to the target width and height."""
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def convert_to_grayscale(image):
    """Converts the image to grayscale."""
    return image.convert("L")

def map_pixels_to_ascii(image):
    """Maps grayscale pixels to ASCII characters based on intensity."""
    pixels = image.getdata()
    ascii_str = []
    num_chars = len(ASCII_CHARS)
    for pixel_value in pixels:
        # Map 0-255 to index in ASCII_CHARS
        idx = int(pixel_value / 256.0 * num_chars)
        # Prevent index out of bounds
        idx = min(idx, num_chars - 1)
        ascii_str.append(ASCII_CHARS[idx])
    return "".join(ascii_str)

def main():
    if len(sys.argv) < 2:
        print("Usage: python image_to_ascii.py <path_to_image>")
        print("Example: python image_to_ascii.py my_face.jpg")
        return

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print(f"Error: File {img_path} not found.")
        return

    try:
        image = Image.open(img_path)
    except Exception as e:
        print(f"Error: Unable to open image. {e}")
        return

    # Resize and convert
    width = 42
    height = 25
    image = scale_image(image, width, height)
    image = convert_to_grayscale(image)

    # Convert pixels to ascii
    ascii_data = map_pixels_to_ascii(image)
    
    # Format into SVG tspan lines
    y_start = 30
    y_step = 20
    
    print("\n--- COPY AND PASTE THIS INTO YOUR SVG FILES (under <text class=\"ascii\">) --- \n")
    for i in range(height):
        start_idx = i * width
        end_idx = start_idx + width
        line_chars = ascii_data[start_idx:end_idx]
        
        # Escape XML special characters
        line_chars = line_chars.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Pad with spaces to keep it aligned if necessary, but keep exact length
        line_chars = line_chars.ljust(width, " ")
        
        y_val = y_start + (i * y_step)
        print(f'<tspan x="15" y="{y_val}">{line_chars}</tspan>')
    print("\n--------------------------------------------------------------------------\n")

if __name__ == "__main__":
    main()
