# Job_App_Manager

## Quickstart (2 Terminals)
### Frontend
1. Enter the frontend directory
```
cd frontend/web
```

2. Install all npm dependencies
```
npm install dev
```

3. Run the frontend server
```
npm run dev
```

<br>

### Backend
1. From root director, create venv and install dependencies
```
python3 -m venv venv

source venv/bin/activate

pip install fastapi uvicorn "psycopg[binary,pool]" pydantic python-dotenv argon2-cffi
```

2. Start backend
```
uvicorn backend:app --reload --port 8000
```