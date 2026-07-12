from loguru import logger
import sys
from app.config.settings import settings


def setup_logging():
    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(sys.stdout, format=log_format, level="DEBUG" if settings.DEBUG else "INFO")
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="30 days",
        format=log_format,
        level="INFO",
    )
    return logger
