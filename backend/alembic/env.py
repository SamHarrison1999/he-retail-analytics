# backend/alembic/env.py
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel
# Import models so autogenerate & metadata work
from src.infra.db import JobRecord, JobLog, Artifact  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

DB_URL = os.getenv("DB_URL", config.get_main_option("sqlalchemy.url"))
if DB_URL:
  # ensure parent dir exists for SQLite
  try:
    url = make_url(DB_URL)
    if url.drivername.startswith("sqlite") and url.database not in (None, "", ":memory:"):
      os.makedirs(os.path.dirname(url.database), exist_ok=True)
  except Exception:
    pass
  config.set_main_option("sqlalchemy.url", DB_URL)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
  url = config.get_main_option("sqlalchemy.url")
  context.configure(
    url=url,
    target_metadata=target_metadata,
    literal_binds=True,
    compare_type=True,
    render_as_batch=True,  # helpful for SQLite migrations
  )
  with context.begin_transaction():
    context.run_migrations()


def run_migrations_online() -> None:
  connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
    future=True,
  )

  with connectable.connect() as connection:
    context.configure(
      connection=connection,
      target_metadata=target_metadata,
      compare_type=True,
      render_as_batch=True,  # helpful for SQLite migrations
    )

    with context.begin_transaction():
      context.run_migrations()


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
