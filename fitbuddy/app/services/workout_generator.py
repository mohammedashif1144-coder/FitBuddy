from ..config import get_settings
from .gemini_service import GeminiService, get_gemini_service
from ..schemas import UserInput


def _demo_plan(user: UserInput) -> str:
    return f"""DEMO PLAN — AI is not configured yet\n\n7-DAY {user.goal.upper()} PLAN\nProfile: {user.name}, age {user.age}, {user.weight:g} kg, {user.intensity} intensity\n\nDay 1 — Full-body foundation\n- Warm-up: 5–10 minutes of easy movement\n- Main: bodyweight squat 2–3 sets, incline push-up 2–3 sets, glute bridge 2–3 sets, easy row/band row 2–3 sets\n- Cooldown: gentle mobility\n\nDay 2 — Cardio + mobility\n- Warm-up: 5 minutes\n- Main: 20–30 minutes comfortable cardio + 10 minutes mobility\n- Cooldown: easy walking and breathing\n\nDay 3 — Recovery\n- Easy walk or gentle mobility for 15–30 minutes\n\nDay 4 — Strength foundation\n- Warm-up: 5–10 minutes\n- Main: split squat, hip hinge, overhead press variation, row variation; 2–3 sets each\n- Cooldown: gentle mobility\n\nDay 5 — Cardio + core\n- Warm-up: 5 minutes\n- Main: moderate cardio + simple core exercises\n- Cooldown: 5 minutes easy movement\n\nDay 6 — Full body, moderate effort\n- Warm-up: 5–10 minutes\n- Main: repeat key movement patterns with comfortable technique\n- Cooldown: gentle mobility\n\nDay 7 — Rest and recovery\n- Light walking or stretching only if comfortable\n\nSafety: Adjust activity to your current ability. Stop if you experience pain, dizziness, or unusual symptoms and seek appropriate professional advice when needed."""


def generate_workout_gemini(user: UserInput, service: GeminiService | None = None) -> tuple[str, bool]:
    settings = get_settings()
    service = service or get_gemini_service()
    if not settings.ai_enabled:
        return _demo_plan(user), True

    prompt = f"""You are FitBuddy, a general wellness fitness-planning assistant.\n\nCreate a structured 7-day fitness plan for:\n- Name: {user.name}\n- Age: {user.age}\n- Weight: {user.weight} kg\n- Goal: {user.goal}\n- Preferred intensity: {user.intensity}\n\nRequirements:\n1. Give Day 1 through Day 7 with a clear focus.\n2. For active days include a 5–10 minute warm-up, main exercises with sets/reps or duration, and cooldown/recovery guidance.\n3. Match volume and intensity to the requested intensity; prioritize gradual progression and rest.\n4. Keep recommendations general and accessible; offer alternatives for common movements.\n5. Do not prescribe extreme exercise, fasting, starvation diets, supplements, medication, or treatment for medical conditions.\n6. Do not diagnose injuries or illnesses. If a medical concern is mentioned, advise consultation with a qualified professional.\n7. Return plain text with headings, not JSON or markdown tables.\n8. Include a brief note that the plan is general wellness guidance and should be adjusted for individual circumstances.\n"""
    return service.generate(model=settings.workout_model, prompt=prompt), False
