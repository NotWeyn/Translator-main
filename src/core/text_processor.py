from typing import List, Dict, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class TextBlock:
    text: str
    bbox: List[List[int]]
    confidence: float

class TextProcessor:
    """
    Handles post-processing of OCR results:
    1. Clustering (grouping nearby text lines).
    2. Correction (fixing OCR errors).
    """

    def __init__(self):
        pass

    def cluster_text(self, raw_results: List[Dict[str, Any]], y_threshold: int = 20) -> List[TextBlock]:
        """
        Groups raw OCR text lines into coherent blocks based on proximity.
        
        Args:
            raw_results: Output from OCRBackend.detect().
            y_threshold: Max vertical distance to consider lines part of the same block.
                        Also controls horizontal merging sensitivity (x_threshold = max(50, y_threshold)).
            
        Returns:
            List of TextBlock objects (merged text).
        """
        if not raw_results:
            return []

        # Dynamic x_threshold: use at least 50px, but scale with y_threshold
        # This allows the "Merge Distance" slider to affect both vertical and horizontal merging
        x_threshold = max(50, y_threshold)

        # Sort by Y coordinate (top to bottom)
        # Use min of all y coordinates for robustness (handles rotated text better)
        sorted_results = sorted(raw_results, key=lambda r: min(p[1] for p in r['bbox']))
        
        clusters = []
        current_cluster = [sorted_results[0]]
        
        for i in range(1, len(sorted_results)):
            prev = current_cluster[-1]
            curr = sorted_results[i]
            
            # Robust vertical distance calculation using min/max of all y coordinates
            prev_bottom = max(p[1] for p in prev['bbox'])
            curr_top = min(p[1] for p in curr['bbox'])
            
            vertical_dist = curr_top - prev_bottom
            
            # Check horizontal overlap or proximity
            prev_left = min(p[0] for p in prev['bbox'])
            prev_right = max(p[0] for p in prev['bbox'])
            curr_left = min(p[0] for p in curr['bbox'])
            curr_right = max(p[0] for p in curr['bbox'])
            
            # Check if they overlap horizontally or are close
            # We relax the x_threshold to allow for indentation or slight misalignment
            horizontal_overlap = (prev_left <= curr_right + x_threshold) and (curr_left <= prev_right + x_threshold)
            
            # Punctuation check: If previous line ends with sentence-ending punctuation, 
            # it's likely a separate block unless very close.
            prev_text = prev['text'].strip()
            ends_with_punct = prev_text.endswith(('.', '!', '?'))
            
            # If it ends with punctuation, we require a much stricter vertical threshold to merge
            effective_y_threshold = y_threshold
            if ends_with_punct:
                effective_y_threshold = y_threshold * 0.5 # Reduce threshold by half if punctuation present
            
            if vertical_dist <= effective_y_threshold and horizontal_overlap:
                current_cluster.append(curr)
            else:
                clusters.append(self._merge_cluster(current_cluster))
                current_cluster = [curr]
                
        if current_cluster:
            clusters.append(self._merge_cluster(current_cluster))
            
        return clusters

    def _merge_cluster(self, cluster: List[Dict[str, Any]]) -> TextBlock:
        """Merges a list of raw results into a single TextBlock."""
        merged_text = " ".join([item['text'] for item in cluster])
        
        # Calculate new bounding box (min x, min y, max x, max y)
        all_points = []
        for item in cluster:
            all_points.extend(item['bbox'])
            
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Create a rectangular bbox
        new_bbox = [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]
        
        # Average confidence
        avg_conf = sum([item['confidence'] for item in cluster]) / len(cluster)
        
        return TextBlock(text=merged_text, bbox=new_bbox, confidence=avg_conf)

    def correct_text(self, text: str) -> str:
        """
        Applies correction logic to the text.
        TODO: Implement spell checker or LLM-based correction.
        """
        # Placeholder for now
        return text
