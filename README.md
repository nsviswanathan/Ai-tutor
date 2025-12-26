# AI Tutor (Conversation-first + Adaptive Learning)

This is a Duolingo-like AI tutor MVP focused on:
- **Conversation-first AI tutor** (role-play chat)
- **Adaptive learning** (practice selection based on mistakes + spaced repetition)
- **Real-world, context-aware lessons** (Airport/Restaurant/Classroom/Office/Shopping)

## Quick start (local)

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend
```bash
cd ../frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open: http://localhost:3000

## Notes
- If you **don’t** set `LLM_API_KEY`, the backend uses a simple local heuristic tutor (still tracks skills and adapts practice).
- If you set `LLM_API_KEY`, it calls an **OpenAI-compatible** endpoint (`LLM_BASE_URL`) and expects the tutor to return a small JSON skill tag block.


## User profiles + progress goals
- Set your daily/weekly minute goals and focus contexts in `/profile`.
- Progress is shown on the home page and profile page.
