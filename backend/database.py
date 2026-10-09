import os
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("AirSenseBackend")

# Load variables from ../.env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DB_NAME = os.getenv("POSTGRES_DB", "airquality_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres_secure_pass")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

_pool: pool.SimpleConnectionPool | None = None


def get_pool() -> pool.SimpleConnectionPool:
    """Initialize or return the existing connection pool."""
    global _pool
    if _pool is None or _pool.closed:
        try:
            _pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT,
            )
            logger.info("Database connection pool created successfully.")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    return _pool


def close_pool() -> None:
    """Close all connections in the pool."""
    global _pool
    if _pool is not None and not _pool.closed:
        _pool.closeall()
        logger.info("Database connection pool closed.")


@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Context manager to safely acquire and release a connection from the pool.
    Rolls back transaction on error and ensures the connection is returned to the pool.
    """
    connection_pool = get_pool()
    conn = connection_pool.getconn()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)


@contextmanager
def get_db_cursor(commit: bool = False) -> Generator[psycopg2.extensions.cursor, None, None]:
    """
    Context manager to safely acquire a connection and RealDictCursor.
    Optionally commits the transaction upon completion.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


def check_db_connection() -> bool:
    """
    Ping/healthcheck helper to verify the database connection.
    Returns True if healthy, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                return result is not None and result[0] == 1
    except Exception as e:
        logger.error(f"Database healthcheck failed: {e}")
        return False
