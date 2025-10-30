"""
Document Model

Represents uploaded documents in a transaction with validation tracking.
This is where the platform's automation shines - automatic classification,
OCR extraction, and validation of documents.

Business Context:
- Each transaction requires multiple documents (purchase agreement, title report, etc.)
- Documents must be validated before transaction can advance
- OCR extracts key data automatically (purchase price, signatures, dates)
- Validation rules check for completeness, accuracy, and compliance
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Enum as SQLEnum
from datetime import datetime
import enum

from backend.database import Base


class DocumentType(enum.Enum):
    """
    Types of documents required in a real estate closing.

    Each document type has specific validation rules:
    - PURCHASE_AGREEMENT: Contract between buyer and seller
    - TITLE_REPORT: Title search results showing ownership/liens
    - PROOF_OF_FUNDS: Bank statement or pre-approval letter
    - CLOSING_DISCLOSURE: Final settlement statement (HUD-1 equivalent)
    - DEED: Warranty or quitclaim deed transferring ownership
    - INSURANCE: Hazard/homeowners insurance policy
    - INSPECTION: Home inspection report
    - APPRAISAL: Property appraisal report
    - WIRE_RECEIPT: Proof of funds transfer
    - ID_DOCUMENT: Driver's license or passport (identity verification)
    - OTHER: Miscellaneous documents
    """
    PURCHASE_AGREEMENT = "purchase_agreement"
    TITLE_REPORT = "title_report"
    PROOF_OF_FUNDS = "proof_of_funds"
    CLOSING_DISCLOSURE = "closing_disclosure"
    DEED = "deed"
    INSURANCE = "insurance_policy"
    INSPECTION = "inspection_report"
    APPRAISAL = "appraisal_report"
    WIRE_RECEIPT = "wire_receipt"
    ID_DOCUMENT = "id_document"
    OTHER = "other"


class DocumentStatus(enum.Enum):
    """
    Lifecycle status of a document.

    Workflow:
    1. PENDING_UPLOAD - Required but not yet uploaded
    2. UPLOADED - File received, awaiting processing
    3. PROCESSING - OCR extraction and classification in progress
    4. PENDING_REVIEW - Processed, awaiting validation
    5. APPROVED - Passed all validation rules
    6. REJECTED - Failed validation, needs correction
    7. SUPERSEDED - Replaced by a newer version
    """
    PENDING_UPLOAD = "pending_upload"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class Document(Base):
    """
    Document table storing uploaded files and their validation results.

    Key features:
    - Automatic classification using AI (GPT-4V or keyword matching)
    - OCR extraction of key fields
    - Validation against transaction data
    - Audit trail of all changes
    """
    __tablename__ = "documents"

    # ============================================================================
    # PRIMARY KEY
    # ============================================================================

    id = Column(String, primary_key=True, index=True)  # e.g., "DOC-2024-001"

    # ============================================================================
    # DOCUMENT METADATA
    # ============================================================================

    transaction_id = Column(String, nullable=False, index=True)  # Links to Transaction.id
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)

    # ============================================================================
    # FILE INFORMATION
    # ============================================================================

    filename = Column(String, nullable=False)          # Original filename
    file_path = Column(String, nullable=False)         # Storage path on disk/cloud
    file_size = Column(Integer)                        # Size in bytes
    mime_type = Column(String)                         # "application/pdf", "image/jpeg"
    page_count = Column(Integer)                       # Number of pages (for PDFs)

    # ============================================================================
    # UPLOAD TRACKING
    # ============================================================================

    uploaded_by = Column(String)                       # Party.id who uploaded
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # ============================================================================
    # OCR AND EXTRACTION RESULTS
    # ============================================================================

    # Raw OCR text extracted from document
    ocr_text = Column(String)                          # Full text extraction

    # Extracted structured data (JSON)
    # Example for purchase agreement:
    # {
    #   "purchase_price": 450000,
    #   "buyer_name": "John Doe",
    #   "seller_name": "Jane Smith",
    #   "property_address": "123 Maple St",
    #   "closing_date": "2024-11-15",
    #   "signatures": {
    #     "buyer_signed": true,
    #     "seller_signed": true,
    #     "buyer_signature_location": [x, y, page]
    #   }
    # }
    extracted_data = Column(JSON, default=dict)

    # ============================================================================
    # VALIDATION TRACKING
    # ============================================================================

    # Validation performed (have rules been run?)
    validation_performed = Column(Boolean, default=False)
    validation_performed_at = Column(DateTime)

    # Validation results (JSON array of rule checks)
    # Format:
    # [
    #   {
    #     "rule_id": "buyer_signature",
    #     "description": "Buyer signature present",
    #     "passed": true,
    #     "severity": "critical"
    #   },
    #   {
    #     "rule_id": "price_match",
    #     "description": "Purchase price matches transaction",
    #     "passed": false,
    #     "expected": 450000,
    #     "found": 445000,
    #     "severity": "critical"
    #   }
    # ]
    validation_results = Column(JSON, default=list)

    # Overall validation status
    validation_passed = Column(Boolean)                # Did document pass all critical rules?

    # ============================================================================
    # APPROVAL/REJECTION
    # ============================================================================

    approved_by = Column(String)                       # Party.id who approved (or "system")
    approved_at = Column(DateTime)
    rejected_by = Column(String)                       # Party.id who rejected
    rejected_at = Column(DateTime)
    rejection_reason = Column(String)                  # Why document was rejected

    # ============================================================================
    # VERSION CONTROL
    # ============================================================================

    version = Column(Integer, default=1)               # Document version number
    superseded_by = Column(String)                     # Document.id that replaced this one
    replaces = Column(String)                          # Document.id this one replaces

    # ============================================================================
    # METADATA
    # ============================================================================

    notes = Column(String)                             # Internal notes
    tags = Column(JSON, default=list)                  # Searchable tags ["urgent", "missing_info"]

    def __repr__(self):
        """String representation for debugging"""
        return f"<Document {self.id} - {self.document_type.value} - Status: {self.status.value}>"

    def to_dict(self):
        """
        Convert document to dictionary for API responses.
        """
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "document_type": self.document_type.value if self.document_type else None,
            "status": self.status.value if self.status else None,
            "filename": self.filename,
            "file_size": self.file_size,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "validation_passed": self.validation_passed,
            "validation_results": self.validation_results,
            "extracted_data": self.extracted_data,
        }

    def is_valid(self):
        """
        Check if document passed validation.
        Returns True if all critical validation rules passed.
        """
        if not self.validation_performed:
            return False

        # Check if any critical rules failed
        for result in self.validation_results:
            if result.get("severity") == "critical" and not result.get("passed"):
                return False

        return True

    def get_critical_issues(self):
        """
        Returns list of critical validation issues.
        Useful for displaying why a document was rejected.
        """
        issues = []
        for result in self.validation_results:
            if result.get("severity") == "critical" and not result.get("passed"):
                issues.append(result.get("description"))
        return issues
