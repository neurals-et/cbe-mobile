"""
CBE Mobile Banking Client
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .config import CBEConfig, DEFAULT_API_BASE, DEFAULT_FOREX_URL


class CBEClient:
    """Core API Client for CBE Mobile Banking."""

    def __init__(self, config: Optional[CBEConfig] = None, token: Optional[str] = None):
        self.config = config or CBEConfig()
        self.token = token or self.config.get("access_token", "")
        self.handshake_id = self.config.get("handshake_id", "")

    def _headers(self) -> Dict[str, str]:
        h = {
            "X-App-Id": "com.combanketh.mobilebanking",
            "X-App-Platform": "android",
            "X-App-Version": "36",
            "X-App-Device": self.config.get("device_model", "Samsung SM-A075F"),
            "X-App-Device-Id": self.config.get("device_id", "cbe_dev_e018a3"),
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if self.handshake_id:
            h["X-Handshake-ID"] = self.handshake_id
        return h

    # ------------------ Security & Auth ------------------

    def secure_handshake(self) -> Dict[str, Any]:
        """POST /api/v1/e2e/secure-handshake"""
        if self.config.get("mock_mode"):
            self.handshake_id = f"hs_{int(time.time())}"
            self.config.set("handshake_id", self.handshake_id)
            self.config.save()
            return {"status": "SUCCESS", "handshakeId": self.handshake_id, "cipher": "AES-GCM"}
        return {"status": "PENDING_GATEWAY", "reason": "Live gateway requires pinned TLS"}

    def sign_in_pin(self, phone: str, pin: str) -> Dict[str, Any]:
        """POST /v1/auth/sign-in/pin"""
        if self.config.get("mock_mode"):
            self.token = f"cbe_jwt_token_{int(time.time())}"
            self.config.set("access_token", self.token)
            self.config.set("phone_number", phone)
            self.config.save()
            return {
                "status": "SUCCESS",
                "accessToken": self.token,
                "tfaRequired": False,
                "tokenType": "Bearer",
                "expiresIn": 1800,
                "user": {
                    "phone": phone,
                    "fullName": "Abebe Kebede",
                    "customerId": "CBE9941028"
                }
            }
        return {"status": "PENDING_GATEWAY"}

    def request_otp(self, phone: str) -> Dict[str, Any]:
        """POST /v1/auth/two-factor/request-token - Send OTP to registered mobile."""
        if self.config.get("mock_mode"):
            tfa_token = f"tfa_token_{int(time.time())}"
            return {
                "status": "SUCCESS",
                "message": f"OTP sent to {phone}",
                "tfaToken": tfa_token,
                "expiresIn": 180
            }
        return {"status": "PENDING_GATEWAY"}

    def verify_otp(self, tfa_token: str, otp: str) -> Dict[str, Any]:
        """POST /v1/auth/two-factor/validate - Verify SMS OTP and obtain JWT."""
        if self.config.get("mock_mode"):
            self.token = f"cbe_jwt_verified_{int(time.time())}"
            self.config.set("access_token", self.token)
            self.config.set("mock_mode", False)  # auto-enable live once authenticated
            self.config.save()
            return {
                "status": "SUCCESS",
                "accessToken": self.token,
                "tokenType": "Bearer",
                "expiresIn": 1800
            }
        return {"status": "PENDING_GATEWAY"}

    def verify_passphrase(self, tfa_token: str, passphrase: str) -> Dict[str, Any]:
        """POST /v1/auth/two-factor/verify-token-with-passphrase - Verify user passphrase."""
        if self.config.get("mock_mode"):
            self.token = f"cbe_jwt_passphrase_{int(time.time())}"
            self.config.set("access_token", self.token)
            self.config.save()
            return {
                "status": "SUCCESS",
                "accessToken": self.token,
                "tokenType": "Bearer",
                "expiresIn": 1800
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Accounts & Name Lookup ------------------

    def lookup_account_info(self, account_number: str) -> Dict[str, Any]:
        """GET /v1/accounts/info/{accountNumber} - Look up recipient name before transfer."""
        if self.config.get("mock_mode"):
            mock_names = {
                "1000123456789": "Abebe Kebede",
                "1000987654321": "Tigist Haile",
                "1000998877665": "Abebe Kebede Biz",
                "1000554433221": "Dawit Tesfaye",
                "1000778899001": "Chaltu Bekele"
            }
            resolved = mock_names.get(account_number, f"Customer {account_number[-4:]}")
            return {
                "status": "SUCCESS",
                "accountNumber": account_number,
                "accountHolderName": resolved,
                "accountCategory": "SAVING",
                "currency": "ETB",
                "active": True
            }
        return {"status": "PENDING_GATEWAY"}

    def lookup_external_account(self, bank_code: str, account_number: str) -> Dict[str, Any]:
        """GET /v1/transfers/external-bank/account-info - EthSwitch external name lookup."""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "bankCode": bank_code,
                "accountNumber": account_number,
                "accountHolderName": f"External Recipient ({bank_code})",
                "active": True
            }
        return {"status": "PENDING_GATEWAY"}

    def get_accounts(self) -> Dict[str, Any]:
        """GET /v1/accounts/mine"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "accounts": [
                    {
                        "accountNumber": self.config.get("account_number", "1000123456789"),
                        "accountType": "SAVING",
                        "accountName": "Abebe Kebede",
                        "availableBalance": 45280.50,
                        "currency": "ETB",
                        "status": "ACTIVE"
                    },
                    {
                        "accountNumber": "1000998877665",
                        "accountType": "CURRENT",
                        "accountName": "Abebe Kebede Biz",
                        "availableBalance": 128400.00,
                        "currency": "ETB",
                        "status": "ACTIVE"
                    }
                ]
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Transfers ------------------

    def transfer_internal(self, from_account: str, to_account: str, amount: float, reason: str = "") -> Dict[str, Any]:
        """POST /v1/transfers/internal-a2a"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "transactionId": f"FT{int(time.time())}",
                "fromAccount": from_account,
                "toAccount": to_account,
                "amount": amount,
                "currency": "ETB",
                "fee": 0.00,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        return {"status": "PENDING_GATEWAY"}

    def transfer_external(self, from_account: str, bank_code: str, to_account: str, amount: float) -> Dict[str, Any]:
        """POST /v1/transfers/external-bank"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "transactionId": f"ET{int(time.time())}",
                "bank": bank_code,
                "toAccount": to_account,
                "amount": amount,
                "fee": 5.00,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ ATM Cardless Withdrawal ------------------

    def initiate_atm_withdrawal(self, account: str, amount: float) -> Dict[str, Any]:
        """POST /v1/customers/withdrawals/initiate"""
        if self.config.get("mock_mode"):
            code = f"{int(time.time()) % 1000000:06d}"
            return {
                "status": "SUCCESS",
                "withdrawalCode": code,
                "account": account,
                "amount": amount,
                "validMinutes": 120,
                "expiry": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 7200))
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Bill & Toll Road Payments ------------------

    def pay_bill(self, biller_id: str, bill_code: str, amount: float) -> Dict[str, Any]:
        """POST /v1/payment-integrations/complete-payment/"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "receiptNumber": f"CBE-BILL-{int(time.time())}",
                "biller": biller_id,
                "billCode": bill_code,
                "amount": amount,
                "currency": "ETB",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        return {"status": "PENDING_GATEWAY"}

    def tollroad_recharge(self, vehicle_plate: str, amount: float) -> Dict[str, Any]:
        """POST /v1/tollroad/recharge"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "plate": vehicle_plate,
                "rechargeAmount": amount,
                "newTollBalance": 350.00,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Live Public Forex Rates ------------------

    def get_forex_rates(self) -> Dict[str, Any]:
        """Fetch daily exchange rates from combanketh.et."""
        url = self.config.get("forex_url", DEFAULT_FOREX_URL)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
                rates = []
                if isinstance(data, list) and data:
                    latest = data[-1] if "ExchangeRate" in data[-1] else data[0]
                    for ex in latest.get("ExchangeRate", []):
                        curr = ex.get("currency", {})
                        code = curr.get("CurrencyCode") if isinstance(curr, dict) else ex.get("currency")
                        name = curr.get("CurrencyName") if isinstance(curr, dict) else code
                        rates.append({
                            "currency": code or "UNKNOWN",
                            "name": name or code,
                            "buying": ex.get("cashBuying") or ex.get("transactionalBuying") or 0.0,
                            "selling": ex.get("cashSelling") or ex.get("transactionalSelling") or 0.0
                        })
                return {"status": "SUCCESS", "source": "LIVE", "rates": rates}
        except Exception:
            return {
                "status": "SUCCESS",
                "source": "SIMULATED",
                "rates": [
                    {"currency": "USD", "name": "US DOLLAR", "buying": 125.40, "selling": 127.90},
                    {"currency": "EUR", "name": "EURO", "buying": 136.20, "selling": 138.90},
                    {"currency": "GBP", "name": "POUND STERLING", "buying": 160.10, "selling": 163.30}
                ]
            }

    # ------------------ Card Management ------------------

    def get_cards(self) -> Dict[str, Any]:
        """GET /v1/customer/cards"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "cards": [
                    {
                        "cardId": "crd_9018",
                        "cardType": "PHYSICAL_VISA",
                        "maskedNumber": "4234-XXXX-XXXX-9018",
                        "expiry": "09/28",
                        "status": "ACTIVE",
                        "linkedAccount": self.config.get("account_number")
                    },
                    {
                        "cardId": "crd_4421",
                        "cardType": "VIRTUAL_MASTERCARD",
                        "maskedNumber": "5312-XXXX-XXXX-4421",
                        "expiry": "11/27",
                        "status": "ACTIVE",
                        "linkedAccount": self.config.get("account_number")
                    }
                ]
            }
        return {"status": "PENDING_GATEWAY"}

    def request_card(self, account_number: str, card_type: str = "VISA_DEBIT") -> Dict[str, Any]:
        """POST /v1/accounts/card/request"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "referenceNumber": f"CRD-REQ-{int(time.time())}",
                "accountNumber": account_number,
                "cardType": card_type,
                "status": "SUBMITTED"
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Microloans & Credit ------------------

    def get_loan_dashboard(self) -> Dict[str, Any]:
        """GET /v1/loan/dashboard"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "eligible": True,
                "maxCreditLimit": 20000.00,
                "currentLoan": {
                    "loanId": "LN-58291",
                    "amount": 3500.00,
                    "interestRate": 2.5,
                    "dueDate": time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400 * 20)),
                    "remainingAmount": 3587.50
                }
            }
        return {"status": "PENDING_GATEWAY"}

    def request_loan(self, amount: float, term_days: int = 30) -> Dict[str, Any]:
        """POST /v1/loan/request-loan"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "loanId": f"LN-{int(time.time()) % 100000}",
                "disbursedAmount": amount,
                "account": self.config.get("account_number"),
                "termDays": term_days,
                "dueDate": time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400 * term_days)),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        return {"status": "PENDING_GATEWAY"}

    def repay_loan(self, loan_id: str, amount: float) -> Dict[str, Any]:
        """POST /v1/loan/repay-loan"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "receiptNumber": f"LN-REP-{int(time.time())}",
                "loanId": loan_id,
                "paidAmount": amount,
                "remaining": 0.00,
                "status": "CLEARED"
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Beneficiaries ------------------

    def get_beneficiaries(self) -> List[Dict[str, Any]]:
        """GET /v1/users/me/beneficiaries"""
        if self.config.get("mock_mode"):
            return [
                {"id": "b1", "name": "Tigist Haile", "accountNumber": "1000987654321", "bank": "CBE"},
                {"id": "b2", "name": "Dawit Tesfaye", "accountNumber": "1000554433221", "bank": "CBE"},
                {"id": "b3", "name": "Almaz Ayana", "accountNumber": "0911556677", "bank": "AWASH"}
            ]
        return []

    def add_beneficiary(self, account_number: str, name: str, bank: str = "CBE") -> Dict[str, Any]:
        """POST /v1/users/me/beneficiaries"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "beneficiaryId": f"b_{int(time.time())}",
                "name": name,
                "accountNumber": account_number,
                "bank": bank
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Scheduled & Split Payments ------------------

    def get_scheduled_payments(self) -> List[Dict[str, Any]]:
        """GET /v1/scheduled-payments"""
        if self.config.get("mock_mode"):
            return [
                {
                    "id": "sch_01",
                    "title": "House Rent",
                    "toAccount": "1000987654321",
                    "amount": 15000.00,
                    "frequency": "MONTHLY",
                    "nextRun": time.strftime("%Y-%m-01")
                }
            ]
        return []

    def initiate_split_payment(self, total_amount: float, participants: List[str], reason: str = "") -> Dict[str, Any]:
        """POST /v1/split-payments/init"""
        if self.config.get("mock_mode"):
            each = round(total_amount / max(1, len(participants)), 2)
            return {
                "status": "SUCCESS",
                "splitId": f"SPL-{int(time.time())}",
                "totalAmount": total_amount,
                "amountPerPerson": each,
                "participants": participants,
                "reason": reason
            }
        return {"status": "PENDING_GATEWAY"}

    # ------------------ Public Transaction Receipt Verification ------------------

    def get_transaction_receipt(self, txn_id: str) -> Dict[str, Any]:
        """GET /v1/transactions/public/transaction-detail/{txnId}"""
        if self.config.get("mock_mode"):
            return {
                "status": "SUCCESS",
                "transactionId": txn_id,
                "payer": "Abebe Kebede (1000****789)",
                "payee": "Tigist Haile (1000****321)",
                "amount": 2500.00,
                "fee": 0.00,
                "vat": 0.00,
                "paymentDate": time.strftime("%Y-%m-%d %H:%M:%S"),
                "reference": f"CBE-REF-{txn_id}",
                "verified": True
            }
        return {"status": "PENDING_GATEWAY"}
