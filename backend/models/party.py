"""
Party Model

Represents any person or entity involved in a real estate transaction.
This includes buyers, sellers, agents, lenders, title officers, etc.

Business Context:
- A single person can have multiple roles (e.g., someone could be both buyer and agent)
- Contact information is critical for notifications and communication
- Role determines what actions they can take and what they see in the system
"""

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from datetime import datetime
import enum

from backend.database import Base


class PartyRole(enum.Enum):
    """
    Roles that parties can have in a transaction.

    Each role has different permissions and responsibilities:
    - BUYER: Person purchasing the property
    - SELLER: Person selling the property
    - BUYER_AGENT: Real estate agent representing buyer
    - SELLER_AGENT: Real estate agent representing seller (listing agent)
    - LOAN_OFFICER: Lender representative handling mortgage
    - TITLE_OFFICER: Title company representative
    - ESCROW_OFFICER: Manages escrow account and funds
    - CLOSING_COORDINATOR: Oversees the entire closing process
    - INSPECTOR: Home/property inspector
    - APPRAISER: Property appraiser
    """
    BUYER = "buyer"
    SELLER = "seller"
    BUYER_AGENT = "buyer_agent"
    SELLER_AGENT = "seller_agent"
    LOAN_OFFICER = "loan_officer"
    TITLE_OFFICER = "title_officer"
    ESCROW_OFFICER = "escrow_officer"
    CLOSING_COORDINATOR = "closing_coordinator"
    INSPECTOR = "inspector"
    APPRAISER = "appraiser"


class Party(Base):
    """
    Party table representing individuals or entities in transactions.

    A Party can participate in multiple transactions over time.
    Contact information enables automated notifications.
    """
    __tablename__ = "parties"

    # ============================================================================
    # PRIMARY KEY
    # ============================================================================

    id = Column(String, primary_key=True, index=True)  # e.g., "PARTY-001"

    # ============================================================================
    # PERSONAL INFORMATION
    # ============================================================================

    name = Column(String, nullable=False)              # "John Doe" or "Jane Smith"
    email = Column(String, nullable=False, index=True) # Primary contact email
    phone = Column(String)                             # Contact phone number

    # ============================================================================
    # ROLE INFORMATION
    # ============================================================================

    # Primary role for this party
    # Note: In production, you might want a many-to-many relationship
    # to allow one person to have multiple roles, but for PoC this is sufficient
    role = Column(SQLEnum(PartyRole), nullable=False)

    # Organization/Company (optional, used for agents, lenders, title companies)
    company = Column(String)                           # "ABC Realty", "First National Bank"
    license_number = Column(String)                    # For agents, brokers (if applicable)

    # ============================================================================
    # ADDRESS (Optional, primarily for buyers/sellers)
    # ============================================================================

    address = Column(String)                           # Current address
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)

    # ============================================================================
    # METADATA
    # ============================================================================

    created_at = Column(DateTime, default=datetime.utcnow)
    last_contacted_at = Column(DateTime)               # Track last communication
    notes = Column(String)                             # Internal notes about this party

    # Notification preferences (for future enhancement)
    # prefer_email = Column(Boolean, default=True)
    # prefer_sms = Column(Boolean, default=False)

    def __repr__(self):
        """String representation for debugging"""
        return f"<Party {self.id} - {self.name} ({self.role.value})>"

    def to_dict(self):
        """
        Convert party to dictionary for API responses.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role.value if self.role else None,
            "company": self.company,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_display_name(self):
        """
        Returns a formatted display name for UI purposes.
        Example: "John Doe (ABC Realty)" or "Jane Smith"
        """
        if self.company:
            return f"{self.name} ({self.company})"
        return self.name
