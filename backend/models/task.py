"""
Task Model

Represents action items that must be completed to advance a transaction.
Tasks drive the workflow - they tell people what needs to be done and by when.

Business Context:
- Each stage generates specific tasks (e.g., "Upload proof of funds")
- Tasks can be assigned to buyers, sellers, agents, or system-generated
- Overdue tasks block transaction progress and trigger notifications
- Completed tasks allow transaction to advance to next stage
"""

from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Integer, JSON
from datetime import datetime
import enum

from backend.database import Base


class TaskType(enum.Enum):
    """
    Categories of tasks in the closing process.

    Different task types may have different handling:
    - DOCUMENT_UPLOAD: Upload a specific document
    - DOCUMENT_SIGN: Sign a document (e-signature)
    - DOCUMENT_REVIEW: Review and approve a document
    - PAYMENT: Make a payment (earnest money, down payment)
    - VERIFICATION: Verify something (funds, employment, insurance)
    - INSPECTION: Schedule/complete property inspection
    - APPROVAL: Obtain approval (lender approval, title clearance)
    - NOTIFICATION: Informational task (no action required)
    - OTHER: Miscellaneous tasks
    """
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_SIGN = "document_sign"
    DOCUMENT_REVIEW = "document_review"
    PAYMENT = "payment"
    VERIFICATION = "verification"
    INSPECTION = "inspection"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    OTHER = "other"


class TaskStatus(enum.Enum):
    """
    Lifecycle status of a task.

    Workflow:
    1. PENDING - Task created, not yet started
    2. IN_PROGRESS - Someone is working on it
    3. BLOCKED - Cannot proceed (waiting on something else)
    4. COMPLETED - Task finished successfully
    5. CANCELLED - Task no longer needed
    6. OVERDUE - Past due date and not completed
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class TaskPriority(enum.Enum):
    """
    Priority levels for tasks.

    Determines urgency and notification frequency:
    - LOW: Nice to have, not blocking
    - NORMAL: Standard task
    - HIGH: Important, may block progress
    - CRITICAL: Urgent, definitely blocking progress
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Task(Base):
    """
    Task table representing action items in a transaction.

    Tasks create accountability and visibility into what needs to happen next.
    The platform automatically generates tasks based on transaction stage
    and document validation results.
    """
    __tablename__ = "tasks"

    # ============================================================================
    # PRIMARY KEY
    # ============================================================================

    id = Column(String, primary_key=True, index=True)  # e.g., "TASK-2024-001"

    # ============================================================================
    # TASK IDENTIFICATION
    # ============================================================================

    transaction_id = Column(String, nullable=False, index=True)  # Links to Transaction.id
    title = Column(String, nullable=False)             # "Upload proof of funds"
    description = Column(String)                       # Detailed instructions
    task_type = Column(SQLEnum(TaskType), nullable=False)

    # ============================================================================
    # ASSIGNMENT AND RESPONSIBILITY
    # ============================================================================

    assigned_to = Column(String, index=True)           # Party.id responsible for this task
    assigned_by = Column(String)                       # Party.id or "system" who created task
    assigned_at = Column(DateTime, default=datetime.utcnow)

    # ============================================================================
    # STATUS AND PRIORITY
    # ============================================================================

    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.NORMAL)

    # ============================================================================
    # TIMELINE
    # ============================================================================

    due_date = Column(DateTime)                        # When task must be completed
    started_at = Column(DateTime)                      # When work began
    completed_at = Column(DateTime)                    # When finished
    completed_by = Column(String)                      # Party.id who completed it

    # ============================================================================
    # BLOCKING AND DEPENDENCIES
    # ============================================================================

    # Is this task blocking transaction progress?
    # If True, transaction cannot advance to next stage until this is done
    is_blocking = Column(Boolean, default=False)

    # Task dependencies (JSON array of task IDs)
    # This task cannot start until these tasks are completed
    # Example: ["TASK-2024-001", "TASK-2024-002"]
    depends_on = Column(JSON, default=list)

    # Blocked reason (if status is BLOCKED)
    blocked_reason = Column(String)                    # Why is this task blocked?

    # ============================================================================
    # RELATED ENTITIES
    # ============================================================================

    # Related document (if task is document-specific)
    related_document_id = Column(String)               # Document.id this task relates to

    # Stage this task belongs to
    # Helps organize tasks by transaction stage
    related_stage = Column(String)                     # e.g., "title_search_ordered"

    # ============================================================================
    # COMPLETION TRACKING
    # ============================================================================

    # Result/outcome of completed task (JSON)
    # Example for document upload:
    # {
    #   "document_id": "DOC-2024-123",
    #   "validation_passed": true
    # }
    completion_data = Column(JSON, default=dict)

    # Notes about task completion
    completion_notes = Column(String)

    # ============================================================================
    # NOTIFICATIONS
    # ============================================================================

    # Track when reminders were sent
    last_reminder_sent_at = Column(DateTime)
    reminder_count = Column(Integer, default=0)        # How many reminders sent

    # ============================================================================
    # METADATA
    # ============================================================================

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Internal notes
    notes = Column(String)

    def __repr__(self):
        """String representation for debugging"""
        return f"<Task {self.id} - {self.title} - Status: {self.status.value}>"

    def to_dict(self):
        """
        Convert task to dictionary for API responses.
        """
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value if self.task_type else None,
            "assigned_to": self.assigned_to,
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_blocking": self.is_blocking,
            "related_document_id": self.related_document_id,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def is_overdue(self):
        """
        Check if task is overdue.
        Returns True if past due date and not completed.
        """
        if self.status == TaskStatus.COMPLETED:
            return False
        if self.due_date and self.due_date < datetime.utcnow():
            return True
        return False

    def can_start(self):
        """
        Check if task can be started.
        Returns True if all dependencies are met.
        """
        # If no dependencies, can start
        if not self.depends_on:
            return True

        # TODO: In actual implementation, check if all dependent tasks are completed
        # This requires querying the database for those task IDs
        # For now, return True (we'll implement this in the service layer)
        return True

    def get_days_until_due(self):
        """
        Calculate days until task is due.
        Returns negative number if overdue.
        """
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.days
