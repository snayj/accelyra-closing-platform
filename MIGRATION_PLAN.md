# Migration Plan: Streamlit to React + TypeScript/Node.js

## Overview

This document outlines the migration strategy for the Accelyra Closing Platform from a Streamlit frontend to a modern React + TypeScript stack.

## Current Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
│    (Python - Single File 1854 lines)   │
│  - Welcome Page                         │
│  - Transaction Simulator                │
│  - Transaction History                  │
│  - About Page                           │
└─────────────────┬───────────────────────┘
                  │ HTTP Requests
┌─────────────────▼───────────────────────┐
│         FastAPI Backend                 │
│           (Python 3.11+)                │
│  - REST API (/api/v1)                   │
│  - SQLAlchemy ORM                       │
│  - State Machine Logic                  │
│  - SQLite/PostgreSQL Database           │
└─────────────────────────────────────────┘
```

## Target Architecture

```
┌─────────────────────────────────────────┐
│      React Frontend (TypeScript)        │
│  - Vite Build Tool                      │
│  - React Router (SPA routing)           │
│  - React Query (data fetching)          │
│  - Tailwind CSS + shadcn/ui             │
│  - Axios (HTTP client)                  │
└─────────────────┬───────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────┐
│   Node.js/Express Backend (TypeScript)  │
│  - Express.js (REST API)                │
│  - Prisma ORM (type-safe database)      │
│  - TypeScript state machine             │
│  - PostgreSQL Database (prod ready)     │
└─────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite (fast, modern)
- **Routing**: React Router v6
- **State Management**: React Query (server state) + Zustand (client state)
- **Styling**: Tailwind CSS + shadcn/ui components
- **HTTP Client**: Axios
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts or Chart.js
- **Date Handling**: date-fns

### Backend
- **Runtime**: Node.js 20+ LTS
- **Framework**: Express.js with TypeScript
- **ORM**: Prisma (type-safe, great DX)
- **Validation**: Zod (shared with frontend)
- **Database**: PostgreSQL (development & production)
- **Migration**: Prisma Migrate
- **Testing**: Jest + Supertest

### Development Tools
- **Package Manager**: pnpm (fast, efficient)
- **Linting**: ESLint + Prettier
- **Type Checking**: TypeScript strict mode
- **Git Hooks**: Husky + lint-staged

## Project Structure

```
accelyra-closing-platform/
├── packages/
│   ├── frontend/                 # React application
│   │   ├── src/
│   │   │   ├── components/       # Reusable UI components
│   │   │   │   ├── ui/           # shadcn/ui components
│   │   │   │   ├── layout/       # Layout components
│   │   │   │   └── shared/       # Shared components
│   │   │   ├── pages/            # Page components
│   │   │   │   ├── Welcome.tsx
│   │   │   │   ├── TransactionSimulator.tsx
│   │   │   │   ├── TransactionHistory.tsx
│   │   │   │   └── About.tsx
│   │   │   ├── features/         # Feature-based modules
│   │   │   │   ├── transactions/
│   │   │   │   ├── tasks/
│   │   │   │   └── parties/
│   │   │   ├── lib/              # Utilities
│   │   │   │   ├── api.ts        # API client
│   │   │   │   └── utils.ts
│   │   │   ├── hooks/            # Custom React hooks
│   │   │   ├── types/            # TypeScript types
│   │   │   ├── App.tsx           # Root component
│   │   │   └── main.tsx          # Entry point
│   │   ├── public/               # Static assets
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   │
│   └── backend/                  # Node.js/Express API
│       ├── src/
│       │   ├── routes/           # API routes
│       │   │   ├── transactions.ts
│       │   │   ├── tasks.ts
│       │   │   └── parties.ts
│       │   ├── services/         # Business logic
│       │   │   └── stateMachine.ts
│       │   ├── middleware/       # Express middleware
│       │   ├── lib/              # Utilities
│       │   ├── types/            # TypeScript types
│       │   └── index.ts          # Entry point
│       ├── prisma/
│       │   ├── schema.prisma     # Database schema
│       │   ├── migrations/       # Migration files
│       │   └── seed.ts           # Seed data
│       ├── package.json
│       └── tsconfig.json
│
├── legacy/                       # Old Streamlit code (archived)
│   ├── backend/                  # Original FastAPI
│   └── frontend/                 # Original Streamlit
│
├── package.json                  # Workspace root
├── pnpm-workspace.yaml           # pnpm workspace config
└── README.md                     # Updated documentation
```

