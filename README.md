# Digital Calibration Certificate (DCC) Generator

This project extracts text from printed calibration certificates using OCR and transforms it into an XML schema conforming to DCC Standards.

## Prerequisites

1. Python 3.7 or higher
2. Tesseract OCR engine installed on your system
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
     - Direct download: https://digi.bib.uni-mannheim.de/tesseract/
     - Download the latest installer (e.g., tesseract-ocr-w64-setup-v5.3.1.20230401.exe)
   - Linux: `sudo apt install tesseract-ocr`
   - Mac: `brew install tesseract`

## Setup

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Configure Tesseract OCR (several options available):
   
   **Option 1: Edit the script directly**
   - Open `ocr_to_dcc.py` in a text editor
   - Find the line: `# TESSERACT_DIRECT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`
   - Uncomment it and change the path to your Tesseract installation
   
   **Option 2: Use the configuration file**
   - Run the script once
   - When prompted, choose option 1 and enter your Tesseract path
   - Choose to save the configuration when asked
   - This will create an `ocr_config.json` file with your settings
   
   **Option 3: Automatic detection**
   - The script will attempt to find Tesseract automatically in common locations
   - If Tesseract is in your system PATH, it will be detected automatically

## Usage

1. Place your calibration certificate images in the `dataset` folder
2. Run the script:
   ```
   python ocr_to_dcc.py
   ```
3. The script will:
   - Try to find your Tesseract OCR installation
   - Extract text from the image using OCR
   - Parse the text to identify key certificate elements
   - Generate an XML file conforming to DCC standards
   - Save the XML to `dcc_certificate.xml`
   - Demonstrate XPath queries on the generated XML

## Troubleshooting Tesseract Installation

If the script cannot find your Tesseract installation:

1. **Verify Installation**:
   - Ensure Tesseract OCR is properly installed on your system
   - On Windows, make sure the installer completed successfully
   - Try running `tesseract --version` in a command prompt to check

2. **Specify the Path**:
   - When prompted, select option 1 to enter the custom path
   - The path should point directly to the tesseract.exe file, not just the directory
   - Common paths:
     - Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`
     - Linux/Mac: Usually `/usr/bin/tesseract` or in PATH

3. **Save Configuration**:
   - When asked, choose to save the configuration for future use
   - This will create an `ocr_config.json` file so you don't need to enter the path again

4. **Fallback to Demo Mode**:
   - If you can't get Tesseract working, use option 2 when prompted
   - This will use sample data to demonstrate the XML generation and XPath functionality

## Customizing the Parser

You may need to adjust the regular expressions in the `parse_certificate_data` function to match the specific format of your calibration certificates:

```python
patterns = {
    'certificate_number': r'Certificate\s+No[.:]\s*([A-Za-z0-9-]+)',
    'calibration_date': r'Date\s+of\s+Calibration[.:]\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{1,2},\s*\d{4})',
    # Add or modify patterns as needed
}
```

## XML Schema

The generated XML follows this structure:

```xml
<DigitalCalibrationCertificate>
  <AdministrativeData>
    <CertificateNumber>...</CertificateNumber>
    <CalibrationDate>...</CalibrationDate>
  </AdministrativeData>
  <Instrument>
    <Name>...</Name>
    <SerialNumber>...</SerialNumber>
    <Manufacturer>...</Manufacturer>
    <Model>...</Model>
  </Instrument>
  <CalibrationResults>
    <Note>Results extracted from certificate</Note>
  </CalibrationResults>
  <RawExtractedText>...</RawExtractedText>
</DigitalCalibrationCertificate>
```

## XPath Queries

The script demonstrates several XPath queries that can be used to locate specific elements in the XML:

- Certificate Number: `//CertificateNumber`
- Instrument Details: `//Instrument/*`
- All Text Elements: `//*[text()]`

You can add custom XPath queries by modifying the `demonstrate_xpath` function. 