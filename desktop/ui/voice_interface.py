#!/usr/bin/env python3
"""
Offline Voice Interface using Vosk and Piper
No internet required once models are downloaded.
"""

import os
import queue
import threading
import json
from pathlib import Path

try:
    import pyaudio
    from vosk import Model, KaldiRecognizer
except ImportError:
    print("⚠️  Install pyaudio and vosk: pip install pyaudio vosk")
    pyaudio = None

class VoiceAssistant:
    def __init__(self, wake_word="eni"):
        self.wake_word = wake_word.lower()
        self.audio_queue = queue.Queue()
        self.model_path = Path.home() / '.eni' / 'models' / 'vosk-model-small-en-us-0.15'
        self._running = False
        self.piper_path = Path.home() / '.eni' / 'piper' / 'piper'

        if self.model_path.exists() and pyaudio:
            self.model = Model(str(self.model_path))
            self.recognizer = KaldiRecognizer(self.model, 16000)
        else:
            self.model = None
            self.recognizer = None
            print("⚠️  Vosk model not found. Run with --download-models first.")

    def _download_models(self):
        """Download Vosk model if missing"""
        if not self.model_path.exists():
            print("📥 Downloading Vosk model...")
            import zipfile
            import requests
            url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
            zip_path = self.model_path.with_suffix('.zip')
            r = requests.get(url, stream=True)
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.model_path.parent)
            zip_path.unlink()
            print("✅ Vosk model ready.")

    def listen_loop(self, callback):
        """Continuously listen for wake word and commands"""
        if not self.recognizer:
            print("Cannot start listening – model missing.")
            return

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=4000)
        stream.start_stream()

        while self._running:
            data = stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').lower()
                if text:
                    print(f"🎤 You said: {text}")
                    if self.wake_word in text:
                        command = text.replace(self.wake_word, '').strip()
                        if command:
                            callback(command)

    def speak(self, text):
        """Text-to-speech placeholder (integrate Piper later)"""
        print(f"🔊 ENI: {text}")

# Integration helper
def voice_knowledge_callback(command):
    from desktop.core.knowledge_engine import get_knowledge_engine
    knowledge = get_knowledge_engine()
    result = knowledge.get_answer(command)
    if result:
        print(f"📚 {result['answer']}")
    else:
        print("I don't have that yet. Teach me later.")

if __name__ == '__main__':
    import sys
    if '--download-models' in sys.argv:
        va = VoiceAssistant()
        va._download_models()
    else:
        print("Voice interface skeleton ready. Use --download-models to fetch Vosk.")
