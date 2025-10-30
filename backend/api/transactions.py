"""
Transaction API Endpoints

Handles all transaction-related operations:
- Create new transactions
- View transaction details and list
- Advance transaction stages
- Track transaction progress
- Workflow operations (earnest money, funds verification)

All operations include comprehensive logging for audit trail.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from backend.database import get_db
from backend.models import Transaction, TransactionStage, EarnestMoneyStatus, Party, Task
from backend.services.state_machine import TransactionStateMachine, StageRequirementError, StageTransitionError

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS (Request/Response Models)
# ============================================================================

class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    property_address: str = Field(..., description="Full property address")
    property_type: Optional[str] = Field(None, description="Property type (single_family, condo, etc.)")
    property_sqft: Optional[int] = Field(None, description="Square footage")
    property_bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    property_bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    property_year_built: Optional[int] = Field(None, description="Year built")
    purchase_price: float = Field(..., description="Purchase price in dollars", gt=0)
    down_payment: Optional[float] = Field(None, description="Down payment amount", ge=0)
    loan_amount: Optional[float] = Field(None, description="Mortgage loan amount", ge=0)
    earnest_money_amount: Optional[float] = Field(None, description="Earnest money deposit", ge=0)
    buyer_id: Optional[str] = Field(None, description="Buyer party ID")
    seller_id: Optional[str] = Field(None, description="Seller party ID")
    buyer_agent_id: Optional[str] = Field(None, description="Buyer's agent party ID")
    seller_agent_id: Optional[str] = Field(None, description="Seller's agent party ID")
    loan_officer_id: Optional[str] = Field(None, description="Loan officer party ID")
    title_officer_id: Optional[str] = Field(None, description="Title officer party ID")

    class Config:
        json_schema_extra = {
            "example": {
                "property_address": "123 Maple St, Springfield, IL 62701",
                "property_type": "single_family",
                "property_sqft": 1850,
                "property_bedrooms": 3,
                "property_bathrooms": 2.5,
                "purchase_price": 450000,
                "down_payment": 90000,
                "loan_amount": 360000,
                "earnest_money_amount": 9000,
                "buyer_id": "PARTY-001",
                "seller_id": "PARTY-002"
            }
        }


class EarnestMoneyDeposit(BaseModel):
    """Schema for recording earnest money deposit."""
    amount: float = Field(..., description="Amount deposited", gt=0)
    deposited_at: Optional[datetime] = Field(None, description="When deposited (defaults to now)")
    notes: Optional[str] = Field(None, description="Additional notes")


class FundsVerification(BaseModel):
    """Schema for verifying buyer funds."""
    verified_by: str = Field(..., description="Who verified (user ID or 'system')")
    verification_method: Optional[str] = Field(None, description="How verified (bank_statement, pre_approval, etc.)")
    notes: Optional[str] = Field(None, description="Verification notes")


class StageAdvancement(BaseModel):
    """Schema for advancing transaction stage."""
    notes: Optional[str] = Field(None, description="Notes about the advancement")
    force: bool = Field(False, description="Force advancement (skip requirement checks)")


# ============================================================================
# TRANSACTION CRUD ENDPOINTS
# ============================================================================

@router.post("/transactions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new real estate closing transaction.

    This initializes a transaction at the "Offer Accepted" stage and
    automatically generates initial tasks.

    **Logging**: Creates audit log entry for transaction creation.
    """
    logger.info("=" * 60)
    logger.info("CREATING NEW TRANSACTION")
    logger.info("=" * 60)
    logger.info(f"Property: {transaction_data.property_address}")
    logger.info(f"Price: ${transaction_data.purchase_price:,.2f}")

    # Generate transaction ID
    txn_count = db.query(Transaction).count()
    txn_id = f"TXN-{datetime.utcnow().year}-{txn_count + 1:04d}"

    # Create transaction
    transaction = Transaction(
        id=txn_id,
        property_address=transaction_data.property_address,
        property_type=transaction_data.property_type,
        property_sqft=transaction_data.property_sqft,
        property_bedrooms=transaction_data.property_bedrooms,
        property_bathrooms=transaction_data.property_bathrooms,
        property_year_built=transaction_data.property_year_built,
        purchase_price=transaction_data.purchase_price,
        down_payment=transaction_data.down_payment,
        loan_amount=transaction_data.loan_amount,
        earnest_money_amount=transaction_data.earnest_money_amount,
        earnest_money_status=EarnestMoneyStatus.PENDING,
        funds_verified=False,
        current_stage=TransactionStage.OFFER_ACCEPTED,
        stage_started_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        estimated_closing_date=datetime.utcnow() + timedelta(days=13),  # Platform timeline
        buyer_id=transaction_data.buyer_id,
        seller_id=transaction_data.seller_id,
        buyer_agent_id=transaction_data.buyer_agent_id,
        seller_agent_id=transaction_data.seller_agent_id,
        loan_officer_id=transaction_data.loan_officer_id,
        title_officer_id=transaction_data.title_officer_id,
        stage_history=[{
            "stage": TransactionStage.OFFER_ACCEPTED.value,
            "entered_at": datetime.utcnow().isoformat(),
            "notes": "Transaction created"
        }]
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Generate initial tasks using state machine
    state_machine = TransactionStateMachine(db)
    state_machine._generate_stage_tasks(transaction, TransactionStage.OFFER_ACCEPTED)
    db.commit()

    logger.info(f"✓ Transaction created: {txn_id}")
    logger.info(f"✓ Initial tasks generated for stage: {TransactionStage.OFFER_ACCEPTED.value}")
    logger.info("=" * 60)

    return {
        "success": True,
        "message": "Transaction created successfully",
        "transaction_id": txn_id,
        "transaction": transaction.to_dict()
    }


@router.get("/transactions", response_model=dict)
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all transactions with optional filtering.

    **Query Parameters:**
    - skip: Number of records to skip (pagination)
    - limit: Maximum records to return
    - stage: Filter by current stage (e.g., "offer_accepted")

    **Logging**: Logs query parameters for audit.
    """
    logger.info(f"Listing transactions (skip={skip}, limit={limit}, stage={stage})")

    query = db.query(Transaction)

    if stage:
        try:
            stage_enum = TransactionStage(stage)
            query = query.filter(Transaction.current_stage == stage_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage: {stage}"
            )

    transactions = query.offset(skip).limit(limit).all()

    logger.info(f"Found {len(transactions)} transactions")

    return {
        "count": len(transactions),
        "transactions": [txn.to_dict() for txn in transactions]
    }


@router.get("/transactions/{transaction_id}", response_model=dict)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific transaction.

    Includes:
    - Transaction details
    - Stage progress
    - Associated tasks
    - Timeline information

    **Logging**: Logs transaction access for audit trail.
    """
    logger.info(f"Fetching transaction: {transaction_id}")

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        logger.warning(f"Transaction not found: {transaction_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )

    # Get stage progress
    state_machine = TransactionStateMachine(db)
    progress = state_machine.get_stage_progress(transaction)
    days_in_stage = state_machine.get_days_in_current_stage(transaction)
    days_to_close = state_machine.estimate_days_to_close(transaction)

    # Get associated tasks
    tasks = db.query(Task).filter(Task.transaction_id == transaction_id).all()

    logger.info(f"✓ Transaction found: {transaction.property_address}")
    logger.info(f"  Current stage: {transaction.current_stage.value}")
    logger.info(f"  Progress: {progress['percent_complete']}%")

    return {
        "transaction": transaction.to_dict(),
        "progress": progress,
        "timeline": {
            "days_in_current_stage": days_in_stage,
            "estimated_days_to_close": days_to_close,
            "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
            "estimated_closing_date": transaction.estimated_closing_date.isoformat() if transaction.estimated_closing_date else None
        },
        "tasks": [task.to_dict() for task in tasks],
        "task_summary": {
            "total": len(tasks),
            "completed": len([t for t in tasks if t.status.value == "completed"]),
            "blocking": len([t for t in tasks if t.is_blocking and t.status.value != "completed"])
        }
    }


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/transactions/{transaction_id}/deposit-earnest-money", response_model=dict)
async def deposit_earnest_money(
    transaction_id: str,
    deposit: EarnestMoneyDeposit,
    db: Session = Depends(get_db)
):
    """
    Record earnest money deposit.

    Updates transaction status and logs the deposit in stage history.

    **Workflow Impact**: This may unblock stage advancement if earnest money
    deposit was required.

    **Logging**: Creates detailed audit log of deposit.
    """
    logger.info("=" * 60)
    logger.info(f"EARNEST MONEY DEPOSIT - {transaction_id}")
    logger.info("=" * 60)

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    deposited_at = deposit.deposited_at or datetime.utcnow()

    logger.info(f"Amount: ${deposit.amount:,.2f}")
    logger.info(f"Deposited at: {deposited_at}")

    # Update transaction
    transaction.earnest_money_status = EarnestMoneyStatus.DEPOSITED
    transaction.earnest_money_deposited_at = deposited_at

    # Log in stage history
    if transaction.stage_history is None:
        transaction.stage_history = []

    transaction.stage_history.append({
        "event": "earnest_money_deposited",
        "timestamp": datetime.utcnow().isoformat(),
        "amount": deposit.amount,
        "notes": deposit.notes or ""
    })

    db.commit()
    db.refresh(transaction)

    logger.info("✓ Earnest money deposit recorded")
    logger.info("=" * 60)

    return {
        "success": True,
        "message": "Earnest money deposit recorded",
        "transaction_id": transaction_id,
        "status": transaction.earnest_money_status.value,
        "deposited_at": deposited_at.isoformat()
    }


@router.post("/transactions/{transaction_id}/verify-funds", response_model=dict)
async def verify_funds(
    transaction_id: str,
    verification: FundsVerification,
    db: Session = Depends(get_db)
):
    """
    Mark buyer funds as verified.

    This is typically done after reviewing bank statements or pre-approval letters.

    **Workflow Impact**: Unblocks stage advancement that requires funds verification.

    **Logging**: Records who verified, when, and how.
    """
    logger.info("=" * 60)
    logger.info(f"FUNDS VERIFICATION - {transaction_id}")
    logger.info("=" * 60)

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    logger.info(f"Verified by: {verification.verified_by}")
    logger.info(f"Method: {verification.verification_method or 'Not specified'}")

    # Update transaction
    transaction.funds_verified = True
    transaction.funds_verified_at = datetime.utcnow()
    transaction.funds_verified_by = verification.verified_by

    # Log in stage history
    if transaction.stage_history is None:
        transaction.stage_history = []

    transaction.stage_history.append({
        "event": "funds_verified",
        "timestamp": datetime.utcnow().isoformat(),
        "verified_by": verification.verified_by,
        "method": verification.verification_method,
        "notes": verification.notes or ""
    })

    db.commit()
    db.refresh(transaction)

    logger.info("✓ Funds verified successfully")
    logger.info("=" * 60)

    return {
        "success": True,
        "message": "Funds verified successfully",
        "transaction_id": transaction_id,
        "verified_at": transaction.funds_verified_at.isoformat(),
        "verified_by": verification.verified_by
    }


@router.post("/transactions/{transaction_id}/advance-stage", response_model=dict)
async def advance_transaction_stage(
    transaction_id: str,
    advancement: StageAdvancement,
    db: Session = Depends(get_db)
):
    """
    Advance transaction to the next stage.

    This is the key workflow operation that moves a transaction through the
    7-stage closing process.

    **Process:**
    1. Validates all requirements are met (unless force=True)
    2. Advances to next stage
    3. Logs stage transition in history
    4. Generates tasks for new stage
    5. Updates timeline estimates

    **Logging**: Comprehensive logging of entire advancement process.
    """
    logger.info("=" * 60)
    logger.info(f"ADVANCING STAGE - {transaction_id}")
    logger.info("=" * 60)

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    state_machine = TransactionStateMachine(db)

    current_stage = transaction.current_stage
    logger.info(f"Current stage: {current_stage.value}")

    # Check if can advance
    if not advancement.force:
        can_advance, reason = state_machine.can_advance_to_next_stage(transaction)
        if not can_advance:
            logger.warning(f"Cannot advance: {reason}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot advance stage: {reason}"
            )

    # Advance stage
    try:
        transaction = state_machine.advance_stage(
            transaction,
            notes=advancement.notes,
            force=advancement.force
        )

        logger.info(f"✓ Advanced to: {transaction.current_stage.value}")
        logger.info(f"  New tasks generated for stage")
        logger.info(f"  Updated estimated close date: {transaction.estimated_closing_date}")
        logger.info("=" * 60)

        return {
            "success": True,
            "message": f"Advanced from {current_stage.value} to {transaction.current_stage.value}",
            "transaction_id": transaction_id,
            "previous_stage": current_stage.value,
            "current_stage": transaction.current_stage.value,
            "stage_history": transaction.stage_history,
            "estimated_closing_date": transaction.estimated_closing_date.isoformat() if transaction.estimated_closing_date else None
        }

    except (StageRequirementError, StageTransitionError) as e:
        logger.error(f"✗ Stage advancement failed: {str(e)}")
        logger.info("=" * 60)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/transactions/{transaction_id}/progress", response_model=dict)
async def get_transaction_progress(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed progress information for a transaction.

    Returns stage-by-stage progress with completion timestamps.

    **Use Case**: Display timeline visualization in dashboard.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    state_machine = TransactionStateMachine(db)
    progress = state_machine.get_stage_progress(transaction)

    logger.info(f"Progress for {transaction_id}: {progress['percent_complete']}% complete")

    return progress
