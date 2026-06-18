# SACCO API

FastAPI backend for Savings and Credit Cooperative Organization (SACCO) management.

## Features

- Member and user registration (multi-tenant by organisation)
- JWT-based sign-in with login audit logs
- Savings account deposits and withdrawals
- Full domain models: loans, shares, ledger, tenants (models + Alembic migrations)

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sacco_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

Run migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/root` | Health check |
| POST | `/api/v1/users/` | Register member + user |
| POST | `/api/v1/auth/signin` | Sign in (returns JWT) |
| GET | `/api/v1/login-logs/` | List login logs |
| GET | `/api/v1/savings/accounts/{id}` | Get savings account |
| POST | `/api/v1/savings/deposit` | Deposit to savings |
| POST | `/api/v1/savings/withdraw` | Withdraw from savings |
