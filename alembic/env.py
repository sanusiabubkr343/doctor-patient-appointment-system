from logging.config import fileConfig
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os
from alembic import context
from dotenv import load_dotenv
from pathlib import Path


# Load environment variables from .env
load_dotenv()
# Add your project directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))


from app.core.database import Base
from app.models.users import User, DoctorProfile
from app.models.appointments import AvailableTimeSlot, Appointment

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def get_url():
    # Get database URL from environment variables
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgrespw")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "la-hospital")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
