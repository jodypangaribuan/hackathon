import { drizzle, type NodePgDatabase } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

import * as schema from "./schema";

/**
 * Koneksi Postgres (lazy — Pool hanya connect saat query pertama, aman saat
 * build time Next.js). DATABASE_URL di-inject dari docker-compose.
 */
const connectionString =
  process.env.DATABASE_URL ??
  "postgresql://sipature:sipature@localhost:5432/sipature";

const globalForDb = globalThis as unknown as { sipaturePool?: Pool };

const pool =
  globalForDb.sipaturePool ??
  new Pool({ connectionString, max: 5 });

if (process.env.NODE_ENV !== "production") {
  globalForDb.sipaturePool = pool;
}

export const db: NodePgDatabase<typeof schema> = drizzle(pool, { schema });
export { schema };
