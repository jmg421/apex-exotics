#!/usr/bin/env python3
"""
Commercial detection for live sports streams
Detects when broadcast switches to commercials
"""
from collections import deque

class CommercialDetector:
    """Detects commercial breaks in sports broadcasts"""
    
    def __init__(self, confidence_threshold=3):
        self.confidence_threshold = confidence_threshold
        self.recent_frames = deque(maxlen=5)
        self.commercial_keywords = [
            'call now', 'limited time', 'visit', '1-800', 'buy now',
            'order today', 'act now', 'offer ends', 'sale'
        ]
    
    def analyze_frame_data(self, frame_data):
        """Analyze single frame for commercial indicators"""
        brightness = frame_data.get('avg_brightness', 128)
        has_scoreboard = frame_data.get('has_scoreboard', True)
        text = frame_data.get('extracted_text', '').lower()
        bitrate_stuck = frame_data.get('bitrate_stuck', False)
        
        # Check black screen
        if brightness < 10:
            return {'is_commercial': True, 'reason': 'black_screen', 'confidence': 0.9}
        
        # Check stuck bitrate (encoding frozen)
        if bitrate_stuck:
            return {'is_commercial': True, 'reason': 'bitrate_stuck', 'confidence': 0.85}
        
        # Check for scoreboard
        if not has_scoreboard and frame_data.get('text_detected', False):
            return {'is_commercial': True, 'reason': 'no_scoreboard', 'confidence': 0.7}
        
        # Check commercial keywords
        if any(keyword in text for keyword in self.commercial_keywords):
            return {'is_commercial': True, 'reason': 'commercial_keywords', 'confidence': 0.8}
        
        # Likely game content
        return {'is_commercial': False, 'reason': 'game_content', 'confidence': 0.6}
    
    def add_frame(self, frame_data):
        """Add frame to history for temporal analysis"""
        analysis = self.analyze_frame_data(frame_data)
        self.recent_frames.append(analysis)
    
    def is_in_commercial_break(self):
        """Determine if currently in commercial break (requires consistency)"""
        if len(self.recent_frames) < self.confidence_threshold:
            return False
        
        # Count recent commercial detections
        commercial_count = sum(1 for f in self.recent_frames if f['is_commercial'])
        return commercial_count >= self.confidence_threshold

def is_commercial(frame_data):
    """Simple function for single-frame analysis"""
    detector = CommercialDetector()
    result = detector.analyze_frame_data(frame_data)
    return result['is_commercial']
