from logging.config import fileConfig

from sqlalchemy import create_engine, engine_from_config
from sqlalchemy import pool

from alembic import context

from app.src.models.users.user_model import UserModel
from app.src.models.users.user_profile import UserProfile
from app.src.models.users.user_address import UserAddress
from app.src.models.users.login_logs import LoginLogs
from app.src.models.accountsandsavings.accounts_model import AccountsModel
from app.src.models.accountsandsavings.transaction_model import TransactionModel
from app.src.models.users.user_accounts import UserAccounts

from app.src.config.base_file import Base

from app.src.config.settings import settings

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
