# Installation Guide for RECON Module Dependencies

## System Dependencies

### 1. Tesseract OCR
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (e.g., tesseract-ocr-w64-setup-5.3.1.20230401.exe)
3. During installation:
   - Install in `C:\Program Files\Tesseract-OCR`
   - Add to system PATH (check the option in installer)
4. Install Spanish language data:
   - Download `spa.traineddata` from: https://github.com/tesseract-ocr/tessdata
   - Place it in `C:\Program Files\Tesseract-OCR\tessdata`

### 2. Poppler for PDF Processing
1. Download Poppler for Windows from: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract the downloaded zip file
3. Move the extracted folder to `C:\Program Files\poppler`
4. Add `C:\Program Files\poppler\Library\bin` to system PATH:
   - Open System Properties > Advanced > Environment Variables
   - Under System Variables, find PATH
   - Add new entry: `C:\Program Files\poppler\Library\bin`

## Verification

To verify the installation:

1. Open Command Prompt and run:
```cmd
tesseract --version
```

2. Test PDF processing by running Python:
```python
from pdf2image import convert_from_path
print("PDF processing libraries installed correctly!")
```

## Troubleshooting

If you encounter "DLL not found" errors:
1. Ensure all PATH variables are set correctly
2. Restart your IDE/terminal after setting PATH variables
3. Verify that all required DLLs are in the specified directories
