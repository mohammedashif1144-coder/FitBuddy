from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility", "endurance"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=13, le=120)
    weight: float = Field(gt=0, le=500)
    goal: Goal
    intensity: Intensity

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be blank")
        return value


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    feedback: str = Field(min_length=5, max_length=1500)


class GenerateResponse(BaseModel):
    user_id: str
    plan: str
    nutrition_tip: str
    demo_mode: bool


class FeedbackResponse(BaseModel):
    user_id: str
    updated_plan: str
    nutrition_tip: str
    demo_mode: bool
