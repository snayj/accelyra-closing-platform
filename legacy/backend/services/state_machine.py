"""
Transaction State Machine Service

Manages the 7-stage real estate closing workflow.
This is the "brain" that orchestrates transaction progression.

Key Responsibilities:
1. Validate stage transitions (ensure proper sequence)
2. Log stage history (audit trail)
3. Check stage requirements (tasks, documents)
4. Generate stage-specific tasks
5. Calculate timeline estimates

Business Rules:
- Stages must progress sequentially (no skipping)
- Cannot move backward (except for admin override)
- Each stage has entry requirements
- Stage transitions are logged with timestamps
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.models import Transaction, TransactionStage, Task, TaskType, TaskStatus, TaskPriority, Document, DocumentStatus


class StageTransitionError(Exception):
    """
    Raised when a stage transition is not allowed.
    Example: Trying to skip from stage 1 to stage 5
    """
    pass


class StageRequirementError(Exception):
    """
    Raised when stage requirements are not met.
    Example: Trying to advance without completing required tasks
    """
    pass


class TransactionStateMachine:
    """
    State machine that manages transaction stage transitions.

    This class encapsulates all the business logic for moving a transaction
    through the 7 stages of the closing process.
    """

    # Define the valid stage progression order
    # This is the linear path a transaction must follow
    STAGE_ORDER = [
        TransactionStage.OFFER_ACCEPTED,
        TransactionStage.TITLE_SEARCH,
        TransactionStage.UNDERWRITING,
        TransactionStage.CLEAR_TO_CLOSE,
        TransactionStage.FINAL_DOCUMENTS,
        TransactionStage.FUNDING_SIGNING,
        TransactionStage.RECORDING_COMPLETE,
    ]

    # Estimated days for each stage (platform-accelerated timeline)
    # Traditional timeline would be 2-3x longer
    STAGE_DURATIONS = {
        TransactionStage.OFFER_ACCEPTED: 1,      # Day 0-1: Set up escrow
        TransactionStage.TITLE_SEARCH: 2,        # Day 1-3: Title search
        TransactionStage.UNDERWRITING: 4,        # Day 3-7: Lender review, inspections
        TransactionStage.CLEAR_TO_CLOSE: 1,      # Day 7-8: Final underwriting approval
        TransactionStage.FINAL_DOCUMENTS: 2,     # Day 8-10: Prepare closing docs
        TransactionStage.FUNDING_SIGNING: 2,     # Day 10-12: Sign docs, wire funds
        TransactionStage.RECORDING_COMPLETE: 1,  # Day 12-13: Record with county
    }

    def __init__(self, db: Session):
        """
        Initialize the state machine with a database session.

        Args:
            db: SQLAlchemy database session for queries and updates
        """
        self.db = db

    def get_current_stage(self, transaction: Transaction) -> TransactionStage:
        """
        Get the current stage of a transaction.

        Args:
            transaction: Transaction object

        Returns:
            Current TransactionStage enum
        """
        return transaction.current_stage

    def can_advance_to_next_stage(self, transaction: Transaction) -> tuple[bool, Optional[str]]:
        """
        Check if transaction can advance to the next stage.

        This method checks:
        1. Transaction is not already in final stage
        2. All blocking tasks are completed
        3. Required documents are approved

        Args:
            transaction: Transaction object

        Returns:
            Tuple of (can_advance: bool, reason: str or None)
            - (True, None) if can advance
            - (False, "reason") if cannot advance
        """
        current_stage = transaction.current_stage

        # Check if already in final stage
        if current_stage == TransactionStage.RECORDING_COMPLETE:
            return False, "Transaction is already complete"

        # Check for blocking tasks
        blocking_tasks = self.db.query(Task).filter(
            Task.transaction_id == transaction.id,
            Task.related_stage == current_stage.value,
            Task.is_blocking == True,
            Task.status != TaskStatus.COMPLETED
        ).all()

        if blocking_tasks:
            task_titles = [task.title for task in blocking_tasks]
            return False, f"Blocking tasks incomplete: {', '.join(task_titles)}"

        # Check for required documents based on stage
        required_doc_checks = self._check_required_documents(transaction, current_stage)
        if not required_doc_checks[0]:
            return False, required_doc_checks[1]

        return True, None

    def _check_required_documents(self, transaction: Transaction, stage: TransactionStage) -> tuple[bool, Optional[str]]:
        """
        Check if required documents for the current stage are approved.

        Different stages have different document requirements.

        Args:
            transaction: Transaction object
            stage: Current stage to check requirements for

        Returns:
            Tuple of (requirements_met: bool, reason: str or None)
        """
        # Define required documents per stage
        stage_document_requirements = {
            TransactionStage.OFFER_ACCEPTED: [],  # No docs required to start
            TransactionStage.TITLE_SEARCH: [],    # Title search is ordered, not uploaded
            TransactionStage.UNDERWRITING: ["proof_of_funds"],
            TransactionStage.CLEAR_TO_CLOSE: ["insurance_policy"],
            TransactionStage.FINAL_DOCUMENTS: ["closing_disclosure"],
            TransactionStage.FUNDING_SIGNING: [],  # Documents prepared by title company
            TransactionStage.RECORDING_COMPLETE: ["deed"],
        }

        required_docs = stage_document_requirements.get(stage, [])

        if not required_docs:
            return True, None

        # Check each required document type
        for doc_type in required_docs:
            doc = self.db.query(Document).filter(
                Document.transaction_id == transaction.id,
                Document.document_type == doc_type,
                Document.status == DocumentStatus.APPROVED
            ).first()

            if not doc:
                return False, f"Required document '{doc_type}' not approved"

        return True, None

    def advance_stage(
        self,
        transaction: Transaction,
        notes: Optional[str] = None,
        force: bool = False
    ) -> Transaction:
        """
        Advance transaction to the next stage.

        This is the main method that:
        1. Validates the transition
        2. Updates the transaction stage
        3. Logs the stage history
        4. Generates new tasks for the next stage
        5. Updates timeline estimates

        Args:
            transaction: Transaction to advance
            notes: Optional notes about the transition
            force: If True, skip requirement checks (admin override)

        Returns:
            Updated transaction object

        Raises:
            StageTransitionError: If transition is invalid
            StageRequirementError: If requirements not met
        """
        current_stage = transaction.current_stage

        # Check if already complete
        if current_stage == TransactionStage.RECORDING_COMPLETE:
            raise StageTransitionError("Transaction is already complete")

        # Check requirements (unless forced)
        if not force:
            can_advance, reason = self.can_advance_to_next_stage(transaction)
            if not can_advance:
                raise StageRequirementError(f"Cannot advance stage: {reason}")

        # Get next stage
        current_index = self.STAGE_ORDER.index(current_stage)
        next_stage = self.STAGE_ORDER[current_index + 1]

        # Log the stage transition in history
        stage_entry = {
            "stage": next_stage.value,
            "entered_at": datetime.utcnow().isoformat(),
            "notes": notes or "",
            "force_advanced": force
        }

        # Initialize stage_history if it's None
        if transaction.stage_history is None:
            transaction.stage_history = []

        transaction.stage_history.append(stage_entry)

        # Update transaction stage
        transaction.current_stage = next_stage
        transaction.stage_started_at = datetime.utcnow()

        # Update estimated closing date based on remaining stages
        remaining_days = sum([
            self.STAGE_DURATIONS[stage]
            for stage in self.STAGE_ORDER[current_index + 1:]
        ])
        transaction.estimated_closing_date = datetime.utcnow() + timedelta(days=remaining_days)

        # Mark as actually closed if reaching final stage
        if next_stage == TransactionStage.RECORDING_COMPLETE:
            transaction.actual_closing_date = datetime.utcnow()

        # Generate tasks for the new stage
        self._generate_stage_tasks(transaction, next_stage)

        # Commit changes
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def _generate_stage_tasks(self, transaction: Transaction, stage: TransactionStage):
        """
        Generate tasks specific to a stage.

        Each stage has predefined tasks that need to be completed.
        These are automatically created when entering a new stage.

        Args:
            transaction: Transaction object
            stage: Stage to generate tasks for
        """
        # Define tasks for each stage
        # Format: (title, description, task_type, assigned_to_role, is_blocking, priority)
        stage_tasks = {
            TransactionStage.OFFER_ACCEPTED: [
                ("Deposit earnest money", "Buyer must deposit earnest money to escrow account",
                 TaskType.PAYMENT, "buyer", True, TaskPriority.CRITICAL),
                ("Upload proof of funds", "Upload bank statement or pre-approval letter",
                 TaskType.DOCUMENT_UPLOAD, "buyer", True, TaskPriority.HIGH),
                ("Open escrow account", "Title company to open escrow account",
                 TaskType.OTHER, "title_officer", True, TaskPriority.HIGH),
            ],
            TransactionStage.TITLE_SEARCH: [
                ("Order title search", "Title company to search property records",
                 TaskType.OTHER, "title_officer", True, TaskPriority.CRITICAL),
                ("Review title report", "Review title search results for issues",
                 TaskType.DOCUMENT_REVIEW, "title_officer", True, TaskPriority.HIGH),
            ],
            TransactionStage.UNDERWRITING: [
                ("Submit loan application", "Complete and submit mortgage application",
                 TaskType.OTHER, "buyer", True, TaskPriority.CRITICAL),
                ("Schedule home inspection", "Hire inspector and schedule inspection",
                 TaskType.INSPECTION, "buyer", False, TaskPriority.NORMAL),
                ("Order appraisal", "Lender to order property appraisal",
                 TaskType.OTHER, "loan_officer", True, TaskPriority.HIGH),
                ("Verify employment", "Lender to verify buyer employment and income",
                 TaskType.VERIFICATION, "loan_officer", True, TaskPriority.HIGH),
            ],
            TransactionStage.CLEAR_TO_CLOSE: [
                ("Obtain clear to close", "Final underwriting approval from lender",
                 TaskType.APPROVAL, "loan_officer", True, TaskPriority.CRITICAL),
                ("Upload insurance policy", "Provide proof of homeowners insurance",
                 TaskType.DOCUMENT_UPLOAD, "buyer", True, TaskPriority.HIGH),
            ],
            TransactionStage.FINAL_DOCUMENTS: [
                ("Prepare closing disclosure", "Title company prepares final settlement statement",
                 TaskType.OTHER, "title_officer", True, TaskPriority.CRITICAL),
                ("Review closing disclosure", "Buyer and seller review closing costs",
                 TaskType.DOCUMENT_REVIEW, "buyer", True, TaskPriority.HIGH),
                ("Prepare deed", "Title company prepares property deed",
                 TaskType.OTHER, "title_officer", True, TaskPriority.HIGH),
            ],
            TransactionStage.FUNDING_SIGNING: [
                ("Wire down payment", "Buyer to wire down payment funds to escrow",
                 TaskType.PAYMENT, "buyer", True, TaskPriority.CRITICAL),
                ("Sign closing documents", "Buyer and seller sign all closing documents",
                 TaskType.DOCUMENT_SIGN, "buyer", True, TaskPriority.CRITICAL),
                ("Lender funds loan", "Lender wires loan amount to escrow",
                 TaskType.PAYMENT, "loan_officer", True, TaskPriority.CRITICAL),
            ],
            TransactionStage.RECORDING_COMPLETE: [
                ("Record deed", "County recorder records deed and transfer",
                 TaskType.OTHER, "title_officer", True, TaskPriority.CRITICAL),
                ("Disburse funds", "Escrow disburses funds to seller and vendors",
                 TaskType.PAYMENT, "title_officer", True, TaskPriority.HIGH),
            ],
        }

        tasks_for_stage = stage_tasks.get(stage, [])

        # Get starting task count once before the loop
        task_count = self.db.query(Task).count()

        for i, task_data in enumerate(tasks_for_stage):
            title, description, task_type, assigned_role, is_blocking, priority = task_data

            # Generate unique task ID
            task_id = f"TASK-{datetime.utcnow().year}-{task_count + i + 1:04d}"

            # Calculate due date based on stage duration
            days_until_due = self.STAGE_DURATIONS.get(stage, 2)
            due_date = datetime.utcnow() + timedelta(days=days_until_due)

            # Find the party with this role in the transaction
            assigned_to = self._get_party_by_role(transaction, assigned_role)

            # Create task
            task = Task(
                id=task_id,
                transaction_id=transaction.id,
                title=title,
                description=description,
                task_type=task_type,
                assigned_to=assigned_to,
                assigned_by="system",
                status=TaskStatus.PENDING,
                priority=priority,
                due_date=due_date,
                is_blocking=is_blocking,
                related_stage=stage.value
            )

            self.db.add(task)

    def _get_party_by_role(self, transaction: Transaction, role: str) -> Optional[str]:
        """
        Get party ID for a specific role in the transaction.

        Args:
            transaction: Transaction object
            role: Role name (buyer, seller, buyer_agent, etc.)

        Returns:
            Party ID or None if not assigned
        """
        role_mapping = {
            "buyer": transaction.buyer_id,
            "seller": transaction.seller_id,
            "buyer_agent": transaction.buyer_agent_id,
            "seller_agent": transaction.seller_agent_id,
            "loan_officer": transaction.loan_officer_id,
            "title_officer": transaction.title_officer_id,
        }
        return role_mapping.get(role)

    def get_stage_progress(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Get detailed progress information about the transaction.

        Returns stage-by-stage status with completion dates.

        Args:
            transaction: Transaction object

        Returns:
            Dictionary with stage progress details
        """
        current_stage = transaction.current_stage
        current_index = self.STAGE_ORDER.index(current_stage)

        progress = {
            "current_stage": current_stage.value,
            "current_stage_index": current_index,
            "total_stages": len(self.STAGE_ORDER),
            "percent_complete": int((current_index / len(self.STAGE_ORDER)) * 100),
            "stages": []
        }

        # Build stage-by-stage progress
        for i, stage in enumerate(self.STAGE_ORDER):
            stage_info = {
                "stage": stage.value,
                "order": i,
                "status": "complete" if i < current_index else ("current" if i == current_index else "pending"),
                "entered_at": None,
                "notes": None
            }

            # Find this stage in history
            if transaction.stage_history:
                for history_entry in transaction.stage_history:
                    if history_entry.get("stage") == stage.value:
                        stage_info["entered_at"] = history_entry.get("entered_at")
                        stage_info["notes"] = history_entry.get("notes")
                        break

            progress["stages"].append(stage_info)

        return progress

    def get_days_in_current_stage(self, transaction: Transaction) -> int:
        """
        Calculate how many days the transaction has been in current stage.

        Args:
            transaction: Transaction object

        Returns:
            Number of days (integer)
        """
        if not transaction.stage_started_at:
            return 0

        delta = datetime.utcnow() - transaction.stage_started_at
        return delta.days

    def estimate_days_to_close(self, transaction: Transaction) -> int:
        """
        Estimate remaining days until closing complete.

        Args:
            transaction: Transaction object

        Returns:
            Estimated days remaining
        """
        current_stage = transaction.current_stage
        current_index = self.STAGE_ORDER.index(current_stage)

        # Sum up durations for remaining stages (including current)
        remaining_days = sum([
            self.STAGE_DURATIONS[stage]
            for stage in self.STAGE_ORDER[current_index:]
        ])

        return remaining_days
