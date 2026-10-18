export type WorkspaceMode = 1 | 2 | 3 | 4 | 5 | 6;

export interface AccountItem {
  accountNumber: string;
  accountType: "SAVING" | "CURRENT";
  accountName: string;
  availableBalance: number;
  currency: string;
  status: string;
}

export interface ForexItem {
  currency: string;
  name: string;
  buying: number;
  selling: number;
}

export interface CardItem {
  cardId: string;
  cardType: string;
  maskedNumber: string;
  expiry: string;
  status: string;
}

export interface BankItem {
  id: string;
  name: string;
  code: string;
}

export interface TrafficCall {
  id: number;
  time: string;
  endpoint: string;
  code: string;
  desc: string;
  data: Record<string, any>;
}

export const SUPPORTED_EXTERNAL_BANKS: BankItem[] = [
  { id: "awash", name: "Awash International Bank", code: "AWASH" },
  { id: "dashen", name: "Dashen Bank", code: "DASHEN" },
  { id: "abyssinia", name: "Bank of Abyssinia", code: "BOA" },
  { id: "telebirr", name: "Telebirr (Ethio Telecom)", code: "TELEBIRR" },
  { id: "wegagen", name: "Wegagen Bank", code: "WEGAGEN" },
  { id: "hibret", name: "Hibret Bank", code: "HIBRET" },
  { id: "coop", name: "Cooperative Bank of Oromia", code: "COOP" },
  { id: "oromia", name: "Oromia Bank", code: "OROMIA" },
  { id: "amhara", name: "Amhara Bank", code: "AMHARA" },
  { id: "berhan", name: "Berhan Bank", code: "BERHAN" }
];
