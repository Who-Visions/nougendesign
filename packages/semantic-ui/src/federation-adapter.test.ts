import { strict as assert } from "node:assert";
import { test } from "node:test";
import { adaptFederation } from "./federation-adapter.js";
import { compileFleetUI } from "./compiler.js";
test("Cloudflare 1033 means route degradation, not host failure", () => {
  const snapshot = adaptFederation({
    checked_utc: "2026-10-07T22:58:26Z",
    routes: [{ route: "whoart", status: "RED", health: "cloudflare_tunnel", mcp: "cloudflare_tunnel", mcp_detail: "gateway 530: error 1033" }]
  }, "sample");
  assert.equal(snapshot.routes[0].health, "degraded");
  assert.equal(snapshot.routes[0].evidence, "verified");
  const spec = compileFleetUI(snapshot);
  const status = spec.nodes.find(n => n.id === "route:whoart");
  assert.ok(status?.type === "status");
  assert.equal(status.value, "degraded");
});
test("ambiguous probe data fails closed", () => {
  const snapshot = adaptFederation({ checked_utc: "2026-10-07T22:58:26Z", routes: [{ route: "blade", status: "GREEN" }] }, "sample");
  assert.equal(snapshot.routes[0].health, "unknown");
});
