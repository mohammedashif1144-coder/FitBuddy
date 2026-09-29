from ..config import get_settings
from .gemini_service import GeminiService, get_gemini_service
from ..schemas import UserInput


def _demo_tip(user: UserInput) -> str:
    tips = {
        "weight loss": "Build meals around vegetables or fruit, a protein source, whole-food carbohydrates, and enough fluids; focus on sustainable habits rather than extreme restriction.",
        "muscle gain": "Include a protein-rich food in regular meals and eat enough varied whole foods to support training and recovery.",
        "general wellness": "Stay hydrated and build balanced meals with a variety of vegetables or fruit, protein, whole grains, and healthy fats.",
        "flexibility": "Regular hydration and balanced meals support normal recovery; pair mobility work with adequate rest.",
        "endurance": "Hydrate regularly and include carbohydrate-rich whole foods around longer activity sessions to support energy and recovery.",
    }
    return tips[user.goal]


def generate_nutrition_tip_with_flash(user: UserInput, service: GeminiService | None = None) -> tuple[str, bool]:
    settings = get_settings()
    service = service or get_gemini_service()
    if not settings.ai_enabled:
        return _demo_tip(user), True

    prompt = f"""Give one concise nutrition or recovery tip for a general wellness fitness plan.\nGoal: {user.goal}\nIntensity: {user.intensity}\nAge: {user.age}\n\nRules: provide practical, non-extreme advice; do not recommend starvation, purging, dangerous restriction, medication, or supplements; do not diagnose conditions. Keep it to 2–4 sentences.\n"""
    return service.generate(model=settings.tip_model, prompt=prompt), False
