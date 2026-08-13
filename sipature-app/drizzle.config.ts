import { defineConfig } from "drizzle-kit";

/**
 * Drizzle Kit configuration.
 *   npm run db:generate   → buat migration SQL dari src/db/schema.ts
 *   npm run db:migrate    → terapkan migration ke DATABASE_URL
 *   npm run db:pull       → introspect DB yang ada → schema.ts (reverse)
 */
export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url:
      process.env.DATABASE_URL ??
      "postgresql://sipature:sipature@localhost:5432/sipature",
  },
  verbose: true,
  strict: true,
});
