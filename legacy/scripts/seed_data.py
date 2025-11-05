"""
Seed Data Generator

Creates comprehensive demo data for the Real Estate Closing Platform.
This generates:
- 15+ parties (buyers, sellers, agents, lenders, title officers)
- 6 transactions at different stages showcasing various scenarios
- Realistic tasks, documents, and history for each transaction

Demo Scenarios:
1. Fast Track - Transaction almost complete (day 11 of 13)
2. Smooth Progress - Transaction at underwriting (day 5 of 13)
3. Just Started - New transaction (day 1)
4. Delayed - Transaction with issues (overdue tasks)
5. Recently Completed - Finished transaction (for success metrics)
6. Stalled - Transaction stuck at title search with issues
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend.models import (
    Transaction, TransactionStage, EarnestMoneyStatus,
    Party, PartyRole,
    Task, TaskType, TaskStatus, TaskPriority
)

# Color codes for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_section(title):
    """Print formatted section header."""
    print(f"\n{BLUE}{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}{RESET}")

def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")

def print_info(message):
    """Print info message."""
    print(f"  {message}")


def create_parties(db):
    """Create diverse set of parties for demo."""
    print_section("Creating Parties")

    parties_data = [
        # Buyers
        {"name": "Sarah Johnson", "email": "sarah.j@email.com", "phone": "555-0101",
         "role": PartyRole.BUYER, "city": "Chicago", "state": "IL"},
        {"name": "Michael Chen", "email": "m.chen@email.com", "phone": "555-0102",
         "role": PartyRole.BUYER, "city": "Springfield", "state": "IL"},
        {"name": "Emily Rodriguez", "email": "emily.r@email.com", "phone": "555-0103",
         "role": PartyRole.BUYER, "city": "Naperville", "state": "IL"},
        {"name": "David Thompson", "email": "d.thompson@email.com", "phone": "555-0104",
         "role": PartyRole.BUYER, "city": "Evanston", "state": "IL"},
        {"name": "Jessica Martinez", "email": "j.martinez@email.com", "phone": "555-0105",
         "role": PartyRole.BUYER, "city": "Oak Park", "state": "IL"},
        {"name": "Robert Kim", "email": "robert.kim@email.com", "phone": "555-0106",
         "role": PartyRole.BUYER, "city": "Schaumburg", "state": "IL"},

        # Sellers
        {"name": "Patricia Williams", "email": "p.williams@email.com", "phone": "555-0201",
         "role": PartyRole.SELLER, "city": "Chicago", "state": "IL"},
        {"name": "James Anderson", "email": "j.anderson@email.com", "phone": "555-0202",
         "role": PartyRole.SELLER, "city": "Springfield", "state": "IL"},
        {"name": "Linda Garcia", "email": "l.garcia@email.com", "phone": "555-0203",
         "role": PartyRole.SELLER, "city": "Naperville", "state": "IL"},
        {"name": "Christopher Lee", "email": "c.lee@email.com", "phone": "555-0204",
         "role": PartyRole.SELLER, "city": "Evanston", "state": "IL"},
        {"name": "Maria Santos", "email": "m.santos@email.com", "phone": "555-0205",
         "role": PartyRole.SELLER, "city": "Oak Park", "state": "IL"},
        {"name": "Thomas Brown", "email": "t.brown@email.com", "phone": "555-0206",
         "role": PartyRole.SELLER, "city": "Schaumburg", "state": "IL"},

        # Buyer Agents
        {"name": "Amanda Foster", "email": "amanda@premierrealty.com", "phone": "555-0301",
         "role": PartyRole.BUYER_AGENT, "company": "Premier Realty Group"},
        {"name": "Kevin Walsh", "email": "kevin@modernhomes.com", "phone": "555-0302",
         "role": PartyRole.BUYER_AGENT, "company": "Modern Homes Realty"},
        {"name": "Rachel Green", "email": "rachel@eliterealty.com", "phone": "555-0303",
         "role": PartyRole.BUYER_AGENT, "company": "Elite Realty Partners"},

        # Seller Agents
        {"name": "Daniel Cooper", "email": "daniel@luxuryproperties.com", "phone": "555-0401",
         "role": PartyRole.SELLER_AGENT, "company": "Luxury Properties LLC"},
        {"name": "Nicole Morgan", "email": "nicole@keystonerealty.com", "phone": "555-0402",
         "role": PartyRole.SELLER_AGENT, "company": "Keystone Realty"},

        # Title Officers
        {"name": "Steven Miller", "email": "steven@abctitle.com", "phone": "555-0501",
         "role": PartyRole.TITLE_OFFICER, "company": "ABC Title Company"},
        {"name": "Jennifer Taylor", "email": "jennifer@securetitle.com", "phone": "555-0502",
         "role": PartyRole.TITLE_OFFICER, "company": "Secure Title Services"},

        # Loan Officers
        {"name": "Brian Patterson", "email": "brian@firstnational.com", "phone": "555-0601",
         "role": PartyRole.LOAN_OFFICER, "company": "First National Bank"},
        {"name": "Michelle Rivera", "email": "michelle@unitybank.com", "phone": "555-0602",
         "role": PartyRole.LOAN_OFFICER, "company": "Unity Bank & Trust"},
        {"name": "Andrew Collins", "email": "andrew@homemortgage.com", "phone": "555-0603",
         "role": PartyRole.LOAN_OFFICER, "company": "Home Mortgage Solutions"},
    ]

    parties = {}
    for idx, party_data in enumerate(parties_data, 1):
        party = Party(
            id=f"PARTY-2025-{idx:04d}",
            name=party_data["name"],
            email=party_data["email"],
            phone=party_data["phone"],
            role=party_data["role"],
            company=party_data.get("company"),
            city=party_data.get("city"),
            state=party_data.get("state"),
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 180))
        )
        db.add(party)
        parties[party_data["role"].value] = parties.get(party_data["role"].value, [])
        parties[party_data["role"].value].append(party)

    db.commit()
    print_success(f"Created {len(parties_data)} parties")
    for role, party_list in parties.items():
        print_info(f"  {role}: {len(party_list)} parties")

    return parties


def create_transaction_scenario(db, scenario_name, scenario_data, parties):
    """Create a transaction for a specific demo scenario."""
    print(f"\n{YELLOW}--- Scenario: {scenario_name} ---{RESET}")

    # Select random parties for this transaction
    buyer = random.choice(parties["buyer"])
    seller = random.choice(parties["seller"])
    buyer_agent = random.choice(parties["buyer_agent"])
    seller_agent = random.choice(parties["seller_agent"]) if "seller_agent" in parties else None
    title_officer = random.choice(parties["title_officer"])
    loan_officer = random.choice(parties["loan_officer"])

    # Create transaction
    txn = Transaction(
        id=scenario_data["id"],
        property_address=scenario_data["address"],
        property_type=scenario_data["property_type"],
        property_sqft=scenario_data["sqft"],
        property_bedrooms=scenario_data["bedrooms"],
        property_bathrooms=scenario_data["bathrooms"],
        property_year_built=scenario_data["year_built"],
        purchase_price=scenario_data["price"],
        down_payment=scenario_data["price"] * 0.20,
        loan_amount=scenario_data["price"] * 0.80,
        earnest_money_amount=scenario_data["price"] * 0.02,
        earnest_money_status=scenario_data["earnest_money_status"],
        earnest_money_deposited_at=scenario_data.get("earnest_money_date"),
        funds_verified=scenario_data["funds_verified"],
        funds_verified_at=scenario_data.get("funds_verified_date"),
        funds_verified_by="system" if scenario_data["funds_verified"] else None,
        current_stage=scenario_data["current_stage"],
        stage_started_at=scenario_data["stage_started_at"],
        created_at=scenario_data["created_at"],
        estimated_closing_date=scenario_data["estimated_close"],
        actual_closing_date=scenario_data.get("actual_close"),
        buyer_id=buyer.id,
        seller_id=seller.id,
        buyer_agent_id=buyer_agent.id,
        seller_agent_id=seller_agent.id if seller_agent else None,
        title_officer_id=title_officer.id,
        loan_officer_id=loan_officer.id,
        stage_history=scenario_data["stage_history"],
        priority=scenario_data.get("priority", "normal")
    )

    db.add(txn)
    db.commit()

    print_success(f"Transaction: {txn.id}")
    print_info(f"  Property: {txn.property_address}")
    print_info(f"  Price: ${txn.purchase_price:,.0f}")
    print_info(f"  Stage: {txn.current_stage.value}")
    print_info(f"  Days since created: {(datetime.utcnow() - txn.created_at).days}")

    # Create tasks for this transaction
    create_tasks_for_scenario(db, txn, scenario_data)

    return txn


def create_tasks_for_scenario(db, transaction, scenario_data):
    """Create tasks appropriate for the transaction's current stage."""
    task_templates = scenario_data.get("tasks", [])

    for idx, task_template in enumerate(task_templates, 1):
        task = Task(
            id=f"TASK-{transaction.id[-4:]}-{idx:03d}",
            transaction_id=transaction.id,
            title=task_template["title"],
            description=task_template.get("description", ""),
            task_type=task_template["type"],
            assigned_to=task_template.get("assigned_to"),
            assigned_by="system",
            assigned_at=transaction.created_at,
            status=task_template["status"],
            priority=task_template.get("priority", TaskPriority.NORMAL),
            due_date=task_template.get("due_date"),
            completed_at=task_template.get("completed_at"),
            is_blocking=task_template.get("is_blocking", False),
            related_stage=task_template.get("related_stage"),
            created_at=transaction.created_at
        )
        db.add(task)

    db.commit()
    print_info(f"  Created {len(task_templates)} tasks")


