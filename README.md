# cbe-mobile

Python client and interactive terminal interface for CBE Mobile Banking.

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
