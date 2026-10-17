#!/usr/bin/env python3
"""
Commercial Bank of Ethiopia (CBE Mobile) Interactive Textual TUI
Terminal dashboard for CBE Mobile Banking services
"""

import time
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Input, Static, Label, TabbedContent, TabPane,
    Select, Switch, DataTable, Log
)
from textual.binding import Binding
from cbe_client import CBEClient, CBEConfig


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
        border-radius: 1;
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
        font-size: 140%;
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
        font-size: 160%;
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
        height: 10;
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
            with TabPane("Accounts & Dashboard", id="tab-dash"):
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
                        yield Label("Customer Status", classes="card-title")
                        yield Label(f"Phone: {self.config.get('phone_number')} | Customer: Abebe Kebede", id="lbl-cust-info")
                        yield Button("Refresh Balances", id="btn-refresh-dash")

                    with Container(classes="card"):
                        yield Label("Recent Activity Stream", classes="card-title")
                        yield Log(id="log-dash")

            # 2. TRANSFERS
            with TabPane("Transfers", id="tab-transfers"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("CBE Account-to-Account (Internal Transfer)", classes="card-title")
                        yield Label("Destination CBE Account:")
                        yield Input(value="1000987654321", id="inp-cbe-to")
                        yield Label("Recipient Name: [Pending Lookup]", id="lbl-cbe-name", classes="stat-val")
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
                        yield Label("Recipient Name: [Pending Lookup]", id="lbl-ext-name", classes="stat-val")
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

            # 4. BILLS & TOLL ROAD
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

            # 5. FOREX & LOANS
            with TabPane("Forex & Loans", id="tab-forex"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("CBE Daily Forex Exchange Rates", classes="card-title")
                        yield DataTable(id="tbl-forex")
                        yield Button("Fetch Latest Rates", id="btn-fetch-forex")

                    with Container(classes="card"):
                        yield Label("CBE Digital Microloan", classes="card-title")
                        yield Label("Status: ELIGIBLE | Credit Line: 20,000.00 ETB", id="lbl-loan-status")
                        yield Button("Request Loan Disbursal", id="btn-loan-request")

            # 6. SETTINGS
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
                        with Horizontal():
                            yield Label("Mock Mode: ")
                            yield Switch(value=self.config.get("mock_mode"), id="sw-cfg-mock")
                        yield Button("Save Configuration", id="btn-cfg-save")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#tbl-forex", DataTable)
        table.add_columns("Currency", "Buying (ETB)", "Selling (ETB)")
        self.action_fetch_forex()
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

        elif bid == "btn-fetch-forex":
            self.action_fetch_forex()

        elif bid == "btn-cfg-save":
            self.config.set("api_base", self.query_one("#inp-cfg-base", Input).value)
            self.config.set("phone_number", self.query_one("#inp-cfg-phone", Input).value)
            self.config.set("device_id", self.query_one("#inp-cfg-dev", Input).value)
            self.config.set("mock_mode", self.query_one("#sw-cfg-mock", Switch).value)
            self.config.save()
            self.log_msg("CBE Configuration saved.")


if __name__ == "__main__":
    app = CBEMobileTUI()
    app.run()