def generate_seed_data(db):
    """Generate all seed data."""
    print_section("SEED DATA GENERATION")
    print("Generating comprehensive demo data for Streamlit dashboard\n")

    # Clear existing data
    print_info("Clearing existing data...")
    db.query(Task).delete()
    db.query(Transaction).delete()
    db.query(Party).delete()
    db.commit()
    print_success("Database cleared")

    # Create parties
    parties = create_parties(db)

    print_section("Creating Transaction Scenarios")

    # Scenario 1: Fast Track - Almost Complete (Day 11 of 13)
    now = datetime.utcnow()
    create_transaction_scenario(db, "Fast Track - Almost Complete", {
        "id": "TXN-2025-1001",
        "address": "456 Oak Avenue, Naperville, IL 60540",
        "property_type": "single_family",
        "sqft": 2400,
        "bedrooms": 4,
        "bathrooms": 3.0,
        "year_built": 2018,
        "price": 625000,
        "earnest_money_status": EarnestMoneyStatus.CLEARED,
        "earnest_money_date": now - timedelta(days=10),
        "funds_verified": True,
        "funds_verified_date": now - timedelta(days=9),
        "current_stage": TransactionStage.FUNDING_SIGNING,
        "stage_started_at": now - timedelta(days=1),
        "created_at": now - timedelta(days=11),
        "estimated_close": now + timedelta(days=2),
        "stage_history": [
            {"stage": "offer_accepted", "entered_at": (now - timedelta(days=11)).isoformat(), "notes": "Offer accepted, escrow opened"},
            {"stage": "title_search_ordered", "entered_at": (now - timedelta(days=10)).isoformat(), "notes": "Clean title"},
            {"stage": "lender_underwriting", "entered_at": (now - timedelta(days=8)).isoformat(), "notes": "Approved"},
            {"stage": "clear_to_close", "entered_at": (now - timedelta(days=4)).isoformat(), "notes": "All conditions met"},
            {"stage": "final_documents_prepared", "entered_at": (now - timedelta(days=2)).isoformat(), "notes": "Documents ready"},
            {"stage": "funding_and_signing", "entered_at": (now - timedelta(days=1)).isoformat(), "notes": "Signing scheduled"},
            {"event": "earnest_money_deposited", "timestamp": (now - timedelta(days=10)).isoformat(), "amount": 12500},
            {"event": "funds_verified", "timestamp": (now - timedelta(days=9)).isoformat(), "verified_by": "system"},
        ],
        "priority": "high",
        "tasks": [
            {"title": "Wire down payment", "type": TaskType.PAYMENT, "status": TaskStatus.IN_PROGRESS,
             "priority": TaskPriority.CRITICAL, "is_blocking": True, "related_stage": "funding_and_signing",
             "due_date": now + timedelta(days=1)},
            {"title": "Sign closing documents", "type": TaskType.DOCUMENT_SIGN, "status": TaskStatus.PENDING,
             "priority": TaskPriority.CRITICAL, "is_blocking": True, "related_stage": "funding_and_signing",
             "due_date": now + timedelta(days=1)},
        ]
    }, parties)

    # Scenario 2: Smooth Progress - At Underwriting (Day 5 of 13)
    create_transaction_scenario(db, "Smooth Progress - Underwriting", {
        "id": "TXN-2025-1002",
        "address": "789 Elm Street, Evanston, IL 60201",
        "property_type": "condo",
        "sqft": 1650,
        "bedrooms": 2,
        "bathrooms": 2.0,
        "year_built": 2020,
        "price": 485000,
        "earnest_money_status": EarnestMoneyStatus.CLEARED,
        "earnest_money_date": now - timedelta(days=4),
        "funds_verified": True,
        "funds_verified_date": now - timedelta(days=3),
        "current_stage": TransactionStage.UNDERWRITING,
        "stage_started_at": now - timedelta(days=2),
        "created_at": now - timedelta(days=5),
        "estimated_close": now + timedelta(days=8),
        "stage_history": [
            {"stage": "offer_accepted", "entered_at": (now - timedelta(days=5)).isoformat(), "notes": "Strong offer"},
            {"stage": "title_search_ordered", "entered_at": (now - timedelta(days=4)).isoformat(), "notes": "Title search initiated"},
            {"stage": "lender_underwriting", "entered_at": (now - timedelta(days=2)).isoformat(), "notes": "Under review"},
            {"event": "earnest_money_deposited", "timestamp": (now - timedelta(days=4)).isoformat(), "amount": 9700},
            {"event": "funds_verified", "timestamp": (now - timedelta(days=3)).isoformat(), "verified_by": "system"},
        ],
        "tasks": [
            {"title": "Submit loan application", "type": TaskType.OTHER, "status": TaskStatus.COMPLETED,
             "completed_at": now - timedelta(days=2), "related_stage": "lender_underwriting"},
            {"title": "Order appraisal", "type": TaskType.OTHER, "status": TaskStatus.COMPLETED,
             "completed_at": now - timedelta(days=1), "related_stage": "lender_underwriting"},
            {"title": "Verify employment", "type": TaskType.VERIFICATION, "status": TaskStatus.IN_PROGRESS,
             "priority": TaskPriority.HIGH, "is_blocking": True, "related_stage": "lender_underwriting",
             "due_date": now + timedelta(days=2)},
        ]
    }, parties)

    # Scenario 3: Just Started - Day 1
    create_transaction_scenario(db, "Just Started - Fresh Transaction", {
        "id": "TXN-2025-1003",
        "address": "321 Maple Drive, Oak Park, IL 60302",
        "property_type": "single_family",
        "sqft": 1850,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "year_built": 2015,
        "price": 450000,
        "earnest_money_status": EarnestMoneyStatus.PENDING,
        "funds_verified": False,
        "current_stage": TransactionStage.OFFER_ACCEPTED,
        "stage_started_at": now - timedelta(hours=6),
        "created_at": now - timedelta(hours=6),
        "estimated_close": now + timedelta(days=13),
        "stage_history": [
            {"stage": "offer_accepted", "entered_at": (now - timedelta(hours=6)).isoformat(), "notes": "Just created"},
        ],
        "tasks": [
            {"title": "Deposit earnest money", "type": TaskType.PAYMENT, "status": TaskStatus.PENDING,
             "priority": TaskPriority.CRITICAL, "is_blocking": True, "related_stage": "offer_accepted",
             "due_date": now + timedelta(days=1)},
            {"title": "Upload proof of funds", "type": TaskType.DOCUMENT_UPLOAD, "status": TaskStatus.PENDING,
             "priority": TaskPriority.HIGH, "is_blocking": True, "related_stage": "offer_accepted",
             "due_date": now + timedelta(days=2)},
            {"title": "Open escrow account", "type": TaskType.OTHER, "status": TaskStatus.PENDING,
             "priority": TaskPriority.HIGH, "is_blocking": True, "related_stage": "offer_accepted",
             "due_date": now + timedelta(days=1)},
        ]
    }, parties)

    # Scenario 4: Delayed - Overdue Tasks (Day 8, should be at Day 5 stage)
    create_transaction_scenario(db, "Delayed - Has Issues", {
        "id": "TXN-2025-1004",
        "address": "555 Pine Lane, Schaumburg, IL 60173",
        "property_type": "townhouse",
        "sqft": 1950,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "year_built": 2017,
        "price": 395000,
        "earnest_money_status": EarnestMoneyStatus.CLEARED,
        "earnest_money_date": now - timedelta(days=7),
        "funds_verified": False,
        "current_stage": TransactionStage.TITLE_SEARCH,
        "stage_started_at": now - timedelta(days=6),
        "created_at": now - timedelta(days=8),
        "estimated_close": now + timedelta(days=10),  # Extended timeline
        "stage_history": [
            {"stage": "offer_accepted", "entered_at": (now - timedelta(days=8)).isoformat(), "notes": "Initial stage"},
            {"stage": "title_search_ordered", "entered_at": (now - timedelta(days=6)).isoformat(), "notes": "Found title issues"},
            {"event": "earnest_money_deposited", "timestamp": (now - timedelta(days=7)).isoformat(), "amount": 7900},
        ],
        "priority": "urgent",
        "tasks": [
            {"title": "Order title search", "type": TaskType.OTHER, "status": TaskStatus.COMPLETED,
             "completed_at": now - timedelta(days=6), "related_stage": "title_search_ordered"},
            {"title": "Resolve title lien", "type": TaskType.OTHER, "status": TaskStatus.IN_PROGRESS,
             "priority": TaskPriority.CRITICAL, "is_blocking": True, "related_stage": "title_search_ordered",
             "due_date": now - timedelta(days=2)},  # OVERDUE!
            {"title": "Upload proof of funds", "type": TaskType.DOCUMENT_UPLOAD, "status": TaskStatus.PENDING,
             "priority": TaskPriority.HIGH, "is_blocking": True, "related_stage": "offer_accepted",
             "due_date": now - timedelta(days=4)},  # OVERDUE!
        ]
    }, parties)

    # Scenario 5: Recently Completed (3 days ago)
    create_transaction_scenario(db, "Recently Completed - Success!", {
        "id": "TXN-2025-1005",
        "address": "888 Cedar Court, Chicago, IL 60614",
        "property_type": "single_family",
        "sqft": 2800,
        "bedrooms": 4,
        "bathrooms": 3.5,
        "year_built": 2019,
        "price": 775000,
        "earnest_money_status": EarnestMoneyStatus.APPLIED,
        "earnest_money_date": now - timedelta(days=15),
        "funds_verified": True,
        "funds_verified_date": now - timedelta(days=14),
        "current_stage": TransactionStage.RECORDING_COMPLETE,
        "stage_started_at": now - timedelta(days=3),
        "created_at": now - timedelta(days=16),
        "estimated_close": now - timedelta(days=3),
        "actual_close": now - timedelta(days=3),
        "stage_history": [
            {"stage": "offer_accepted", "entered_at": (now - timedelta(days=16)).isoformat(), "notes": "Competitive offer"},
            {"stage": "title_search_ordered", "entered_at": (now - timedelta(days=15)).isoformat(), "notes": "Clean title"},
            {"stage": "lender_underwriting", "entered_at": (now - timedelta(days=13)).isoformat(), "notes": "Fast approval"},
            {"stage": "clear_to_close", "entered_at": (now - timedelta(days=9)).isoformat(), "notes": "No issues"},
            {"stage": "final_documents_prepared", "entered_at": (now - timedelta(days=7)).isoformat(), "notes": "All docs ready"},
            {"stage": "funding_and_signing", "entered_at": (now - timedelta(days=5)).isoformat(), "notes": "Signed"},
            {"stage": "recording_complete", "entered_at": (now - timedelta(days=3)).isoformat(), "notes": "Successfully recorded!"},
            {"event": "earnest_money_deposited", "timestamp": (now - timedelta(days=15)).isoformat(), "amount": 15500},
            {"event": "funds_verified", "timestamp": (now - timedelta(days=14)).isoformat(), "verified_by": "system"},
        ],
        "tasks": [
            {"title": "Record deed", "type": TaskType.OTHER, "status": TaskStatus.COMPLETED,
             "completed_at": now - timedelta(days=3), "related_stage": "recording_complete"},
            {"title": "Disburse funds", "type": TaskType.PAYMENT, "status": TaskStatus.COMPLETED,
             "completed_at": now - timedelta(days=3), "related_stage": "recording_complete"},
        ]
    }, parties)

    # Scenario 6: High-Value Property - At Clear to Close
    create_transaction_scenario(db, "High-Value - Clear to Close", {
        "id": "TXN-2025-1006",
        "address": "1234 Lakeshore Drive, Chicago, IL 60611",
        "property_type": "single_family",
        "sqft": 3500,
        "bedrooms": 5,
        "bathrooms": 4.5,
        "year_built": 2021,
        "price": 1250000,
        "earnest_money_status": EarnestMoneyStatus.CLEARED,
        "earnest_money_date": now - timedelta(days=9),
        "funds_verified": True,
        "funds_verified_date": now - timedelta(days=8),
        "current_stage": TransactionStage.CLEAR_TO_CLOSE,
        "stage_started_at": now - timedelta(days=2),
        "created_at": now - timedelta(days=10),
        "estimated_close": now + timedelta(days=4),
        "stage_history": [
            {"stage": "offer_accepted", "entered_at": (now - timedelta(days=10)).isoformat(), "notes": "Premium property"},
            {"stage": "title_search_ordered", "entered_at": (now - timedelta(days=9)).isoformat(), "notes": "Title clear"},
            {"stage": "lender_underwriting", "entered_at": (now - timedelta(days=7)).isoformat(), "notes": "Jumbo loan approved"},
            {"stage": "clear_to_close", "entered_at": (now - timedelta(days=2)).isoformat(), "notes": "Final approval received"},
            {"event": "earnest_money_deposited", "timestamp": (now - timedelta(days=9)).isoformat(), "amount": 25000},
            {"event": "funds_verified", "timestamp": (now - timedelta(days=8)).isoformat(), "verified_by": "system"},
        ],
        "priority": "high",
        "tasks": [
            {"title": "Obtain clear to close", "type": TaskType.APPROVAL, "status": TaskStatus.COMPLETED,
             "completed_at": now - timedelta(days=2), "related_stage": "clear_to_close"},
            {"title": "Upload insurance policy", "type": TaskType.DOCUMENT_UPLOAD, "status": TaskStatus.COMPLETED,
             "completed_at": now - timedelta(days=1), "related_stage": "clear_to_close"},
        ]
    }, parties)

    db.commit()

    print_section("Seed Data Generation Complete")
    print_success("Created 6 transaction scenarios")
    print_success("Transactions span all 7 stages")
    print_success("Includes completed, in-progress, and delayed scenarios")
    print_info("\nScenarios created:")
    print_info("  1. Fast Track (Day 11) - Almost done")
    print_info("  2. Smooth Progress (Day 5) - On track")
    print_info("  3. Just Started (Day 1) - New")
    print_info("  4. Delayed (Day 8) - Has issues")
    print_info("  5. Recently Completed - Success story")
    print_info("  6. High-Value - Clear to close")
    print()


def main():
    """Run seed data generation."""
    print("\n" + "=" * 70)
    print("  SEED DATA GENERATOR - Real Estate Closing Platform")
    print("=" * 70)
    print("\nThis will populate the database with demo data for Streamlit.\n")

    db = SessionLocal()

    try:
        generate_seed_data(db)

        print_section("Next Steps")
        print_success("Seed data ready!")
        print_info("Start the API server:")
        print_info("  uvicorn backend.main:app --reload --port 8000")
        print_info("\nView the data:")
        print_info("  http://localhost:8000/api/v1/transactions")
        print_info("\nReady to build Streamlit dashboard!")
        print()

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
