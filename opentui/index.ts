import { CBETUIApp } from "./src/app";

async function main() {
  const app = new CBETUIApp();
  await app.start();
  await app.waitForExit();
}

main().catch((err) => {
  console.error("Fatal error in CBE TUI:", err);
  process.exit(1);
});
