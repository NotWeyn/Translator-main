
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.text_processor import TextProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_merge():
    processor = TextProcessor()
    
    # Mock data approximating the user's image
    # Line 1: "I know, I know. Septimont's current Ephor doesn't quite heed the"
    # Line 2: "Senate's wishes, but we'll see to that."
    
    # Assuming 1920x1080 screen, text is centered bottom
    
    # Block 1 (Top)
    block1 = {
        'text': "I know, I know. Septimont's current Ephor doesn't quite heed the",
        'bbox': [[400, 800], [1500, 800], [1500, 850], [400, 850]], # x1,y1 ...
        'confidence': 0.99
    }
    
    # Block 2 (Bottom)
    block2 = {
        'text': "Senate's wishes, but we'll see to that.",
        'bbox': [[600, 900], [1300, 900], [1300, 950], [600, 950]],
        'confidence': 0.98
    }
    
    raw_results = [block1, block2]
    
    print("--- Test 1: Standard Merge (Distance 200) ---")
    # User said they tried 200 and it didn't work.
    # Vertical distance: 900 (top of block2) - 850 (bottom of block1) = 50.
    # 50 <= 200. Should merge.
    
    merged = processor.cluster_text(raw_results, y_threshold=200)
    print(f"Input blocks: {len(raw_results)}")
    print(f"Merged blocks: {len(merged)}")
    for i, block in enumerate(merged):
        print(f"Block {i}: {block.text}")
        
    if len(merged) == 1:
        print("✓ SUCCESS: Merged into 1 block.")
    else:
        print("✗ FAILURE: Remained split.")

    print("\n--- Test 2: Split Line 1 (Simulating OCR split) ---")
    # Maybe OCR split the first line?
    # "I know, I know." ... "Septimont's..."
    
    block1a = {
        'text': "I know, I know.",
        'bbox': [[400, 800], [600, 800], [600, 850], [400, 850]],
        'confidence': 0.99
    }
    block1b = {
        'text': "Septimont's current Ephor doesn't quite heed the",
        'bbox': [[620, 800], [1500, 800], [1500, 850], [620, 850]],
        'confidence': 0.99
    }
    
    raw_results_split = [block1a, block1b, block2]
    
    merged_split = processor.cluster_text(raw_results_split, y_threshold=200)
    print(f"Input blocks: {len(raw_results_split)}")
    print(f"Merged blocks: {len(merged_split)}")
    for i, block in enumerate(merged_split):
        print(f"Block {i}: {block.text}")

    if len(merged_split) == 1:
        print("✓ SUCCESS: Merged all 3 into 1 block.")
    else:
        print("✗ FAILURE: Not fully merged.")

    print("\n--- Test 3: Large Horizontal Gap (4K) ---")
    # Simulating 4K (3840x2160) with large horizontal gap
    block_left = {
        'text': "This is the start of a sentence that continues",
        'bbox': [[100, 1500], [1600, 1500], [1600, 1580], [100, 1580]],
        'confidence': 0.95
    }
    block_right = {
        'text': "on the next line with a large gap.",
        'bbox': [[200, 1650], [1500, 1650], [1500, 1730], [200, 1730]],
        'confidence': 0.94
    }
    
    # Test with merge_distance=100 (should work with new dynamic x_threshold)
    raw_4k = [block_left, block_right]
    merged_4k = processor.cluster_text(raw_4k, y_threshold=100)
    
    print(f"Input blocks: {len(raw_4k)}")
    print(f"Merged blocks (y_threshold=100): {len(merged_4k)}")
    for i, block in enumerate(merged_4k):
        print(f"Block {i}: {block.text}")
    
    if len(merged_4k) == 1:
        print("✓ SUCCESS: Merged with high threshold.")
    else:
        print("✗ FAILURE: Not merged.")

    print("\n--- Test 4: Slightly Rotated Text (Robustness) ---")
    # Simulating slightly rotated text with non-standard bbox
    block_rotated1 = {
        'text': "Rotated text line one",
        'bbox': [[400, 800], [1100, 790], [1105, 850], [405, 860]], # slight rotation
        'confidence': 0.97
    }
    block_rotated2 = {
        'text': "continues here on line two",
        'bbox': [[420, 900], [1050, 895], [1055, 955], [425, 960]],
        'confidence': 0.96
    }
    
    raw_rotated = [block_rotated1, block_rotated2]
    merged_rotated = processor.cluster_text(raw_rotated, y_threshold=50)
    
    print(f"Input blocks: {len(raw_rotated)}")
    print(f"Merged blocks: {len(merged_rotated)}")
    for i, block in enumerate(merged_rotated):
        print(f"Block {i}: {block.text}")
    
    if len(merged_rotated) == 1:
        print("✓ SUCCESS: Handled rotated text correctly.")
    else:
        print("✗ FAILURE: Failed on rotated text.")

if __name__ == "__main__":
    test_merge()
