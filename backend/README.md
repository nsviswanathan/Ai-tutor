# AI Tutor Backend (FastAPI)

## What it does
- Conversation-first tutor (`/api/chat`)
- Adaptive practice selection based on **mistakes** + **spaced repetition** (`/api/practice/next`)
- Skill tracking + review scheduling (`/api/skills`)

## Run locally
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The DB will auto-create at `backend/data/app.db`.

## API quick test
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","context":"Airport","level":"Beginner","message":"Hi, I need to check in for my flight"}'
```


## Profiles & progress
- `GET /api/profile/{user_id}`
- `PUT /api/profile/{user_id}`
- `GET /api/progress/{user_id}`
- `POST /api/activity/log`

## Using Gemini as the LLM
1) Install deps:
```bash
pip install -r requirements.txt
```

2) Set env in `backend/.env`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=gemini-1.5-flash
```

Restart the backend.
