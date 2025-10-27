
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re
from tqdm import tqdm
import fitz  # PyMuPDF
import io
import img2pdf

# --- PDF Processing Functions ---

def pdf_to_images(pdf_path, dpi=200):
    """Converts a PDF file to a list of PIL images."""
    print(f"Converting PDF '{os.path.basename(pdf_path)}' to images at {dpi} DPI...")
    images = []
    try:
        pdf_document = fitz.open(pdf_path)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        
        for page_num in tqdm(range(len(pdf_document)), desc="Converting PDF pages"):
            page = pdf_document.load_page(page_num)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            img_data = pixmap.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            images.append(image)
        pdf_document.close()
    except Exception as e:
        print(f"Failed to convert PDF to images: {e}")
        return []
    print("PDF conversion complete.")
    return images

def save_images_to_pdf(images, output_path):
    """Saves a list of PIL images to a single PDF file."""
    if not images:
        print("Warning: No images to save to PDF.")
        return
        
    print(f"Saving {len(images)} annotated pages to '{os.path.basename(output_path)}'...")
    try:
        # img2pdf requires bytes-like objects
        image_bytes_list = []
        for img in tqdm(images, desc="Preparing images for PDF"):
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=95)
            image_bytes_list.append(img_buffer.getvalue())
        
        pdf_bytes = img2pdf.convert(image_bytes_list)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        print("Annotated PDF saved successfully.")
    except Exception as e:
        print(f"Failed to save images to PDF: {e}")

# --- Post-processing Functions ---

def re_match(text):
    """Extracts layout information (references and detections) from the model's output."""
    pattern = r'(<\|ref\|>(.*?)<\|/ref\|><\|det\|>(.*?)<\|/det\|>)'
    matches = re.findall(pattern, text, re.DOTALL)

    mathes_image = []
    mathes_other = []
    for a_match in matches:
        if '<|ref|>image<|/ref|>' in a_match[0]:
            mathes_image.append(a_match[0])
        else:
            mathes_other.append(a_match)
    return matches, mathes_image, mathes_other

def extract_coordinates_and_label(ref_text, image_width, image_height):
    """Parses a single reference to get the label and coordinates."""
    try:
        label_type = ref_text[1]
        # Use regex to find the list within the string, as eval is unsafe
        coord_str_match = re.search(r'\[.*\]', ref_text[2])
        if not coord_str_match:
            return None
        # Safely evaluate the list of coordinates
        cor_list = eval(coord_str_match.group(0))
    except Exception as e:
        print(f"Error parsing coordinates: {e}")
        return None
    return (label_type, cor_list)

def draw_bounding_boxes(image: Image.Image, refs, output_path):
    """Draws bounding boxes on the image based on model output."""
    image_width, image_height = image.size
    img_draw = image.copy()
    draw = ImageDraw.Draw(img_draw)
    overlay = Image.new('RGBA', img_draw.size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(overlay)
    
    font = ImageFont.load_default()
    img_idx = 0

    # print(f"Drawing {len(refs)} bounding box sets...")
    for i, ref in enumerate(refs):
        try:
            result = extract_coordinates_and_label(ref, image_width, image_height)
            if not result:
                continue
            
            label_type, points_list = result
            color = (np.random.randint(0, 200), np.random.randint(0, 200), np.random.randint(0, 255))
            color_a = color + (20,)

            for points in points_list:
                x1, y1, x2, y2 = points
                x1 = int(x1 / 999 * image_width)
                y1 = int(y1 / 999 * image_height)
                x2 = int(x2 / 999 * image_width)
                y2 = int(y2 / 999 * image_height)

                if label_type == 'image':
                    try:
                        # The output_path here is the main output dir, let's save sub-images in its 'images' subdir
                        sub_image_dir = os.path.join(output_path, "images")
                        os.makedirs(sub_image_dir, exist_ok=True)
                        cropped = image.crop((x1, y1, x2, y2))
                        cropped.save(f"{sub_image_dir}/img_{img_idx}.jpg")
                    except Exception as e:
                        print(f"Could not save cropped image: {e}")
                    img_idx += 1
                
                # Draw rectangle and label
                width = 4 if label_type == 'title' else 2
                draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
                draw2.rectangle([x1, y1, x2, y2], fill=color_a, outline=(0, 0, 0, 0), width=1)
                
                text_x = x1
                text_y = max(0, y1 - 15)
                text_bbox = draw.textbbox((text_x, text_y), label_type, font=font)
                draw.rectangle(text_bbox, fill=(255, 255, 255, 80))
                draw.text((text_x, text_y), label_type, font=font, fill=color)

        except Exception as e:
            print(f"An error occurred while drawing a box: {e}")
            continue
            
    img_draw.paste(overlay, (0, 0), overlay)
    return img_draw
