from logging.config import fileConfig

from sqlalchemy import create_engine, engine_from_config
from sqlalchemy import pool

from alembic import context

# Import all models via the package init to register them on Base.metadata.
# This includes: users, member, shares, savings, ledger, tenant, and accounts/transactions.
from app.src.models import *  # noqa: F401, F403

from app.src.models import Base

from app.src.config.settings import settings

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- ADD THESE TWO LINES TO THE TOP OF alembic/env.py ---
from dotenv import load_dotenv
load_dotenv()  # This pulls values from your local .env file

config = context.config

# --- OVERRIDE THE INI URL WITH YOUR ENVIRONMENT VARIABLE ---
if os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:

    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
