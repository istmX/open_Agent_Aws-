"""FastAPI application lifecycle management."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""

    logger.info("Starting Open Agent AWS")

    # Resources will be initialized here later.
    #
    # Examples:
    # - Database connection pool
    # - Qdrant client
    # - LLM client
    # - Agent runtime
    # - Browser manager

    yield

    # Resources will be cleaned up here later.
    #
    # Examples:
    # - Close database pool
    # - Close Qdrant client
    # - Close HTTP clients
    # - Shut down browser resources

    logger.info("Shutting down Open Agent AWS")