import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

from control_tower.ocr.paddle_engine import PaddleOCREngine


def test_paddle_engine_import_error():
    """Test que l'absence de paddleocr lève une RuntimeError explicite."""
    with patch.dict("sys.modules", {"paddleocr": None, "numpy": None}):
        with pytest.raises(RuntimeError, match="PaddleOCR n'est pas installé"):
            PaddleOCREngine()


def test_paddle_engine_extract_text():
    """Test que PaddleOCREngine convertit bien l'image et extrait le texte de la réponse."""
    mock_paddleocr_module = MagicMock()
    mock_numpy_module = MagicMock()
    
    mock_ocr_instance = MagicMock()
    mock_ocr_instance.ocr.return_value = [
        [
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ("Ligne 1", 0.99)),
            ([[0, 15], [10, 15], [10, 25], [0, 25]], ("Ligne 2", 0.95)),
        ]
    ]
    mock_paddleocr_module.PaddleOCR.return_value = mock_ocr_instance
    mock_numpy_module.array.return_value = "mock_array_data"

    with patch.dict("sys.modules", {"paddleocr": mock_paddleocr_module, "numpy": mock_numpy_module}):
        engine = PaddleOCREngine(lang="fr", use_gpu=False)
        image = Image.new("RGB", (100, 100))
        text = engine.image_to_string(image, lang="ignored", config="ignored")

        assert text == "Ligne 1\nLigne 2"
        mock_ocr_instance.ocr.assert_called_once()


def test_paddle_engine_extract_structured():
    """Test que PaddleOCREngine extrait correctement les LayoutBlocks."""
    mock_paddleocr_module = MagicMock()
    mock_numpy_module = MagicMock()
    
    mock_ocr_instance = MagicMock()
    mock_ocr_instance.ocr.return_value = [
        [
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ("Bloc 1", 0.99)),
        ]
    ]
    mock_paddleocr_module.PaddleOCR.return_value = mock_ocr_instance
    mock_numpy_module.array.return_value = "mock_array_data"

    with patch.dict("sys.modules", {"paddleocr": mock_paddleocr_module, "numpy": mock_numpy_module}):
        engine = PaddleOCREngine(lang="fr", use_gpu=False)
        image = Image.new("RGB", (100, 100))
        blocks = engine.extract_structured(image, lang="ignored", config="ignored")

        assert len(blocks) == 1
        assert blocks[0].text == "Bloc 1"
        assert blocks[0].box.x0 == 0
        assert blocks[0].box.x1 == 10
        assert blocks[0].box.y0 == 0
        assert blocks[0].box.y1 == 10
        assert blocks[0].confidence == 0.99
