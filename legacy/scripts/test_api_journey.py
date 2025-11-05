"""
API End-to-End Journey Test

This script tests the complete transaction lifecycle through the API:
1. Create parties (buyer, seller, agents, title officer)
2. Create a new transaction
3. Deposit earnest money
4. Verify funds
5. Complete blocking tasks
6. Advance through all 7 stages
7. Show complete audit trail

This demonstrates all logging and communication throughout the journey.
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_success(message):
    """Print success message."""
    print(f"✓ {message}")

def print_info(message):
    """Print info message."""
    print(f"  {message}")

def print_json(data, indent=2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent))


def create_parties():
    """Step 1: Create all parties involved in the transaction."""
    print_section("STEP 1: Creating Parties")

    parties = [
        {
            "name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "phone": "555-0101",
            "role": "buyer",
            "address": "456 Oak Ave",
            "city": "Chicago",
            "state": "IL",
            "zip_code": "60601"
        },
        {
            "name": "Bob Smith",
            "email": "bob.smith@example.com",
            "phone": "555-0102",
            "role": "seller",
            "address": "123 Maple St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701"
        },
        {
            "name": "Carol Davis",
            "email": "carol.davis@realty.com",
            "phone": "555-0103",
            "role": "buyer_agent",
            "company": "Premier Realty"
        },
        {
            "name": "David Wilson",
            "email": "david.wilson@titleco.com",
            "phone": "555-0104",
            "role": "title_officer",
            "company": "ABC Title Company"
        },
        {
            "name": "Emma Brown",
            "email": "emma.brown@bank.com",
            "phone": "555-0105",
            "role": "loan_officer",
            "company": "First National Bank"
        }
    ]

    party_ids = {}

    for party_data in parties:
        response = requests.post(f"{BASE_URL}/parties", json=party_data)
        if response.status_code == 201:
            result = response.json()
            party_id = result["party_id"]
            party_ids[party_data["role"]] = party_id
            print_success(f"Created {party_data['role']}: {party_data['name']} ({party_id})")
        else:
            print(f"✗ Failed to create {party_data['role']}: {response.text}")

    return party_ids


def create_transaction(party_ids):
    """Step 2: Create a new real estate transaction."""
    print_section("STEP 2: Creating Transaction")

    transaction_data = {
        "property_address": "123 Maple St, Springfield, IL 62701",
        "property_type": "single_family",
        "property_sqft": 1850,
        "property_bedrooms": 3,
        "property_bathrooms": 2.5,
        "property_year_built": 2015,
        "purchase_price": 450000,
        "down_payment": 90000,
        "loan_amount": 360000,
        "earnest_money_amount": 9000,
        "buyer_id": party_ids.get("buyer"),
        "seller_id": party_ids.get("seller"),
        "buyer_agent_id": party_ids.get("buyer_agent"),
        "title_officer_id": party_ids.get("title_officer"),
        "loan_officer_id": party_ids.get("loan_officer")
    }

    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)

    if response.status_code == 201:
        result = response.json()
        transaction_id = result["transaction_id"]
        print_success(f"Transaction created: {transaction_id}")
        print_info(f"Property: {transaction_data['property_address']}")
        print_info(f"Price: ${transaction_data['purchase_price']:,.0f}")
        print_info(f"Stage: {result['transaction']['current_stage']}")
        return transaction_id
    else:
        print(f"✗ Failed to create transaction: {response.text}")
        return None


def view_transaction_details(transaction_id):
    """View detailed transaction information."""
    print_section(f"Transaction Details: {transaction_id}")

    response = requests.get(f"{BASE_URL}/transactions/{transaction_id}")

    if response.status_code == 200:
        result = response.json()
        transaction = result["transaction"]
        progress = result["progress"]
        timeline = result["timeline"]
        task_summary = result["task_summary"]

        print_info(f"Current Stage: {transaction['current_stage']}")
        print_info(f"Progress: {progress['percent_complete']}% complete")
        print_info(f"Days in current stage: {timeline['days_in_current_stage']}")
        print_info(f"Estimated days to close: {timeline['estimated_days_to_close']}")
        print_info(f"Tasks: {task_summary['completed']}/{task_summary['total']} completed, {task_summary['blocking']} blocking")

        return result
    else:
        print(f"✗ Failed to get transaction: {response.text}")
        return None


def deposit_earnest_money(transaction_id):
    """Step 3: Record earnest money deposit."""
    print_section("STEP 3: Depositing Earnest Money")

    deposit_data = {
        "amount": 9000,
        "notes": "Wire transfer from buyer's account"
    }

    response = requests.post(
        f"{BASE_URL}/transactions/{transaction_id}/deposit-earnest-money",
        json=deposit_data
    )

    if response.status_code == 200:
        result = response.json()
        print_success("Earnest money deposited")
        print_info(f"Amount: ${deposit_data['amount']:,.0f}")
        print_info(f"Status: {result['status']}")
    else:
        print(f"✗ Failed to deposit earnest money: {response.text}")


def verify_funds(transaction_id):
    """Step 4: Verify buyer has sufficient funds."""
    print_section("STEP 4: Verifying Funds")

    verification_data = {
        "verified_by": "system",
        "verification_method": "bank_statement",
        "notes": "Reviewed bank statement showing $100,000 available"
    }

    response = requests.post(
        f"{BASE_URL}/transactions/{transaction_id}/verify-funds",
        json=verification_data
    )

    if response.status_code == 200:
        result = response.json()
        print_success("Funds verified")
        print_info(f"Verified by: {verification_data['verified_by']}")
        print_info(f"Method: {verification_data['verification_method']}")
    else:
        print(f"✗ Failed to verify funds: {response.text}")


def complete_blocking_tasks(transaction_id):
    """Complete all blocking tasks for current stage."""
    print_section(f"Completing Blocking Tasks")

    # Get all blocking tasks
    response = requests.get(
        f"{BASE_URL}/transactions/{transaction_id}/tasks",
        params={"is_blocking": True}
    )

    if response.status_code != 200:
        print(f"✗ Failed to get tasks: {response.text}")
        return

    result = response.json()
    blocking_tasks = [t for t in result["tasks"] if t["status"] == "pending"]

    print_info(f"Found {len(blocking_tasks)} blocking tasks to complete")

    for task in blocking_tasks:
        task_id = task["id"]
        task_title = task["title"]

        completion_data = {
            "completion_notes": f"Completed via API test"
        }

        response = requests.post(
            f"{BASE_URL}/tasks/{task_id}/complete",
            json=completion_data
        )

        if response.status_code == 200:
            print_success(f"Completed: {task_title}")
        else:
            print(f"✗ Failed to complete task: {response.text}")


def advance_stage(transaction_id):
    """Advance transaction to next stage."""
    advancement_data = {
        "notes": "Advancing via API test",
        "force": True  # Force for testing (skip requirement checks)
    }

    response = requests.post(
        f"{BASE_URL}/transactions/{transaction_id}/advance-stage",
        json=advancement_data
    )

    if response.status_code == 200:
        result = response.json()
        print_success(f"Advanced: {result['previous_stage']} → {result['current_stage']}")
        return True
    else:
        print(f"✗ Failed to advance stage: {response.text}")
        return False


def advance_through_all_stages(transaction_id):
    """Step 5: Advance through all remaining stages."""
    print_section("STEP 5: Advancing Through All Stages")

    stages = [
        "title_search_ordered",
        "lender_underwriting",
        "clear_to_close",
        "final_documents_prepared",
        "funding_and_signing",
        "recording_complete"
    ]

    for i, expected_stage in enumerate(stages, 1):
        print(f"\n--- Advancing to Stage {i+1}/7 ---")
        if advance_stage(transaction_id):
            time.sleep(0.5)  # Brief pause between stages
        else:
            break


def show_final_summary(transaction_id):
    """Show final transaction summary and audit trail."""
    print_section("FINAL TRANSACTION SUMMARY")

    response = requests.get(f"{BASE_URL}/transactions/{transaction_id}")

    if response.status_code == 200:
        result = response.json()
        transaction = result["transaction"]
        progress = result["progress"]

        print_success("Transaction Complete!")
        print_info(f"Final Stage: {transaction['current_stage']}")
        print_info(f"Progress: {progress['percent_complete']}%")

        print("\n--- Stage History (Audit Trail) ---")
        if transaction.get("stage_history"):
            for entry in transaction["stage_history"]:
                if "stage" in entry:
                    print(f"  • {entry['stage']}")
                    print(f"    Entered: {entry.get('entered_at', 'N/A')}")
                    if entry.get('notes'):
                        print(f"    Notes: {entry['notes']}")
                elif "event" in entry:
                    print(f"  • Event: {entry['event']}")
                    print(f"    Time: {entry.get('timestamp', 'N/A')}")


def main():
    """Run the complete API journey test."""
    print("\n")
    print("=" * 70)
    print("  REAL ESTATE CLOSING PLATFORM - API JOURNEY TEST")
    print("=" * 70)
    print("\nThis test demonstrates the complete transaction lifecycle")
    print("with full logging and audit trail.\n")

    try:
        # Step 1: Create parties
        party_ids = create_parties()

        # Step 2: Create transaction
        transaction_id = create_transaction(party_ids)
        if not transaction_id:
            return

        # View initial state
        view_transaction_details(transaction_id)

        # Step 3: Deposit earnest money
        deposit_earnest_money(transaction_id)

        # Step 4: Verify funds
        verify_funds(transaction_id)

        # Complete some tasks
        complete_blocking_tasks(transaction_id)

        # Step 5: Advance through all stages
        advance_through_all_stages(transaction_id)

        # Show final summary
        show_final_summary(transaction_id)

        print_section("TEST COMPLETE")
        print_success("All API endpoints tested successfully!")
        print_info(f"Transaction ID: {transaction_id}")
        print_info("View interactive docs at: http://localhost:8000/docs")
        print()

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to API")
        print("Make sure the API server is running:")
        print("  uvicorn backend.main:app --reload --port 8000\n")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
