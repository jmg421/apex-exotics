#!/usr/bin/env python3
"""
Lower third OCR - Extract game info from video stream using kiro-cli
"""
import subprocess
import json
import time
import os

def capture_lower_third():
    """Capture lower third of video stream"""
    output_path = '/Users/apple/apex-exotics/sports-monitor/lower_third.png'
    
    # Find latest m3u8 file
    import glob
    m3u8_files = glob.glob('/Users/apple/Movies/*.m3u8')
    if not m3u8_files:
        return None
    
    latest_m3u8 = max(m3u8_files, key=os.path.getmtime)
    
    # Use ffmpeg to capture a frame from the HLS stream and crop to lower third
    cmd = [
        'ffmpeg',
        '-i', latest_m3u8,
        '-vf', 'crop=iw:ih/3:0:ih*2/3',  # Crop to bottom third
        '-frames:v', '1',
        '-update', '1',
        '-y',
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"Error capturing frame: {e}")
        return None

def capture_main_content():
    """Capture upper 2/3 of video stream (where commercials appear)"""
    output_path = '/Users/apple/apex-exotics/sports-monitor/main_content.png'
    
    # Find latest m3u8 file
    import glob
    m3u8_files = glob.glob('/Users/apple/Movies/*.m3u8')
    if not m3u8_files:
        return None
    
    latest_m3u8 = max(m3u8_files, key=os.path.getmtime)
    
    # Use ffmpeg to capture upper 2/3 of frame
    cmd = [
        'ffmpeg',
        '-i', latest_m3u8,
        '-vf', 'crop=iw:ih*2/3:0:0',  # Crop to top 2/3
        '-frames:v', '1',
        '-update', '1',
        '-y',
        output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"Error capturing frame: {e}")
        return None

def extract_game_info(image_path):
    """Use kiro-cli to extract game info from lower third - two pass approach"""
    
    # PASS 1: Extract all visible text
    prompt1 = f"List ALL text visible in {image_path}. Just the text, nothing else."
    
    try:
        result1 = subprocess.run(
            ['timeout', '40', 'kiro-cli', 'chat', '--no-interactive', '--trust-all-tools', prompt1],
            capture_output=True,
            text=True,
            cwd='/Users/apple/apex-exotics/sports-monitor'
        )
        
        # Clean output
        import re
        raw_text = result1.stdout.strip()
        raw_text = re.sub(r'\x1b\[[0-9;]*m', '', raw_text)  # Remove ANSI codes
        
        # Remove kiro-cli status messages
        lines = []
        for line in raw_text.split('\n'):
            if any(skip in line for skip in ['Reading images:', 'using tool:', 'Successfully read', 'Completed in', "I'll", 'Tool validation']):
                continue
            line = line.strip()
            if line.startswith('>'):
                line = line[1:].strip()
            if line:
                lines.append(line)
        
        extracted_text = '\n'.join(lines)
        print(f"Pass 1 - Extracted text:\n{extracted_text}\n")
        
        if not extracted_text:
            return None
        
        # PASS 2: Compress to headline
        prompt2 = f"""Extract the SINGLE most important news headline from this text. Return ONE declarative statement (no questions):

{extracted_text}

Rules:
- Pick only ONE story
- Make it a complete, standalone headline
- If multiple stories, pick the most newsworthy one
- Return 'No headline found' if unclear"""
        
        result2 = subprocess.run(
            ['timeout', '25', 'kiro-cli', 'chat', '--no-interactive', '--trust-all-tools', prompt2],
            capture_output=True,
            text=True,
            cwd='/Users/apple/apex-exotics/sports-monitor'
        )
        
        output = result2.stdout.strip()
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        # Clean up kiro-cli wrapper text
        lines = []
        for line in output.split('\n'):
            if any(skip in line for skip in ['Reading', 'using tool:', 'Successfully', 'Completed', "I'll", 'Time:']):
                continue
            line = line.strip()
            if line.startswith('>'):
                line = line[1:].strip()
            if line:
                lines.append(line)
        
        headline = ' '.join(lines).strip()
        
        print(f"Pass 2 - Headline:\n{headline}\n")
        
        if headline and 'No headline found' not in headline:
            return {
                'current_game': {'away_team': '', 'home_team': '', 'away_score': 0, 'home_score': 0, 'status': '', 'top_performers': []},
                'next_game': f"📰 {headline}"
            }
        
        return None
    except Exception as e:
        print(f"Error extracting game info: {e}")
        return None

def get_live_game_info():
    """Main function to get live game info from stream"""
    image_path = capture_lower_third()
    if not image_path:
        return None
    
    game_info = extract_game_info(image_path)
    
    # Don't clean up - keep file for debugging
    # try:
    #     os.remove(image_path)
    # except:
    #     pass
    
    return game_info

if __name__ == "__main__":
    info = get_live_game_info()
    if info:
        print(json.dumps(info, indent=2))
    else:
        print("No game info extracted")
