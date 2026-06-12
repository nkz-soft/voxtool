from __future__ import annotations

import uvicorn


def main() -> None:
    """Serve the optional local demo API: python -m apps.api"""
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
