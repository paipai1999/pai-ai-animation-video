from backend.app.services.tts import tts_service
from backend.app.services.generators import get_generator
from backend.app.api.routes.styles import ANIMATION_STYLES


def test_styles_catalog():
    assert len(ANIMATION_STYLES) >= 5
    for style in ANIMATION_STYLES:
        assert "id" in style
        assert "name" in style
        assert "prompt_template" in style


def test_tts_voice_catalog():
    voices = tts_service.get_supported_voices()
    assert len(voices) >= 5
    assert any(v["id"] == "f5-tts-clone" for v in voices)
    assert any(v["language"] == "Burmese" for v in voices)
    assert any(v["language"] == "English" for v in voices)


def test_generator_factory():
    pollinations_gen = get_generator("pollinations")
    assert pollinations_gen is not None
    
    veo_gen = get_generator("veo")
    assert veo_gen is not None
    
    ltx_gen = get_generator("ltx")
    assert ltx_gen is not None


def test_bgm_catalog():
    from backend.app.api.routes.styles import BGM_TRACKS
    assert len(BGM_TRACKS) >= 3
    assert any(b["id"] == "cinematic" for b in BGM_TRACKS)


def test_languages_catalog():
    from backend.app.api.routes.styles import SUPPORTED_LANGUAGES
    assert len(SUPPORTED_LANGUAGES) >= 10
    assert any(l["code"] == "Burmese" for l in SUPPORTED_LANGUAGES)

