# SACCO API - Comprehensive Features Implementation

This document provides a complete overview of all the new features implemented in the SACCO API.

## Table of Contents
1. [Withdrawal Feature](#withdrawal-feature)
2. [Fund Transfer](#fund-transfer)
3. [Loan Management](#loan-management)
4. [Share Purchase & Dividends](#share-purchase--dividends)
5. [Notifications](#notifications)
6. [Mobile Money Integration](#mobile-money-integration)
7. [Configuration](#configuration)

---

## Withdrawal Feature

### Service: `execute_savings_withdrawal_with_ledger()`
**Location**: `app/services/transaction_ledger_service.py`

Processes withdrawal from a savings account with complete double-entry ledger posting.

### Endpoint
```
POST /api/v1/savings/withdraw
```

### Request Body
```json
{
  "account_id": "uuid",
  "amount": 1000.00,
  "reference": "WTH-2026-001",
  "payment_channel_code": "CASH",
  "description": "Withdrawal for personal use"
}
```

### Payment Channels
- `CASH`: Cash Vault withdrawal
- `BANK`: Bank transfer withdrawal
- `MOBILE_MONEY`: Mobile money withdrawal

### Ledger Entries
- **DEBIT**: Cash/Asset Account (reduces asset balance)
- **CREDIT**: Member Savings Liability Account (reduces member balance)

### Features
✅ Automatic balance validation
✅ Double-entry ledger posting
✅ Transaction record creation
✅ Email notification to member
✅ SMS notification to member

### Response
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "amount": 1000.00,
  "balance_after": 5000.00,
  "reference": "WTH-2026-001",
  "description": "Withdrawal for personal use",
  "transaction_date": "2026-05-24",
  "created_at": "2026-05-24T10:30:00Z"
}
```

---

## Fund Transfer

### Service: `execute_fund_transfer_with_ledger()`
**Location**: `app/services/transaction_ledger_service.py`

Transfers funds between two member savings accounts with complete ledger posting.

### Endpoint
```
POST /api/v1/savings/transfer
```

### Request Body
```json
{
  "from_account_id": "uuid",
  "to_account_id": "uuid",
  "amount": 500.00,
  "reference": "TRF-2026-001",
  "description": "Payment to John"
}
```

### Ledger Entries
- **DEBIT**: Receiver's Savings Liability (increases receiver balance)
- **CREDIT**: Sender's Savings Liability (decreases sender balance)

### Features
✅ Dual-account locking for concurrency
✅ Sender balance validation
✅ Balanced ledger posting
✅ Separate transaction records for both accounts
✅ Notifications to both sender and receiver

### Response
```json
{
  "status": "success",
  "from_account": "SAV-001",
  "to_account": "SAV-002",
  "amount": 500.00,
  "reference": "TRF-2026-001"
}
```

---

## Loan Management

### 1. Loan Application

#### Endpoint
```
POST /api/v1/loans-extended/applications
```

#### Request Body
```json
{
  "product_id": "uuid",
  "requested_amount": 50000.00,
  "proposed_term_months": 12,
  "purpose": "Business expansion",
  "guarantor_ids": ["uuid1", "uuid2"],
  "collateral_description": "Plot LR No. 1234"
}
```

#### Validation
- Amount within product min/max limits
- Term within product min/max months
- Minimum guarantors met if required
- Collateral provided if required

---

### 2. Loan Approval

#### Service: `approve_loan_application_with_ledger()`
**Location**: `app/services/loan_ledger_service.py`

#### Endpoint
```
POST /api/v1/loans-extended/applications/{application_id}/approve
```

#### Request Body
```json
{
  "application_id": "uuid",
  "approved_amount": 45000.00
}
```

#### What It Does
1. Validates application status (must be PENDING)
2. Validates approved amount ≤ requested amount
3. Creates Loan record with ACTIVE status
4. Generates repayment schedule
5. Creates ledger entries
6. Sends approval notifications (email + SMS)

#### Ledger Entries
- **DEBIT**: Cash/Loan Disbursement Account
- **CREDIT**: Loan Receivable Account

#### Features
✅ Automatic repayment schedule generation
✅ Interest calculation (reducing balance/flat rate)
✅ Application status transition
✅ Loan record creation
✅ Email & SMS notifications

---

### 3. Loan Repayment

#### Service: `process_loan_repayment_with_ledger()`
**Location**: `app/services/loan_ledger_service.py`

#### Endpoint
```
POST /api/v1/loans-extended/{loan_id}/repay
```

#### Request Body
```json
{
  "loan_id": "uuid",
  "amount": 5000.00,
  "reference": "REPAY-2026-001",
  "payment_channel_code": "BANK"
}
```

#### Payment Allocation
1. **Interest Payment First**: Accrued interest is paid first
2. **Principal Payment**: Remaining amount reduces principal
3. **Automatic Completion**: Loan marked COMPLETED when balance = 0

#### Ledger Entries
- **DEBIT**: Cash/Asset Account (increases asset)
- **CREDIT**: Loan Receivable Account (decreases receivable - principal)
- **CREDIT**: Interest Income Account (records interest earned)

#### Features
✅ Intelligent payment allocation (interest → principal)
✅ Daily interest calculation
✅ Automatic loan completion
✅ Transaction tracking
✅ Payment confirmation notifications

---

### 4. Late Payment Penalty

#### Service: `apply_late_payment_penalty()`
**Location**: `app/services/loan_ledger_service.py`

Applies penalty for late loan payments (configurable per product).

#### Ledger Entries
- **DEBIT**: Penalty Income Account
- **CREDIT**: Loan Receivable (penalty accrual)

---

## Share Purchase & Dividends

### 1. Purchase Shares

#### Service: `purchase_shares_with_ledger()`
**Location**: `app/services/shares_ledger_service.py`

#### Endpoint
```
POST /api/v1/shares-extended/purchase
```

#### Request Body
```json
{
  "product_id": "uuid",
  "num_shares": 100,
  "price_per_share": 1000.00,
  "reference": "SHP-2026-001",
  "payment_channel_code": "BANK"
}
```

#### Validation
- Shares ≥ product minimum
- Shares ≤ product maximum (if set)
- Sufficient payment method balance

#### Ledger Entries
- **DEBIT**: Cash/Asset Account (from payment)
- **CREDIT**: Share Capital Account (equity increase)

#### Features
✅ Automatic share account creation if needed
✅ Share balance updates
✅ Total value calculation (shares × price)
✅ Transaction recording
✅ Email & SMS notifications

#### Response
```json
{
  "status": "success",
  "account": {
    "id": "uuid",
    "shares_held": 100,
    "total_value": 100000.00
  },
  "transaction": {
    "id": "uuid",
    "shares": 100,
    "total_amount": 100000.00
  }
}
```

---

### 2. Dividend Declaration

#### Service: `declare_dividend()`
**Location**: `app/services/shares_ledger_service.py`

#### Endpoint
```
POST /api/v1/shares-extended/dividends/declare
```

#### Request Body
```json
{
  "product_id": "uuid",
  "period_label": "FY2026",
  "period_start": "2026-01-01",
  "period_end": "2026-12-31",
  "rate_percent": 5.0
}
```

#### Features
✅ Automatic total dividend calculation
✅ Status starts as DRAFT
✅ Can be moved to DECLARED for distribution

---

### 3. Dividend Distribution

#### Service: `calculate_and_distribute_dividends()`
**Location**: `app/services/shares_ledger_service.py`

#### Endpoint
```
POST /api/v1/shares-extended/dividends/{dividend_id}/distribute
```

#### Calculation
```
Dividend per Shareholder = shares_held × nominal_value × (rate_percent / 100)
```

#### Ledger Entries (per shareholder)
- **DEBIT**: Dividend Expense Account
- **CREDIT**: Dividends Payable Account

#### Features
✅ Automatic calculation for all shareholders
✅ Skips zero-balance accounts
✅ Creates separate ledger entry per payment
✅ Updates dividend status to DISTRIBUTED
✅ Notifications to all recipients

---

## Notifications

### Email Notifications

**Service**: `EmailNotificationService`
**Location**: `app/services/email_notification_service.py`

#### Configured SMTP Settings
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
```

#### Notification Types

1. **Deposit Confirmation**
   ```python
   email_service.send_deposit_confirmation(
       recipient_email="member@example.com",
       member_name="John Doe",
       account_number="SAV-001",
       amount=1000.00,
       balance_after=5000.00
   )
   ```

2. **Withdrawal Confirmation**
   ```python
   email_service.send_withdrawal_confirmation(
       recipient_email="member@example.com",
       member_name="John Doe",
       account_number="SAV-001",
       amount=500.00,
       balance_after=4500.00
   )
   ```

3. **Loan Approval**
   ```python
   email_service.send_loan_approval_notification(
       recipient_email="member@example.com",
       member_name="John Doe",
       loan_amount=50000.00,
       interest_rate=10.0,
       maturity_date="2027-05-24"
   )
   ```

4. **Fund Transfer**
   ```python
   email_service.send_transfer_notification(
       sender_email="sender@example.com",
       sender_name="Alice",
       recipient_name="Bob",
       amount=500.00,
       from_account="SAV-001",
       to_account="SAV-002"
   )
   ```

5. **Dividend Distribution**
   ```python
   email_service.send_dividend_notification(
       recipient_email="member@example.com",
       member_name="John Doe",
       dividend_amount=5000.00,
       product_name="Ordinary Shares"
   )
   ```

---

### SMS Notifications

**Service**: `SMSGatewayService`
**Location**: `app/services/sms_gateway_service.py`

#### Supported Providers
- **Africa's Talking** (Default)
- **Twilio**

#### Configuration
```python
# Africa's Talking
AFRICAS_TALKING_API_KEY = "your-api-key"
AFRICAS_TALKING_SENDER_ID = "SACCO"

# OR Twilio
TWILIO_ACCOUNT_SID = "your-account-sid"
TWILIO_AUTH_TOKEN = "your-auth-token"
TWILIO_PHONE_FROM = "+1234567890"
```

#### Notification Types

1. **Deposit Notification**
   ```python
   sms_service.send_deposit_notification(
       phone_number="+254712345678",
       amount=1000.00,
       account_number="SAV-001"
   )
   ```

2. **Withdrawal Notification**
   ```python
   sms_service.send_withdrawal_notification(
       phone_number="+254712345678",
       amount=500.00,
       account_number="SAV-001",
       balance=4500.00
   )
   ```

3. **Transfer Notification**
   ```python
   sms_service.send_transfer_notification(
       phone_number="+254712345678",
       amount=500.00,
       recipient="Bob"
   )
   ```

4. **Loan Approval**
   ```python
   sms_service.send_loan_approval_notification(
       phone_number="+254712345678",
       loan_amount=50000.00,
       loan_term=12
   )
   ```

5. **Dividend Notification**
   ```python
   sms_service.send_dividend_notification(
       phone_number="+254712345678",
       dividend_amount=5000.00
   )
   ```

---

## Mobile Money Integration

### Service: `MobileMoneyProcessor`
**Location**: `app/src/api/endpoints/mobile_money.py`

### Supported Providers
- **M-Pesa** (Safaricom)
- **Airtel Money**

### Endpoint
```
POST /api/v1/mobile-money/pay
```

### Request Body
```json
{
  "phone_number": "+254712345678",
  "amount": 1000.00,
  "transaction_type": "DEPOSIT",
  "reference": "DEP-2026-001",
  "account_id": "uuid",
  "loan_id": null
}
```

### Transaction Types
1. **DEPOSIT**: Add funds to savings account
   - Required: `account_id`
   - Processes via M-Pesa STK Push

2. **WITHDRAWAL**: Withdraw from savings account
   - Required: `account_id`
   - Triggers payout to member's phone

3. **LOAN_PAYMENT**: Repay loan
   - Required: `loan_id`
   - Allocates to interest then principal

### Configuration
```python
MOBILE_MONEY_PROVIDER = "mpesa"  # or "airtel_money"
MOBILE_MONEY_API_KEY = "your-api-key"
MOBILE_MONEY_API_SECRET = "your-api-secret"
API_BASE_URL = "https://your-api.com"

# M-Pesa Specific
MPESA_BUSINESS_CODE = "174379"
MPESA_PASSWORD = "your-password"
MPESA_CONSUMER_KEY = "your-consumer-key"
MPESA_CONSUMER_SECRET = "your-consumer-secret"
```

### Callback Webhook
```
POST /api/v1/mobile-money/callback
```

Providers send payment confirmation to this endpoint.

### Features
✅ STK Push for M-Pesa
✅ Real-time payment processing
✅ Transaction status tracking
✅ Automatic ledger posting
✅ Payment confirmation callbacks

### Response
```json
{
  "id": "uuid",
  "phone_number": "+254712345678",
  "amount": 1000.00,
  "transaction_type": "DEPOSIT",
  "status": "PENDING",
  "reference": "DEP-2026-001",
  "transaction_id": "mpesa-transaction-id",
  "created_at": "2026-05-24T10:30:00Z"
}
```

---

## Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sacco_db

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# SMS Gateway - Africa's Talking
AFRICAS_TALKING_API_KEY=your-api-key
AFRICAS_TALKING_SENDER_ID=SACCO

# SMS Gateway - Twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_FROM=+1234567890

# Mobile Money - M-Pesa
MPESA_BUSINESS_CODE=174379
MPESA_PASSWORD=your-password
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret

# Mobile Money - Airtel Money
MOBILE_MONEY_API_KEY=your-api-key
MOBILE_MONEY_API_SECRET=your-api-secret

# API Configuration
API_BASE_URL=https://your-api.com
MOBILE_MONEY_PROVIDER=mpesa
```

---

## Summary of Models & Services

### New Models
- `MobileMoneyTransaction`: Tracks all mobile money transactions

### Updated Models
- All existing models leverage the new ledger services

### New Services
1. **transaction_ledger_service.py**
   - `execute_savings_withdrawal_with_ledger()`
   - `execute_fund_transfer_with_ledger()`

2. **loan_ledger_service.py**
   - `approve_loan_application_with_ledger()`
   - `process_loan_repayment_with_ledger()`
   - `apply_late_payment_penalty()`
   - `calculate_loan_repayment_schedule()`

3. **shares_ledger_service.py**
   - `purchase_shares_with_ledger()`
   - `calculate_and_distribute_dividends()`
   - `declare_dividend()`

4. **email_notification_service.py**
   - Complete email notification system with templates

5. **sms_gateway_service.py**
   - SMS integration with multiple providers

### New Endpoints
- `POST /api/v1/savings/withdraw`
- `POST /api/v1/savings/transfer`
- `POST /api/v1/loans-extended/applications`
- `POST /api/v1/loans-extended/applications/{id}/approve`
- `POST /api/v1/loans-extended/{id}/repay`
- `POST /api/v1/shares-extended/purchase`
- `POST /api/v1/shares-extended/dividends/declare`
- `POST /api/v1/shares-extended/dividends/{id}/distribute`
- `POST /api/v1/mobile-money/pay`
- `POST /api/v1/mobile-money/callback`

---

## Error Handling

All endpoints implement comprehensive error handling:

```json
{
  "detail": "Insufficient balance. Available: 1000.00, Requested: 1500.00"
}
```

Common HTTP Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation failed)
- `404`: Not Found
- `500`: Internal Server Error

---

## Next Steps

1. **Database Migration**: Create Alembic migrations for new models
2. **Testing**: Implement comprehensive unit and integration tests
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Audit Logging**: Track all financial transactions
5. **Approval Workflows**: Add multi-level approval for large transactions
6. **Reporting**: Create financial reports and statements

