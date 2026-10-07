import { strict as assert } from "node:assert";
import { test } from "node:test";
import { adaptFederation } from "./federation-adapter.js";
import { compileFleetUI } from "./compiler.js";
const at = "2026-10-07T22:58:26Z";
const options = { asOf: at, maxAgeMs: 60_000 };

test("Cloudflare 1033 is route degradation, not host death", () => {
  const snapshot = adaptFederation({
    checked_utc: at,
    routes: [{ route: "whoart", status: "RED", health: "cloudflare_tunnel", mcp: "cloudflare_tunnel", mcp_detail: "gateway 530: error 1033" }]
  }, "fixture");
  assert.equal(snapshot.routes[0].health, "degraded");
  assert.equal(snapshot.routes[0].evidence, "verified");
  const status = compileFleetUI(snapshot, options).nodes.find(node => node.id === "route:whoart");
  assert.ok(status?.type === "status");
  assert.equal(status.value, "degraded");
  assert.equal(status.detail, "gateway 530: error 1033");
});

test("ambiguous probe data fails closed", () => {
  const snapshot = adaptFederation({ checked_utc: at, routes: [{ route: "blade", status: "GREEN" }] }, "fixture");
  assert.equal(snapshot.routes[0].health, "unknown");
  assert.equal(compileFleetUI(snapshot, options).nodes.find(node => node.id === "route:blade")?.type, "status");
});

test("missing federation timestamp rejected by compiler", () => {
  const snapshot = adaptFederation({ checked_utc: at, routes: [{ route: "blade", checked_utc: "yesterday", status: "GREEN", health: "ok", mcp: "ok" }] }, "fixture");
  assert.throws(() => compileFleetUI(snapshot, options));
});
