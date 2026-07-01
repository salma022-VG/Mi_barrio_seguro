"""Punto de entrada local."""
from config.settings import HOST, PORT


def main() -> None:
    import uvicorn

    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    main()
