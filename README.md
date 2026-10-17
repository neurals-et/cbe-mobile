# cbe-mobile

Python client and interactive terminal interface for CBE Mobile Banking.

---

## Features

- **Name Lookup**: Instant recipient name resolution before transfers.
- **Transfers**: Internal CBE and EthSwitch interbank transfers.
- **Cardless ATM**: Generate 6-digit withdrawal codes for cardless cash pickup.
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
# Set your session JWT token and credentials
cbe config --token <your_jwt_token> --live

# Check balances
cbe balance

# Look up account name
cbe lookup <account_number>

# Check daily forex rates
cbe forex
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
