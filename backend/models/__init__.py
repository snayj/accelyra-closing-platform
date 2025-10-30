"""
Database Models Package

This package contains all database table definitions (models).

Models:
- Transaction: Main closing transaction with workflow tracking
- Document: Uploaded files with OCR and validation
- Party: People involved in transactions (buyers, sellers, agents, etc.)
- Task: Action items that drive the closing process

Usage:
    from backend.models import Transaction, Document, Party, Task
"""

from backend.models.transaction import Transaction, TransactionStage, EarnestMoneyStatus
from backend.models.document import Document, DocumentType, DocumentStatus
from backend.models.party import Party, PartyRole
from backend.models.task import Task, TaskType, TaskStatus, TaskPriority

__all__ = [
    # Models
    "Transaction",
    "Document",
    "Party",
    "Task",
    # Enums
    "TransactionStage",
    "EarnestMoneyStatus",
    "DocumentType",
    "DocumentStatus",
    "PartyRole",
    "TaskType",
    "TaskStatus",
    "TaskPriority",
]
