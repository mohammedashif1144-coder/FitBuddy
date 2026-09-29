from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .config import get_settings
from .database import get_db
from .models import Plan, User
from .schemas import FeedbackRequest, FeedbackResponse, GenerateResponse, UserInput
from .services.nutrition_generator import generate_nutrition_tip_with_flash
from .services.plan_updater import update_workout_plan
from .services.workout_generator import generate_workout_gemini

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()
api_router = APIRouter(prefix="/api")


def _find_user(db: Session, user_id: str) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))


def _save_generated_plan(db: Session, data: UserInput, plan_text: str, tip: str) -> User:
    user = _find_user(db, data.user_id)
    if user is None:
        user = User(
            user_id=data.user_id,
            name=data.name,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )
        db.add(user)
        db.flush()
    else:
        user.name = data.name
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

    user.plans.append(Plan(original_plan=plan_text, nutrition_tip=tip))
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return TEMPLATES.TemplateResponse(request=request, name="index.html", context={"title": "FitBuddy"})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(user_id=user_id, name=name, age=age, weight=weight, goal=goal, intensity=intensity)
        plan, demo_mode = generate_workout_gemini(data)
        tip, tip_demo = generate_nutrition_tip_with_flash(data)
        _save_generated_plan(db, data, plan, tip)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "title": "Your FitBuddy Plan",
                "user": data,
                "workout_plan": plan,
                "nutrition_tip": tip,
                "demo_mode": demo_mode or tip_demo,
                "message": None,
            },
        )
    except ValueError as exc:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={"title": "FitBuddy", "error": str(exc)},
            status_code=422,
        )
    except Exception as exc:
        db.rollback()
        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={"title": "FitBuddy", "error": f"Could not generate the plan: {exc}"},
            status_code=500,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = _find_user(db, data.user_id)
        if not user or not user.plans:
            raise HTTPException(status_code=404, detail="User or workout plan not found")
        latest = user.plans[-1]
        profile = UserInput(
            user_id=user.user_id,
            name=user.name,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )
        updated, demo_mode = update_workout_plan(profile, latest.original_plan, data.feedback)
        latest.updated_plan = updated
        latest.feedback = data.feedback
        latest.nutrition_tip, tip_demo = generate_nutrition_tip_with_flash(profile)
        db.commit()
        return TEMPLATES.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "title": "Updated FitBuddy Plan",
                "user": profile,
                "workout_plan": updated,
                "nutrition_tip": latest.nutrition_tip,
                "demo_mode": demo_mode or tip_demo,
                "message": "Your plan was updated using your feedback.",
                "original_plan": latest.original_plan,
            },
        )
    except HTTPException:
        raise
    except ValueError as exc:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="result.html",
            context={"title": "FitBuddy", "error": str(exc), "user_id": user_id},
            status_code=422,
        )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    settings = get_settings()
    if not token or token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
    users = db.scalars(select(User).options(joinedload(User.plans)).order_by(User.created_at.desc())).unique().all()
    return TEMPLATES.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"title": "FitBuddy Admin", "users": users},
    )


@api_router.post("/generate-workout", response_model=GenerateResponse)
def generate_workout_api(data: UserInput, db: Session = Depends(get_db)):
    plan, demo_mode = generate_workout_gemini(data)
    tip, tip_demo = generate_nutrition_tip_with_flash(data)
    _save_generated_plan(db, data, plan, tip)
    return GenerateResponse(user_id=data.user_id, plan=plan, nutrition_tip=tip, demo_mode=demo_mode or tip_demo)


@api_router.post("/submit-feedback", response_model=FeedbackResponse)
def submit_feedback_api(data: FeedbackRequest, db: Session = Depends(get_db)):
    user = _find_user(db, data.user_id)
    if not user or not user.plans:
        raise HTTPException(status_code=404, detail="User or workout plan not found")
    latest = user.plans[-1]
    profile = UserInput(
        user_id=user.user_id,
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )
    updated, demo_mode = update_workout_plan(profile, latest.original_plan, data.feedback)
    tip, tip_demo = generate_nutrition_tip_with_flash(profile)
    latest.updated_plan = updated
    latest.feedback = data.feedback
    latest.nutrition_tip = tip
    db.commit()
    return FeedbackResponse(user_id=data.user_id, updated_plan=updated, nutrition_tip=tip, demo_mode=demo_mode or tip_demo)


@api_router.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "created_at": user.created_at.isoformat(),
        }
        for user in users
    ]
