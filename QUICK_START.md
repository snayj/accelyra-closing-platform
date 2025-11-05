# Quick Start Guide

## Prerequisites
- Node.js 20+ installed
- pnpm installed (`npm install -g pnpm`)
- Docker installed (for PostgreSQL)

## Run the Application (5 minutes)

### 1. Install Dependencies
```bash
# From the root directory
pnpm install
```

### 2. Start PostgreSQL
```bash
docker-compose up -d
```

### 3. Set Up Backend Environment
```bash
# Copy environment file
cp packages/backend/.env.example packages/backend/.env

# The .env file should contain:
# DATABASE_URL="postgresql://accelyra:accelyra_dev_password@localhost:5432/accelyra_closing?schema=public"
```

### 4. Initialize Database
```bash
cd packages/backend
pnpm prisma:generate
pnpm prisma:migrate
```

### 5. Start Backend (Terminal 1)
```bash
cd packages/backend
pnpm dev
# Should start on http://localhost:3001
```

### 6. Set Up Frontend Environment
```bash
# Copy environment file
cp packages/frontend/.env.example packages/frontend/.env

# The .env file should contain:
# VITE_API_URL=http://localhost:3001/api/v1
```

### 7. Start Frontend (Terminal 2)
```bash
cd packages/frontend
pnpm dev
# Should start on http://localhost:3000
```

### 8. Open Browser
Navigate to: **http://localhost:3000**

## What You'll See

### Welcome Page (/)
- Hero section with Accelyra branding
- Platform stats (7-14 days, 70% faster, 100% compliance)
- 7-stage process overview cards
- Quick start guide
- Call-to-action buttons

### Transaction Simulator (/simulator)
**Configuration Screen:**
- 6 scenario buttons (Perfect, Insufficient Funds, Title Issue, etc.)
- Property address input
- Purchase price input
- Buyer/Seller name inputs
- "Start Simulation" button

**Active Simulation:**
- Transaction header with ID and property details
- Stage progress bar (visual timeline)
- Current stage details card showing:
  - Required documents with OCR results
  - Required actions with blocking indicators
  - Validation checks (pass/fail with reasons)
- "Advance to Next Stage" button
- Activity log with color-coded events

### Transaction History (/history)
- Filter by stage dropdown
- Transaction cards with:
  - Transaction ID and stage badge
  - Property address
  - Purchase price
  - Created date
  - Buyer/Seller names

### About (/about)
- Mission statement
- 6 platform capability cards
- Traditional vs Accelyra comparison
- Value metrics (7-14 days, 70%, 100%, 24/7)

## Troubleshooting

**Port already in use:**
```bash
# Kill processes on ports
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
```

**Database connection issues:**
```bash
# Check if PostgreSQL is running
docker ps

# Restart PostgreSQL
docker-compose restart
```

**Missing dependencies:**
```bash
# Clean and reinstall
rm -rf node_modules packages/*/node_modules
pnpm install
```
