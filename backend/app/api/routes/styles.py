from fastapi import APIRouter
from backend.app.services.tts import tts_service

router = APIRouter(prefix="/styles", tags=["Styles & Voices"])

ANIMATION_STYLES = [
    {
        "id": "3d_pixar",
        "name": "3D Pixar / Disney Style",
        "description": "Vibrant 3D cinematic animation with expressive cartoon characters and soft warm lighting.",
        "prompt_template": "3D Pixar Disney animation style, expressive characters, vibrant colors, cinematic volumetric lighting, 8k render, masterpiece"
    },
    {
        "id": "anime_ghibli",
        "name": "Anime / Studio Ghibli",
        "description": "Lush hand-painted Japanese anime style with watercolor aesthetics and emotional storytelling.",
        "prompt_template": "Studio Ghibli anime style, Makoto Shinkai aesthetic, lush scenery, hand-drawn detailing, soft atmospheric lighting"
    },
    {
        "id": "cyberpunk_sci_fi",
        "name": "Cyberpunk 3D / Sci-Fi",
        "description": "Futuristic neon-drenched aesthetic with holographic glow and high-tech atmosphere.",
        "prompt_template": "Cyberpunk futuristic animation style, neon reflections, holographic details, cinematic night scene, unreal engine 5"
    },
    {
        "id": "comic_book",
        "name": "Comic Book / Spider-Verse",
        "description": "Stylized comic halftone textures with bold ink outlines and dynamic action flair.",
        "prompt_template": "Spider-Verse comic book animation style, halftone textures, bold line art, dynamic perspective, pop art color palette"
    },
    {
        "id": "claymation",
        "name": "Claymation / Stop Motion",
        "description": "Whimsical clay stop-motion aesthetic with tactile textures and handmade charm.",
        "prompt_template": "Claymation stop-motion animation style, tactile plasticine texture, studio miniature lighting, Aardman aesthetic"
    }
]


SUPPORTED_LANGUAGES = [
    {"code": "Burmese", "name": "မြန်မာစာ (Burmese)", "flag": "🇲🇲", "default_voice": "my-MM-ThihaNeural"},
    {"code": "English", "name": "English (အင်္ဂလိပ်)", "flag": "🇺🇸", "default_voice": "en-US-ChristopherNeural"},
    {"code": "Japanese", "name": "日本語 (Japanese)", "flag": "🇯🇵", "default_voice": "ja-JP-NanamiNeural"},
    {"code": "Korean", "name": "한국어 (Korean)", "flag": "🇰🇷", "default_voice": "ko-KR-SunHiNeural"},
    {"code": "Thai", "name": "ไทย (Thai)", "flag": "🇹🇭", "default_voice": "th-TH-PremwadeeNeural"},
    {"code": "Chinese", "name": "中文 (Chinese Mandarin)", "flag": "🇨🇳", "default_voice": "zh-CN-XiaoxiaoNeural"},
    {"code": "French", "name": "Français (French)", "flag": "🇫🇷", "default_voice": "fr-FR-DeniseNeural"},
    {"code": "German", "name": "Deutsch (German)", "flag": "🇩🇪", "default_voice": "de-DE-KatjaNeural"},
    {"code": "Spanish", "name": "Español (Spanish)", "flag": "🇪🇸", "default_voice": "es-ES-AlvaroNeural"},
    {"code": "Hindi", "name": "हिन्दी (Hindi)", "flag": "🇮🇳", "default_voice": "hi-IN-SwaraNeural"},
    {"code": "Vietnamese", "name": "Tiếng Việt (Vietnamese)", "flag": "🇻🇳", "default_voice": "vi-VN-HoaiMyNeural"},
    {"code": "Indonesian", "name": "Bahasa Indonesia", "flag": "🇮🇩", "default_voice": "id-ID-ArdiNeural"},
    {"code": "Russian", "name": "Русский (Russian)", "flag": "🇷🇺", "default_voice": "ru-RU-SvetlanaNeural"},
]


BGM_TRACKS = [
    {"id": "cinematic", "name": "Cinematic Ambient (ရုပ်ရှင်ဆန်သော နောက်ခံတေး)", "description": "Atmospheric, inspiring strings and harmonic drone"},
    {"id": "lofi", "name": "Playful Lo-Fi (သက်တောင့်သက်သာ Lo-Fi)", "description": "Warm chillhop chords with relaxed beats"},
    {"id": "ambient", "name": "Deep Storyteller (ဇာတ်လမ်းဆန်သော အသံ)", "description": "Subtle meditative emotional pads"},
    {"id": "none", "name": "No Background Music (အသံသီးသန့်)", "description": "Voiceover narration only"},
]


@router.get("/")
def get_available_styles():
    return {
        "styles": ANIMATION_STYLES,
        "languages": SUPPORTED_LANGUAGES,
        "voices": tts_service.get_supported_voices(),
        "bgm_tracks": BGM_TRACKS,
        "generators": [
            {"id": "pollinations", "name": "Pollinations AI (100% Free / Instant)", "is_free": True},
            {"id": "veo", "name": "Google Veo 3.1 (Cinematic High-Fidelity)", "is_free": False},
            {"id": "ltx", "name": "LTX-Video (Open-Source)", "is_free": True}
        ],
        "aspect_ratios": [
            {"id": "16:9", "label": "Landscape (16:9 - YouTube, TV)"},
            {"id": "9:16", "label": "Portrait (9:16 - TikTok, Shorts, Reels)"},
            {"id": "1:1", "label": "Square (1:1 - Instagram Feed)"}
        ]
    }


