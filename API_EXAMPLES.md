---
title: SACCO API - Quick Reference Examples
---

# SACCO API - Quick Reference Examples

## Authentication Header
All endpoints (except public ones) require:
```
Authorization: Bearer <jwt-token>
```

---

## Savings Operations

### 1. Deposit Money
```bash
curl -X POST http://localhost:8000/api/v1/savings/deposit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 5000,
    "reference": "DEP-20260524-001",
    "payment_channel_code": "CASH",
    "processed_by_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 2. Withdraw Money
```bash
curl -X POST http://localhost:8000/api/v1/savings/withdraw \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 1000,
    "reference": "WTH-20260524-001",
    "payment_channel_code": "BANK"
  }'
```

### 3. Transfer Between Accounts
```bash
curl -X POST http://localhost:8000/api/v1/savings/transfer \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_account_id": "550e8400-e29b-41d4-a716-446655440000",
    "to_account_id": "660e8400-e29b-41d4-a716-446655440001",
    "amount": 2500,
    "reference": "TRF-20260524-001"
  }'
```

### 4. Get Account Balance
```bash
curl -X GET http://localhost:8000/api/v1/savings/balance/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

### 5. Get Transaction History
```bash
curl -X GET "http://localhost:8000/api/v1/savings/transactions/550e8400-e29b-41d4-a716-446655440000?skip=0&limit=50" \
  -H "Authorization: Bearer <token>"
```

---

## Loan Operations

### 1. Create Loan Application
```bash
curl -X POST http://localhost:8000/api/v1/loans-extended/applications \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440002",
    "requested_amount": 100000,
    "proposed_term_months": 12,
    "purpose": "Business expansion",
    "guarantor_ids": [
      "550e8400-e29b-41d4-a716-446655440003"
    ]
  }'
```

### 2. Get Pending Applications (Admin)
```bash
curl -X GET "http://localhost:8000/api/v1/loans-extended/applications/pending?skip=0&limit=10" \
  -H "Authorization: Bearer <admin-token>"
```

### 3. Approve Loan Application (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/loans-extended/applications/550e8400-e29b-41d4-a716-446655440000/approve \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "550e8400-e29b-41d4-a716-446655440000",
    "approved_amount": 95000
  }'
```

### 4. Get Member Loans
```bash
curl -X GET "http://localhost:8000/api/v1/loans-extended/member/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <token>"
```

### 5. Process Loan Repayment
```bash
curl -X POST http://localhost:8000/api/v1/loans-extended/550e8400-e29b-41d4-a716-446655440000/repay \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "loan_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 8500,
    "reference": "REP-20260524-001",
    "payment_channel_code": "BANK"
  }'
```

### 6. Get Loan Repayment History
```bash
curl -X GET "http://localhost:8000/api/v1/loans-extended/550e8400-e29b-41d4-a716-446655440000/repayment-history" \
  -H "Authorization: Bearer <token>"
```

---

## Share Operations

### 1. Purchase Shares
```bash
curl -X POST http://localhost:8000/api/v1/shares-extended/purchase \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440002",
    "num_shares": 100,
    "price_per_share": 1000,
    "reference": "SHP-20260524-001",
    "payment_channel_code": "BANK"
  }'
```

### 2. Get Member Share Accounts
```bash
curl -X GET http://localhost:8000/api/v1/shares-extended/accounts/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

### 3. Get Member Shareholdings
```bash
curl -X GET http://localhost:8000/api/v1/shares-extended/holdings/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

### 4. Get Share Transactions
```bash
curl -X GET "http://localhost:8000/api/v1/shares-extended/transactions/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <token>"
```

---

## Dividend Operations

### 1. Declare Dividend (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/shares-extended/dividends/declare \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440002",
    "period_label": "FY2026",
    "period_start": "2026-01-01",
    "period_end": "2026-12-31",
    "rate_percent": 5.0
  }'
```

### 2. Distribute Dividends (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/shares-extended/dividends/550e8400-e29b-41d4-a716-446655440000/distribute \
  -H "Authorization: Bearer <admin-token>"
```

### 3. Get Product Dividends
```bash
curl -X GET http://localhost:8000/api/v1/shares-extended/dividends/product/550e8400-e29b-41d4-a716-446655440002 \
  -H "Authorization: Bearer <token>"
