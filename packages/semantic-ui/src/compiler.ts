/**
 * NouGenDesign Semantic UI Compiler v0.
 * Pure, bounded, deterministic; no React, I/O, current clock or executable output.
 */
export type EvidenceState = "verified" | "inferred" | "unknown";
export type Health = "healthy" | "degraded" | "down" | "unknown";
export type Freshness = "fresh" | "stale";
export type RouteObservation = {
  id: string; name: string; health: Health; evidence: EvidenceState;
  observedAt: string; detail?: string;
};
export type FleetSnapshot = {
  kind: "fleet-status"; snapshotId: string; observedAt: string;
  routes: readonly RouteObservation[];
};
export type CompileOptions = { asOf: string; maxAgeMs: number };
export type UINode =
  | { id: string; type: "heading"; text: string }
  | { id: string; type: "metric"; label: string; value: string; source: string }
  | { id: string; type: "status"; label: string; value: Health; evidence: EvidenceState; freshness: Freshness; observedAt: string; source: string; detail?: string }
  | { id: string; type: "notice"; text: string };
export type UISpec = {
  schemaVersion: "0.1.0"; sourceSnapshot: string;
  generatedFrom: string; asOf: string; nodes: readonly UINode[];
};

const validHealth = new Set<Health>(["healthy", "degraded", "down", "unknown"]);
const validEvidence = new Set<EvidenceState>(["verified", "inferred", "unknown"]);
const rfc3339 = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
function timestamp(raw: string, field: string): number {
  if (typeof raw !== "string" || !rfc3339.test(raw)) throw new Error(`${field}: RFC3339 timestamp required`);
  const result = Date.parse(raw);
  if (!Number.isFinite(result)) throw new Error(`${field}: invalid timestamp`);
  return result;
}
function requireString(value: unknown, field: string, maxLength = 256): asserts value is string {
  if (typeof value !== "string" || !value.trim() || value.length > maxLength) {
    throw new Error(`${field}: nonempty bounded string required`);
  }
}
function assertValid(snapshot: FleetSnapshot, options: CompileOptions): void {
  if (!snapshot || snapshot.kind !== "fleet-status") throw new Error("Invalid snapshot kind");
  requireString(snapshot.snapshotId, "snapshotId", 128);
  if (!Array.isArray(snapshot.routes) || snapshot.routes.length > 128) throw new Error("Expected <=128 routes");
  const observed = timestamp(snapshot.observedAt, "snapshot.observedAt");
  const asOf = timestamp(options?.asOf, "options.asOf");
  if (asOf < observed) throw new Error("Cannot compile a future snapshot");
  if (!Number.isFinite(options?.maxAgeMs) || options.maxAgeMs < 0 || options.maxAgeMs > 86_400_000) {
    throw new Error("Invalid maxAgeMs");
  }
  const seen = new Set<string>();
  for (const route of snapshot.routes) {
    if (!route || typeof route.id !== "string" || !/^[a-zA-Z0-9_-]{1,64}$/.test(route.id) || seen.has(route.id)) {
      throw new Error("Invalid or duplicate route ID");
    }
    requireString(route.name, "route.name");
    if (!validHealth.has(route.health) || !validEvidence.has(route.evidence)) throw new Error("Invalid route health or evidence");
    if (route.detail !== undefined && (typeof route.detail !== "string" || route.detail.length > 2048)) throw new Error("Invalid route detail");
    if (timestamp(route.observedAt, `routes.${route.id}.observedAt`) > observed) {
      throw new Error("Route observed after snapshot");
    }
    seen.add(route.id);
  }
}
/** "asOf" is injected by the caller. The same snapshot + policy always produces identical output. */
export function compileFleetUI(snapshot: FleetSnapshot, options: CompileOptions): UISpec {
  assertValid(snapshot, options);
  // Compare code points, never environment-dependent locale collation.
  const routes = [...snapshot.routes].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
  const checked = routes.map(route => {
    const freshness: Freshness = Date.parse(options.asOf) - Date.parse(route.observedAt) <= options.maxAgeMs ? "fresh" : "stale";
    const value: Health = freshness === "fresh" && route.evidence === "verified" ? route.health : "unknown";
    return { route, freshness, value };
  });
  const verifiedHealthy = checked.filter(r => r.value === "healthy").length;
  const verifiedDegraded = checked.filter(r => r.value === "degraded").length;
  const nodes: UINode[] = [
    { id: "title", type: "heading", text: "Fleet status" },
    { id: "serving", type: "metric", label: "Verified healthy routes", value: routes.length ? `${verifiedHealthy}/${routes.length}` : "Unavailable", source: "routes" },
    { id: "degraded", type: "metric", label: "Verified degraded routes", value: routes.length ? String(verifiedDegraded) : "Unavailable", source: "routes" },
    ...(routes.length === 0 ? [{ id: "empty", type: "notice" as const, text: "No route observations available." }] : []),
    ...checked.map(({route, freshness, value}) => ({
      id: `route:${route.id}`, type: "status" as const, label: route.name, value,
      evidence: route.evidence, freshness, observedAt: route.observedAt,
      source: `routes.${route.id}`, ...(route.detail ? { detail: route.detail } : {})
    }))
  ];
  return { schemaVersion: "0.1.0", sourceSnapshot: snapshot.snapshotId, generatedFrom: snapshot.observedAt, asOf: options.asOf, nodes };
}
