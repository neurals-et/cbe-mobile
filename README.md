# cbe-mobile

> Unofficial Python SDK and interactive Terminal User Interface (TUI) for the **Commercial Bank of Ethiopia (CBE Mobile)** application (`com.combanketh.mobilebanking`).

Maintained by [NeuralS](https://github.com/neurals-et).

---

## Features

- **Reverse-Engineered Architecture**: Full API mapping reconstructed from the official CBE Next-Gen Flutter mobile application (`package:cbe_mb_next/`, `libapp.so`).
- **Real-Time Name Resolution**: Queries recipient holder names (`/v1/accounts/info/{accountNumber}`) before executing transfers to prevent misdirected funds.
- **EthSwitch Interbank Lookup**: Interbank transfer and account lookup across Ethiopian banks (Awash, Dashen, Telebirr, Abyssinia, etc.).
- **Cardless ATM Cash Out**: Instant 6-digit withdrawal code generation (`/v1/customers/withdrawals/initiate`) for debit-cardless cash pickup.
- **Utility & Toll Road Payments**: Bill payments (Ethio Telecom, Water, Electric, DSTV) and Addis Ababa Expressway toll pass recharge.
- **Live Daily Forex Ticker**: Real-time CBE foreign currency exchange rates feed.
- **Royal CBE Themed TUI**: Rich terminal interface styled in CBE Royal Purple and Gold.

---

## Installation

```bash
pip install .
```

---

## Interactive TUI

Launch the full CBE terminal dashboard:

```bash
cbe
# or
cbe tui
```

### Shortcuts
- `r` - Refresh accounts & balances
- `q` - Quit application

---

## CLI Commands

### View Account Balances
```bash
cbe balance
```

### Look Up Recipient Name by Account Number
```bash
cbe lookup 1000987654321
```

### View Live CBE Daily Forex Rates
```bash
cbe forex
```

---

## Python SDK Usage

```python
from cbe import CBEClient

client = CBEClient()

# 1. Look up recipient name before sending money
recipient = client.lookup_account_info("1000987654321")
print(f"Holder Name: {recipient['accountHolderName']}")

# 2. Check accounts & balances
accounts = client.get_accounts()
for acc in accounts.get("accounts", []):
    print(f"{acc['accountType']}: {acc['accountNumber']} -> {acc['availableBalance']} ETB")

# 3. Generate instant cardless ATM cash-out code
atm = client.initiate_atm_withdrawal("1000123456789", 500.0)
print(f"ATM Code: {atm['withdrawalCode']} (Expires: {atm['expiry']})")

# 4. Fetch live exchange rates
forex = client.get_forex_rates()
for rate in forex.get("rates", []):
    print(f"{rate['currency']}: Buying {rate['buying']} | Selling {rate['selling']}")
```

---

## Reverse-Engineered Endpoints

| Category | Endpoint | Method | Description |
|---|---|---|---|
| **Security** | `/api/v1/e2e/secure-handshake` | `POST` | E2E encrypted handshake |
| **Auth** | `/v1/auth/sign-in/pin` | `POST` | User PIN authentication |
| **Auth** | `/v1/auth/two-factor/validate` | `POST` | SMS OTP verification |
| **Accounts** | `/v1/accounts/mine` | `GET` | List user accounts & balances |
| **Inquiry** | `/v1/accounts/info/{accountNumber}` | `GET` | **Resolve account holder name** |
| **Transfer** | `/v1/transfers/internal-a2a` | `POST` | Account-to-Account transfer |
| **Transfer** | `/v1/transfers/external-bank` | `POST` | EthSwitch interbank transfer |
| **ATM** | `/v1/customers/withdrawals/initiate` | `POST` | Generate cardless ATM cash code |
| **Bills** | `/v1/payment-integrations/complete-payment/` | `POST` | Complete utility bill payment |
| **Toll** | `/v1/tollroad/recharge` | `POST` | Top-up Expressway toll pass |

---

## License

MIT License. Developed for research and developer tooling by NeuralS.