## Migration Strategy

### Phase 1: Project Setup ✓
1. Set up monorepo structure with pnpm workspaces
2. Initialize React frontend with Vite + TypeScript
3. Initialize Node.js backend with Express + TypeScript
4. Set up Prisma with PostgreSQL
5. Configure ESLint, Prettier, and TypeScript
6. Set up development environment

### Phase 2: Backend Migration
1. **Define Prisma Schema** (map from SQLAlchemy models)
   - Transaction model
   - Task model
   - Party model
   - Document model (with enums)

2. **Migrate State Machine**
   - Convert Python state machine to TypeScript
   - Implement stage transition logic
   - Add validation rules

3. **Migrate API Endpoints**
   - Transaction CRUD operations
   - Stage advancement logic
   - Earnest money & funds verification
   - Task management
   - Party management

4. **Database Seeding**
   - Port seed_data.py to Prisma seed script
   - Generate demo transactions

### Phase 3: Frontend Migration
1. **Set up Base Layout & Routing**
   - App shell with navigation
   - React Router configuration
   - Responsive layout

2. **Create Shared Components**
   - StageProgressBar
   - TransactionCard
   - TaskList
   - ActivityLog
   - Buttons, forms, modals (shadcn/ui)

3. **Migrate Pages**
   - **Welcome Page**: Hero section, quick start, feature overview
   - **Transaction Simulator**: Form, scenario selector, stage visualizer
   - **Transaction History**: Filters, transaction list, detail view
   - **About Page**: Company info, comparison table

4. **Set up Data Fetching**
   - Configure React Query
   - Create API client hooks
   - Implement optimistic updates

### Phase 4: Polish & Enhancement
1. **UI/UX Improvements**
   - Modern design with Tailwind CSS
   - Smooth transitions and animations
   - Loading states and error handling
   - Toast notifications

2. **Testing**
   - Backend API tests (Jest + Supertest)
   - Frontend component tests (Vitest + Testing Library)
   - E2E tests (Playwright)

3. **Documentation**
   - API documentation (OpenAPI/Swagger)
   - Component documentation (Storybook - optional)
   - Updated README with new setup instructions

4. **Deployment Configuration**
   - Docker setup for both services
   - Environment variable management
   - CI/CD pipeline

## Data Model Migration

### Transaction Model Mapping

**SQLAlchemy (Python) → Prisma (TypeScript)**

```typescript
model Transaction {
  id                      String   @id @default("TXN-{year}-{seq}")

  // Property Details
  propertyAddress         String
  propertyType            PropertyType
  propertySqft            Int?
  propertyBedrooms        Int?
  propertyBathrooms       Float?
  propertyYearBuilt       Int?

  // Financial
  purchasePrice           Float
  downPayment             Float?
  loanAmount              Float?
  earnestMoneyAmount      Float?
  earnestMoneyStatus      EarnestMoneyStatus @default(PENDING)
  earnestMoneyDepositedAt DateTime?
  earnestMoneyClearedAt   DateTime?
  fundsVerified           Boolean @default(false)
  fundsVerifiedAt         DateTime?
  fundsVerifiedBy         String?

  // Workflow State
  currentStage            TransactionStage @default(OFFER_ACCEPTED)
  stageHistory            Json @default([])
  stageStartedAt          DateTime @default(now())

  // Timeline
  createdAt               DateTime @default(now())
  estimatedClosingDate    DateTime?
  actualClosingDate       DateTime?

  // Relationships
  buyerId                 String
  buyer                   Party @relation("BuyerTransactions", fields: [buyerId], references: [id])
  sellerId                String
  seller                  Party @relation("SellerTransactions", fields: [sellerId], references: [id])

  // ... other relationships
  tasks                   Task[]
  documents               Document[]

  // Metadata
  notes                   String?
  priority                Priority @default(NORMAL)
}

enum TransactionStage {
  OFFER_ACCEPTED
  TITLE_SEARCH
  UNDERWRITING
  CLEAR_TO_CLOSE
  FINAL_DOCUMENTS
  FUNDING_SIGNING
  RECORDING_COMPLETE
}
```

