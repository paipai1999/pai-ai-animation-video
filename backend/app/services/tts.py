import os
import uuid
import asyncio
from typing import List, Dict
import edge_tts
from backend.app.core.config import settings


# Supported popular voices
VOICE_CATALOG = [
    # AI Voice Cloning (F5-TTS)
    {"id": "f5-tts-clone", "name": "✨ Clone Original Speaker Voice (F5-TTS Voice Clone)", "language": "Auto / Cloned"},
    
    # Burmese (မြန်မာဘာသာ)
    {"id": "my-MM-ThihaNeural", "name": "Thiha (မြန်မာ အသံ - ယောက်ျားလေး)", "language": "Burmese"},
    {"id": "my-MM-NilarNeural", "name": "Nilar (မြန်မာ အသံ - မိန်းကလေး)", "language": "Burmese"},

    
    # English (အင်္ဂလိပ်)
    {"id": "en-US-ChristopherNeural", "name": "Christopher (US Male - Cinematic / Storyteller)", "language": "English"},
    {"id": "en-US-JennyNeural", "name": "Jenny (US Female - Natural)", "language": "English"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female - Documentary)", "language": "English"},
    {"id": "en-AU-WilliamNeural", "name": "William (Australia Male)", "language": "English"},

    # Asian Languages
    {"id": "ja-JP-NanamiNeural", "name": "Nanami (Japanese Female - Anime Style)", "language": "Japanese"},
    {"id": "ja-JP-KeitaNeural", "name": "Keita (Japanese Male)", "language": "Japanese"},
    {"id": "ko-KR-SunHiNeural", "name": "Sun-Hi (Korean Female)", "language": "Korean"},
    {"id": "ko-KR-InJoonNeural", "name": "In-Joon (Korean Male)", "language": "Korean"},
    {"id": "th-TH-PremwadeeNeural", "name": "Premwadee (Thai Female)", "language": "Thai"},
    {"id": "th-TH-NiwatNeural", "name": "Niwat (Thai Male)", "language": "Thai"},
    {"id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao (Chinese Mandarin Female)", "language": "Chinese"},
    {"id": "zh-CN-YunxiNeural", "name": "Yunxi (Chinese Mandarin Male)", "language": "Chinese"},
    {"id": "vi-VN-HoaiMyNeural", "name": "Hoai My (Vietnamese Female)", "language": "Vietnamese"},
    {"id": "id-ID-ArdiNeural", "name": "Ardi (Indonesian Male)", "language": "Indonesian"},
    {"id": "hi-IN-SwaraNeural", "name": "Swara (Hindi Female)", "language": "Hindi"},

    # European Languages
    {"id": "fr-FR-DeniseNeural", "name": "Denise (French Female)", "language": "French"},
    {"id": "de-DE-KatjaNeural", "name": "Katja (German Female)", "language": "German"},
    {"id": "es-ES-AlvaroNeural", "name": "Alvaro (Spanish Male)", "language": "Spanish"},
    {"id": "it-IT-ElsaNeural", "name": "Elsa (Italian Female)", "language": "Italian"},
    {"id": "ru-RU-SvetlanaNeural", "name": "Svetlana (Russian Female)", "language": "Russian"},
]


class TTSService:
    def __init__(self, audio_dir: str = None):
        self.audio_dir = audio_dir or os.path.join(settings.STORAGE_DIR, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

    async def synthesize(self, text: str, voice: str = "en-US-ChristopherNeural", output_file: str = None) -> str:
        """
        Synthesizes text to speech using Edge-TTS and returns the local mp3 file path.
        """
        if not output_file:
            output_file = os.path.join(self.audio_dir, f"{uuid.uuid4()}.mp3")
            
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Clean text
        clean_text = text.strip()
        if not clean_text:
            clean_text = "..."

        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(output_file)
        return output_file

    def synthesize_sync(self, text: str, voice: str = "en-US-ChristopherNeural", output_file: str = None) -> str:
        """
        Synchronous thread-safe wrapper for voice synthesis.
        """
        try:
            return asyncio.run(self.synthesize(text, voice, output_file))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.synthesize(text, voice, output_file))
            finally:
                loop.close()

    def get_supported_voices(self) -> List[Dict[str, str]]:
        return VOICE_CATALOG


tts_service = TTSService()

