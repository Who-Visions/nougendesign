/**
 * NouGenDesign Semantic UI Compiler v0.
 * Pure, deterministic, no React dependency and no generated executable code.
 */
export type EvidenceState = "verified" | "inferred" | "unknown";
export type Health = "healthy" | "degraded" | "down" | "unknown";
export type RouteObservation = {
  id: string;
  name: string;
  health: Health;
  evidence: EvidenceState;
  observedAt: string;
  detail?: string;
};
export type FleetSnapshot = {
  kind: "fleet-status";
  snapshotId: string;
  observedAt: string;
  routes: readonly RouteObservation[];
};
export type UINode =
  | { id: string; type: "heading"; text: string }
  | { id: string; type: "metric"; label: string; value: string; source: string }
  | { id: string; type: "status"; label: string; value: Health; evidence: EvidenceState; source: string; detail?: string };
export type UISpec = {
  schemaVersion: "0.1.0";
  sourceSnapshot: string;
  generatedFrom: string;
  nodes: readonly UINode[];
};
const validHealth = new Set<Health>(["healthy", "degraded", "down", "unknown"]);
const validEvidence = new Set<EvidenceState>(["verified", "inferred", "unknown"]);
function assertValid(snapshot: FleetSnapshot): void {
  if (snapshot.kind !== "fleet-status" || !snapshot.snapshotId.trim()) throw new Error("Invalid snapshot");
  if (!Number.isFinite(Date.parse(snapshot.observedAt))) throw new Error("Invalid observation timestamp");
  const seen = new Set<string>();
  for (const route of snapshot.routes) {
    if (!route.id.trim() || !route.name.trim() || seen.has(route.id)) throw new Error("Invalid or duplicate route ID");
    if (!validHealth.has(route.health) || !validEvidence.has(route.evidence)) throw new Error("Invalid route state");
    if (!Number.isFinite(Date.parse(route.observedAt))) throw new Error("Invalid route timestamp");
    if (Date.parse(route.observedAt) > Date.parse(snapshot.observedAt)) throw new Error("Route observed after snapshot");
    seen.add(route.id);
  }
}
export function compileFleetUI(snapshot: FleetSnapshot): UISpec {
  assertValid(snapshot);
  const routes = [...snapshot.routes].sort((a, b) => a.id.localeCompare(b.id, "en"));
  const verifiedHealthy = routes.filter(r => r.health === "healthy" && r.evidence === "verified").length;
  const verifiedDegraded = routes.filter(r => r.health === "degraded" && r.evidence === "verified").length;
  const nodes: UINode[] = [
    { id: "title", type: "heading", text: "Fleet status" },
    { id: "serving", type: "metric", label: "Verified healthy routes", value: `${verifiedHealthy}/${routes.length}`, source: "routes" },
    { id: "degraded", type: "metric", label: "Verified degraded routes", value: String(verifiedDegraded), source: "routes" },
    ...routes.map(r => ({
      id: `route:${r.id}`, type: "status" as const, label: r.name,
      value: r.evidence === "verified" ? r.health : "unknown" as Health,
      evidence: r.evidence, source: `routes.${r.id}`, ...(r.detail ? { detail: r.detail } : {})
    }))
  ];
  return { schemaVersion: "0.1.0", sourceSnapshot: snapshot.snapshotId, generatedFrom: snapshot.observedAt, nodes };
}
