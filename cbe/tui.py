"""
CBE Mobile Interactive Textual TUI Application
"""

import time
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Input, Static, Label, TabbedContent, TabPane,
    Select, Switch, DataTable, Log
)
from textual.binding import Binding
import os
import sys

try:
    from .client import CBEClient
    from .config import CBEConfig
except (ImportError, ValueError):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from cbe.client import CBEClient
    from cbe.config import CBEConfig


class CBEMobileTUI(App):
    """CBE Mobile Banking Terminal Interface."""

    CSS = """
    Screen {
        background: #1a0826;
        color: #fdf4ff;
    }

    Header {
        background: #581845;
        color: #ffc300;
        text-style: bold;
    }

    Footer {
        background: #2b0b30;
        color: #fbcfe8;
    }

    .card {
        background: #2b0b30;
        border: solid #701a75;
        padding: 1 2;
        margin: 1;
    }

    .card-title {
        text-style: bold;
        color: #ffc300;
        margin-bottom: 1;
    }

    .bal-card {
        background: #4a044e;
        border: solid #ffc300;
        padding: 1 2;
        margin: 1;
        text-align: center;
    }

    .bal-val {
        color: #fde047;
        text-style: bold;
    }

    .code-box {
        background: #022c22;
        border: solid #10b981;
        padding: 1;
        margin: 1;
        text-align: center;
    }

    .code-val {
        color: #34d399;
        text-style: bold;
    }

    Button {
        margin-top: 1;
        width: 100%;
        background: #701a75;
        color: white;
    }

    Button:hover {
        background: #86198f;
    }

    Button.accent {
        background: #d97706;
    }

    Button.accent:hover {
        background: #f59e0b;
    }

    Button.success {
        background: #047857;
    }

    Button.success:hover {
        background: #059669;
    }

    Input {
        margin-bottom: 1;
        border: solid #86198f;
        background: #14051d;
        color: #fdf4ff;
    }

    Label {
        color: #f5d0fe;
        margin-top: 1;
    }

    DataTable {
        height: 11;
        border: solid #701a75;
        background: #14051d;
    }

    Log {
        height: 12;
        border: solid #701a75;
        background: #0d0214;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh_accounts", "Refresh", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = CBEConfig()
        self.client = CBEClient(self.config)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab-dash"):

            # 1. DASHBOARD
            with TabPane("Dashboard", id="tab-dash"):
                with ScrollableContainer():
                    with Horizontal():
                        with Vertical(classes="card bal-card"):
                            yield Label("Primary Savings (CBE)", classes="card-title")
                            yield Label("45,280.50 ETB", id="lbl-saving-bal", classes="bal-val")
                            yield Label("Acc: 1000123456789", id="lbl-saving-num")

                        with Vertical(classes="card bal-card"):
                            yield Label("Current / Commercial", classes="card-title")
                            yield Label("128,400.00 ETB", id="lbl-current-bal", classes="bal-val")
                            yield Label("Acc: 1000998877665", id="lbl-current-num")

                    with Container(classes="card"):
                        yield Label("Customer Profile", classes="card-title")
                        yield Label(f"Phone: {self.config.get('phone_number')} | Customer: Abebe Kebede", id="lbl-cust-info")
                        yield Button("Refresh Balances", id="btn-refresh-dash")

                    with Container(classes="card"):
                        yield Label("Recent Activity Stream", classes="card-title")
                        yield Log(id="log-dash")

            # 2. TRANSFERS & CONTACTS
            with TabPane("Transfers", id="tab-transfers"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("CBE Account-to-Account (Internal Transfer)", classes="card-title")
                        yield Label("Destination CBE Account:")
                        yield Input(value="1000987654321", id="inp-cbe-to")
                        yield Label("Recipient Name: [Pending Lookup]", id="lbl-cbe-name", classes="card-title")
                        with Horizontal():
                            yield Button("Lookup Account Name", id="btn-lookup-cbe")
                            yield Button("Send CBE Transfer", id="btn-send-cbe", classes="accent")
                        yield Label("Amount (ETB):")
                        yield Input(placeholder="500.00", id="inp-cbe-amt")
                        yield Label("Transfer Reason:")
                        yield Input(placeholder="Payment for goods", id="inp-cbe-reason")

                    with Container(classes="card"):
                        yield Label("Other Bank Transfer (EthSwitch)", classes="card-title")
                        yield Label("Target Bank:")
                        yield Select([("Awash Bank", "AWASH"), ("Dashen Bank", "DASHEN"), ("Bank of Abyssinia", "BOA"), ("Telebirr", "TELEBIRR")], id="sel-ext-bank")
                        yield Label("Account / Phone Number:")
                        yield Input(placeholder="0911223344", id="inp-ext-acc")
                        yield Label("Recipient Name: [Pending Lookup]", id="lbl-ext-name", classes="card-title")
                        with Horizontal():
                            yield Button("Lookup Other Bank Name", id="btn-lookup-ext")
                            yield Button("Send External Transfer", id="btn-send-ext")
                        yield Label("Amount (ETB):")
                        yield Input(placeholder="1000.00", id="inp-ext-amt")

            # 3. ATM CASH-OUT (CARDLESS)
            with TabPane("Cardless ATM", id="tab-atm"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Instant ATM Cardless Withdrawal Code", classes="card-title")
                        yield Label("Withdraw cash from any CBE ATM without a physical debit card.")
                        yield Label("Select Source Account:")
                        yield Select([("Primary Savings (1000123456789)", "1000123456789"), ("Current (1000998877665)", "1000998877665")], id="sel-atm-acc")
                        yield Label("Amount (ETB):")
                        yield Input(placeholder="500.00", id="inp-atm-amt")
                        yield Button("Generate 6-Digit Withdrawal Code", id="btn-atm-gen", classes="accent")

                    with Vertical(classes="code-box"):
                        yield Label("ATM Withdrawal Code:", classes="card-title")
                        yield Label("------", id="lbl-atm-code", classes="code-val")
                        yield Label("Valid for 2 hours at any CBE ATM.", id="lbl-atm-expiry")

            # 4. CARDS MANAGEMENT
            with TabPane("Cards", id="tab-cards"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Linked CBE Debit Cards", classes="card-title")
                        yield DataTable(id="tbl-cards")
                        yield Button("Refresh Cards", id="btn-refresh-cards")

                    with Container(classes="card"):
                        yield Label("Request New Debit Card", classes="card-title")
                        yield Label("Card Brand & Type:")
                        yield Select([("Visa Physical Debit Card", "VISA_DEBIT"), ("Mastercard Virtual Card", "MASTERCARD_VIRTUAL")], id="sel-new-card")
                        yield Button("Submit Card Request", id="btn-card-req", classes="success")

            # 5. BILL PAY & TOLL ROAD
            with TabPane("Bill Pay & Toll", id="tab-bills"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Utility & Bill Payments", classes="card-title")
                        yield Label("Select Biller:")
                        yield Select([("Ethio Telecom Airtime / Bill", "ETHIO_TEL"), ("Addis Ababa Water", "AAWSA"), ("Ethiopian Electric Utility", "EEU"), ("DSTV Subscription", "DSTV")], id="sel-biller")
                        yield Label("Bill Reference / Account Number:")
                        yield Input(placeholder="0911000000", id="inp-bill-ref")
                        yield Label("Amount (ETB):")
                        yield Input(placeholder="100.00", id="inp-bill-amt")
                        yield Button("Pay Bill", id="btn-bill-pay")

                    with Container(classes="card"):
                        yield Label("Expressway Toll Road Top-up", classes="card-title")
                        yield Label("Vehicle Plate Number:")
                        yield Input(placeholder="A23456AA", id="inp-toll-plate")
                        yield Label("Amount (ETB):")
                        yield Input(placeholder="300.00", id="inp-toll-amt")
                        yield Button("Recharge Toll Pass", id="btn-toll-pay")

            # 6. DIGITAL MICROLOANS
            with TabPane("Loans & Split", id="tab-loans"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("CBE Digital Microloan (Credit)", classes="card-title")
                        yield Label("Status: ELIGIBLE | Credit Line: 20,000.00 ETB", id="lbl-loan-status")
                        yield Label("Active Loan: LN-58291 | 3,587.50 ETB due soon", id="lbl-loan-active")
                        yield Label("Loan Amount to Request (ETB):")
                        yield Input(placeholder="5000.00", id="inp-loan-req-amt")
                        with Horizontal():
                            yield Button("Disburse Loan", id="btn-loan-disburse", classes="success")
                            yield Button("Repay Active Loan", id="btn-loan-repay", classes="accent")

                    with Container(classes="card"):
                        yield Label("Split Bill Calculator", classes="card-title")
                        yield Label("Total Amount (ETB):")
                        yield Input(placeholder="1200.00", id="inp-split-amt")
                        yield Label("Participants (comma separated):")
                        yield Input(placeholder="0911000001, 0911000002, 0911000003", id="inp-split-users")
                        yield Button("Create Split Request", id="btn-split-submit")
                        yield Label("", id="lbl-split-result")

            # 7. FOREX RATES
            with TabPane("Forex Rates", id="tab-forex"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("CBE Daily Forex Exchange Rates (Live)", classes="card-title")
                        yield DataTable(id="tbl-forex")
                        yield Button("Fetch Latest Rates", id="btn-fetch-forex")

            # 8. SETTINGS
            with TabPane("Settings", id="tab-settings"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Connection & Security", classes="card-title")
                        yield Label("Gateway Base URL:")
                        yield Input(value=self.config.get("api_base"), id="inp-cfg-base")
                        yield Label("Phone Number:")
                        yield Input(value=self.config.get("phone_number"), id="inp-cfg-phone")
                        yield Label("Device ID:")
                        yield Input(value=self.config.get("device_id"), id="inp-cfg-dev")
                        yield Label("Session JWT Token:")
                        yield Input(value=self.config.get("access_token"), id="inp-cfg-token", password=True)
                        with Horizontal():
                            yield Label("Mock Mode: ")
                            yield Switch(value=self.config.get("mock_mode"), id="sw-cfg-mock")
                        yield Button("Save Configuration", id="btn-cfg-save")

        yield Footer()

    def on_mount(self) -> None:
        forex_table = self.query_one("#tbl-forex", DataTable)
        forex_table.add_columns("Currency", "Buying (ETB)", "Selling (ETB)")

        cards_table = self.query_one("#tbl-cards", DataTable)
        cards_table.add_columns("Type", "Card Number", "Expiry", "Status")

        self.action_fetch_forex()
        self.action_refresh_cards()
        self.log_msg("CBE Mobile TUI initialized.")

    def log_msg(self, msg: str) -> None:
        try:
            self.query_one("#log-dash", Log).write_line(f"[{time.strftime('%H:%M:%S')}] {msg}")
        except Exception:
            pass

    def action_fetch_forex(self) -> None:
        res = self.client.get_forex_rates()
        rates = res.get("rates", [])
        table = self.query_one("#tbl-forex", DataTable)
        table.clear()
        if isinstance(rates, list):
            for r in rates:
                table.add_row(r.get("currency", "-"), f"{r.get('buying', 0):.2f}", f"{r.get('selling', 0):.2f}")
        self.log_msg("Daily exchange rates updated.")

    def action_refresh_cards(self) -> None:
        res = self.client.get_cards()
        cards = res.get("cards", [])
        table = self.query_one("#tbl-cards", DataTable)
        table.clear()
        for c in cards:
            table.add_row(c.get("cardType", "-"), c.get("maskedNumber", "-"), c.get("expiry", "-"), c.get("status", "-"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-refresh-dash":
            accs = self.client.get_accounts().get("accounts", [])
            if len(accs) >= 2:
                self.query_one("#lbl-saving-bal", Label).update(f"{accs[0]['availableBalance']:,.2f} ETB")
                self.query_one("#lbl-current-bal", Label).update(f"{accs[1]['availableBalance']:,.2f} ETB")
            self.log_msg("Balances refreshed.")

        elif bid == "btn-lookup-cbe":
            to_acc = self.query_one("#inp-cbe-to", Input).value or "1000987654321"
            res = self.client.lookup_account_info(to_acc)
            name = res.get("accountHolderName", "Not Found")
            self.query_one("#lbl-cbe-name", Label).update(f"Recipient Name: {name}")
            self.log_msg(f"Looked up CBE Account {to_acc} -> {name}")

        elif bid == "btn-lookup-ext":
            bank = self.query_one("#sel-ext-bank", Select).value or "AWASH"
            to_acc = self.query_one("#inp-ext-acc", Input).value or "0911000000"
            res = self.client.lookup_external_account(bank, to_acc)
            name = res.get("accountHolderName", "Not Found")
            self.query_one("#lbl-ext-name", Label).update(f"Recipient Name: {name}")
            self.log_msg(f"Looked up {bank} Account {to_acc} -> {name}")

        elif bid == "btn-send-cbe":
            to_acc = self.query_one("#inp-cbe-to", Input).value or "1000987654321"
            amt = float(self.query_one("#inp-cbe-amt", Input).value or "0")
            r = self.client.transfer_internal(self.config.get("account_number"), to_acc, amt)
            self.log_msg(f"Transfer {amt:.2f} ETB to CBE Acc {to_acc}: {r.get('status')} (TxID: {r.get('transactionId')})")

        elif bid == "btn-send-ext":
            bank = self.query_one("#sel-ext-bank", Select).value
            to_acc = self.query_one("#inp-ext-acc", Input).value
            amt = float(self.query_one("#inp-ext-amt", Input).value or "0")
            r = self.client.transfer_external(self.config.get("account_number"), bank, to_acc, amt)
            self.log_msg(f"External Transfer to {bank} ({to_acc}): {r.get('status')} (TxID: {r.get('transactionId')})")

        elif bid == "btn-atm-gen":
            acc = self.query_one("#sel-atm-acc", Select).value
            amt = float(self.query_one("#inp-atm-amt", Input).value or "500")
            r = self.client.initiate_atm_withdrawal(acc, amt)
            code = r.get("withdrawalCode", "------")
            self.query_one("#lbl-atm-code", Label).update(code)
            self.query_one("#lbl-atm-expiry", Label).update(f"Valid until: {r.get('expiry')}")
            self.log_msg(f"Generated cardless ATM code: {code} for {amt} ETB")

        elif bid == "btn-refresh-cards":
            self.action_refresh_cards()
            self.log_msg("Cards list refreshed.")

        elif bid == "btn-card-req":
            ctype = self.query_one("#sel-new-card", Select).value
            r = self.client.request_card(self.config.get("account_number"), ctype)
            self.log_msg(f"Requested card ({ctype}): {r.get('referenceNumber')}")

        elif bid == "btn-bill-pay":
            biller = self.query_one("#sel-biller", Select).value
            ref = self.query_one("#inp-bill-ref", Input).value
            amt = float(self.query_one("#inp-bill-amt", Input).value or "0")
            r = self.client.pay_bill(biller, ref, amt)
            self.log_msg(f"Paid {biller} ({ref}): {r.get('status')} (Receipt: {r.get('receiptNumber')})")

        elif bid == "btn-toll-pay":
            plate = self.query_one("#inp-toll-plate", Input).value
            amt = float(self.query_one("#inp-toll-amt", Input).value or "0")
            r = self.client.tollroad_recharge(plate, amt)
            self.log_msg(f"Toll recharged for {plate}: {amt} ETB (New Balance: {r.get('newTollBalance')} ETB)")

        elif bid == "btn-loan-disburse":
            amt = float(self.query_one("#inp-loan-req-amt", Input).value or "5000")
            r = self.client.request_loan(amt)
            self.log_msg(f"Loan disbursed: {amt} ETB (ID: {r.get('loanId')})")

        elif bid == "btn-loan-repay":
            r = self.client.repay_loan("LN-58291", 3587.50)
            self.log_msg(f"Loan repaid: 3,587.50 ETB (Receipt: {r.get('receiptNumber')})")

        elif bid == "btn-split-submit":
            amt = float(self.query_one("#inp-split-amt", Input).value or "1200")
            raw_users = self.query_one("#inp-split-users", Input).value
            users = [u.strip() for u in raw_users.split(",") if u.strip()]
            r = self.client.initiate_split_payment(amt, users)
            self.query_one("#lbl-split-result", Label).update(f"Split {amt:.2f} ETB: {r.get('amountPerPerson')} ETB/person with {len(users)} users.")
            self.log_msg(f"Split payment created: {r.get('splitId')}")

        elif bid == "btn-fetch-forex":
            self.action_fetch_forex()

        elif bid == "btn-cfg-save":
            self.config.set("api_base", self.query_one("#inp-cfg-base", Input).value)
            self.config.set("phone_number", self.query_one("#inp-cfg-phone", Input).value)
            self.config.set("device_id", self.query_one("#inp-cfg-dev", Input).value)
            token_val = self.query_one("#inp-cfg-token", Input).value
            self.config.set("access_token", token_val)
            self.client.token = token_val
            self.config.set("mock_mode", self.query_one("#sw-cfg-mock", Switch).value)
            self.config.save()
            self.log_msg("CBE Configuration saved.")
