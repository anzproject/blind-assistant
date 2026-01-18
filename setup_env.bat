@echo off
call blind_assistant_env\Scripts\activate.bat
pip install --upgrade pip
pip install opencv-python picamera2 pytesseract vosk pyttsx3 gpsd-client tensorflow-lite transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install flask
echo Environment setup complete.
