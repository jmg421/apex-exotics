#!/usr/bin/env python3
"""
Integration: Commercial detection with OCR snapshots
"""
import subprocess
import os
from PIL import Image
import numpy as np
from commercial_detector import CommercialDetector

detector = CommercialDetector()

def analyze_brightness(image_path):
    """Calculate average brightness of image"""
    img = Image.open(image_path).convert('L')
    pixels = np.array(img)
    return int(pixels.mean())

def detect_scoreboard(image_path):
    """Check if scoreboard is visible (simple heuristic)"""
    # Scoreboards typically in top corners
    img = Image.open(image_path)
    width, height = img.size
    
    # Check top-left and top-right corners
    top_left = img.crop((0, 0, width//4, height//6))
    top_right = img.crop((3*width//4, 0, width, height//6))
    
    # Convert to grayscale and check for text-like patterns
    tl_gray = np.array(top_left.convert('L'))
    tr_gray = np.array(top_right.convert('L'))
    
    # High variance suggests text/graphics (scoreboard)
    tl_variance = tl_gray.std()
    tr_variance = tr_gray.std()
    
    return tl_variance > 30 or tr_variance > 30

def check_commercial_break(image_path=None):
    """Ask kiro-cli if this is a commercial and identify it"""
    import subprocess
    import re
    from lower_third_ocr import capture_main_content
    
    # Capture main content if no image provided
    if not image_path:
        image_path = capture_main_content()
        if not image_path:
            return {'is_commercial': False, 'error': 'Could not capture frame'}
    
    # Single prompt: detect and identify
    prompt = f"Is {image_path} showing a commercial? If YES, name the product/company in 3 words. If NO, say 'Game Content'. Format: YES - ProductName OR NO - Game Content"
    
    try:
        result = subprocess.run(
            ['timeout', '35', 'kiro-cli', 'chat', '--no-interactive', '--trust-all-tools', prompt],
            capture_output=True,
            text=True,
            cwd='/Users/apple/apex-exotics/sports-monitor'
        )
        
        output = result.stdout.strip()
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        # Extract last meaningful line
        lines = [l.strip() for l in output.split('\n') if l.strip() and not any(skip in l.lower() for skip in ['reading', 'time:', 'successfully', 'tool', 'completed'])]
        response = lines[-1] if lines else ''
        
        is_commercial = 'YES' in response.upper()
        
        # Extract product name after dash
        if '-' in response:
            commercial_type = response.split('-', 1)[1].strip()
        elif is_commercial:
            commercial_type = 'Unknown Commercial'
        else:
            commercial_type = 'Game Content'
        
        return {
            'is_commercial': is_commercial,
            'commercial_type': commercial_type[:50]
        }
        
    except Exception as e:
        return {
            'is_commercial': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Capture and test main content area
    print("Analyzing stream for commercials...")
    result = check_commercial_break()
    
    if result['is_commercial']:
        print(f"🚫 COMMERCIAL DETECTED: {result['commercial_type']}")
    else:
        print(f"✅ Game Content: {result.get('commercial_type', 'Live Action')}")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
