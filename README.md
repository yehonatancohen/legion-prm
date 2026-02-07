# Legion PRM - Distributed Agent Management Platform

A comprehensive platform for managing distributed promotional agents, campaigns, contact pools, and tracking performance through unique referral links.

## 🏗️ Architecture

```
legion-prm/
├── backend/           # FastAPI Python backend
├── admin-portal/      # Next.js admin dashboard (port 3000)
├── agent-portal/      # Next.js agent dashboard (port 3001)
└── docker-compose.yaml
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, SQLAlchemy (async), PostgreSQL, Redis, Alembic |
| **Admin Portal** | Next.js 16, React 19, TailwindCSS 4, Recharts |
| **Agent Portal** | Next.js 16, React 19, TailwindCSS 4 |
| **Auth** | JWT tokens with Argon2 password hashing |

## ✨ Features

### Admin Portal
- 📊 **Dashboard Analytics** - Campaign performance, agent metrics, conversion tracking
- 👥 **Agent Management** - Create, manage, and monitor promotional agents
- 📋 **Campaign Management** - Create campaigns with budget caps and payout configuration
- 📇 **Contact Pool** - Upload and manage contact lists with VCF generation
- 🔗 **Trackable Links** - Generate unique referral links per agent
- 💰 **Wallet & Payouts** - Track agent earnings and manage payments

### Agent Portal
- 🔗 **Personal Referral Links** - Unique trackable links for each campaign
- 📊 **Performance Dashboard** - View personal stats, score, and earnings
- 📱 **Contact Downloads** - Download assigned contacts as VCF files
- 💼 **Wallet Balance** - Track earnings and pending payouts

### Backend Services
- 🔀 **Link Redirect Service** - Fast redirects with analytics tracking
- 📈 **Analytics Engine** - Track clicks, conversions, and attribution
- 📤 **Export Service** - Generate Excel/VCF exports
- 🔐 **Authentication** - Secure JWT-based auth with role management

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yehonatancohen/legion-prm.git
cd legion-prm

# Start all services
docker-compose up -d --build

# Run database migrations
docker-compose exec backend alembic upgrade head

# Seed demo data (optional)
docker-compose exec backend python seed.py
```

**Access Points:**
- Admin Portal: http://localhost:3000
- Agent Portal: http://localhost:3001
- API Docs: http://localhost:8000/docs
- API Base: http://localhost:8000

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup (Admin Portal)
```bash
cd admin-portal

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Start development server
npm run dev
```

#### Frontend Setup (Agent Portal)
```bash
cd agent-portal

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Start development server (uses port 3001)
npm run dev -- -p 3001
```

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | *required* |
| `POSTGRES_SERVER` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `POSTGRES_DB` | Database name | `promotion_manager` |
| `DATABASE_URL` | Full database URL (overrides above) | - |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | *required for production* |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## 📁 Project Structure

### Backend (`/backend`)
```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/     # Route handlers
│   │   └── deps.py        # Dependencies (auth, db)
│   ├── core/
│   │   ├── config.py      # Settings management
│   │   ├── database.py    # Database connection
│   │   └── security.py    # Auth utilities
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── alembic/               # Database migrations
├── seed.py                # Demo data seeder
└── requirements.txt
```

### Admin Portal (`/admin-portal`)
```
admin-portal/
└── src/
    ├── app/               # Next.js pages (App Router)
    │   ├── dashboard/     # Main dashboard
    │   ├── agents/        # Agent management
    │   ├── campaigns/     # Campaign management
    │   └── contacts/      # Contact pool management
    ├── components/        # Reusable UI components
    └── lib/               # Utilities
```

### Agent Portal (`/agent-portal`)
```
agent-portal/
└── src/
    ├── app/               # Next.js pages (App Router)
    │   ├── dashboard/     # Agent dashboard
    │   ├── campaigns/     # Available campaigns
    │   └── login/         # Authentication
    ├── components/        # Reusable UI components
    └── lib/               # Utilities
```

## 🗄️ Database Schema

### Core Models
- **Tenant** - Multi-tenant organization support
- **User** - Users with roles (ADMIN, AGENT)
- **Campaign** - Promotional campaigns with budgets
- **Assignment** - Agent-Campaign assignments with unique links
- **Click/Conversion** - Analytics tracking
- **ContactPool/ContactEntry** - Contact list management

## 🔗 API Endpoints

### Authentication
- `POST /api/v1/auth/token` - Login and get JWT token

### Admin Routes
- `GET /api/v1/admin/dashboard` - Dashboard statistics
- `GET/POST /api/v1/admin/agents` - Agent management
- `GET/POST /api/v1/admin/campaigns` - Campaign management
- `GET /api/v1/admin/analytics` - Analytics data

### Agent Routes
- `GET /api/v1/agent/me` - Current agent profile
- `GET /api/v1/agent/assignments` - Agent's campaign assignments
- `GET /api/v1/agent/wallet` - Wallet balance and history

### Contacts
- `POST /api/v1/contacts/pool` - Create contact pool
- `POST /api/v1/contacts/pool/{id}/upload` - Upload contacts (Excel/CSV)
- `GET /api/v1/contacts/pool/{id}/vcf` - Download contacts as VCF

### Redirect
- `GET /r/{short_code}` - Trackable redirect link

## 🧪 Development

### Running Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Hot-Reloading
- **Backend**: Auto-reloads on Python file changes (with `--reload`)
- **Frontend**: Next.js hot module replacement enabled by default

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `db` | 5432 | PostgreSQL 16 database |
| `redis` | 6379 | Redis cache |
| `backend` | 8000 | FastAPI application |
| `admin-portal` | 3000 | Admin Next.js app |
| `agent-portal` | 3001 | Agent Next.js app |

## 📜 License

This project is proprietary software. All rights reserved.

## 👥 Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

---

Built with ❤️ for distributed promotional team management
