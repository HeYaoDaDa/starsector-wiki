import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 45_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  retries: 1,
  workers: 1,
  use: {
    baseURL: 'http://localhost:9180',
    headless: true,
    viewport: { width: 1280, height: 800 },
  },
  webServer: {
    command: 'pnpm dev --port 9180',
    port: 9180,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
