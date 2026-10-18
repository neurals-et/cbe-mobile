import { expect, test, describe } from "bun:test";
import { CBEApi } from "../src/api";
import { TrafficHistory } from "../src/traffic";
import { SUPPORTED_EXTERNAL_BANKS } from "../src/types";

describe("CBE API & Traffic", () => {
  test("traffic records calls correctly", () => {
    const traffic = new TrafficHistory();
    expect(traffic.getCalls().length).toBeGreaterThan(0);

    traffic.record("GET /test", "200", "Test call", { foo: "bar" });
    const calls = traffic.getCalls();
    expect(calls[0].endpoint).toBe("GET /test");
    expect(traffic.formatOutput()).toContain("GET /test");
  });

  test("getAccounts returns account list", async () => {
    const traffic = new TrafficHistory();
    const api = new CBEApi(traffic);
    const accounts = await api.getAccounts();
    expect(accounts.length).toBe(2);
    expect(accounts[0].accountNumber).toBe("1000123456789");
    expect(accounts[0].currency).toBe("ETB");
  });

  test("lookupAccount resolves recipient names", async () => {
    const traffic = new TrafficHistory();
    const api = new CBEApi(traffic);
    const name = await api.lookupAccount("1000987654321");
    expect(name).toBe("Tigist Haile");
  });

  test("generateAtmCode produces 6-digit code", async () => {
    const traffic = new TrafficHistory();
    const api = new CBEApi(traffic);
    const res = await api.generateAtmCode("1000123456789", 500);
    expect(res.code.length).toBe(6);
    expect(res.expiry).toBeDefined();
  });

  test("forex rates return currencies", async () => {
    const traffic = new TrafficHistory();
    const api = new CBEApi(traffic);
    const rates = await api.getForexRates();
    expect(rates.length).toBeGreaterThan(0);
    expect(rates.some((r) => r.currency === "USD")).toBe(true);
  });

  test("external banks list is defined", () => {
    expect(SUPPORTED_EXTERNAL_BANKS.length).toBeGreaterThanOrEqual(10);
    expect(SUPPORTED_EXTERNAL_BANKS[0].code).toBe("AWASH");
  });
});
