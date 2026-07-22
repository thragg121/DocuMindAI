from pathlib import Path

from loguru import logger

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    LOG_DIR / "application.log",
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    level="INFO",
    enqueue=True,
)

logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
)

app_logger = logger
