import asyncio
import os
import sys
from logging.config import fileConfig

# Add the project root to sys.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.db.database import Base
from dotenv import load_dotenv

load_dotenv()

# Import all models here for Alembic to detect them
from app.models.article import Article
from app.models.auth import Auth
from app.models.bio import Bio
from app.models.cv import Cv
from app.models.degree import ScientificDegree
from app.models.education import Education
from app.models.education_translation import EducationTranslation
from app.models.experience import Experience
from app.models.experience_translation import ExperienceTranslations
from app.models.inter_coor import InterCoor
from app.models.inter_corp_users import InternationalCorporationsUsers
from app.models.language import Language
from app.models.links import Links
from app.models.otp import Otp
from app.models.publication import Publication
from app.models.research_areas import ResearchAreas
from app.models.scientific_name import ScientificName
from app.models.user import User
from app.models.work import Work
from app.models.translations.article_translation import ArticleTranslation
from app.models.translations.bio_translation import BioTranslation
from app.models.translations.inter_coor_translations import InterCoorTranslations
from app.models.translations.language_translations import LanguageTranslations
from app.models.translations.publication_translation import PublicationTranslation
from app.models.translations.research_areas_translations import ResearchAreasTranslations
from app.models.translations.scientific_name_translation import ScientificNameTranslation
from app.models.translations.user_translations import UserTranslations
from app.models.translations.work_translations import WorkTranslations

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the sqlalchemy.url from environment if not set in ini
section = config.config_ini_section
db_url = os.getenv("DATABASE_URL")
if db_url:
    # Alembic needs the async driver for the online migration if using async_engine_from_config
    if "postgresql://" in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    config.set_section_option(section, "sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
