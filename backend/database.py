import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import psycopg2


def _clean_database_url(url: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    allowed = {"sslmode", "sslcert", "sslkey", "sslrootcert", "connect_timeout", "application_name"}
    filtered = {k: v for k, v in params.items() if k in allowed}
    parsed = parsed._replace(query=urlencode(filtered, doseq=True))
    return urlunparse(parsed)


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(_clean_database_url(database_url))
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "reservibe"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "1234"),
        port=os.getenv("DB_PORT", "5432")
    )