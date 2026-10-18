import { expect, test } from "bun:test";
import { CBETUIApp } from "../src/app";

test("CBETUIApp instantiates cleanly", () => {
  const app = new CBETUIApp();
  expect(app).toBeDefined();
});
