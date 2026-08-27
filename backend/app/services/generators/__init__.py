from backend.app.services.generators.base import BaseVisualGenerator
from backend.app.services.generators.pollinations import PollinationsGenerator
from backend.app.services.generators.veo import GoogleVeoGenerator
from backend.app.services.generators.ltx import LTXVideoGenerator


def get_generator(generator_type: str = "pollinations") -> BaseVisualGenerator:
    gen_type = (generator_type or "pollinations").lower()
    if gen_type == "veo":
        return GoogleVeoGenerator()
    elif gen_type == "ltx":
        return LTXVideoGenerator()
    else:
        return PollinationsGenerator()
