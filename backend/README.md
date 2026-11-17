# JAM Backend API
> `jam/backend/`

This is JAM's backend server built with Python and FastAPI. In needs to be running in a background process in order for the JAM frontend to work.

## Setup
From this folder, create/activate a new virtual environment:
```bash
python3 -m venv .venv
```
Then, activate the environment: 

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/MacOS:**
```bash
source .venv/bin/activate
```

## Install & Run
Once the virtual environment is activated, first install the package:
```bash
pip install .
```
This will add the `jam-api` command to PATH.
Launch the server with:
```bash
jam-api
```
> *Launches the server with Uvicorn on port 8000*