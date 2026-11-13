# JAM - Job Application Manager

Welcome to JAM!

## Setup and Install
First, clone the repository and `cd` into it. The app runs from two processes:

### Neon Database Connection
User data is stored in a Postgres database hosted on Neon. To establish the connection, first create the `.env` file:
```bash
cp .env.example .env
```

Then replace the "<<PASSWORD_HERE>>" placeholder with the connection string from the Neon database before continuing.

---

### Backend Server
The backend server runs on python with FastAPI, launched via uvicorn. Install it into a new virtual environment with:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate # for linux/mac; run .venv\Scripts\Activate.ps1 for Windows
pip install .
```

This adds the `jam-api` script to PATH. With the virtual environment activated, launch it in one process with:
```bash
jam-api
```
> Opens the FastAPI server on port `8000`

---

### Frontend Application
Launch the frontend in a new process with node:

1. Enter the frontend directory
```bash
cd frontend
```

2. Install all npm dependencies
```bash
npm install
```

3. Run the frontend server
```bash
npm run dev
```
> Launches on port 5173 by default, open in a browser at `localhost:5173`