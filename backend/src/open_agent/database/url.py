"""Normalize configured PostgreSQL URLs for the asyncpg driver."""

from sqlalchemy.engine import make_url


def async_database_url(value: str) -> str:
    """Return a SQLAlchemy asyncpg URL with libpq-only options translated."""
    url = make_url(value)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+asyncpg")

    query = dict(url.query)
    sslmode = query.pop("sslmode", None)
    if sslmode is not None and "ssl" not in query:
        query["ssl"] = sslmode
    # asyncpg negotiates channel binding itself and has no libpq channel_binding
    # connection option.
    query.pop("channel_binding", None)
    return url.set(query=query).render_as_string(hide_password=False)
