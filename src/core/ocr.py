from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            self.reader = easyocr.Reader(lang_list, gpu=use_gpu)
            logger.info(f"EasyOCR initialized (GPU={use_gpu}, Langs={lang_list})")
        except ImportError:
            logger.error("EasyOCR not installed. Please install 'easyocr'.")
            raise

    def detect(self, image: Union[str, np.ndarray]) -> List[Dict[str, Any]]:
        # EasyOCR readtext returns: [(bbox, text, prob), ...]
        # bbox is usually a list of 4 points [[x,y], [x,y], [x,y], [x,y]]
        results = self.reader.readtext(image)
        
        output = []
        for bbox, text, confidence in results:
            # Convert bbox to list of lists if it's not already
            bbox_list = [list(point) for point in bbox]
            
            output.append({
                'text': text,
                'bbox': bbox_list,
                'confidence': confidence
            })
            
        return output
