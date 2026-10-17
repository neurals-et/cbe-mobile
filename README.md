# cbe-mobile

Python client and interactive terminal interface for CBE Mobile Banking.

---

## Features

- **Name Lookup**: Instant recipient name resolution before transfers.
- **Transfers**: Internal CBE and EthSwitch interbank transfers.
- **Cardless ATM**: Generate 6-digit withdrawal codes for cardless cash pickup.
- **Cards Management**: View and request physical/virtual debit cards.
- **Digital Microloans**: Check eligibility, request loan disbursal, and repay.
- **Beneficiaries**: Save and manage frequent transfer contacts.
- **Split Payments**: Calculate and initiate group split bill requests.
- **Digital Receipts**: Instant verification of public transaction details.
- **Bills & Tolls**: Pay utilities (Ethio Telecom, Water, Electricity) and top up Expressway passes.
- **Forex Ticker**: Live daily exchange rates feed.
- **Terminal UI**: Interactive Textual dashboard and standalone CLI commands.

---

## Installation

```bash
pip install .
```

---

## Quickstart

### Terminal Dashboard
```bash
cbe
```

### CLI Commands
```bash
# Log in with Phone + PIN (direct JWT issuance)
cbe login --phone +251911000000 --pin 1234

# Or request an SMS OTP code
cbe login --phone +251911000000 --otp

# Verify OTP and save session JWT automatically
cbe verify-otp <code> --tfa <TFA_TOKEN>

# Set token manually
cbe config --token <your_jwt_token> --live

# Check balances
cbe balance

# Look up recipient name
cbe lookup <account_number>

# Check daily forex rates
cbe forex

# View linked cards / request new card
cbe cards
cbe cards --request VISA_DEBIT

# Microloans dashboard / request loan
cbe loans
cbe loans --request 5000

# Saved transfer contacts
cbe beneficiaries

# Verify official digital receipt
cbe receipt <transaction_id>

# Split bill with friends
cbe split 1200 --with-users 0911000001 0911000002
```

### Python Library
```python
from cbe import CBEClient

client = CBEClient()

# Check accounts
accounts = client.get_accounts()
print(accounts)

# Account lookup
info = client.lookup_account_info("1000987654321")
print(info["accountHolderName"])
```

---

## License

MIT
