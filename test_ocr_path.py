from pathlib import Path
from control_tower.config import OCRConfig
from control_tower.ocr.pdf import PDFOCRProvider
import sys

def test_ocr():
    print("Python path:", sys.path)
    config = OCRConfig(mode="force_ocr")
    provider = PDFOCRProvider()
    print("Provider loaded from:", sys.modules['control_tower.ocr.pdf'].__file__)
    
    use_native = provider._use_native_text("Test", config)
    print("use_native:", use_native)
    
if __name__ == "__main__":
    test_ocr()
