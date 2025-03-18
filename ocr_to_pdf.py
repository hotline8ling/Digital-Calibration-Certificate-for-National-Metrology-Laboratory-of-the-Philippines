import os
import sys
import pytesseract
from PIL import Image
import xml.etree.ElementTree as ET
import fitz  # PyMuPDF
import json
import platform
import subprocess
import tempfile
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, transparent, Color
from io import BytesIO

# ======== TESSERACT CONFIGURATION ========
TESSERACT_DIRECT_PATH = None  # Set to None for automatic detection
CONFIG_FILE = "ocr_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('tesseract_path')
        except Exception as e:
            print(f"Error loading config file: {e}")
    return None

def save_config(tesseract_path):
    try:
        config = {'tesseract_path': tesseract_path}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print(f"Configuration saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error saving config file: {e}")
        return False

def find_tesseract_path():
    if TESSERACT_DIRECT_PATH and os.path.exists(TESSERACT_DIRECT_PATH):
        return TESSERACT_DIRECT_PATH
    
    config_path = load_config()
    if config_path and os.path.exists(config_path):
        return config_path
    
    system = platform.system()
    
    if system == 'Windows':
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Tesseract-OCR', 'tesseract.exe'),
            'tesseract'
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
            elif path == 'tesseract':
                try:
                    subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    return 'tesseract'
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
    
    elif system in ['Linux', 'Darwin']:
        try:
            subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return 'tesseract'
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    return None

TESSERACT_PATH = find_tesseract_path()
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"Using Tesseract OCR at: {TESSERACT_PATH}")
else:
    print("WARNING: Tesseract OCR not found. Please install it.")
    sys.exit(1)

def get_text_blocks(image_path):
    """Extract text blocks with their positions from the image"""
    try:
        image = Image.open(image_path)
        # Get detailed OCR data including bounding boxes
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        blocks = []
        current_block = {"text": [], "bbox": None}
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:  # Filter out low-confidence results
                text = data['text'][i].strip()
                if text:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    if not current_block["bbox"]:
                        current_block["bbox"] = [x, y, w, h]
                    else:
                        # Extend bounding box if needed
                        current_block["bbox"] = [
                            min(current_block["bbox"][0], x),
                            min(current_block["bbox"][1], y),
                            max(current_block["bbox"][2], w),
                            max(current_block["bbox"][3], h)
                        ]
                    
                    current_block["text"].append(text)
                else:
                    if current_block["text"]:
                        blocks.append({
                            "text": " ".join(current_block["text"]),
                            "bbox": current_block["bbox"]
                        })
                        current_block = {"text": [], "bbox": None}
        
        # Add the last block if it exists
        if current_block["text"]:
            blocks.append({
                "text": " ".join(current_block["text"]),
                "bbox": current_block["bbox"]
            })
        
        return blocks
    except Exception as e:
        print(f"Error processing image: {e}")
        return []

def create_pdf_with_metadata(image_path, output_pdf):
    """Create a PDF with bounding boxes around text blocks"""
    try:
        # Get text blocks from the image
        text_blocks = get_text_blocks(image_path)
        
        # Create a PDF with the image using reportlab
        c = canvas.Canvas(output_pdf, pagesize=letter)
        
        # Add the image
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        # Scale image to fit on the page while maintaining aspect ratio
        aspect = img_height / float(img_width)
        if aspect > 1:
            # Portrait
            pdf_width = 7 * inch
            pdf_height = pdf_width * aspect
        else:
            # Landscape
            pdf_height = 9 * inch
            pdf_width = pdf_height / aspect
        
        # Center the image on the page
        x = (letter[0] - pdf_width) / 2
        y = (letter[1] - pdf_height) / 2
        
        c.drawImage(image_path, x, y, width=pdf_width, height=pdf_height)
        
        # Calculate scaling factors
        scale_x = pdf_width / img_width
        scale_y = pdf_height / img_height
        
        # Draw rectangles around text blocks
        c.setStrokeColor(Color(0, 0, 1, alpha=0.5))  # Blue color with 50% transparency
        c.setLineWidth(1)
        
        for block in text_blocks:
            # Convert image coordinates to PDF coordinates
            pdf_x = x + block['bbox'][0] * scale_x
            pdf_y = letter[1] - (y + (block['bbox'][1] + block['bbox'][3]) * scale_y)  # Flip Y coordinate
            pdf_width = block['bbox'][2] * scale_x
            pdf_height = block['bbox'][3] * scale_y
            
            # Draw rectangle
            c.rect(pdf_x, pdf_y, pdf_width, pdf_height)
        
        c.save()
        
        print(f"PDF created successfully: {output_pdf}")
        print(f"Number of text blocks with bounding boxes: {len(text_blocks)}")
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        raise

def main():
    # Set up input and output paths
    image_path = os.path.join('dataset', 'cert0.jpg')
    output_pdf = "certificate_with_boxes.pdf"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return
    
    print(f"Processing image: {image_path}")
    create_pdf_with_metadata(image_path, output_pdf)
    print("Process completed successfully!")

if __name__ == "__main__":
    main()