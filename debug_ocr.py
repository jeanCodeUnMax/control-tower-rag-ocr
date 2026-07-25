import sys
import os
from pathlib import Path

# Ajouter src au pythonpath artificiellement pour imiter uvicorn
sys.path.insert(0, str(Path("src").resolve()))

from control_tower.config import OCRConfig
from control_tower.ocr.pdf import PDFOCRProvider

def test_ocr():
    print("=== DÉBUT DU TEST DE DÉBOGAGE ===")
    import control_tower.ocr.pdf as pdf_mod
    print("1. Fichier chargé pour OCR :", pdf_mod.__file__)
    
    config = OCRConfig(mode="force_ocr")
    print("2. Mode configuré :", config.mode)
    
    provider = PDFOCRProvider()
    use_native = provider._use_native_text("Test de texte bidon", config)
    print("3. _use_native_text renvoie :", use_native)
    
    print("4. Si _use_native_text est True, c'est l'ancien code qui tourne.")
    print("   Si c'est False, le nouveau code tourne correctement.")
    print("================================")

if __name__ == "__main__":
    test_ocr()
