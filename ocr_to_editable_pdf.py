import os
import sys
import subprocess
import platform
import json
import tempfile
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

# ======== TESSERACT CONFIGURATION ========
CONFIG_FILE = "ocr_config.json"

def load_config():
    """Load Tesseract path from config file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('tesseract_path')
        except Exception as e:
            print(f"Error loading config file: {e}")
    return None

def save_config(tesseract_path):
    """Save Tesseract path to config file"""
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
    """Find Tesseract OCR installation path"""
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

# Initialize Tesseract
TESSERACT_PATH = find_tesseract_path()
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"Using Tesseract OCR at: {TESSERACT_PATH}")
else:
    print("WARNING: Tesseract OCR not found. Please install it.")
    sys.exit(1)

def image_to_editable_pdf(image_path, output_pdf, overlay_visible=False):
    """
    Convert an image to an editable PDF with searchable text
    
    Args:
        image_path: Path to the input image
        output_pdf: Path to save the output PDF
        overlay_visible: If True, the text overlay will be visible (for debugging)
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return False
        
        # Open the image
        img = Image.open(image_path)
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Create a new PDF document
        pdf_doc = fitz.open()
        
        # Add a page with the same dimensions as the image (in points, 72 points = 1 inch)
        dpi = 72  # Default PDF resolution
        width_in_points = img_width * 72 / dpi
        height_in_points = img_height * 72 / dpi
        page = pdf_doc.new_page(width=width_in_points, height=height_in_points)
        
        # Insert the image to fill the page
        rect = fitz.Rect(0, 0, width_in_points, height_in_points)
        page.insert_image(rect, filename=image_path)
        
        # Perform OCR
        print("Performing OCR on the image...")
        text_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        # Group text by block_num to create paragraphs
        blocks = {}
        for i in range(len(text_data['text'])):
            if int(text_data['conf'][i]) > 20:  # Filter out low-confidence results
                text = text_data['text'][i].strip()
                if text:
                    block_num = text_data['block_num'][i]
                    
                    if block_num not in blocks:
                        blocks[block_num] = {
                            'text': [],
                            'left': text_data['left'][i],
                            'top': text_data['top'][i],
                            'right': text_data['left'][i] + text_data['width'][i],
                            'bottom': text_data['top'][i] + text_data['height'][i]
                        }
                    else:
                        # Update the bounding box
                        blocks[block_num]['left'] = min(blocks[block_num]['left'], text_data['left'][i])
                        blocks[block_num]['top'] = min(blocks[block_num]['top'], text_data['top'][i])
                        blocks[block_num]['right'] = max(blocks[block_num]['right'], 
                                                        text_data['left'][i] + text_data['width'][i])
                        blocks[block_num]['bottom'] = max(blocks[block_num]['bottom'], 
                                                        text_data['top'][i] + text_data['height'][i])
                    
                    blocks[block_num]['text'].append(text)
        
        # Add text blocks to the PDF
        for block_num, block_data in blocks.items():
            # Convert image coordinates to PDF coordinates
            x = block_data['left'] * 72 / dpi
            y = block_data['top'] * 72 / dpi
            width = (block_data['right'] - block_data['left']) * 72 / dpi
            height = (block_data['bottom'] - block_data['top']) * 72 / dpi
            
            # Join the text in the block
            text = ' '.join(block_data['text'])
            
            # Create a text block on the PDF page
            text_rect = fitz.Rect(x, y, x + width, y + height)
            
            # Set text color - transparent for normal use, visible for debugging
            text_color = (0, 0, 0, 1) if overlay_visible else (0, 0, 0, 0)
            
            # Insert text
            page.insert_textbox(
                text_rect, 
                text, 
                fontname="helv",  # Use a standard font
                fontsize=11,  # Reasonable font size
                align=fitz.TEXT_ALIGN_LEFT,
                color=text_color
            )
            
            # For debugging: draw rectangles around text blocks
            if overlay_visible:
                page.draw_rect(text_rect, color=(1, 0, 0), width=0.5)
        
        # Add document properties
        pdf_doc.set_metadata({
            "title": "Searchable PDF from Image",
            "subject": "OCR-processed document",
            "keywords": "OCR, searchable PDF, text recognition",
            "creator": "OCR to PDF Converter",
        })
        
        # Save the PDF
        pdf_doc.save(output_pdf)
        pdf_doc.close()
        
        print(f"Editable PDF created successfully: {output_pdf}")
        return True
        
    except Exception as e:
        print(f"Error creating editable PDF: {e}")
        return False

def main():
    """Main execution function"""
    # Set up input and output paths
    image_path = os.path.join('dataset', 'cert0.jpg')
    output_pdf = "editable_certificate.pdf"
    
    # For debugging: set to True to make text visible
    debug_mode = False
    
    print(f"Processing image: {image_path}")
    success = image_to_editable_pdf(image_path, output_pdf, overlay_visible=debug_mode)
    
    if success:
        print("Process completed successfully!")
        print("The PDF contains searchable text overlaid on the image.")
        print("You can now search for text in the PDF using any PDF viewer.")
    else:
        print("Failed to create editable PDF.")

if __name__ == "__main__":
    main() 