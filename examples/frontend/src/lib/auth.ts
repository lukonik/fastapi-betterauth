import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { tanstackStartCookies } from "better-auth/tanstack-start";
import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";

const databasePath = resolve(
  process.cwd(),
  process.env.BETTER_AUTH_SQLITE_PATH ?? "data/auth.sqlite",
);

mkdirSync(dirname(databasePath), { recursive: true });

const database = new Database(databasePath);
database.pragma("foreign_keys = ON");
database.pragma("journal_mode = WAL");

export const auth = betterAuth({
  database,
  emailAndPassword: {
    enabled: true,
  },
  trustedOrigins: [
    process.env.BETTER_AUTH_TRUSTED_ORIGIN ?? "http://localhost:3000",
  ],
  plugins: [jwt(),tanstackStartCookies()],
});

let migrationPromise: Promise<void> | undefined;

export function ensureAuthSchema() {
  migrationPromise ??= auth.$context.then((ctx) => ctx.runMigrations());
  return migrationPromise;
}
