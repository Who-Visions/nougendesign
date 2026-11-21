import type { FleetSnapshot, Health, EvidenceState } from "./compiler";
/** Maps route-level probe evidence only; a failed tunnel does not prove its machine is down. */
export type FederationRoute = {
  route: string; status?: string; health?: string; mcp?: string;
  checked_utc?: string; mcp_detail?: string;
};
export type FederationResponse = { routes: readonly FederationRoute[]; checked_utc: string };
function routeHealth(route: FederationRoute): { health: Health; evidence: EvidenceState } {
  if (route.status === "GREEN" && route.health === "ok" && route.mcp === "ok") {
    return { health: "healthy", evidence: "verified" };
  }
  if (route.status === "RED" && route.health === "cloudflare_tunnel") {
    return { health: "degraded", evidence: "verified" };
  }
  return { health: "unknown", evidence: "unknown" };
}
export function adaptFederation(response: FederationResponse, snapshotId: string): FleetSnapshot {
  if (!response.checked_utc || !snapshotId.trim()) throw new Error("Missing federation identity or timestamp");
  return {
    kind: "fleet-status", snapshotId, observedAt: response.checked_utc,
    routes: response.routes.map(route => ({
      id: route.route, name: route.route,
      ...routeHealth(route),
      observedAt: route.checked_utc ?? response.checked_utc,
      ...(route.mcp_detail ? { detail: route.mcp_detail.trim() } : {})
    }))
  };
}
