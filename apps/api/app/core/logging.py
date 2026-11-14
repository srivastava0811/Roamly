import logging
import sys


def setup_logging(env: str = "development") -> None:
    log_level = logging.DEBUG if env == "development" else logging.INFO
    
    log_format = (
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)


logger = logging.getLogger("roamly")
