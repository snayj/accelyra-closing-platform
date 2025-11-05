"""
Task API Endpoints

Handles task operations - viewing, updating status, completing tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from backend.database import get_db
from backend.models import Task, TaskStatus

logger = logging.getLogger(__name__)
router = APIRouter()


class TaskComplete(BaseModel):
    """Schema for completing a task."""
    completion_notes: Optional[str] = Field(None, description="Notes about completion")
    completion_data: Optional[dict] = Field(None, description="Additional completion data")


@router.get("/transactions/{transaction_id}/tasks", response_model=dict)
async def get_transaction_tasks(
    transaction_id: str,
    status_filter: Optional[str] = None,
    is_blocking: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all tasks for a transaction.

    **Logging**: Logs task query for audit trail.
    """
    logger.info(f"Fetching tasks for transaction: {transaction_id}")

    query = db.query(Task).filter(Task.transaction_id == transaction_id)

    if status_filter:
        try:
            status_enum = TaskStatus(status_filter)
            query = query.filter(Task.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    if is_blocking is not None:
        query = query.filter(Task.is_blocking == is_blocking)

    tasks = query.all()

    logger.info(f"Found {len(tasks)} tasks")

    return {
        "transaction_id": transaction_id,
        "count": len(tasks),
        "tasks": [task.to_dict() for task in tasks]
    }


@router.post("/tasks/{task_id}/complete", response_model=dict)
async def complete_task(
    task_id: str,
    completion: TaskComplete,
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed.

    **Workflow Impact**: Completing blocking tasks may allow stage advancement.

    **Logging**: Records task completion with timestamp.
    """
    logger.info("=" * 60)
    logger.info(f"COMPLETING TASK - {task_id}")
    logger.info("=" * 60)

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.status == TaskStatus.COMPLETED:
        logger.warning(f"Task already completed: {task_id}")
        return {
            "success": True,
            "message": "Task was already completed",
            "task_id": task_id
        }

    logger.info(f"Task: {task.title}")
    logger.info(f"Was blocking: {task.is_blocking}")

    # Update task
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    task.completion_notes = completion.completion_notes
    if completion.completion_data:
        task.completion_data = completion.completion_data

    db.commit()
    db.refresh(task)

    logger.info(f"✓ Task completed at: {task.completed_at}")
    logger.info("=" * 60)

    return {
        "success": True,
        "message": "Task completed successfully",
        "task_id": task_id,
        "completed_at": task.completed_at.isoformat(),
        "was_blocking": task.is_blocking
    }


@router.get("/tasks/{task_id}", response_model=dict)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific task."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task.to_dict()
