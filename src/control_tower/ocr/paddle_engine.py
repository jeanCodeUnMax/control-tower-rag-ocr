from __future__ import annotations

import logging
from typing import Any

from PIL import Image

logger = logging.getLogger(__name__)


class PaddleOCREngine:
    """
    Adaptateur pour PaddleOCR implémentant (partiellement) le protocole ImageToTextEngine.
    L'import de paddleocr est retardé (lazy loading) pour éviter de plomber
    le temps de démarrage si l'utilisateur n'a configuré que Tesseract.
    """

    def __init__(self, lang: str = "fr", use_gpu: bool = False) -> None:
        try:
            from paddleocr import PaddleOCR
            import numpy as np  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "PaddleOCR n'est pas installé. Exécutez : pip install paddleocr paddlepaddle"
            ) from exc

        # Stocker les références pour utilisation ultérieure
        self.np = np
        self.lang = lang
        self.use_gpu = use_gpu

        # Initialisation du modèle en mémoire
        # use_angle_cls=True permet de détecter l'orientation du texte (utile pour les PDF scannés)
        self.ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, use_gpu=self.use_gpu)

    def image_to_string(self, image: Image.Image, *, lang: str, config: str) -> str:
        """
        Convertit une image PIL en texte brut via PaddleOCR.
        NOTE : `lang` et `config` sont ignorés ici car le modèle PaddleOCR est déjà initialisé
        avec sa propre langue. L'interface est maintenue pour respecter le protocole.
        """
        # Convertir l'image PIL (RGB) en array numpy pour Paddle
        img_array = self.np.array(image.convert("RGB"))

        # cls=True permet la classification d'angle à la volée
        result = self.ocr.ocr(img_array, cls=True)

        if not result or not result[0]:
            return ""

        # result[0] contient une liste de blocs.
        # Chaque bloc est formaté ainsi : [ [points de la boite], (texte, score de confiance) ]
        texts = [line[1][0] for line in result[0]]
        
        return "\n".join(texts)

    def extract_structured(self, image: Image.Image, *, lang: str, config: str) -> list["LayoutBlock"]:
        """
        Convertit une image PIL en blocs structurés via PaddleOCR.
        """
        from control_tower.ocr.layout import LayoutBlock, BoundingBox

        img_array = self.np.array(image.convert("RGB"))
        result = self.ocr.ocr(img_array, cls=True)

        if not result or not result[0]:
            return []

        blocks = []
        for line in result[0]:
            # line[0] = [[x0,y0], [x1,y1], [x2,y2], [x3,y3]] (polygone)
            # line[1] = (texte, score)
            points = line[0]
            text, conf = line[1]
            
            # Convertir le polygone en BoundingBox (min/max)
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            x0, x1 = int(min(xs)), int(max(xs))
            y0, y1 = int(min(ys)), int(max(ys))
            
            blocks.append(
                LayoutBlock(
                    type="text",
                    text=text,
                    box=BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1),
                    confidence=float(conf)
                )
            )
        return blocks
