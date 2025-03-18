import os
import sys
import pytesseract
from PIL import Image
import xml.etree.ElementTree as ET
import re
from lxml import etree
import subprocess
import platform
import json

# ======== TESSERACT CONFIGURATION ========
# OPTION 1: Set the path directly here (uncomment and modify the line below)
# TESSERACT_DIRECT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_DIRECT_PATH = None  # Set to None if you want automatic detection

# Configuration file path
CONFIG_FILE = "ocr_config.json"

# Try to load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('tesseract_path')
        except Exception as e:
            print(f"Error loading config file: {e}")
    return None

# Save configuration to file
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

# Try to find Tesseract installation automatically based on platform
def find_tesseract_path():
    # First check if path is specified directly in the script
    if TESSERACT_DIRECT_PATH and os.path.exists(TESSERACT_DIRECT_PATH):
        return TESSERACT_DIRECT_PATH
        
    # Then check if path is in config file
    config_path = load_config()
    if config_path and os.path.exists(config_path):
        return config_path
    
    system = platform.system()
    
    if system == 'Windows':
        # Common installation paths on Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            # Add user's Local AppData path
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Tesseract-OCR', 'tesseract.exe'),
            # Check in PATH
            'tesseract'
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
            elif path == 'tesseract':
                # Check if available in PATH
                try:
                    subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    return 'tesseract'  # Return just the command if found in PATH
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
                
    elif system in ['Linux', 'Darwin']:  # Linux or macOS
        # On Linux/Mac, check if tesseract is in PATH
        try:
            subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return 'tesseract'
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
    return None

# Try to find Tesseract path
TESSERACT_PATH = find_tesseract_path()
IMAGE_PATH = os.path.join('dataset', 'cert0.jpg')

