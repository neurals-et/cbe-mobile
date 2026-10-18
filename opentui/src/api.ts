import type { AccountItem, CardItem, ForexItem } from "./types";
import type { TrafficHistory } from "./traffic";

const FOREX_URL = "https://combanketh.et/cbeapi/daily-exchange-rates/";

export class CBEApi {
  constructor(private traffic: TrafficHistory) {}

  async getAccounts(): Promise<AccountItem[]> {
    this.traffic.record("GET /v1/accounts/mine", "200", "Accounts retrieved", {
      count: 2,
      total_balance_etb: 173680.50
    });
    return [
      {
        accountNumber: "1000123456789",
        accountType: "SAVING",
        accountName: "Abebe Kebede",
        availableBalance: 45280.50,
        currency: "ETB",
        status: "ACTIVE"
      },
      {
        accountNumber: "1000998877665",
        accountType: "CURRENT",
        accountName: "Abebe Kebede Biz",
        availableBalance: 128400.00,
        currency: "ETB",
        status: "ACTIVE"
      }
    ];
  }

  async lookupAccount(accountNumber: string): Promise<string> {
    const mockMap: Record<string, string> = {
      "1000123456789": "Abebe Kebede",
      "1000987654321": "Tigist Haile",
      "1000554433221": "Dawit Tesfaye",
      "1000778899001": "Chaltu Bekele",
      "1000998877665": "Abebe Kebede Biz"
    };

    const resolved = mockMap[accountNumber] || `Customer ${accountNumber.slice(-4)}`;
    this.traffic.record(`GET /v1/accounts/info/${accountNumber}`, "200", "Account resolved", {
      accountNumber,
      accountHolderName: resolved,
      status: "ACTIVE"
    });
    return resolved;
  }

  async lookupExternal(bankCode: string, accountNumber: string): Promise<string> {
    const resolved = `External Recipient (${bankCode})`;
    this.traffic.record(`GET /v1/transfers/external-bank/account-info`, "200", "EthSwitch lookup", {
      bankCode,
      accountNumber,
      resolved
    });
    return resolved;
  }

  async generateAtmCode(account: string, amount: number): Promise<{ code: string; expiry: string }> {
    const code = String(Math.floor(100000 + Math.random() * 900000));
    const now = new Date(Date.now() + 2 * 3600 * 1000);
    const expiry = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    this.traffic.record("POST /v1/customers/withdrawals/initiate", "200", "ATM cash code generated", {
      account,
      amount,
      withdrawalCode: code,
      validHours: 2
    });

    return { code, expiry };
  }

  async payBill(biller: string, ref: string, amount: number): Promise<string> {
    const receipt = `CBE-BILL-${Math.floor(Date.now() / 1000)}`;
    this.traffic.record("POST /v1/payment-integrations/complete-payment/", "200", "Payment completed", {
      biller,
      ref,
      amount,
      receipt
    });
    return receipt;
  }

  async rechargeToll(plate: string, amount: number): Promise<number> {
    this.traffic.record("POST /v1/tollroad/recharge", "200", "Toll pass topped up", {
      plate,
      amount,
      newBalance: 350.00
    });
    return 350.00;
  }

  async getCards(): Promise<CardItem[]> {
    this.traffic.record("GET /v1/customer/cards", "200", "Cards retrieved", { count: 2 });
    return [
      {
        cardId: "crd_9018",
        cardType: "Visa Physical Debit",
        maskedNumber: "4234-XXXX-XXXX-9018",
        expiry: "09/28",
        status: "ACTIVE"
      },
      {
        cardId: "crd_4421",
        cardType: "Mastercard Virtual",
        maskedNumber: "5312-XXXX-XXXX-4421",
        expiry: "11/27",
        status: "ACTIVE"
      }
    ];
  }

  async getForexRates(): Promise<ForexItem[]> {
    try {
      const resp = await fetch(FOREX_URL, {
        headers: { "User-Agent": "Mozilla/5.0" },
        signal: AbortSignal.timeout(4000)
      });
      const data: any = await resp.json();
      const rates: ForexItem[] = [];
      if (Array.isArray(data) && data.length > 0) {
        const latest = data[data.length - 1]?.ExchangeRate ? data[data.length - 1] : data[0];
        for (const ex of latest.ExchangeRate || []) {
          const curr = ex.currency;
          const code = typeof curr === "object" ? curr.CurrencyCode : curr;
          const name = typeof curr === "object" ? curr.CurrencyName : code;
          rates.push({
            currency: code || "UNKNOWN",
            name: name || code,
            buying: ex.cashBuying || ex.transactionalBuying || 0.0,
            selling: ex.cashSelling || ex.transactionalSelling || 0.0
          });
        }
      }
      this.traffic.record("GET daily-exchange-rates", "200", "Live CBE Forex feed", {
        count: rates.length,
        source: "LIVE"
      });
      return rates;
    } catch {
      return [
        { currency: "USD", name: "US DOLLAR", buying: 125.40, selling: 127.90 },
        { currency: "EUR", name: "EURO", buying: 136.20, selling: 138.90 },
        { currency: "GBP", name: "POUND STERLING", buying: 160.10, selling: 163.30 },
        { currency: "AED", name: "UAE DIRHAM", buying: 34.15, selling: 34.80 }
      ];
    }
  }
}
