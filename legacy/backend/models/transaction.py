"""
Transaction Model

Represents a single real estate closing transaction from offer acceptance to recording.
This is the central model that ties together all parties, documents, and tasks.

Business Context:
- A transaction represents one property sale
- Tracks financial details (purchase price, down payment, loan amount)
- Manages the current stage in the 7-stage closing workflow
- Records earnest money and funds verification status
- Maintains timeline information (start date, estimated close, actual close)
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database import Base


class TransactionStage(enum.Enum):
    """
    The 7 stages of a real estate closing transaction.

    Each stage represents a major milestone in the closing process:
    1. OFFER_ACCEPTED - Buyer's offer accepted, escrow opened
    2. TITLE_SEARCH - Title company researching property ownership/liens
    3. UNDERWRITING - Lender reviewing loan application, inspections happening
    4. CLEAR_TO_CLOSE - All conditions met, ready to prepare final documents
    5. FINAL_DOCUMENTS - Closing disclosure and final paperwork prepared
    6. FUNDING_SIGNING - Buyer signs documents, funds wired
    7. RECORDING_COMPLETE - Deed recorded with county, transaction complete

    Traditional timeline: 30-45 days total
    Platform timeline: 7-14 days total (60-70% faster)
    """
    OFFER_ACCEPTED = "offer_accepted"
    TITLE_SEARCH = "title_search_ordered"
    UNDERWRITING = "lender_underwriting"
    CLEAR_TO_CLOSE = "clear_to_close"
    FINAL_DOCUMENTS = "final_documents_prepared"
    FUNDING_SIGNING = "funding_and_signing"
    RECORDING_COMPLETE = "recording_complete"


class EarnestMoneyStatus(enum.Enum):
    """
    Status of earnest money deposit (good faith deposit from buyer).

    Earnest money is typically 1-2% of purchase price, held in escrow
    to show buyer's commitment to the transaction.
    """
    PENDING = "pending"           # Not yet deposited
    DEPOSITED = "deposited"       # Deposited but not cleared
    CLEARED = "cleared"           # Funds cleared and verified
    REFUNDED = "refunded"         # Returned to buyer (deal fell through)
    APPLIED = "applied"           # Applied to down payment at closing


class Transaction(Base):
    """
    Main transaction table representing a real estate closing.

    This model stores all core information about a property sale and tracks
    its progress through the closing workflow.
    """
    __tablename__ = "transactions"

    # ============================================================================
    # PRIMARY KEY
    # ============================================================================

    id = Column(String, primary_key=True, index=True)  # e.g., "TXN-2024-001"

    # ============================================================================
    # PROPERTY INFORMATION
    # ============================================================================

    property_address = Column(String, nullable=False)  # "123 Maple St, Springfield, IL 62701"
    property_type = Column(String)                     # "single_family", "condo", "townhouse"
    property_sqft = Column(Integer)                    # Square footage
    property_bedrooms = Column(Integer)                # Number of bedrooms
    property_bathrooms = Column(Float)                 # Number of bathrooms (e.g., 2.5)
    property_year_built = Column(Integer)              # Year constructed

    # ============================================================================
    # FINANCIAL DETAILS
    # ============================================================================

    purchase_price = Column(Float, nullable=False)     # Total sale price
    down_payment = Column(Float)                       # Buyer's down payment amount
    loan_amount = Column(Float)                        # Mortgage loan amount

    # Earnest money tracking (workflow-enabled)
    earnest_money_amount = Column(Float)               # Good faith deposit amount
    earnest_money_status = Column(
        SQLEnum(EarnestMoneyStatus),
        default=EarnestMoneyStatus.PENDING
    )
    earnest_money_deposited_at = Column(DateTime)      # When funds were deposited
    earnest_money_cleared_at = Column(DateTime)        # When funds cleared escrow

    # Funds verification tracking (workflow-enabled)
    funds_verified = Column(Boolean, default=False)    # Has buyer's full funds been verified?
    funds_verified_at = Column(DateTime)               # When verification completed
    funds_verified_by = Column(String)                 # Who verified (user_id or "system")

    # ============================================================================
    # WORKFLOW STATE MANAGEMENT
    # ============================================================================

    current_stage = Column(
        SQLEnum(TransactionStage),
        default=TransactionStage.OFFER_ACCEPTED,
        nullable=False
    )

    # Stage history - JSON array tracking all stage transitions
    # Format: [
    #   {"stage": "offer_accepted", "entered_at": "2024-10-25T10:00:00", "notes": "..."},
    #   {"stage": "title_search_ordered", "entered_at": "2024-10-26T14:30:00", "notes": "..."}
    # ]
    # This provides full audit trail of transaction progress
    stage_history = Column(JSON, default=list)

    stage_started_at = Column(DateTime)                # When current stage began

    # ============================================================================
    # TIMELINE TRACKING
    # ============================================================================

    created_at = Column(DateTime, default=datetime.utcnow)  # Transaction created
    estimated_closing_date = Column(DateTime)               # Target close date
    actual_closing_date = Column(DateTime)                  # When actually closed

    # Days to close (calculated field we can add via property)
    # Traditional: 30-45 days
    # Our platform: 7-14 days

    # ============================================================================
    # PARTY REFERENCES (Foreign Keys to Party table)
    # ============================================================================

    buyer_id = Column(String, index=True)              # Reference to Party.id
    seller_id = Column(String, index=True)             # Reference to Party.id
    buyer_agent_id = Column(String, index=True)        # Reference to Party.id
    seller_agent_id = Column(String, index=True)       # Reference to Party.id
    loan_officer_id = Column(String, index=True)       # Reference to Party.id
    title_officer_id = Column(String, index=True)      # Reference to Party.id

    # ============================================================================
    # ADDITIONAL METADATA
    # ============================================================================

    notes = Column(String)                             # Internal notes
    priority = Column(String, default="normal")        # "low", "normal", "high", "urgent"

    # ============================================================================
    # RELATIONSHIPS (defined but not enforced as foreign keys for flexibility)
    # ============================================================================
    # These allow easy access: transaction.documents, transaction.tasks, etc.
    # We'll define these after creating Document and Task models

    # documents = relationship("Document", back_populates="transaction")
    # tasks = relationship("Task", back_populates="transaction")

    def __repr__(self):
        """String representation for debugging"""
        return f"<Transaction {self.id} - {self.property_address} - Stage: {self.current_stage.value}>"

    def to_dict(self):
        """
        Convert transaction to dictionary for API responses.
        This makes it easy to return JSON from API endpoints.
        """
        return {
            "id": self.id,
            "property_address": self.property_address,
            "property_type": self.property_type,
            "purchase_price": self.purchase_price,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "stage_history": self.stage_history,
            "earnest_money_status": self.earnest_money_status.value if self.earnest_money_status else None,
            "funds_verified": self.funds_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "estimated_closing_date": self.estimated_closing_date.isoformat() if self.estimated_closing_date else None,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
        }