# Configure pytesseract path if found
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"Using Tesseract OCR at: {TESSERACT_PATH}")
else:
    print("=" * 80)
    print("WARNING: Tesseract OCR not found. Please install it or specify the correct path.")
    print("Installation instructions:")
    print("  - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("      Direct download: https://digi.bib.uni-mannheim.de/tesseract/")
    print("      Download the latest installer (e.g., tesseract-ocr-w64-setup-v5.3.1.20230401.exe)")
    print("  - Linux: sudo apt install tesseract-ocr")
    print("  - macOS: brew install tesseract")
    print("=" * 80)
    print("WAYS TO FIX THIS ERROR:")
    print("1. Install Tesseract using the instructions above")
    print("2. Edit this script and set TESSERACT_DIRECT_PATH to your Tesseract installation path")
    print("3. When prompted, enter the path to save it to a configuration file")
    print("=" * 80)

def is_tesseract_available():
    """Check if Tesseract is available"""
    if not TESSERACT_PATH:
        return False
        
    try:
        if TESSERACT_PATH == 'tesseract':
            # Check in PATH
            subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            # Check specific path
            subprocess.run([TESSERACT_PATH, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def extract_text_from_image(image_path):
    """Extract text from an image using OCR"""
    # Verify image exists
    if not os.path.isfile(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None
        
    # Check if Tesseract is available
    if not is_tesseract_available():
        print("\nTesseract OCR is not available. Would you like to:")
        print("1. Enter a custom path to Tesseract (recommended)")
        print("2. Use sample data for demonstration purposes")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            custom_path = input("Enter the full path to tesseract executable: ").strip()
            if os.path.isfile(custom_path):
                pytesseract.pytesseract.tesseract_cmd = custom_path
                print(f"Using Tesseract at: {custom_path}")
                
                # Ask if user wants to save this configuration
                save_choice = input("Would you like to save this path for future use? (y/n): ").strip().lower()
                if save_choice == 'y':
                    save_config(custom_path)
                
                # Try again with the new path
                return extract_text_from_image(image_path)
            else:
                print(f"Invalid path: {custom_path}")
                print("Please verify that the file exists and you have the correct path.")
                retry = input("Would you like to try again? (y/n): ").strip().lower()
                if retry == 'y':
                    return extract_text_from_image(image_path)
                else:
                    # Fall back to sample data
                    print("Using sample data instead...")
                    return get_sample_data()
                
        elif choice == '2':
            # Return sample data for demonstration
            return get_sample_data()
            
        else:  # choice 3 or invalid
            print("Exiting program.")
            sys.exit(0)
    
    # If we get here, Tesseract should be available
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        print("Falling back to sample data...")
        return get_sample_data()

def get_sample_data():
    """Return sample data for demonstration"""
    print("Using sample data for demonstration...")
    return """
    CALIBRATION CERTIFICATE
    
    Certificate No: CAL-2023-12345
    
    Date of Calibration: March 15, 2023
    
    Instrument: Digital Multimeter
    Serial No: DMM-9876543
    Manufacturer: TechMeter Inc.
    Model: DMM-2000
    
    Calibration Results:
    - DC Voltage: PASS
    - AC Voltage: PASS
    - Resistance: PASS
    
    This certificate is issued in accordance with standard procedures.
    """

def parse_certificate_data(text):
    """Parse the extracted text to identify key certificate elements"""
    data = {}
    
    # Example patterns to extract (customize based on your certificate format)
    patterns = {
        'certificate_number': r'Certificate\s+No[.:]\s*([A-Za-z0-9-]+)',
        'calibration_date': r'Date\s+of\s+Calibration[.:]\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{1,2},\s*\d{4})',
        'instrument_name': r'Instrument[.:]\s*([A-Za-z0-9\s]+)',
        'serial_number': r'Serial\s+No[.:]\s*([A-Za-z0-9-]+)',
        'manufacturer': r'Manufacturer[.:]\s*([A-Za-z0-9\s]+)',
        'model': r'Model[.:]\s*([A-Za-z0-9\s-]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1).strip()
        else:
            data[key] = "Not found"
    
    # Add the full text for manual inspection
    data['full_text'] = text
    
    return data

def create_dcc_xml(data):
    """Create XML in DCC format from extracted data"""
    # Create the root element
    root = ET.Element("DigitalCalibrationCertificate")
    
    # Add administrative data
    admin_data = ET.SubElement(root, "AdministrativeData")
    ET.SubElement(admin_data, "CertificateNumber").text = data.get('certificate_number', 'Unknown')
    ET.SubElement(admin_data, "CalibrationDate").text = data.get('calibration_date', 'Unknown')
    
    # Add instrument data
    instrument = ET.SubElement(root, "Instrument")
    ET.SubElement(instrument, "Name").text = data.get('instrument_name', 'Unknown')
    ET.SubElement(instrument, "SerialNumber").text = data.get('serial_number', 'Unknown')
    ET.SubElement(instrument, "Manufacturer").text = data.get('manufacturer', 'Unknown')
    ET.SubElement(instrument, "Model").text = data.get('model', 'Unknown')
    
    # Add results section (placeholder)
    results = ET.SubElement(root, "CalibrationResults")
    ET.SubElement(results, "Note").text = "Results extracted from certificate"
    
    # Add raw text for verification
    raw_data = ET.SubElement(root, "RawExtractedText")
    raw_data.text = data.get('full_text', '')
    
    # Convert to string with proper formatting
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    
    return tree

def save_xml(tree, output_path):
    """Save the XML tree to a file"""
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

def demonstrate_xpath(xml_path):
    """Demonstrate XPath queries on the generated XML"""
    # Parse the XML file
    tree = etree.parse(xml_path)
    root = tree.getroot()
    
    print("\nXPath Query Examples:")
    print("-" * 50)
    
    # Example XPath queries
    queries = {
        "Certificate Number": "//CertificateNumber",
        "Instrument Details": "//Instrument/*",
        "All Text Elements": "//*[text()]",
    }
    
    for description, xpath in queries.items():
        print(f"\n{description}:")
        elements = root.xpath(xpath)
        for element in elements:
            if hasattr(element, 'tag'):
                print(f"  {element.tag}: {element.text}")
            else:
                print(f"  {element}")

def main():
    """Main execution function"""
    print("Starting OCR to DCC conversion process...")
    
    # Step 1: Extract text from the certificate image
    print(f"Processing image: {IMAGE_PATH}")
    extracted_text = extract_text_from_image(IMAGE_PATH)
    
    if not extracted_text:
        print("Failed to extract text from the image. Please check the image and Tesseract installation.")
        return
    
    print("Text extraction completed.")
    
    # Step 2: Parse the extracted text
    print("Parsing certificate data...")
    certificate_data = parse_certificate_data(extracted_text)
    
    # Step 3: Create XML in DCC format
    print("Creating DCC XML...")
    xml_tree = create_dcc_xml(certificate_data)
    
    # Step 4: Save the XML
    output_xml_path = "dcc_certificate.xml"
    save_xml(xml_tree, output_xml_path)
    print(f"XML saved to: {output_xml_path}")
    
    # Step 5: Demonstrate XPath queries
    demonstrate_xpath(output_xml_path)
    
    print("\nProcess completed successfully!")

if __name__ == "__main__":
    main() 