"""
FastAPI Main Application

This is the entry point for the Real Estate Closing Platform API.
It sets up the FastAPI application, includes all route modules, and configures middleware.

To run the server:
    uvicorn backend.main:app --reload --port 8000

Then visit:
    - http://localhost:8000/docs - Interactive API documentation (Swagger UI)
    - http://localhost:8000/redoc - Alternative API documentation (ReDoc)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging to track API requests and transaction steps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Real Estate Closing Platform API",
    description="""
    Automated real estate closing platform that reduces closing time from 30-45 days to 7-14 days.

    ## Features
    * **Transaction Management** - Create and track real estate transactions
    * **State Machine** - 7-stage workflow with automatic progression
    * **Document Processing** - Upload, validate, and approve documents
    * **Task Management** - Automated task generation and tracking
    * **Workflow APIs** - Earnest money, funds verification, stage transitions

    ## Stages
    1. Offer Accepted
    2. Title Search Ordered
    3. Lender Underwriting
    4. Clear to Close
    5. Final Documents Prepared
    6. Funding & Signing
    7. Recording Complete
    """,
    version="1.0.0",
    contact={
        "name": "Real Estate Closing Platform",
        "email": "support@reclosing.example.com"
    }
)

# Configure CORS (allows frontend to call API from different port/domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run when server starts up."""
    logger.info("=" * 60)
    logger.info("REAL ESTATE CLOSING PLATFORM API STARTING")
    logger.info("=" * 60)
    logger.info("API Documentation available at: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run when server shuts down."""
    logger.info("API shutting down")


@app.get("/")
async def root():
    """
    Root endpoint - API health check.

    Returns basic information about the API.
    """
    return {
        "status": "online",
        "message": "Real Estate Closing Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "transactions": "/api/v1/transactions",
            "parties": "/api/v1/parties",
            "documents": "/api/v1/documents",
            "tasks": "/api/v1/tasks"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Used by monitoring systems to verify API is running.
    """
    return {"status": "healthy"}


# Import and include route modules
# We'll create these next
from backend.api import transactions, parties, tasks

app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(parties.router, prefix="/api/v1", tags=["Parties"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])

logger.info("All routes loaded successfully")
