from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import numpy as np
import logging
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_package(package_name: str):
    logger.info(f"Installing missing package: {package_name}")
    try:
        packages = package_name.split()
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        logger.info(f"Successfully installed {package_name}")
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to install {package_name}. Your Python version ({sys.version_info.major}.{sys.version_info.minor}) might not be supported by this package. Please try a different OCR backend."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

class OCRBackend(ABC):
    """Abstract base class for OCR backends."""
    
    @abstractmethod
    def detect(self, image: Union[str, np.ndarray]) -> List[Dict[str, Any]]:
        """
        Detect text in an image.
        
        Args:
            image: Path to image file or numpy array.
            
        Returns:
            List of dictionaries containing:
            - 'text': The detected text string.
            - 'bbox': Bounding box coordinates [[x1, y1], [x2, y2], [x3, y3], [x4, y4]].
            - 'confidence': Confidence score (0-1).
        """
        pass

class EasyOCRBackend(OCRBackend):
    """OCR backend using EasyOCR."""
    
    def __init__(self, use_gpu: bool = True, lang_list: List[str] = ['en']):
        try:
            import easyocr
        except ImportError:
            install_package("easyocr")
            import easyocr

        self.reader = easyocr.Reader(lang_list, gpu=use_gpu)
        logger.info(f"EasyOCR initialized (GPU={use_gpu}, Langs={lang_list})")

    def detect(self, image: Union[str, np.ndarray]) -> List[Dict[str, Any]]:
        # EasyOCR readtext returns: [(bbox, text, prob), ...]
        results = self.reader.readtext(image)
        
        output = []
        for bbox, text, confidence in results:
            bbox_list = [list(point) for point in bbox]
            output.append({
                'text': text,
                'bbox': bbox_list,
                'confidence': confidence
            })
            
        return output

class PaddleOCRBackend(OCRBackend):
    """OCR backend using PaddleOCR (via RapidOCR-ONNX for broader compatibility)."""
    
    def __init__(self, use_gpu: bool = True, lang: str = 'en'):
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError:
            install_package("rapidocr-onnxruntime")
            from rapidocr_onnxruntime import RapidOCR
            
        self.ocr = RapidOCR()
        logger.info(f"PaddleOCR (RapidOCR) initialized")
        
    def detect(self, image: Union[str, np.ndarray]) -> List[Dict[str, Any]]:
        results, elapse = self.ocr(image)
        output = []
        if not results:
            return output
            
        for line in results:
            if not line: continue
            bbox, text, confidence = line
            output.append({
                'text': text,
                'bbox': bbox,
                'confidence': float(confidence)
            })
        return output
