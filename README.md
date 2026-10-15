# Job_App_Manager

## Quickstart
1. Create `.env` and add `DATABASE_URL` pointing to the neon database.

2. Create a new python virtual environment and install the package.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```
> We can switch to docker compose soon.

3. In one session, start the FastAPI backend:
```bash
$ jam-api
```

and launch the TUI in another:
```bash
$ jam
```