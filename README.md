# Rail Optimizer AI — starter project

## Structure
```text
rail-optimizer-ai/
├── frontend/       React + Vite website
├── backend/        FastAPI API and demo planning engine
├── datasets/       Local datasets (ignored by Git except template/docs)
└── .gitignore
```

## Run backend (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Run frontend (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the Vite URL, normally http://localhost:5173. API docs: http://localhost:8000/docs.

## Notes
- Current route, time, and price values are synthetic demo estimates, not official quotes or live rail data.
- Confirmation only records user intent in a local CSV; it does not reserve railway capacity.
- Authentication/admin access is not yet implemented. Add real authentication before deployment.
- The CSV preview endpoint does not save data or train a model yet.
- Dataset files are ignored by Git by default. Test files are also ignored as requested.
