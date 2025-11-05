"""
Party API Endpoints

Handles operations for parties (people/entities) involved in transactions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from backend.database import get_db
from backend.models import Party, PartyRole

logger = logging.getLogger(__name__)
router = APIRouter()


class PartyCreate(BaseModel):
    """Schema for creating a new party."""
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="Role (buyer, seller, buyer_agent, etc.)")
    company: Optional[str] = Field(None, description="Company name")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="ZIP code")


@router.post("/parties", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_party(
    party_data: PartyCreate,
    db: Session = Depends(get_db)
):
    """Create a new party (person/entity)."""
    logger.info(f"Creating new party: {party_data.name} ({party_data.role})")

    # Generate party ID
    party_count = db.query(Party).count()
    party_id = f"PARTY-{datetime.utcnow().year}-{party_count + 1:04d}"

    # Validate role
    try:
        role_enum = PartyRole(party_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {party_data.role}"
        )

    party = Party(
        id=party_id,
        name=party_data.name,
        email=party_data.email,
        phone=party_data.phone,
        role=role_enum,
        company=party_data.company,
        address=party_data.address,
        city=party_data.city,
        state=party_data.state,
        zip_code=party_data.zip_code,
        created_at=datetime.utcnow()
    )

    db.add(party)
    db.commit()
    db.refresh(party)

    logger.info(f"✓ Party created: {party_id}")

    return {
        "success": True,
        "message": "Party created successfully",
        "party_id": party_id,
        "party": party.to_dict()
    }


@router.get("/parties", response_model=dict)
async def list_parties(
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all parties with optional role filtering."""
    query = db.query(Party)

    if role:
        try:
            role_enum = PartyRole(role)
            query = query.filter(Party.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}"
            )

    parties = query.offset(skip).limit(limit).all()

    return {
        "count": len(parties),
        "parties": [party.to_dict() for party in parties]
    }


@router.get("/parties/{party_id}", response_model=dict)
async def get_party(
    party_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific party."""
    party = db.query(Party).filter(Party.id == party_id).first()

    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Party {party_id} not found"
        )

    return party.to_dict()
