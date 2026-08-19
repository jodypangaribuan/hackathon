import { ne } from "drizzle-orm";
import { NextResponse } from "next/server";

import { db, schema } from "@/db";

export async function GET() {
  const [signals, alerts, destinations] = await Promise.all([
    db
      .select()
      .from(schema.destinationSignals)
      .where(ne(schema.destinationSignals.priority, "Insufficient Data")),
    db.select().from(schema.alerts),
    db.select().from(schema.destinations),
  ]);

  const nameById = new Map(destinations.map((d) => [d.id, d.name]));
  const alertByKey = new Map(
    alerts.map((a) => [`${a.destinationId}--${a.aspect}`, a]),
  );

  const items = signals
    .map((signal) => {
      const alert = alertByKey.get(`${signal.destinationId}--${signal.aspect}`);
      return {
        id: alert?.id ?? `${signal.destinationId}--${signal.aspect}`,
        key: `${signal.destinationId}--${signal.aspect}`,
        destinationId: signal.destinationId,
        destinationName: nameById.get(signal.destinationId) ?? signal.destinationId,
        aspect: signal.aspect,
        priority: signal.priority,
        priorityScore: signal.priorityScore,
        recommendedVerification: signal.recommendedVerification,
        candidateIntervention: signal.candidateIntervention,
        status: alert?.status ?? "pending",
        assignedTo: alert?.assignedTo ?? null,
      };
    })
    .sort(
      (a, b) =>
        (b.priorityScore ?? -1) - (a.priorityScore ?? -1) ||
        a.key.localeCompare(b.key),
    );

  return NextResponse.json({ count: items.length, items });
}
