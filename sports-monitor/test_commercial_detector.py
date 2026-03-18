#!/usr/bin/env python3
"""
Tests for commercial detection
Following TDD: Write tests first, then implementation
"""
import unittest
from commercial_detector import is_commercial, CommercialDetector

class TestCommercialDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = CommercialDetector()
    
    def test_detects_black_screen(self):
        """Black screens often indicate commercial breaks"""
        # Simulate black screen (low brightness)
        result = self.detector.analyze_frame_data({
            'avg_brightness': 5,
            'text_detected': False
        })
        self.assertTrue(result['is_commercial'])
        self.assertEqual(result['reason'], 'black_screen')
    
    def test_detects_missing_scoreboard(self):
        """No scoreboard = likely commercial"""
        result = self.detector.analyze_frame_data({
            'avg_brightness': 128,
            'has_scoreboard': False,
            'text_detected': True
        })
        self.assertTrue(result['is_commercial'])
        self.assertEqual(result['reason'], 'no_scoreboard')
    
    def test_detects_commercial_keywords(self):
        """Common commercial phrases"""
        commercial_texts = [
            "Call now",
            "Limited time offer",
            "Visit our website",
            "1-800-",
            "Buy now"
        ]
        for text in commercial_texts:
            result = self.detector.analyze_frame_data({
                'avg_brightness': 128,
                'has_scoreboard': False,
                'extracted_text': text
            })
            self.assertTrue(result['is_commercial'], f"Failed to detect: {text}")
    
    def test_game_content_not_commercial(self):
        """Active game should not be flagged"""
        result = self.detector.analyze_frame_data({
            'avg_brightness': 128,
            'has_scoreboard': True,
            'extracted_text': "MIA 45 UNC 42 2nd Half 8:23"
        })
        self.assertFalse(result['is_commercial'])
    
    def test_requires_multiple_frames_for_confidence(self):
        """Single frame shouldn't trigger - need consistency"""
        # First suspicious frame
        self.detector.add_frame({'avg_brightness': 5})
        self.assertFalse(self.detector.is_in_commercial_break())
        
        # Second suspicious frame
        self.detector.add_frame({'avg_brightness': 5})
        self.assertFalse(self.detector.is_in_commercial_break())
        
        # Third suspicious frame - now confident
        self.detector.add_frame({'avg_brightness': 5})
        self.assertTrue(self.detector.is_in_commercial_break())

if __name__ == '__main__':
    unittest.main()