```

---

## Mobile Money Operations

### 1. Deposit via Mobile Money
```bash
curl -X POST http://localhost:8000/api/v1/mobile-money/pay \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+254712345678",
    "amount": 5000,
    "transaction_type": "DEPOSIT",
    "reference": "MM-DEP-20260524-001",
    "account_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 2. Withdraw via Mobile Money
```bash
curl -X POST http://localhost:8000/api/v1/mobile-money/pay \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+254712345678",
    "amount": 2000,
    "transaction_type": "WITHDRAWAL",
    "reference": "MM-WTH-20260524-001",
    "account_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 3. Pay Loan via Mobile Money
```bash
curl -X POST http://localhost:8000/api/v1/mobile-money/pay \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+254712345678",
    "amount": 8500,
    "transaction_type": "LOAN_PAYMENT",
    "reference": "MM-LPN-20260524-001",
    "loan_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 4. Get Mobile Money Transaction Status
```bash
curl -X GET http://localhost:8000/api/v1/mobile-money/transaction/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

---

## Response Examples

### Success Response (Savings Transaction)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_id": "550e8400-e29b-41d4-a716-446655440001",
  "amount": 5000.0,
  "balance_after": 25000.0,
  "reference": "DEP-20260524-001",
  "description": "Deposit via CASH",
  "transaction_date": "2026-05-24",
  "created_at": "2026-05-24T10:30:00Z"
}
```

### Error Response
```json
{
  "detail": "Insufficient balance. Available: 1000.00, Requested: 2500.00"
}
```

### Loan Application Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "member_id": "550e8400-e29b-41d4-a716-446655440001",
  "product_id": "550e8400-e29b-41d4-a716-446655440002",
  "requested_amount": 100000.0,
  "approved_amount": null,
  "status": "PENDING",
  "created_at": "2026-05-24T10:30:00Z",
  "approved_date": null
}
```

### Approved Loan Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "member_id": "550e8400-e29b-41d4-a716-446655440001",
  "product_id": "550e8400-e29b-41d4-a716-446655440002",
  "principal_amount": 95000.0,
  "outstanding_balance": 95000.0,
  "interest_rate": 10.0,
  "term_months": 12,
  "disbursal_date": "2026-05-24",
  "maturity_date": "2027-05-24",
  "status": "ACTIVE",
  "created_at": "2026-05-24T10:30:00Z"
}
```

### Share Purchase Response
```json
{
  "status": "success",
  "account": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "member_id": "550e8400-e29b-41d4-a716-446655440001",
    "product_id": "550e8400-e29b-41d4-a716-446655440002",
    "account_no": "SHA-550e8400-550e8400-e29b-41d4",
    "shares_held": 100.0,
    "total_value": 100000.0,
    "is_active": true
  },
  "transaction": {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "shares": 100.0,
    "total_amount": 100000.0
  }
}
```

### Mobile Money Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "phone_number": "+254712345678",
  "amount": 5000.0,
  "transaction_type": "DEPOSIT",
  "status": "PENDING",
  "reference": "MM-DEP-20260524-001",
  "transaction_id": "mpesa-123456789",
  "created_at": "2026-05-24T10:30:00Z"
}
```

---

## Payment Channels

Available payment channels for deposits/withdrawals/loans:
- `CASH`: Direct cash transaction
- `BANK`: Bank transfer
- `MOBILE_MONEY`: Mobile money (M-Pesa, Airtel Money, etc.)

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Successful GET/PUT/DELETE |
| 201 | Created - Successful POST |
| 400 | Bad Request - Validation failed |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server error |

---

## Notes

1. **Timestamps**: All timestamps are in UTC format (ISO 8601)
2. **Currency**: All amounts are in the base currency (e.g., KES)
3. **Concurrency**: Database uses row-level locking for concurrent access
4. **Ledger**: All transactions create double-entry ledger entries
5. **Notifications**: Email and SMS sent automatically based on configuration

---

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize Database**
   ```bash
   alembic upgrade head
   ```

4. **Run Server**
   ```bash
   uvicorn app.src.main:app --reload
   ```

5. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

