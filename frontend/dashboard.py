"""
Real Estate Closing Platform - Dashboard

Simple, functional dashboard with readable design.
"""

import streamlit as st
import requests
from datetime import datetime
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# Use environment variable for API URL, fallback to localhost for local dev
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Page config - use default Streamlit theme
st.set_page_config(
    page_title="Real Estate Closing Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# DATA FUNCTIONS
# ============================================================================

@st.cache_data(ttl=5)
def get_transactions():
    """Fetch all transactions."""
    try:
        response = requests.get(f"{API_BASE_URL}/transactions", timeout=5)
        response.raise_for_status()
        return response.json()["transactions"]
    except Exception as e:
        st.error(f"Cannot connect to API: {e}")
        return []


@st.cache_data(ttl=5)
def get_transaction_detail(txn_id):
    """Fetch transaction details."""
    try:
        response = requests.get(f"{API_BASE_URL}/transactions/{txn_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error loading transaction: {e}")
        return None


def calculate_days(created_at: str) -> int:
    """Calculate days since creation."""
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return (datetime.now(created.tzinfo) - created).days
    except:
        return 0


STAGE_NAMES = {
    "offer_accepted": "Offer Accepted",
    "title_search_ordered": "Title Search",
    "lender_underwriting": "Underwriting",
    "clear_to_close": "Clear to Close",
    "final_documents_prepared": "Final Documents",
    "funding_and_signing": "Funding & Signing",
    "recording_complete": "Complete"
}


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

def show_welcome():
    """Welcome page with usage instructions."""

    st.title("🏠 Welcome to Accelyra Closing Platform")
    st.write("*AI-Driven Real Estate Transaction Simulator*")
    st.divider()

    # Quick start
    st.subheader("🚀 Quick Start Guide")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 1️⃣ Run a Simulation")
        st.write("Navigate to **Transaction Simulator** to:")
        st.write("- Choose a transaction scenario")
        st.write("- Set property details and price")
        st.write("- Watch the transaction progress through 7 stages")
        st.write("- See realistic blocking conditions and outcomes")

    with col2:
        st.markdown("### 2️⃣ Review Results")
        st.write("Go to **Transaction History** to:")
        st.write("- View all tested transactions")
        st.write("- Filter by stage or sort by price/date")
        st.write("- Examine detailed stage progressions")
        st.write("- Clear history when needed")

    st.divider()

    # Available scenarios
    st.subheader("📋 Available Transaction Scenarios")

    st.write("Test different real-world situations to see how the platform handles them:")

    scenarios = [
        {
            "emoji": "✅",
            "name": "Perfect Transaction",
            "description": "All checks pass, smooth progression through all 7 stages",
            "outcome": "Closes successfully in 7-10 days",
            "key_points": [
                "Strong buyer credit (750 score)",
                "Adequate funds verified ($110k+ liquid assets)",
                "Clear title with no liens",
                "Property appraises at contract price"
            ]
        },
        {
            "emoji": "💰",
            "name": "Insufficient Funds",
            "description": "Buyer cannot qualify due to inadequate funds",
            "outcome": "❌ Blocked at Stage 1 (Offer Accepted)",
            "key_points": [
                "Pre-approval too low for purchase price",
                "Insufficient funds for 20% down payment",
                "Earnest money check bounces",
                "Options: gift funds, lower price, or terminate"
            ]
        },
        {
            "emoji": "📋",
            "name": "Missing Documentation",
            "description": "Transaction stalls due to incomplete paperwork",
            "outcome": "⚠️ Stalled at Stage 3 (Underwriting)",
            "key_points": [
                "Buyer unresponsive to document requests",
                "Missing pay stubs, W-2s, tax returns",
                "5 days overdue on submissions",
                "Risk: lender may deny if not provided quickly"
            ]
        },
        {
            "emoji": "🏚️",
            "name": "Title Issue",
            "description": "Property has liens discovered during title search",
            "outcome": "❌ Blocked at Stage 2 (Title Search)",
            "key_points": [
                "Mechanic's lien from previous work",
                "Delinquent property taxes",
                "Undisclosed utility easement",
                "Must clear liens before proceeding"
            ]
        },
        {
            "emoji": "🔍",
            "name": "Failed Inspection",
            "description": "Major property defects found during inspection",
            "outcome": "❌ Blocked at Stage 3 (Underwriting)",
            "key_points": [
                "Foundation, roof, electrical issues",
                "$82k+ in estimated repairs",
                "Property value drops significantly",
                "Lender won't fund in current condition"
            ]
        },
        {
            "emoji": "⚖️",
            "name": "Low Appraisal",
            "description": "Property appraises below contract price",
            "outcome": "⚠️ Blocked at Stage 3 (Underwriting)",
            "key_points": [
                "Appraisal 12% below purchase price",
                "Lender won't loan on inflated value",
                "Buyer needs extra cash or price reduction",
                "Options: renegotiate or terminate"
            ]
        }
    ]

    for scenario in scenarios:
        with st.expander(f"{scenario['emoji']} **{scenario['name']}** - {scenario['description']}"):
            st.markdown(f"**Outcome:** {scenario['outcome']}")
            st.write("")
            st.write("**Key Points:**")
            for point in scenario['key_points']:
                st.write(f"• {point}")

    st.divider()

    # The 7 stages
    st.subheader("🔄 The 7 Closing Stages")

    stages_info = [
        ("1. Offer Accepted", "Escrow opened, earnest money deposited", "1-2 days"),
        ("2. Title Search", "Property ownership and liens verified", "2-3 days"),
        ("3. Underwriting", "Lender review, credit check, inspection", "3-5 days"),
        ("4. Clear to Close", "All conditions satisfied, ready for closing", "1 day"),
        ("5. Final Documents", "Closing disclosure and documents prepared", "1-2 days"),
        ("6. Funding & Signing", "Documents signed, funds wired", "1-2 days"),
        ("7. Recording Complete", "Deed recorded, transaction closed", "1 day")
    ]

    col1, col2 = st.columns([2, 1])

    with col1:
        for stage, description, timeline in stages_info:
            st.markdown(f"**{stage}**")
            st.text(f"  {description}")

    with col2:
        st.markdown("**Timeline**")
        for _, _, timeline in stages_info:
            st.text(f"{timeline}")

    st.write("")
    st.info("**Total Platform Timeline:** 7-13 days (vs. traditional 30-45 days)")

    st.divider()

    # Tips for testing
    st.subheader("💡 Tips for Testing")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Do's:**")
        st.write("✓ Test each scenario to understand failure points")
        st.write("✓ Adjust purchase price to see dynamic calculations")
        st.write("✓ Read the detailed explanations at each stage")
        st.write("✓ Review 'Next Steps' for resolution options")

    with col2:
        st.markdown("**Understanding Results:**")
        st.write("• 🟢 Green = Stage passed, can advance")
        st.write("• 🔴 Red = Blocked, cannot proceed")
        st.write("• 🟡 Yellow = Warning, delays expected")
        st.write("• Check History page for all details")

    st.divider()

    # Platform value
    st.subheader("🎯 Platform Value Proposition")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Closing Time", "7-10 days", "-70% vs traditional")

    with col2:
        st.metric("Cost Reduction", "60%+", "Operational savings")

    with col3:
        st.metric("Compliance", "100%", "Fully auditable")

    st.write("")
    st.success("**Ready to test?** Click **Transaction Simulator** in the sidebar to begin!")


def show_about():
    """About page with company vision."""

    st.title("🏠 Accelyra Autonomous Closing Platform")
    st.write("*The Future of Real Estate Closings*")
    st.divider()

    # Vision summary
    st.subheader("Our Vision")
    st.write("""
    Accelyra is building the foundational infrastructure for digital real estate closings—enabling any licensed
    title or escrow agent to execute compliant, end-to-end closings through a single, AI-driven platform.
    """)

    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Target Closing Time", "7-10 days", "From 30-45 days")
    with col2:
        st.metric("Cost Reduction", "60%+", "Operational savings")
    with col3:
        st.metric("Compliance", "100%", "RESPA, ALTA, CFPB")

    st.divider()

    # Platform capabilities
    st.subheader("Platform Capabilities")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🤖 AI-Native Processing**")
        st.write("- NLP and computer vision for document classification")
        st.write("- Automated data extraction from contracts and disclosures")
        st.write("- Intelligent validation with human oversight")

        st.write("")
        st.markdown("**🔧 Modular Architecture**")
        st.write("- Microservices for document intake, validation, orchestration")
        st.write("- Scalable design for partner integrations")
        st.write("- Independent service deployment")

    with col2:
        st.markdown("**⚖️ Compliance-Embedded**")
        st.write("- Auditable and explainable AI decisions")
        st.write("- Immutable compliance trail")
        st.write("- Regulatory requirement automation")

        st.write("")
        st.markdown("**🔗 Interoperable Integrations**")
        st.write("- Fund verification (Plaid)")
        st.write("- Property data (CoreLogic)")
        st.write("- E-signing (Notarize)")
        st.write("- Title/Escrow (Qualia)")

    st.divider()

    # Comparison
    st.subheader("Traditional vs. Accelyra")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**❌ Traditional Process**")
        st.write("- 30-45 day closing cycle")
        st.write("- Manual document review")
        st.write("- Fragmented systems")
        st.write("- Limited stakeholder visibility")
        st.write("- Error-prone manual processes")

    with col2:
        st.markdown("**✅ Accelyra Platform**")
        st.write("- 7-10 day closing cycle")
        st.write("- AI-powered automation")
        st.write("- Unified orchestration layer")
        st.write("- Real-time transparency")
        st.write("- Human-in-the-loop validation")

    st.divider()

    st.info("💡 **Analogous to:** Stripe for payments or Carta for equity management—standardizing and automating a complex, fragmented industry process.")


def show_overview():
    """Main overview page."""

    st.title("Real Estate Closing Platform")
    st.write("Monitor all active transactions")
    st.divider()

    # Fetch data
    transactions = get_transactions()
    if not transactions:
        st.warning("No transactions found. Make sure the API is running:")
        st.code("uvicorn backend.main:app --reload --port 8000")
        return

    # Calculate metrics
    total = len(transactions)
    completed = len([t for t in transactions if t["current_stage"] == "recording_complete"])
    active = total - completed

    # Average days
    if transactions:
        avg_days = sum(calculate_days(t["created_at"]) for t in transactions) / len(transactions)
    else:
        avg_days = 0

    # Count delayed
    delayed = sum(1 for t in transactions if calculate_days(t["created_at"]) > 15
                  and t["current_stage"] != "recording_complete")

    # Show metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Average Days to Close", f"{avg_days:.0f} days")

    with col2:
        st.metric("Active Transactions", active)

    with col3:
        st.metric("Completed", completed)

    with col4:
        st.metric("Needs Attention", delayed)

    st.divider()

    # Transaction list
    st.subheader("All Transactions")
    st.write("Click on a transaction to view details and trigger workflows")

    for txn in transactions:
        days = calculate_days(txn["created_at"])
        stage = STAGE_NAMES.get(txn["current_stage"], txn["current_stage"])

        # Determine status
        if txn["current_stage"] == "recording_complete":
            status = "✅ Complete"
        elif days > 15:
            status = "🔴 Delayed"
        else:
            status = "🟢 On Track"

        # Create card
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        with col1:
            if st.button(txn['property_address'], key=f"btn_{txn['id']}", use_container_width=True):
                st.session_state.selected_txn = txn['id']
                st.session_state.page = "detail"
                st.rerun()

        with col2:
            st.write(f"${txn['purchase_price']:,.0f}")

        with col3:
            st.write(f"{stage} (Day {days})")

        with col4:
            st.write(status)

        st.divider()


# ============================================================================
# PAGE: TRANSACTION DETAIL
# ============================================================================

def show_transaction_detail():
    """Detailed transaction view with workflow actions."""

    st.title("Transaction Details")

    # Get transactions
    transactions = get_transactions()
    if not transactions:
        st.warning("No transactions found")
        return

    # Transaction selector
    if "selected_txn" not in st.session_state:
        st.session_state.selected_txn = transactions[0]["id"]

    txn_options = {f"{t['property_address']} ({t['id']})": t['id'] for t in transactions}
    selected_label = st.selectbox("Select Transaction", list(txn_options.keys()))
    selected_id = txn_options[selected_label]
    st.session_state.selected_txn = selected_id

    st.divider()

    # Fetch details
    detail = get_transaction_detail(selected_id)
    if not detail:
        st.error("Failed to load transaction")
        return

    txn = detail["transaction"]
    progress = detail["progress"]
    tasks = detail.get("tasks", [])

    # Header
    st.subheader(txn['property_address'])
    st.write(f"**Purchase Price:** ${txn['purchase_price']:,.0f}")
    st.write(f"**Current Stage:** {STAGE_NAMES.get(txn['current_stage'], txn['current_stage'])}")
    st.write(f"**Days Elapsed:** {calculate_days(txn['created_at'])}")

    # Progress
    st.divider()
    st.write("**Progress**")
    st.progress(progress['percent_complete'] / 100)
    st.caption(f"{progress['percent_complete']}% Complete - Stage {progress['current_stage_index'] + 1} of 7")

    # Timeline
    st.divider()
    st.subheader("Timeline")

    stages = progress['stages']
    for i, stage_info in enumerate(stages, 1):
        stage_name = STAGE_NAMES.get(stage_info['stage'], stage_info['stage'])
        status = stage_info['status']

        if status == "complete":
            entered = stage_info.get('entered_at', '')
            if entered:
                date = datetime.fromisoformat(entered.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                st.write(f"✅ **{i}. {stage_name}** - Entered: {date}")
            else:
                st.write(f"✅ **{i}. {stage_name}** - Completed")
        elif status == "current":
            entered = stage_info.get('entered_at', '')
            if entered:
                date = datetime.fromisoformat(entered.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                st.write(f"▶️ **{i}. {stage_name}** - IN PROGRESS (since {date})")
            else:
                st.write(f"▶️ **{i}. {stage_name}** - IN PROGRESS")
        else:
            st.write(f"⚪ {i}. {stage_name} - Pending")

    # Complete Stage History with all actions
    st.divider()
    st.subheader("📜 Complete History Log")
    st.write("Detailed audit trail of all actions taken on this transaction")

    if txn.get('stage_history'):
        history = txn['stage_history']
        if isinstance(history, list):
            # Reverse to show newest first
            for i, entry in enumerate(reversed(history)):
                # Handle both timestamp formats
                timestamp = entry.get('entered_at') or entry.get('timestamp')

                # Format timestamp
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_time = str(timestamp)
                else:
                    formatted_time = 'Unknown time'

                st.write(f"**{formatted_time}**")

                # Show event
                if 'event' in entry:
                    st.write(f"🔸 Event: `{entry['event']}`")
                elif 'stage' in entry:
                    st.write(f"🔸 Event: `Stage Advanced`")

                # Show stage
                if 'stage' in entry:
                    stage_name = STAGE_NAMES.get(entry['stage'], entry['stage'])
                    st.write(f"📍 Stage: **{stage_name}**")

                # Show notes
                if entry.get('notes'):
                    st.write(f"📝 Notes: _{entry['notes']}_")

                # Show additional data
                if 'amount' in entry:
                    st.write(f"💰 Amount: ${entry['amount']:,.0f}")
                if 'verified_by' in entry:
                    st.write(f"✅ Verified by: {entry['verified_by']}")
                if 'method' in entry:
                    st.write(f"🔧 Method: {entry['method']}")

                st.divider()
        else:
            st.info("No history entries yet")
    else:
        st.info("No history available")

    # Tasks
    st.divider()
    st.subheader("Tasks")

    if tasks:
        pending = [t for t in tasks if t['status'] == 'pending']
        completed_tasks = [t for t in tasks if t['status'] == 'completed']

        st.write(f"**Pending ({len(pending)})**")
        if pending:
            for task in pending:
                blocking = "🚫 BLOCKING" if task.get('is_blocking') else ""
                st.write(f"- {task['title']} {blocking}")
                if task.get('due_date'):
                    due = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                    if due < datetime.now(due.tzinfo):
                        st.error("⚠️ OVERDUE!")
        else:
            st.success("No pending tasks")

        st.write(f"**Completed ({len(completed_tasks)})**")
        for task in completed_tasks:
            st.write(f"- ✅ {task['title']}")
    else:
        st.info("No tasks yet")

    # WORKFLOW ACTIONS - This is what the user wanted!
    st.divider()
    st.subheader("🎯 Workflow Actions")
    st.write("Trigger workflows and watch the system respond")

    if txn['current_stage'] != 'recording_complete':

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Transaction Workflows**")

            # Earnest Money
            if txn['earnest_money_status'] == 'pending':
                st.write("💰 Earnest Money Deposit")
                amount = st.number_input("Amount ($)", min_value=100, value=5000, step=100)
                if st.button("Process Deposit"):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/transactions/{selected_id}/deposit-earnest-money",
                            json={"amount": amount},
                            timeout=5
                        )
                        response.raise_for_status()
                        st.success(f"✅ Deposited ${amount:,.0f}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.success(f"✅ Earnest money: {txn['earnest_money_status']}")

            st.write("")

            # Funds Verification
            if not txn['funds_verified']:
                st.write("💵 Verify Buyer Funds")
                if st.button("Verify Funds"):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/transactions/{selected_id}/verify-funds",
                            timeout=5
                        )
                        response.raise_for_status()
                        st.success("✅ Funds verified")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.success("✅ Funds verified")

            st.write("")

            # Advance Stage
            st.write("⏭️ Advance Transaction Stage")
            if pending and any(t.get('is_blocking') for t in pending):
                st.warning("⚠️ Cannot advance: blocking tasks pending")
            else:
                force = st.checkbox("Force advance")
                if st.button("Advance to Next Stage"):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/transactions/{selected_id}/advance-stage",
                            json={"force": force},
                            timeout=5
                        )
                        response.raise_for_status()
                        result = response.json()
                        new_stage = STAGE_NAMES.get(result['transaction']['current_stage'])
                        st.success(f"✅ Advanced to: {new_stage}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col2:
            st.write("**Task Actions**")

            if pending:
                st.write("Complete a Task")
                task_labels = {f"{t['title']}": t['id'] for t in pending}
                selected_task_label = st.selectbox("Select task", list(task_labels.keys()))
                selected_task_id = task_labels[selected_task_label]

                notes = st.text_area("Completion notes (optional)")

                if st.button("Mark Complete"):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/tasks/{selected_task_id}/complete",
                            json={"completion_notes": notes if notes else "Completed via dashboard"},
                            timeout=5
                        )
                        response.raise_for_status()
                        st.success("✅ Task completed")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("No pending tasks to complete")

        st.divider()
        st.info("💡 Watch the terminal running the API to see real-time logs of these actions!")

    else:
        st.success("🎉 Transaction complete!")


# ============================================================================
# PAGE: COMPARISON
# ============================================================================

def show_transaction_history():
    """View detailed history of all simulated transactions."""

    st.title("📋 Transaction History")
    st.write("Review all transactions that have been tested in the simulator")
    st.divider()

    # Fetch all transactions
    transactions = get_transactions()
    if not transactions:
        st.info("No transactions found. Create transactions using the simulator to see them here.")
        return

    # Filter options
    st.subheader("Filter Transactions")
    col1, col2 = st.columns(2)

    with col1:
        stage_filter = st.selectbox(
            "Filter by Stage",
            ["All Stages"] + list(STAGE_NAMES.values())
        )

    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Oldest First", "Purchase Price (High to Low)", "Purchase Price (Low to High)"]
        )

    st.divider()

    # Apply filters and sorting
    filtered_txns = transactions.copy()

    if stage_filter != "All Stages":
        stage_key = [k for k, v in STAGE_NAMES.items() if v == stage_filter][0]
        filtered_txns = [t for t in filtered_txns if t["current_stage"] == stage_key]

    # Sort
    if sort_by == "Most Recent":
        filtered_txns = sorted(filtered_txns, key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort_by == "Oldest First":
        filtered_txns = sorted(filtered_txns, key=lambda x: x.get("created_at", ""))
    elif sort_by == "Purchase Price (High to Low)":
        filtered_txns = sorted(filtered_txns, key=lambda x: x.get("purchase_price", 0), reverse=True)
    else:  # Low to High
        filtered_txns = sorted(filtered_txns, key=lambda x: x.get("purchase_price", 0))

    # Display count and clear button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**Showing {len(filtered_txns)} of {len(transactions)} transactions**")
    with col2:
        # Check if we're in confirmation mode
        is_confirming = st.session_state.get('confirm_clear', False)
        button_label = "⚠️ CONFIRM DELETE" if is_confirming else "🗑️ Clear All History"
        button_type = "primary" if is_confirming else "secondary"

        if st.button(button_label, type=button_type, help="Delete all transactions from the database", key=f"clear_btn_{is_confirming}"):
            if is_confirming:
                # Actually delete
                try:
                    for txn in transactions:
                        requests.delete(f"{API_BASE_URL}/transactions/{txn['id']}", timeout=5)
                    st.success("All transaction history cleared!")
                    st.session_state.confirm_clear = False
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing history: {e}")
                    st.session_state.confirm_clear = False
            else:
                # Ask for confirmation
                st.session_state.confirm_clear = True
                st.rerun()

    if st.session_state.get('confirm_clear'):
        st.warning("⚠️ **Are you sure?** This will delete ALL transaction data. Click the button above again to confirm.")

    st.write("")

    # Display transactions
    for txn in filtered_txns:
        with st.expander(f"🏠 {txn['property_address']} - ${txn['purchase_price']:,.0f} - {STAGE_NAMES.get(txn['current_stage'], txn['current_stage'])}"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Transaction Details**")
                st.write(f"**ID:** {txn['id']}")
                st.write(f"**Property:** {txn['property_address']}")
                st.write(f"**Purchase Price:** ${txn['purchase_price']:,.0f}")
                st.write(f"**Current Stage:** {STAGE_NAMES.get(txn['current_stage'], txn['current_stage'])}")

                if txn.get('created_at'):
                    days_old = calculate_days(txn['created_at'])
                    st.write(f"**Days Since Created:** {days_old}")

            with col2:
                st.markdown("**Financial Details**")
                if txn.get('earnest_money_status'):
                    st.write(f"**Earnest Money:** {txn['earnest_money_status']}")
                if txn.get('funds_verified'):
                    st.write(f"**Funds Verified:** {'✓ Yes' if txn['funds_verified'] else '✗ No'}")

            # Show stage history
            if txn.get('stage_history'):
                st.write("")
                st.markdown("**Stage History**")

                history = txn['stage_history']
                if isinstance(history, list) and history:
                    for entry in history:
                        timestamp = entry.get('entered_at') or entry.get('timestamp')
                        stage = entry.get('stage', 'Unknown')
                        stage_name = STAGE_NAMES.get(stage, stage)

                        if timestamp:
                            try:
                                dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                            except:
                                formatted_time = str(timestamp)
                        else:
                            formatted_time = 'Unknown time'

                        st.text(f"{formatted_time} - {stage_name}")

                        if entry.get('notes'):
                            st.text(f"  └─ {entry['notes']}")
                else:
                    st.write("No history available")


def show_comparison():
    """Show traditional vs platform comparison."""

    st.title("Traditional vs Platform")
    st.write("See how we save time")
    st.divider()

    # Metrics
    traditional_days = 42
    platform_days = 13
    savings = traditional_days - platform_days

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Traditional Process", f"{traditional_days} days")

    with col2:
        st.metric("Our Platform", f"{platform_days} days")

    with col3:
        st.metric("Time Saved", f"{savings} days ({savings/traditional_days*100:.0f}%)")

    st.divider()

    # Comparison
    st.subheader("Process Comparison")

    col1, col2 = st.columns(2)

    traditional_stages = [
        ("Offer Accepted", 2),
        ("Title Search", 5),
        ("Underwriting", 14),
        ("Clear to Close", 3),
        ("Final Documents", 5),
        ("Funding & Signing", 3),
        ("Recording", 2)
    ]

    platform_stages = [
        ("Offer Accepted", 1),
        ("Title Search", 2),
        ("Underwriting", 4),
        ("Clear to Close", 1),
        ("Final Documents", 2),
        ("Funding & Signing", 2),
        ("Recording", 1)
    ]

    with col1:
        st.write("**Traditional (42 days total)**")
        for stage, days in traditional_stages:
            st.write(f"- {stage}: {days} days")

    with col2:
        st.write("**Platform (13 days total)**")
        for stage, days in platform_stages:
            st.write(f"- {stage}: {days} days ✅")

    st.divider()

    st.subheader("Key Benefits")
    st.write("**Automation**")
    st.write("- Instant document validation")
    st.write("- Automatic task generation")
    st.write("- Real-time status updates")

    st.write("")
    st.write("**Parallel Processing**")
    st.write("- Multiple stages run simultaneously")
    st.write("- No waiting for sequential steps")
    st.write("- Faster approvals")


# ============================================================================
# MAIN APP
# ============================================================================

def get_scenario_outcome(scenario, stage_index, purchase_price, buyer_name, property_address):
    """
    Returns scenario-specific content for each stage.

    Returns: (can_advance, status_type, content_dict)
    - can_advance: bool - whether this stage passes
    - status_type: 'success', 'error', 'warning' - for st.success/error/warning
    - content_dict: dict with 'title', 'details', 'explanation', 'next_steps'
    """

    # Perfect Transaction - all stages pass
    if "Perfect Transaction" in scenario:
        earnest_money = int(purchase_price * 0.02)
        proof_of_funds = int(purchase_price * 0.25)
        pre_approval = int(purchase_price * 0.90)

        outcomes = {
            0: (True, 'success', {
                'title': "✅ Stage Passed: All Requirements Met",
                'details': [
                    "Purchase agreement signed by all parties",
                    f"Earnest money (${earnest_money:,}) deposited and cleared",
                    f"Proof of funds verified: ${proof_of_funds:,} in liquid assets",
                    f"Credit pre-approval: ${pre_approval:,} at 6.5% interest"
                ],
                'explanation': "**Why this passed:** Buyer has demonstrated financial capability with verified funds and strong credit. All parties have executed the purchase agreement.",
                'next_steps': "✓ Moving to Title Search stage"
            }),
            1: (True, 'success', {
                'title': "✅ Stage Passed: Clear Title",
                'details': [
                    "Title search completed: No liens found",
                    "No judgments or encumbrances on property",
                    "Legal description verified and matches deed",
                    "Preliminary title report issued"
                ],
                'explanation': "**Why this passed:** Property has clean title with no ownership disputes, liens, or legal issues.",
                'next_steps': "✓ Moving to Underwriting stage"
            }),
            2: (True, 'success', {
                'title': "✅ Stage Passed: Loan Approved",
                'details': [
                    f"Credit score: 750 (Excellent)",
                    f"Debt-to-income ratio: 28% (Well below 43% max)",
                    f"Employment verified: 5 years, stable income",
                    f"Appraisal: ${purchase_price:,} (Matches contract price)",
                    f"Home inspection: Minor issues, $2,000 seller credit"
                ],
                'explanation': "**Why this passed:** Buyer has excellent creditworthiness, stable employment, low debt ratio, and property appraised at purchase price.",
                'next_steps': "✓ Moving to Clear to Close stage"
            }),
            3: (True, 'success', {
                'title': "✅ Stage Passed: Clear to Close Issued",
                'details': [
                    "All lender conditions satisfied",
                    "Homeowners insurance policy bound",
                    "Final verification of employment completed",
                    "No material changes to buyer's credit",
                    "Closing Disclosure delivered to buyer (3-day review)"
                ],
                'explanation': "**Why this passed:** All underwriting conditions met, insurance in place, buyer's financial status remains stable.",
                'next_steps': "✓ Moving to Final Documents stage"
            }),
            4: (True, 'success', {
                'title': "✅ Stage Passed: Documents Approved",
                'details': [
                    "Closing Disclosure reviewed and accepted by buyer",
                    "Deed prepared and reviewed",
                    "Promissory note and mortgage prepared",
                    "Settlement statement approved by all parties",
                    "No objections raised during 3-day review period"
                ],
                'explanation': "**Why this passed:** All closing documents properly prepared, reviewed by parties, and approved within required timeframes.",
                'next_steps': "✓ Moving to Funding & Signing stage"
            }),
            5: (True, 'success', {
                'title': "✅ Stage Passed: Funding Complete",
                'details': [
                    f"Buyer's down payment received: ${purchase_price * 0.20:,.0f}",
                    f"Lender's loan funds received: ${purchase_price * 0.80:,.0f}",
                    "All documents signed by buyer and seller",
                    f"Total funds in escrow: ${purchase_price:,.0f}",
                    "Title company authorized to disburse"
                ],
                'explanation': "**Why this passed:** All funds received and verified, all parties have executed required documents.",
                'next_steps': "✓ Moving to Recording stage"
            }),
            6: (True, 'success', {
                'title': "🎉 TRANSACTION CLOSED SUCCESSFULLY!",
                'details': [
                    f"Deed recorded with county on {datetime.now().strftime('%Y-%m-%d')}",
                    f"Funds disbursed to seller: ${purchase_price * 0.96:,.0f} (after fees)",
                    "Title insurance policies issued to buyer and lender",
                    f"Keys delivered to {buyer_name}",
                    f"Property address: {property_address}"
                ],
                'explanation': "**Transaction Complete:** Property ownership has been legally transferred and recorded. Buyer is now the legal owner.",
                'next_steps': "Transaction lifecycle complete"
            })
        }
        return outcomes.get(stage_index, (True, 'success', {'title': 'Unknown stage', 'details': [], 'explanation': '', 'next_steps': ''}))

    # Insufficient Funds scenario
    elif "Insufficient Funds" in scenario:
        down_payment_needed = int(purchase_price * 0.20)
        pre_approval = int(purchase_price * 0.67)  # 67% of purchase price
        bank_balance = int(purchase_price * 0.08)  # Only 8% available

        outcomes = {
            0: (False, 'error', {
                'title': "❌ Stage BLOCKED: Insufficient Funds",
                'details': [
                    "Purchase agreement signed by all parties",
                    f"Credit pre-approval: ${pre_approval:,} (below ${purchase_price:,.0f} needed)",
                    f"Bank statement shows: ${bank_balance:,} (needs ${down_payment_needed:,}+ for 20% down)",
                    "Earnest money check BOUNCED - insufficient funds"
                ],
                'explanation': f"**Why this failed:** Buyer does not have adequate liquid funds for down payment (${down_payment_needed:,} required) and earnest money deposit. Pre-approval amount is also insufficient for purchase price.",
                'next_steps': [
                    "Option 1: Buyer obtains gift funds from family (requires gift letter)",
                    "Option 2: Negotiate lower purchase price to match buyer's pre-approval",
                    "Option 3: Find co-borrower to increase buying power",
                    "Option 4: Transaction terminates, earnest money refunded (if contract allows)"
                ]
            }),
            2: (False, 'error', {
                'title': "❌ Stage BLOCKED: Cannot proceed (previous stage failed)",
                'details': [],
                'explanation': "**Cannot advance:** Previous stage (Offer Accepted) has unresolved blocking issues. Must resolve funds issue before continuing.",
                'next_steps': "Go back and resolve insufficient funds issue from Stage 1"
            })
        }
        # For any stage > 0, show blocked message
        if stage_index > 0:
            return outcomes.get(2, outcomes[2])
        return outcomes.get(stage_index, outcomes[0])

    # Missing Documentation scenario
    elif "Missing Documentation" in scenario:
        earnest_money = int(purchase_price * 0.02)
        proof_of_funds = int(purchase_price * 0.25)

        outcomes = {
            0: (True, 'success', {
                'title': "✅ Stage Passed: Initial Requirements Met",
                'details': [
                    "Purchase agreement signed",
                    f"Earnest money deposited: ${earnest_money:,}",
                    "Verbal pre-approval from lender",
                    f"Proof of funds: bank statement showing ${proof_of_funds:,}"
                ],
                'explanation': "**Why this passed:** Basic requirements met to open escrow and begin title search.",
                'next_steps': "✓ Moving to Title Search stage"
            }),
            1: (True, 'success', {
                'title': "✅ Stage Passed: Title Search Complete",
                'details': [
                    "Title search completed without issues",
                    "Preliminary title report issued"
                ],
                'explanation': "**Why this passed:** Title is clear.",
                'next_steps': "✓ Moving to Underwriting stage"
            }),
            2: (False, 'warning', {
                'title': "⚠️ Stage STALLED: Missing Required Documents",
                'details': [
                    "Lender requesting documents - OVERDUE by 5 days:",
                    "  ❌ Pay stubs (last 2 months) - NOT PROVIDED",
                    "  ❌ W-2 forms (last 2 years) - NOT PROVIDED",
                    "  ❌ Tax returns (last 2 years) - NOT PROVIDED",
                    "  ❌ Bank statements (last 2 months) - INCOMPLETE (only 1 month)",
                    "  ✓ Credit report - COMPLETED",
                    "  ✓ Employment verification - COMPLETED"
                ],
                'explanation': "**Why this is stalled:** Lender cannot complete underwriting without complete income documentation. Buyer has been unresponsive to document requests.",
                'next_steps': [
                    "Action Required: Buyer must provide ALL missing documents within 48 hours",
                    "Risk: If not provided, lender will deny loan application",
                    "Timeline Impact: Already delayed 5 days, affecting estimated closing date",
                    "Recommended: Set up document collection meeting with buyer immediately"
                ]
            })
        }
        # Any stage >= 2 shows the stalled message
        if stage_index >= 2:
            return outcomes.get(2, outcomes[2])
        return outcomes.get(stage_index, outcomes[0])

    # Title Issue scenario
    elif "Title Issue" in scenario:
        earnest_money = int(purchase_price * 0.02)  # 2% earnest money
        mechanics_lien = int(purchase_price * 0.08)  # 8% of price
        tax_lien = int(purchase_price * 0.03)  # 3% of price
        total_liens = mechanics_lien + tax_lien

        outcomes = {
            0: (True, 'success', {
                'title': "✅ Stage Passed: Escrow Opened",
                'details': [
                    "Purchase agreement executed",
                    f"Earnest money deposited: ${earnest_money:,}",
                    "All parties ready to proceed"
                ],
                'explanation': "**Why this passed:** Standard escrow opening process completed.",
                'next_steps': "✓ Moving to Title Search stage"
            }),
            1: (False, 'error', {
                'title': "❌ Stage BLOCKED: Title Issue Discovered",
                'details': [
                    "Title search completed - ISSUES FOUND:",
                    f"  🚨 **Mechanic's Lien**: ${mechanics_lien:,} from ABC Roofing Co (2022)",
                    f"  🚨 **Tax Lien**: ${tax_lien:,} county property taxes (2 years delinquent)",
                    "  ⚠️ **Easement**: Utility easement not disclosed in listing",
                    "",
                    f"Total liens: ${total_liens:,} must be cleared before closing"
                ],
                'explanation': "**Why this failed:** Property has unresolved liens that must be cleared before title can be transferred. Lender will not fund a loan on a property with liens.",
                'next_steps': [
                    "Option 1: Seller pays off liens at closing (deducted from proceeds)",
                    "Option 2: Negotiate purchase price reduction to offset lien amounts",
                    "Option 3: Seller clears liens before proceeding (delays closing 30-45 days)",
                    "Option 4: Buyer walks away, earnest money refunded (contingency clause)",
                    "",
                    "Immediate Action: Title company requests lien payoff statements",
                    "Timeline Impact: Minimum 2-week delay if seller pays at closing"
                ]
            })
        }
        # Any stage > 1 shows blocked
        if stage_index > 1:
            return (False, 'error', {
                'title': "❌ Cannot Proceed: Title Issues Unresolved",
                'details': [],
                'explanation': "Must resolve title liens from Stage 2 before advancing.",
                'next_steps': "Return to Title Search stage and resolve lien issues"
            })
        return outcomes.get(stage_index, outcomes[0])

    # Failed Inspection scenario
    elif "Failed Inspection" in scenario:
        outcomes = {
            0: (True, 'success', {
                'title': "✅ Stage Passed: Escrow Opened",
                'details': ["All initial requirements met"],
                'explanation': "Initial stage complete.",
                'next_steps': "✓ Moving to Title Search"
            }),
            1: (True, 'success', {
                'title': "✅ Stage Passed: Clear Title",
                'details': ["Title search complete, no issues"],
                'explanation': "Title is clear.",
                'next_steps': "✓ Moving to Underwriting"
            }),
            2: (False, 'error', {
                'title': "❌ Stage BLOCKED: Inspection Issues",
                'details': [
                    "Home inspection completed - MAJOR ISSUES FOUND:",
                    "  🚨 **Foundation**: Significant cracks, potential structural damage ($35,000 to repair)",
                    "  🚨 **Roof**: End of life, leaking in multiple areas ($18,000 to replace)",
                    "  🚨 **Electrical**: Outdated panel, fire hazard ($8,000 to update)",
                    "  🚨 **Plumbing**: Polybutylene pipes (insurance won't cover) ($15,000 to replumb)",
                    "  ⚠️ **HVAC**: Not functioning, needs replacement ($6,000)",
                    "",
                    "**Total estimated repairs: $82,000**",
                    "",
                    "**Lender's appraiser response**:",
                    f"  • Property value 'as-is': ${purchase_price * 0.82:,.0f}",
                    f"  • Will not loan ${purchase_price:,.0f} on property in this condition",
                    "  • Requires repairs before funding OR reduced purchase price"
                ],
                'explanation': f"**Why this failed:** Property has significant defects that affect both value and insurability. Lender will not fund a loan on a property with these issues. Property is worth ~${purchase_price * 0.82:,.0f}, not ${purchase_price:,.0f}.",
                'next_steps': [
                    "Option 1: Seller repairs all issues before closing (delays 60-90 days)",
                    "Option 2: Renegotiate purchase price to $370,000 (reflecting true condition)",
                    "Option 3: Seller provides $82,000 credit at closing for buyer to make repairs",
                    "Option 4: Buyer walks away using inspection contingency (common choice)",
                    "",
                    "Buyer's decision: Most buyers would terminate this transaction",
                    "Timeline: If pursuing repairs, add 60-90 days to closing"
                ]
            })
        }
        if stage_index >= 2:
            return outcomes.get(2, outcomes[2])
        return outcomes.get(stage_index, outcomes[0])

    # Low Appraisal scenario
    elif "Low Appraisal" in scenario:
        outcomes = {
            0: (True, 'success', {
                'title': "✅ Stage Passed: Escrow Opened",
                'details': ["All initial requirements met"],
                'explanation': "Initial stage complete.",
                'next_steps': "✓ Moving to Title Search"
            }),
            1: (True, 'success', {
                'title': "✅ Stage Passed: Clear Title",
                'details': ["Title search complete, no issues"],
                'explanation': "Title is clear.",
                'next_steps': "✓ Moving to Underwriting"
            }),
            2: (False, 'warning', {
                'title': "⚠️ Stage BLOCKED: Appraisal Came In Low",
                'details': [
                    f"**Purchase contract price**: ${purchase_price:,.0f}",
                    f"**Appraisal value**: ${purchase_price * 0.88:,.0f}",
                    f"**Shortfall**: ${purchase_price * 0.12:,.0f}",
                    "",
                    "**Impact on financing**:",
                    f"  • Lender will only loan 80% of APPRAISED value: ${purchase_price * 0.88 * 0.80:,.0f}",
                    f"  • Buyer expected to get: ${purchase_price * 0.80:,.0f}",
                    f"  • Loan amount shortfall: ${purchase_price * 0.80 - purchase_price * 0.88 * 0.80:,.0f}",
                    "",
                    "**Buyer's options**:",
                    f"  • Bring additional ${purchase_price * 0.12:,.0f} cash to make up difference (unlikely)",
                    f"  • Increase down payment to cover gap",
                    "",
                    "**Why appraisal was low**:",
                    "  • Recent comparable sales averaged lower",
                    "  • Market cooling in this neighborhood",
                    "  • Property was likely overpriced by seller"
                ],
                'explanation': f"**Why this is blocked:** Lender will not loan more than 80% of the appraised value. The appraisal came in ${purchase_price * 0.12:,.0f} below purchase price. Buyer cannot get the expected loan amount.",
                'next_steps': [
                    f"Option 1: Seller reduces price to appraised value (${purchase_price * 0.88:,.0f})",
                    f"Option 2: Buyer and seller meet in the middle (${purchase_price * 0.94:,.0f})",
                    f"Option 3: Buyer brings extra ${purchase_price * 0.12:,.0f} cash to closing (rare)",
                    "Option 4: Buyer walks away using appraisal contingency (common)",
                    "",
                    "Immediate Action: Schedule negotiation call with both parties",
                    "Most Likely Outcome: Price reduction or transaction termination"
                ]
            })
        }
        if stage_index >= 2:
            return outcomes.get(2, outcomes[2])
        return outcomes.get(stage_index, outcomes[0])

    # Default fallback
    return (True, 'success', {
        'title': 'Unknown scenario',
        'details': [],
        'explanation': '',
        'next_steps': ''
    })


def show_transaction_simulator():
    """Transaction Lifecycle Viewer - Watch a transaction progress through all stages."""

    st.title("🎬 Transaction Lifecycle Simulator")
    st.write("Watch a real estate transaction progress through all 7 closing stages")
    st.divider()

    # Initialize simulator state
    if 'simulator_running' not in st.session_state:
        st.session_state.simulator_running = False
    if 'simulator_stage' not in st.session_state:
        st.session_state.simulator_stage = 0
    if 'simulator_log' not in st.session_state:
        st.session_state.simulator_log = []
    if 'simulator_txn_id' not in st.session_state:
        st.session_state.simulator_txn_id = None

    # Stage definitions
    stages = [
        "Offer Accepted / Escrow Opened",
        "Title Search Ordered",
        "Lender Underwriting / Inspections",
        "Clear to Close",
        "Final Documents Prepared",
        "Funding & Signing",
        "Recording & Disbursement Complete"
    ]

    # Start new simulation
    st.subheader("Step 1: Create Transaction Scenario")

    # Scenario selection
    st.markdown("**Select Transaction Scenario:**")
    scenario = st.selectbox(
        "Choose what type of transaction to simulate",
        [
            "✅ Perfect Transaction (All Checks Pass)",
            "💰 Insufficient Funds (Buyer Cannot Qualify)",
            "📋 Missing Documentation (Stalled Progress)",
            "🏚️ Title Issue (Lien Discovered)",
            "🔍 Failed Inspection (Property Issues)",
            "⚖️ Low Appraisal (Value Too Low)"
        ]
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        property_address = st.text_input("Property Address", "123 Demo Street, Chicago, IL 60601")
        purchase_price = st.number_input("Purchase Price", min_value=100000, value=450000, step=10000)
    with col2:
        buyer_name = st.text_input("Buyer Name", "John Demo")
        seller_name = st.text_input("Seller Name", "Jane Seller")

    # Store scenario in session state
    if 'simulator_scenario' not in st.session_state:
        st.session_state.simulator_scenario = scenario

    if st.button("🚀 Start Transaction Simulation", type="primary"):
        st.session_state.simulator_running = True
        st.session_state.simulator_stage = 0
        st.session_state.simulator_log = []
        st.session_state.simulator_txn_id = None
        st.session_state.simulator_scenario = scenario  # Store selected scenario

        # Create the transaction
        try:
            # First get or create parties
            st.session_state.simulator_log.append("📝 Creating parties...")

            # Create transaction
            response = requests.post(
                f"{API_BASE_URL}/transactions",
                json={
                    "property_address": property_address,
                    "purchase_price": purchase_price,
                    "buyer_id": "PARTY-2025-0001",  # Use existing from seed data
                    "seller_id": "PARTY-2025-0002"
                },
                timeout=5
            )
            response.raise_for_status()
            txn_data = response.json()
            st.session_state.simulator_txn_id = txn_data["transaction_id"]
            st.session_state.simulator_log.append(f"✅ Transaction created: {txn_data['transaction_id']}")
            st.success(f"Transaction created: {txn_data['transaction_id']}")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to create transaction: {e}")
            return

    # Show simulation progress
    if st.session_state.simulator_running and st.session_state.simulator_txn_id:
        st.divider()
        st.subheader("Step 2: Transaction Progress")

        # Progress bar
        progress = st.session_state.simulator_stage / len(stages)
        st.progress(progress)
        st.caption(f"Stage {st.session_state.simulator_stage + 1} of {len(stages)}")

        # Current stage info
        current_stage = stages[st.session_state.simulator_stage]
        st.markdown(f"### Current Stage: {current_stage}")

        # Get transaction details
        detail = get_transaction_detail(st.session_state.simulator_txn_id)
        if detail and isinstance(detail, dict):
            txn = detail.get("transaction")
            tasks = detail.get("tasks", [])

            # Validate we have transaction data
            if not txn:
                st.error(f"Invalid transaction data received from API")
                return

            # Get scenario-specific outcome for this stage
            can_advance, status_type, content = get_scenario_outcome(
                st.session_state.simulator_scenario,
                st.session_state.simulator_stage,
                purchase_price,
                buyer_name,
                property_address
            )

            # Display scenario outcome
            st.markdown("#### Stage Outcome:")

            # Show status message
            if status_type == 'success':
                st.success(content['title'])
            elif status_type == 'error':
                st.error(content['title'])
            else:  # warning
                st.warning(content['title'])

            # Show details
            if content['details']:
                st.write("")
                st.write("**Details:**")
                if isinstance(content['details'], list):
                    # Convert to bulleted text block
                    details_text = "\n".join([f"• {item}" for item in content['details']])
                    st.text(details_text)
                else:
                    st.text(content['details'])

            # Show explanation
            if content['explanation']:
                st.write("")
                st.markdown(content['explanation'])

            # Show next steps
            if content['next_steps']:
                st.write("")
                st.write("**Next Steps:**")
                if isinstance(content['next_steps'], list):
                    for step in content['next_steps']:
                        st.write(f"• {step}")
                else:
                    st.write(content['next_steps'])

            # Show balloons for successful completion
            if st.session_state.simulator_stage == 6 and can_advance:
                st.balloons()

            # Store can_advance state for button logic
            st.session_state.can_advance_stage = can_advance

        # Show active tasks
        if detail and tasks:
            pending = [t for t in tasks if t['status'] == 'pending']
            if pending:
                st.write("")
                st.write("**Active Tasks:**")
                for task in pending[:3]:
                    st.write(f"- {task['title']}")

        st.divider()

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.session_state.simulator_stage < len(stages) - 1:
                # Check if this scenario allows advancing
                can_advance_flag = st.session_state.get('can_advance_stage', True)

                if can_advance_flag:
                    button_label = "▶️ Advance to Next Stage"
                    button_help = "Continue to the next stage of the transaction"
                else:
                    button_label = "🚫 Cannot Advance (Blocked)"
                    button_help = "This transaction is blocked and cannot advance. Review the issues above."

                if st.button(button_label, type="primary" if can_advance_flag else "secondary",
                            disabled=not can_advance_flag, help=button_help):
                    # Complete blocking tasks and advance
                    try:
                        # Complete all pending tasks for current stage
                        if detail and tasks:
                            for task in [t for t in tasks if t['status'] == 'pending']:
                                requests.post(
                                    f"{API_BASE_URL}/tasks/{task['id']}/complete",
                                    json={"completion_notes": "Auto-completed by simulator"},
                                    timeout=5
                                )

                        # Advance stage
                        response = requests.post(
                            f"{API_BASE_URL}/transactions/{st.session_state.simulator_txn_id}/advance-stage",
                            json={"force": True},
                            timeout=5
                        )
                        response.raise_for_status()

                        st.session_state.simulator_stage += 1
                        st.session_state.simulator_log.append(f"✅ Advanced to Stage {st.session_state.simulator_stage + 1}")
                        st.cache_data.clear()
                        st.rerun()
                    except requests.exceptions.HTTPError as e:
                        error_detail = e.response.json().get('detail', str(e))
                        st.error(f"Cannot advance stage: {error_detail}")
                    except Exception as e:
                        st.error(f"Error advancing stage: {e}")

        with col2:
            if st.button("🔄 Refresh"):
                st.cache_data.clear()
                st.rerun()

        with col3:
            if st.button("🗑️ Reset Simulation"):
                st.session_state.simulator_running = False
                st.session_state.simulator_stage = 0
                st.session_state.simulator_log = []
                st.session_state.simulator_txn_id = None
                st.rerun()

        # Show activity log
        st.divider()
        st.subheader("Step 3: Activity Log")
        if st.session_state.simulator_log:
            for entry in st.session_state.simulator_log:
                st.write(entry)
        else:
            st.info("No activity yet")

        # Show complete transaction history
        st.divider()
        st.subheader("Step 4: Complete Transaction History")
        st.write("Detailed audit trail from the database")

        if detail and isinstance(detail, dict) and "transaction" in detail:
            txn = detail["transaction"]
            if txn.get('stage_history'):
                history = txn['stage_history']
                if isinstance(history, list) and history:
                    st.write(f"**Total history entries: {len(history)}**")
                    st.write("")

                    for i, entry in enumerate(reversed(history)):
                        # Handle both timestamp formats
                        timestamp = entry.get('entered_at') or entry.get('timestamp')

                        # Format timestamp
                        if timestamp:
                            try:
                                dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                formatted_time = str(timestamp)
                        else:
                            formatted_time = 'Unknown time'

                        st.write(f"**{formatted_time}**")

                        # Show event
                        if 'event' in entry:
                            st.write(f"🔸 Event: `{entry['event']}`")
                        elif 'stage' in entry:
                            st.write(f"🔸 Event: `Stage Advanced`")

                        # Show stage
                        if 'stage' in entry:
                            stage_name = STAGE_NAMES.get(entry['stage'], entry['stage'])
                            st.write(f"📍 Stage: **{stage_name}**")

                        # Show notes
                        if entry.get('notes'):
                            st.write(f"📝 Notes: _{entry['notes']}_")

                        # Show additional data
                        if 'amount' in entry:
                            st.write(f"💰 Amount: ${entry['amount']:,.0f}")
                        if 'verified_by' in entry:
                            st.write(f"✅ Verified by: {entry['verified_by']}")
                        if 'method' in entry:
                            st.write(f"🔧 Method: {entry['method']}")

                        st.write("---")
                else:
                    st.info("No history entries yet")
            else:
                st.info("No history available")


def show_workflow_demo():
    """Interactive workflow demonstration - trigger steps and watch what happens."""

    st.title("🎯 Workflow Demo")
    st.write("Trigger workflow steps and watch the system respond in real-time")
    st.divider()

    # Get transactions
    transactions = get_transactions()
    if not transactions:
        st.error("No transactions found. Run seed data first: python scripts/seed_data.py")
        return

    # Select transaction to work with
    st.subheader("Step 1: Select Transaction")
    txn_options = {f"{t['id']} - {t['property_address']} (Stage: {STAGE_NAMES.get(t['current_stage'], t['current_stage'])})": t['id']
                   for t in transactions}
    selected_label = st.selectbox("Choose a transaction to work with", list(txn_options.keys()))
    selected_id = txn_options[selected_label]

    # Fetch full details
    detail = get_transaction_detail(selected_id)
    if not detail:
        st.error("Failed to load transaction")
        return

    txn = detail["transaction"]
    tasks = detail.get("tasks", [])

    st.divider()

    # Show current state
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Stage", STAGE_NAMES.get(txn['current_stage'], txn['current_stage']))
    with col2:
        st.metric("Days Elapsed", calculate_days(txn['created_at']))
    with col3:
        pending_tasks = [t for t in tasks if t['status'] == 'pending']
        st.metric("Pending Tasks", len(pending_tasks))

    st.divider()

    # Workflow Actions
    st.subheader("Step 2: Trigger Workflow Actions")
    st.write("Click buttons below to execute workflow steps and see what happens")

    # Create action log area
    if 'action_log' not in st.session_state:
        st.session_state.action_log = []

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Transaction Workflows**")

        # Action 1: Deposit Earnest Money
        st.write("---")
        st.write("**1. Deposit Earnest Money**")
        if txn['earnest_money_status'] == 'pending':
            amount = st.number_input("Amount", min_value=1000, value=5000, step=500, key="earnest")
            if st.button("💰 Process Deposit", key="btn_deposit"):
                with st.spinner("Processing..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/transactions/{selected_id}/deposit-earnest-money",
                            json={"amount": amount},
                            timeout=5
                        )
                        response.raise_for_status()
                        st.session_state.action_log.append(f"✅ Deposited ${amount:,.0f} earnest money")
                        st.success("Done!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.success(f"✅ Already done: {txn['earnest_money_status']}")

        # Action 2: Verify Funds
        st.write("---")
        st.write("**2. Verify Buyer Funds**")
        if not txn['funds_verified']:
            if st.button("💵 Verify Funds", key="btn_verify"):
                with st.spinner("Verifying..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/transactions/{selected_id}/verify-funds",
                            timeout=5
                        )
                        response.raise_for_status()
                        st.session_state.action_log.append("✅ Verified buyer funds")
                        st.success("Done!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.success("✅ Already verified")

        # Action 3: Advance Stage
        st.write("---")
        st.write("**3. Advance to Next Stage**")
        blocking_tasks = [t for t in pending_tasks if t.get('is_blocking')]
        if blocking_tasks:
            st.warning(f"⚠️ {len(blocking_tasks)} blocking task(s) must be completed first")
            for task in blocking_tasks:
                st.write(f"- {task['title']}")

        force = st.checkbox("Force advance anyway", key="force")
        if st.button("⏭️ Advance Stage", key="btn_advance"):
            with st.spinner("Advancing..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/transactions/{selected_id}/advance-stage",
                        json={"force": force},
                        timeout=5
                    )
                    response.raise_for_status()
                    result = response.json()
                    new_stage = STAGE_NAMES.get(result['transaction']['current_stage'])
                    st.session_state.action_log.append(f"✅ Advanced to: {new_stage}")
                    st.success(f"Advanced to: {new_stage}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        st.write("**Task Actions**")

        # Action 4: Complete Tasks
        st.write("---")
        if pending_tasks:
            for i, task in enumerate(pending_tasks[:5]):  # Show first 5
                st.write(f"**Task: {task['title']}**")
                blocking_badge = "🚫 BLOCKING" if task.get('is_blocking') else "ℹ️ Optional"
                st.caption(blocking_badge)

                if st.button(f"✓ Complete", key=f"task_{task['id']}"):
                    with st.spinner("Completing..."):
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/tasks/{task['id']}/complete",
                                json={"completion_notes": "Completed via workflow demo"},
                                timeout=5
                            )
                            response.raise_for_status()
                            st.session_state.action_log.append(f"✅ Completed task: {task['title']}")
                            st.success("Done!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                st.write("---")
        else:
            st.info("No pending tasks")

    # Action Log
    st.divider()
    st.subheader("Step 3: View Action Log")
    st.write("Watch what happens as you trigger actions")

    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    if st.button("🗑️ Clear Log"):
        st.session_state.action_log = []
        st.rerun()

    if st.session_state.action_log:
        for log_entry in reversed(st.session_state.action_log[-10:]):  # Show last 10
            st.write(log_entry)
    else:
        st.info("No actions yet. Click buttons above to trigger workflows.")

    # Complete transaction history
    st.divider()
    st.subheader("Step 4: Complete Transaction History")

    if txn.get('stage_history'):
        history = txn['stage_history']
        if isinstance(history, list) and history:
            st.write(f"**Total history entries: {len(history)}**")

            # Show expandable history
            with st.expander("View Full History", expanded=False):
                for i, entry in enumerate(reversed(history)):
                    # Debug: show what we have
                    st.write(f"DEBUG Entry {i}: {entry}")

                    # Handle both timestamp formats (entered_at is more common)
                    timestamp = entry.get('entered_at') or entry.get('timestamp', 'Unknown')

                    # Format timestamp if it exists
                    if timestamp and timestamp != 'Unknown':
                        try:
                            dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            formatted_time = str(timestamp)
                    else:
                        formatted_time = 'Unknown time'

                    st.write(f"**{formatted_time}**")

                    # Show event type if present, otherwise infer from stage
                    if 'event' in entry:
                        st.write(f"Event: `{entry['event']}`")
                    elif 'stage' in entry:
                        st.write(f"Event: `Stage Advanced`")

                    # Show stage
                    if 'stage' in entry:
                        stage_name = STAGE_NAMES.get(entry['stage'], entry['stage'])
                        st.write(f"Stage: **{stage_name}**")

                    # Show notes
                    if entry.get('notes'):
                        st.write(f"Notes: _{entry['notes']}_")

                    # Show additional data
                    if 'amount' in entry:
                        st.write(f"Amount: ${entry['amount']:,.0f}")
                    if 'method' in entry:
                        st.write(f"Method: {entry['method']}")
                    if 'verified_by' in entry:
                        st.write(f"Verified by: {entry['verified_by']}")

                    st.write("---")
        else:
            st.info("No history yet")
    else:
        st.info("No history available")


def main():
    """Main application."""

    # Sidebar
    st.sidebar.title("Navigation")

    # Page selection
    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    page = st.sidebar.radio(
        "Select Page",
        ["welcome", "simulator", "history", "about"],
        format_func=lambda x: {
            "welcome": "🏠 Welcome",
            "simulator": "🎬 Transaction Simulator",
            "history": "📋 Transaction History",
            "about": "ℹ️ About Accelyra"
        }[x]
    )

    st.session_state.page = page

    # API status
    st.sidebar.divider()
    st.sidebar.write("**API Status**")
    try:
        resp = requests.get("http://localhost:8000/health", timeout=2)
        if resp.ok:
            st.sidebar.success("✅ Connected")
        else:
            st.sidebar.error("❌ Error")
    except:
        st.sidebar.error("❌ Offline")

    # Render page
    if page == "welcome":
        show_welcome()
    elif page == "simulator":
        show_transaction_simulator()
    elif page == "history":
        show_transaction_history()
    elif page == "about":
        show_about()


if __name__ == "__main__":
    main()
