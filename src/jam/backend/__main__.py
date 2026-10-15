"""Start the FastAPI backend exposing the Neon database interface."""

import os

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    """Entry point for `jam-api` CLI script."""
    import uvicorn

    uvicorn.run(
        "jam.backend:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=bool(int(os.getenv("RELOAD", "0"))),
    )


if __name__ == "__main__":
    main()
