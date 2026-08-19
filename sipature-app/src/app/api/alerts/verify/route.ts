import { and, eq } from "drizzle-orm";
import { NextResponse } from "next/server";

import { db, schema } from "@/db";
import { SIGNAL_ASPECTS } from "@/lib/format";

function badRequest(message: string, code: string) {
  return NextResponse.json({ error: message, code }, { status: 400 });
}

export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return badRequest("Body permintaan bukan JSON yang valid.", "INVALID_JSON");
  }
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return badRequest("Body harus berupa objek JSON.", "INVALID_BODY");
  }

  const {
    destinationId,
    aspect,
    status,
    rejectionReason,
    verdictNote,
    verifiedBy,
  } = body as {
    destinationId?: unknown;
    aspect?: unknown;
    status?: unknown;
    rejectionReason?: unknown;
    verdictNote?: unknown;
    verifiedBy?: unknown;
  };

  if (typeof destinationId !== "string" || destinationId.length === 0) {
    return badRequest("Field `destinationId` wajib berupa string.", "DESTINATION_REQUIRED");
  }
  if (typeof aspect !== "string" || !SIGNAL_ASPECTS.includes(aspect as never)) {
    return badRequest("Field `aspect` tidak dikenal.", "UNKNOWN_ASPECT");
  }
  if (
    status !== "confirmed" &&
    status !== "rejected" &&
    status !== "uncertain"
  ) {
    return badRequest(
      "Field `status` harus confirmed, rejected, atau uncertain.",
      "INVALID_STATUS",
    );
  }
  if (status === "rejected" && typeof rejectionReason !== "string") {
    return badRequest(
      "Field `rejectionReason` wajib diisi saat status rejected.",
      "REJECTION_REASON_REQUIRED",
    );
  }

  const [signal] = await db
    .select()
    .from(schema.destinationSignals)
    .where(
      and(
        eq(schema.destinationSignals.destinationId, destinationId),
        eq(schema.destinationSignals.aspect, aspect),
      ),
    )
    .limit(1);

  if (!signal || signal.priority === "Insufficient Data") {
    return NextResponse.json(
      { error: "Alert tidak ditemukan atau bukan isu actionable.", code: "ALERT_NOT_FOUND" },
      { status: 404 },
    );
  }

  const [alert] = await db
    .insert(schema.alerts)
    .values({
      destinationId: signal.destinationId,
      aspect: signal.aspect,
      priority: signal.priority,
      priorityScore: signal.priorityScore,
      recommendedVerification: signal.recommendedVerification,
      candidateIntervention: signal.candidateIntervention,
      status,
    })
    .onConflictDoUpdate({
      target: [schema.alerts.destinationId, schema.alerts.aspect],
      set: { status, updatedAt: new Date() },
    })
    .returning();

  const [verification] = await db
    .insert(schema.alertVerifications)
    .values({
      alertId: alert.id,
      status,
      verdictNote: typeof verdictNote === "string" ? verdictNote : null,
      rejectionReason: typeof rejectionReason === "string" ? rejectionReason : null,
      verifiedBy: typeof verifiedBy === "string" ? verifiedBy : null,
    })
    .returning();

  return NextResponse.json({
    id: alert.id,
    destinationId: alert.destinationId,
    aspect: alert.aspect,
    status: alert.status,
    verification: {
      id: verification.id,
      status: verification.status,
      rejectionReason: verification.rejectionReason,
      verdictNote: verification.verdictNote,
      verifiedAt: verification.verifiedAt,
    },
  });
}
