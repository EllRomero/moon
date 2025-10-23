"""
metadata.py

This module serves as the central registry for all SQLAlchemy models in the project.


Purpose:
- Provides a single entry point to collect all models.
- Ensures Alembic can discover every table definition during autogeneration of migrations.
- Simplifies maintenance: Alembic’s `env.py` only needs to import this module instead of
  manually importing each model from different files.
- shortcut import for db models

Usage:
- Add new model imports here whenever a new model is created.
"""

from .activity import Activity
from .organization import Organization
from .point import Point

__all__ = [
    "Organization",
    "Point",
    "Activity",
]
