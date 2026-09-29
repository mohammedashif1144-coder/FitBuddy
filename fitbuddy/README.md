# FitBuddy – AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite application based on the supplied FitBuddy project documentation. It generates a structured 7-day fitness plan, a concise nutrition/recovery tip, and can revise a saved plan from user feedback.

## Architecture

- **Frontend:** Jinja2 HTML templates + responsive CSS
- **Backend:** FastAPI
- **AI:** Google Gemini through the current `google-genai` Python SDK
- **Database:** SQLite + SQLAlchemy ORM
- **Validation:** Pydantic
- **Testing:** pytest + FastAPI TestClient

The original documentation specifies Gemini 1.5 Pro and Gemini Flash. Those model IDs are kept configurable rather than hard-coded because Gemini model availability changes over time. The default configuration uses current model IDs; set the environment variables to any models available to your Gemini API account.

## Features

1. Generate a personalized 7-day plan from name, user ID, age, weight, goal, and intensity.
2. Generate a separate nutrition/recovery tip.
3. Submit feedback and regenerate the plan while preserving the original plan.
4. Store users and plans in SQLite.
5. Admin dashboard at `/view-all-users` protected by a simple token.
6. JSON API endpoints for programmatic use.
7. Health check endpoint.
8. AI-disabled fallback mode for local UI/testing when no API key is configured.

## Safety note

FitBuddy is a general wellness/planning demo, not a medical or diagnostic system. The prompts explicitly tell the model to avoid unsafe exercise, extreme dieting, medical diagnosis, or medication advice and to suggest professional guidance for medical concerns.

## Project structure

```text
fitbuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   └── services/
│       ├── __init__.py
│       ├── gemini_service.py
│       ├── workout_generator.py
│       ├── nutrition_generator.py
│       └── plan_updater.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── static/
│   └── styles.css
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_database.py
├── data/.gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup

### 1. Open the project

Open the `fitbuddy` folder in VS Code.

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
py -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini

Copy `.env.example` to `.env`.

```text
GEMINI_API_KEY=your_real_key
```

If you leave the key blank, the application still starts and uses a clearly marked demo fallback so you can test the UI/database without making an AI call.

### 5. Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

### 6. Admin dashboard

Set `ADMIN_TOKEN` in `.env`, then open:

```text
http://127.0.0.1:8000/view-all-users?token=YOUR_TOKEN
```

For a real deployment, replace this simple demo token with proper authentication/authorization.

## Testing

With the virtual environment active:

```bash
pytest -q
```

The tests use a temporary SQLite database and a fake AI service, so they do not need a Gemini API key.

## API examples

### Generate a plan

```bash
curl -X POST http://127.0.0.1:8000/api/generate-workout \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"demo-001",
    "name":"Alex",
    "age":25,
    "weight":70,
    "goal":"general wellness",
    "intensity":"medium"
  }'
```

### Submit feedback

```bash
curl -X POST http://127.0.0.1:8000/api/submit-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"demo-001",
    "feedback":"Add more mobility work and keep one full rest day."
  }'
```

## Notes on the supplied documentation

The implementation follows the documented scenarios and milestones: user input, 7-day generation, nutrition/recovery tip, feedback-based revision, SQLite persistence, Jinja2 pages, and an all-users/admin view. The code is expanded beyond the snippets/descriptions in the document so every required module is runnable together.
