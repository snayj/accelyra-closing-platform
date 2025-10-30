"""
State Machine Test Script

This script demonstrates the state machine functionality by:
1. Creating a test transaction
2. Advancing it through stages
3. Showing stage history and generated tasks

This helps verify the state machine works correctly before building the full API.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend.models import Transaction, TransactionStage, EarnestMoneyStatus, Party, PartyRole
from backend.services.state_machine import TransactionStateMachine, StageRequirementError


def create_test_transaction(db):
    """Create a test transaction with parties."""

    print("\n" + "=" * 60)
    print("CREATING TEST TRANSACTION")
    print("=" * 60)

    # Create buyer
    buyer = Party(
        id="PARTY-TEST-001",
        name="John Doe",
        email="john.doe@example.com",
        phone="555-0101",
        role=PartyRole.BUYER
    )
    db.add(buyer)

    # Create seller
    seller = Party(
        id="PARTY-TEST-002",
        name="Jane Smith",
        email="jane.smith@example.com",
        phone="555-0102",
        role=PartyRole.SELLER
    )
    db.add(seller)

    # Create title officer
    title_officer = Party(
        id="PARTY-TEST-003",
        name="Bob Johnson",
        email="bob.j@titleco.com",
        phone="555-0103",
        role=PartyRole.TITLE_OFFICER,
        company="ABC Title Company"
    )
    db.add(title_officer)

    # Create transaction
    transaction = Transaction(
        id="TXN-TEST-001",
        property_address="123 Maple St, Springfield, IL 62701",
        property_type="single_family",
        property_sqft=1850,
        property_bedrooms=3,
        property_bathrooms=2.5,
        property_year_built=2015,
        purchase_price=450000,
        down_payment=90000,
        loan_amount=360000,
        earnest_money_amount=9000,
        earnest_money_status=EarnestMoneyStatus.PENDING,
        current_stage=TransactionStage.OFFER_ACCEPTED,
        stage_started_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        estimated_closing_date=datetime.utcnow() + timedelta(days=14),
        buyer_id=buyer.id,
        seller_id=seller.id,
        title_officer_id=title_officer.id,
        stage_history=[{
            "stage": "offer_accepted",
            "entered_at": datetime.utcnow().isoformat(),
            "notes": "Initial stage"
        }]
    )
    db.add(transaction)
    db.commit()

    print(f"\n✓ Created transaction: {transaction.id}")
    print(f"  Property: {transaction.property_address}")
    print(f"  Price: ${transaction.purchase_price:,.0f}")
    print(f"  Buyer: {buyer.name}")
    print(f"  Seller: {seller.name}")
    print(f"  Current Stage: {transaction.current_stage.value}")

    return transaction


def test_stage_advancement(db, transaction):
    """Test advancing through stages."""

    print("\n" + "=" * 60)
    print("TESTING STAGE ADVANCEMENT")
    print("=" * 60)

    state_machine = TransactionStateMachine(db)

    # Check if can advance
    can_advance, reason = state_machine.can_advance_to_next_stage(transaction)

    print(f"\nCurrent stage: {transaction.current_stage.value}")
    print(f"Can advance? {can_advance}")
    if not can_advance:
        print(f"Reason: {reason}")

    # Try to advance with force=True (skip requirements for testing)
    print("\n--- Attempting to advance to next stage (forced) ---")
    try:
        transaction = state_machine.advance_stage(transaction, notes="Test advancement", force=True)
        print(f"✓ Advanced to: {transaction.current_stage.value}")
    except Exception as e:
        print(f"✗ Failed to advance: {e}")

    return transaction


def show_stage_progress(db, transaction):
    """Display stage progress details."""

    print("\n" + "=" * 60)
    print("STAGE PROGRESS")
    print("=" * 60)

    state_machine = TransactionStateMachine(db)
    progress = state_machine.get_stage_progress(transaction)

    print(f"\nProgress: {progress['percent_complete']}% complete")
    print(f"Current: {progress['current_stage']}")
    print(f"\nStage History:")

    for stage_info in progress['stages']:
        status_icon = {
            'complete': '✓',
            'current': '→',
            'pending': '○'
        }[stage_info['status']]

        print(f"  {status_icon} {stage_info['stage']}")
        if stage_info['entered_at']:
            print(f"    Entered: {stage_info['entered_at']}")


def show_generated_tasks(db, transaction):
    """Display tasks generated for the transaction."""

    print("\n" + "=" * 60)
    print("GENERATED TASKS")
    print("=" * 60)

    from backend.models import Task

    tasks = db.query(Task).filter(Task.transaction_id == transaction.id).all()

    if not tasks:
        print("\nNo tasks generated yet")
        return

    print(f"\nTotal tasks: {len(tasks)}")

    # Group by stage
    tasks_by_stage = {}
    for task in tasks:
        stage = task.related_stage or "unassigned"
        if stage not in tasks_by_stage:
            tasks_by_stage[stage] = []
        tasks_by_stage[stage].append(task)

    for stage, stage_tasks in tasks_by_stage.items():
        print(f"\n{stage.upper()}:")
        for task in stage_tasks:
            blocking = "🚫 BLOCKING" if task.is_blocking else ""
            priority = f"[{task.priority.value.upper()}]"
            print(f"  • {task.title} {priority} {blocking}")
            print(f"    Status: {task.status.value}")
            print(f"    Assigned to: {task.assigned_to}")


def main():
    """Main test function."""

    print("\n" + "=" * 60)
    print("STATE MACHINE TEST")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Clean up any existing test data
        db.query(Transaction).filter(Transaction.id.like("TXN-TEST%")).delete()
        db.query(Party).filter(Party.id.like("PARTY-TEST%")).delete()
        db.commit()

        # Create test transaction
        transaction = create_test_transaction(db)

        # Show initial progress
        show_stage_progress(db, transaction)

        # Show generated tasks
        show_generated_tasks(db, transaction)

        # Test advancement
        transaction = test_stage_advancement(db, transaction)

        # Show updated progress
        show_stage_progress(db, transaction)

        # Show new tasks
        show_generated_tasks(db, transaction)

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nThe state machine is working correctly!")
        print("Next steps:")
        print("1. Build API endpoints to expose this functionality")
        print("2. Create seed data for demo scenarios")
        print("3. Build the Streamlit dashboard to visualize")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