## API Endpoint Migration

### FastAPI → Express.js

**Before (FastAPI - Python):**
```python
@router.post("/transactions")
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    # Logic
    return transaction_dict
```

**After (Express - TypeScript):**
```typescript
router.post("/transactions", async (req: Request, res: Response) => {
  const transactionData = transactionCreateSchema.parse(req.body);
  const transaction = await prisma.transaction.create({
    data: transactionData
  });
  return res.json(transaction);
});
```

## UI Component Migration Examples

### Before (Streamlit):
```python
st.title("🏠 Welcome to Accelyra")
st.markdown("### Autonomous Real Estate Closing Platform")

if st.button("Start Simulation"):
    # logic
```

### After (React + TypeScript):
```tsx
export function Welcome() {
  return (
    <div className="container mx-auto px-4">
      <h1 className="text-4xl font-bold">🏠 Welcome to Accelyra</h1>
      <h2 className="text-2xl text-gray-600">
        Autonomous Real Estate Closing Platform
      </h2>

      <Button onClick={handleStartSimulation}>
        Start Simulation
      </Button>
    </div>
  );
}
```

## Key Improvements

### 1. **Performance**
   - React's virtual DOM for efficient updates
   - Code splitting and lazy loading
   - Optimized bundle size with Vite
   - React Query caching for API responses

### 2. **Developer Experience**
   - Type safety across entire stack
   - Hot module replacement (HMR)
   - Better debugging tools
   - IntelliSense and autocomplete

### 3. **User Experience**
   - SPA (no page reloads)
   - Smooth transitions and animations
   - Better responsive design
   - Modern UI components

### 4. **Scalability**
   - Component reusability
   - Feature-based architecture
   - Easier to add new pages/features
   - Better code organization

### 5. **Deployment**
   - Separate frontend and backend deployments
   - Frontend on Vercel/Netlify (static)
   - Backend on Railway/Render/AWS
   - Better CDN utilization

## Timeline Estimate

- **Phase 1 (Setup)**: 1-2 days
- **Phase 2 (Backend)**: 3-4 days
- **Phase 3 (Frontend)**: 5-7 days
- **Phase 4 (Polish)**: 2-3 days

**Total**: ~2 weeks for full migration

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Data loss during migration | Keep original SQLite database, run both systems in parallel initially |
| Feature parity gaps | Comprehensive checklist of all Streamlit features to migrate |
| Performance issues | Load testing, React Query caching, proper indexing |
| Learning curve for new stack | Good documentation, TypeScript types for guidance |

## Next Steps

1. Review and approve this migration plan
2. Choose UI component library (recommend shadcn/ui)
3. Decide on state machine library for TypeScript
4. Begin Phase 1: Project setup

## Questions for Consideration

1. **Backend**: Do you want to keep FastAPI (Python) or migrate to Node.js/Express (TypeScript)?
   - *Recommendation*: Migrate to Node.js for full TypeScript stack, better integration

2. **UI Library**: shadcn/ui (Tailwind-based) vs Material-UI vs Ant Design?
   - *Recommendation*: shadcn/ui for modern, customizable components

3. **Database**: Continue with SQLite for dev, or switch to PostgreSQL for both dev/prod?
   - *Recommendation*: PostgreSQL everywhere with Docker for dev environment

4. **Monorepo**: Use pnpm workspaces, Turborepo, or Nx?
   - *Recommendation*: pnpm workspaces (simple, fast, no extra complexity)

---

**Ready to proceed?** Let me know if you'd like to start with Phase 1, or if you have any questions or changes to this plan!
