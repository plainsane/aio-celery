from __future__ import annotations

from ._state import get_current_app as current_app
from .app import Celery, shared_task
from .canvas import chain, signature
from .task import Task
from .cli import create_parser, create_worker_parser

__version__ = "0.22.0.dev1"

__all__ = (
    "Celery",
    "Task",
    "chain",
    "current_app",
    "shared_task",
    "signature",
    "create_parser",
    "create_worker_parser",
)
