"""
Simple test script to verify basic functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all core modules can be imported"""
    print("Testing imports...")
    
    try:
        from utils.config_loader import get_config
        print("✓ Config loader")
        
        from utils.logger import setup_logger
        print("✓ Logger")
        
        from core.system_manager import SystemManager
        print("✓ System Manager")
        
        from core.command_processor import CommandProcessor
        print("✓ Command Processor")
        
        from vision.object_detector import ObjectDetector
        print("✓ Object Detector")
        
        from vision.scene_describer import SceneDescriber
        print("✓ Scene Describer")
        
        from vision.ocr_engine import OCREngine
        print("✓ OCR Engine")
        
        from audio.speech_to_text import SpeechToText
        print("✓ Speech-to-Text")
        
        from audio.text_to_speech import TextToSpeech
        print("✓ Text-to-Speech")
        
        from audio.audio_manager import AudioManager
        print("✓ Audio Manager")
        
        from hardware.camera_interface import CameraInterface
        print("✓ Camera Interface")
        
        print("\n✅ All core modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from utils.config_loader import get_config
        
        config = get_config()
        
        # Test some config values
        device = config.get('system.device', 'unknown')
        print(f"✓ Device: {device}")
        
        camera_res = config.get('camera.resolution', [])
        print(f"✓ Camera resolution: {camera_res}")
        
        print("\n✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False

def test_camera():
    """Test camera capture"""
    print("\nTesting camera...")
    
    try:
        import cv2
        from utils.config_loader import get_config
        from hardware.camera_interface import CameraInterface
        
        config = get_config()
        camera = CameraInterface(config)
        
        # Try to capture an image
        image = camera.capture()
        
        if image is not None:
            print(f"✓ Captured image: {image.shape}")
            camera.release()
            print("\n✅ Camera test passed!")
            return True
        else:
            print("❌ Failed to capture image")
            return False
            
    except Exception as e:
        print(f"\n❌ Camera error: {e}")
        return False

def test_tts():
    """Test text-to-speech"""
    print("\nTesting text-to-speech...")
    
    try:
        from utils.config_loader import get_config
        from audio.text_to_speech import TextToSpeech
        
        config = get_config()
        tts = TextToSpeech(config)
        
        print("Speaking test message...")
        tts.speak("Hello, this is a test of the blind assistant system.", blocking=True)
        
        tts.shutdown()
        print("\n✅ Text-to-speech test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ TTS error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI-Based Blind Assistant - System Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Camera", test_camera()))
    results.append(("Text-to-Speech", test_tts()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
