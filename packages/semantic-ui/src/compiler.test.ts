import { strict as assert } from "node:assert";
import { test } from "node:test";
import { compileFleetUI, type FleetSnapshot } from "./compiler.js";

const options = { asOf: "2026-10-07T22:58:30Z", maxAgeMs: 60_000 } as const;
const snapshot: FleetSnapshot = {
  kind: "fleet-status",
  snapshotId: "fixture-1",
  observedAt: "2026-10-07T22:58:30Z",
  routes: [
    { id: "whoart", name: "Who Art", health: "down", evidence: "inferred", observedAt: "2026-10-07T22:58:26Z", detail: "Tunnel error; host unverified" },
    { id: "blade", name: "Blade", health: "healthy", evidence: "verified", observedAt: "2026-10-07T22:58:26Z" }
  ]
};

test("equal input and policy produce identical output without mutation", () => {
  const before = JSON.stringify(snapshot);
  assert.deepEqual(compileFleetUI(snapshot, options), compileFleetUI(snapshot, options));
  assert.equal(JSON.stringify(snapshot), before);
});

test("unverified host state cannot become down or healthy", () => {
  const spec = compileFleetUI(snapshot, options);
  const whoart = spec.nodes.find(node => node.id === "route:whoart");
  assert.ok(whoart?.type === "status");
  assert.equal(whoart.value, "unknown");
  assert.equal(whoart.evidence, "inferred");
  const blade = spec.nodes.find(node => node.id === "route:blade");
  assert.ok(blade?.type === "status");
  assert.equal(blade.value, "healthy");
});

test("stale healthy probe fails closed but carries original evidence", () => {
  const spec = compileFleetUI(snapshot, { ...options, asOf: "2026-10-07T23:10:00Z" });
  const blade = spec.nodes.find(node => node.id === "route:blade");
  assert.ok(blade?.type === "status");
  assert.equal(blade.value, "unknown");
  assert.equal(blade.freshness, "stale");
  assert.equal(blade.evidence, "verified");
});

test("zero routes must be unavailable, not 0/0 healthy", () => {
  const spec = compileFleetUI({ ...snapshot, routes: [] }, options);
  assert.ok(spec.nodes.some(node => node.type === "notice"));
  const healthy = spec.nodes.find(node => node.id === "serving");
  assert.ok(healthy?.type === "metric");
  assert.equal(healthy.value, "Unavailable");
});

test("route order independent of upstream ordering", () => {
  const swapped = { ...snapshot, routes: [...snapshot.routes].reverse() };
  assert.deepEqual(compileFleetUI(snapshot, options), compileFleetUI(swapped, options));
});

test("reject duplicate IDs, invalid timestamps, future observations, bad age policy", () => {
  assert.throws(() => compileFleetUI({ ...snapshot, routes: [snapshot.routes[0], snapshot.routes[0]] }, options));
  assert.throws(() => compileFleetUI({ ...snapshot, observedAt: "yesterday" }, options));
  assert.throws(() => compileFleetUI({ ...snapshot, routes: [{ ...snapshot.routes[0], observedAt: "2026-10-08T00:00:00Z" }] }, options));
  assert.throws(() => compileFleetUI(snapshot, { ...options, maxAgeMs: -1 }));
  assert.throws(() => compileFleetUI(snapshot, { ...options, asOf: "2026-10-07T22:00:00Z" }));
});
