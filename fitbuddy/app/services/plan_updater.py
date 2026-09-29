from ..config import get_settings
from .gemini_service import GeminiService, get_gemini_service
from ..schemas import UserInput


def _demo_update(original_plan: str, feedback: str) -> str:
    return f"""DEMO UPDATED PLAN\n\nThe original plan has been retained. Requested feedback: {feedback}\n\nSuggested adjustment:\n- Keep the same seven-day structure.\n- Add the requested preference gradually without removing recovery time.\n- Keep exercise technique and comfortable effort as priorities.\n- Reassess after several sessions rather than making large sudden changes.\n\nOriginal plan:\n{original_plan}"""


def update_workout_plan(
    user: UserInput,
    original_plan: str,
    feedback: str,
    service: GeminiService | None = None,
) -> tuple[str, bool]:
    settings = get_settings()
    service = service or get_gemini_service()
    if not settings.ai_enabled:
        return _demo_update(original_plan, feedback), True

    prompt = f"""You are updating a general wellness 7-day fitness plan.\n\nUser profile:\nName: {user.name}\nAge: {user.age}\nWeight: {user.weight} kg\nGoal: {user.goal}\nIntensity: {user.intensity}\n\nOriginal plan:\n{original_plan}\n\nUser feedback:\n{feedback}\n\nCreate a revised 7-day plan that incorporates reasonable parts of the feedback while preserving safe progression and adequate recovery. Do not provide extreme exercise, dangerous challenges, starvation/restrictive eating instructions, supplements, medication, diagnosis, or treatment. If the feedback requests something unsafe, replace it with a safer general-wellness alternative. Use plain text headings for Day 1–Day 7.\n"""
    return service.generate(model=settings.workout_model, prompt=prompt), False
