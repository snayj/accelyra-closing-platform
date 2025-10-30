# Accelyra Autonomous Closing Platform

**Revolutionizing Real Estate Closings with AI-Driven Automation**

![Status](https://img.shields.io/badge/status-demo-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Vision

Accelyra is building the foundational infrastructure for digital real estate closings—enabling any licensed title or escrow agent to execute compliant, end-to-end closings through a single, AI-driven platform.

**Analogous to:** Stripe for payments or Carta for equity management—standardizing and automating a complex, fragmented industry process.

### Key Metrics

- **Closing Time:** 7-10 days (from 30-45 days traditional)
- **Cost Reduction:** 60%+ operational savings
- **Compliance:** 100% RESPA, ALTA, CFPB compliant

---

## 🚀 Features

### Transaction Simulator
Test realistic transaction scenarios through all 7 closing stages:
- ✅ **Perfect Transaction** - Smooth progression
- 💰 **Insufficient Funds** - Buyer qualification issues
- 📋 **Missing Documentation** - Stalled progress
- 🏚️ **Title Issues** - Lien discoveries
- 🔍 **Failed Inspection** - Property condition problems
- ⚖️ **Low Appraisal** - Value mismatches

### Transaction History
- Filter and sort all tested transactions
- View complete stage progression timelines
- Track financial status and verification

### Platform Capabilities
- **AI-Native Processing:** NLP and computer vision for document classification
- **Modular Architecture:** Microservices for scalability
- **Compliance-Embedded:** Auditable and explainable decisions
- **Interoperable:** Integrations with Plaid, CoreLogic, Notarize, Qualia

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI (REST API)
- SQLAlchemy (ORM)
- SQLite (demo) / PostgreSQL (production-ready)
- Python 3.11+

**Frontend:**
- Streamlit (interactive dashboard)
- Plotly (visualizations)

**State Management:**
- 7-stage transaction state machine
- Automatic task generation
- Blocking task validation

---

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/snayj/accelyra-closing-platform.git
cd accelyra-closing-platform
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Initialize database:**
```bash
python scripts/init_db.py
python scripts/seed_data.py  # Optional: Load demo data
```

---

## 🎮 Usage

### Start the Application

**Terminal 1 - Start API Backend:**
```bash
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Start Dashboard:**
```bash
source .venv/bin/activate
streamlit run frontend/dashboard.py --server.port 8501
```

### Access the Application

- **Dashboard:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs
- **API Health Check:** http://localhost:8000/health

---

## 📖 Documentation

### Project Structure
```
ARS/
├── backend/
│   ├── api/              # API endpoints
│   ├── models/           # Database models
│   ├── services/         # Business logic (state machine)
│   ├── database.py       # Database configuration
│   └── main.py          # FastAPI application
├── frontend/
│   └── dashboard.py     # Streamlit dashboard
├── scripts/
│   ├── init_db.py       # Database initialization
│   └── seed_data.py     # Demo data generator
├── .streamlit/
│   └── config.toml      # Streamlit theme configuration
└── requirements.txt     # Python dependencies
```

### API Endpoints

**Transactions:**
- `GET /api/v1/transactions` - List all transactions
- `POST /api/v1/transactions` - Create new transaction
- `GET /api/v1/transactions/{id}` - Get transaction details
- `POST /api/v1/transactions/{id}/advance-stage` - Advance to next stage
- `POST /api/v1/transactions/{id}/deposit-earnest-money` - Record earnest money
- `POST /api/v1/transactions/{id}/verify-funds` - Verify buyer funds

**Tasks:**
- `GET /api/v1/transactions/{id}/tasks` - Get transaction tasks
- `POST /api/v1/tasks/{id}/complete` - Mark task complete

**Parties:**
- `GET /api/v1/parties` - List all parties
- `POST /api/v1/parties` - Create new party

---

## 🧪 Testing

### Run Tests
```bash
# State machine tests
python scripts/test_state_machine.py

# End-to-end API tests
python scripts/test_api_journey.py
```

---

## 🗺️ Roadmap

### Current Phase: MVP Demo (Completed ✅)
- [x] 7-stage state machine with workflow automation
- [x] Interactive transaction simulator
- [x] Realistic blocking scenarios
- [x] Transaction history viewer
- [x] About/Vision page

### Phase 2: Document Processing (Next)
- [ ] OCR integration (Tesseract/AWS Textract)
- [ ] Document upload API
- [ ] Validation rules engine
- [ ] Signature detection

### Phase 3: External Integrations
- [ ] Plaid (fund verification)
- [ ] CoreLogic (property data)
- [ ] Notarize (e-signing)
- [ ] Qualia (title/escrow)

### Phase 4: Production Readiness
- [ ] User authentication & authorization
- [ ] PostgreSQL migration
- [ ] Cloud deployment (AWS/Azure)
- [ ] Advanced analytics
- [ ] Mobile app (optional)

---

## 🤝 Contributing

This is currently a private demo project. For questions or partnership inquiries, please contact the team.

---

## 📄 License

Copyright © 2025 Accelyra. All rights reserved.

---

## 📞 Contact

For inquiries about Accelyra's Autonomous Closing Platform:
- **GitHub:** [@snayj](https://github.com/snayj)
- **Project Link:** [https://github.com/snayj/accelyra-closing-platform](https://github.com/snayj/accelyra-closing-platform)

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Data app framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
