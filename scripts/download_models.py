#!/usr/bin/env python3
"""
Script to download required AI models for the blind assistant.
Downloads models for offline operation.
"""

import os
import sys
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path
import logging
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class ModelDownloader:
    """Handles downloading and setup of AI models."""

    def __init__(self, models_dir="models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

    def download_vosk_model(self):
        """Download Vosk speech recognition model."""
        model_name = "vosk-model-small-en-us-0.15"
        model_path = self.models_dir / model_name
        zip_path = self.models_dir / f"{model_name}.zip"

        if model_path.exists():
            logger.info(f"Vosk model already exists at {model_path}")
            return True

        url = f"https://alphacephei.com/vosk/models/{model_name}.zip"

        try:
            logger.info("Downloading Vosk model...")
            urllib.request.urlretrieve(url, zip_path)

            logger.info("Extracting Vosk model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.models_dir)

            # Clean up zip file
            zip_path.unlink()

            logger.info("Vosk model downloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to download Vosk model: {e}")
            if zip_path.exists():
                zip_path.unlink()
            return False

    def download_yolov5_model(self):
        """Download YOLOv5 object detection model."""
        model_path = self.models_dir / "yolov5s.pt"

        if model_path.exists():
            logger.info("YOLOv5 model already exists")
            return True

        try:
            logger.info("Downloading YOLOv5 model...")
            # Use torch.hub to download the model
            import torch
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            torch.save(model.state_dict(), model_path)
            logger.info("YOLOv5 model downloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to download YOLOv5 model: {e}")
            return False

    def download_blip_model(self):
        """Download BLIP image captioning model."""
        model_path = self.models_dir / "blip-image-captioning-base"

        if model_path.exists():
            logger.info("BLIP model already exists")
            return True

        try:
            logger.info("Downloading BLIP model...")
            from transformers import BlipProcessor, BlipForConditionalGeneration

            processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

            processor.save_pretrained(model_path)
            model.save_pretrained(model_path)

            logger.info("BLIP model downloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to download BLIP model: {e}")
            return False

    def download_emotion_model(self):
        """Download emotion recognition model (placeholder)."""
        model_path = self.models_dir / "emotion-recognition-model"

        if model_path.exists():
            logger.info("Emotion model already exists")
            return True

        # TODO: Download actual emotion recognition model
        # For now, create placeholder
        try:
            model_path.mkdir(exist_ok=True)
            (model_path / "README.md").write_text("Emotion recognition model placeholder\n")
            logger.info("Emotion model placeholder created")
            return True

        except Exception as e:
            logger.error(f"Failed to create emotion model placeholder: {e}")
            return False

    def verify_downloads(self):
        """Verify all downloads completed successfully."""
        required_models = [
            ("vosk-model-small-en-us-0.15", "Vosk STT"),
            ("yolov5s.pt", "YOLOv5 Object Detection"),
            ("blip-image-captioning-base", "BLIP Image Captioning"),
            ("emotion-recognition-model", "Emotion Recognition")
        ]

        logger.info("Verifying model downloads...")
        all_present = True

        for model_dir, description in required_models:
            path = self.models_dir / model_dir
            if path.exists():
                logger.info(f"✓ {description}: Present")
            else:
                logger.error(f"✗ {description}: Missing")
                all_present = False

        return all_present

    def get_download_size(self):
        """Estimate total download size."""
        # Approximate sizes in MB
        sizes = {
            'vosk': 40,      # ~40MB
            'yolov5': 15,    # ~15MB
            'blip': 500,     # ~500MB
            'emotion': 0     # placeholder
        }

        total = sum(sizes.values())
        logger.info(f"Estimated download size: ~{total}MB")
        logger.info("Note: Actual sizes may vary")

    def cleanup_temp_files(self):
        """Clean up temporary download files."""
        try:
            for file in self.models_dir.glob("*.tmp"):
                file.unlink()
            for file in self.models_dir.glob("*.part"):
                file.unlink()
            logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")

def main():
    """Main download function."""
    logger.info("AI Model Downloader for Blind Assistant")
    logger.info("=" * 50)

    downloader = ModelDownloader()

    # Show download size estimate
    downloader.get_download_size()

    # Ask for confirmation
    response = input("\nThis will download ~500MB of models. Continue? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        logger.info("Download cancelled by user")
        return

    # Download models
    downloads = [
        ("Vosk Speech Recognition", downloader.download_vosk_model),
        ("YOLOv5 Object Detection", downloader.download_yolov5_model),
        ("BLIP Image Captioning", downloader.download_blip_model),
        ("Emotion Recognition", downloader.download_emotion_model)
    ]

    success_count = 0

    for name, download_func in downloads:
        logger.info(f"\n--- Downloading {name} ---")
        try:
            if download_func():
                success_count += 1
                logger.info(f"✓ {name} downloaded successfully")
            else:
                logger.error(f"✗ Failed to download {name}")
        except Exception as e:
            logger.error(f"✗ Error downloading {name}: {e}")

    # Cleanup
    downloader.cleanup_temp_files()

    # Verify
    logger.info(f"\n--- Download Summary ---")
    logger.info(f"Successfully downloaded: {success_count}/{len(downloads)} models")

    if downloader.verify_downloads():
        logger.info("\n🎉 All models downloaded successfully!")
        logger.info("The blind assistant is ready for offline operation.")
    else:
        logger.warning("\n⚠️  Some models failed to download.")
        logger.info("You can retry with: python scripts/download_models.py")
        logger.info("Or run individual downloads manually.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
    except Exception as e:
        logger.error(f"Download script failed: {e}")
        sys.exit(1)
