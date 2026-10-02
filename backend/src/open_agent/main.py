"""Open Agent AWS application entry point."""

import logging

from fastapi import FastAPI

from open_agent import __version__
from open_agent.core.config import get_settings
from open_agent.core.lifecycle import lifespan
from open_agent.core.logging import configure_logging


settings = get_settings()

configure_logging(settings)

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    debug=settings.debug,
    lifespan=lifespan,

)


@app.get("/")
async def root() -> dict[str, str]:
    """Return basic application information."""

    return {
        "service": settings.app_name,
        "status": "running",
        "version": __version__,
    }