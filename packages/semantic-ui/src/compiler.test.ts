import { strict as assert } from "node:assert";
import { test } from "node:test";
import { compileFleetUI, type FleetSnapshot } from "./compiler.js";
const snapshot: FleetSnapshot = {
  kind: "fleet-status", snapshotId: "fixture-1", observedAt: "2026-10-07T22:58:30Z",
  routes: [
    { id: "whoart", name: "Who Art", health: "down", evidence: "inferred", observedAt: "2026-10-07T22:58:26Z", detail: "Tunnel error, host unverified" },
    { id: "blade", name: "Blade", health: "healthy", evidence: "verified", observedAt: "2026-10-07T22:58:26Z" }
  ]
};
test("identical inputs yield identical UI specifications", () => {
  assert.deepEqual(compileFleetUI(snapshot), compileFleetUI(snapshot));
});
test("unverified down state never becomes a verified node status", () => {
  const ui = compileFleetUI(snapshot);
  assert.equal(ui.nodes.find(n => n.id === "route:whoart")?.type, "status");
  const whoart = ui.nodes.find(n => n.id === "route:whoart");
  assert.ok(whoart?.type === "status");
  assert.equal(whoart.value, "unknown");
  assert.equal(ui.nodes.find(n => n.id === "serving")?.type, "metric");
});
test("rejects duplicate IDs", () => {
  assert.throws(() => compileFleetUI({ ...snapshot, routes: [snapshot.routes[0], snapshot.routes[0]] }));
});
test("rejects observations from the future", () => {
  assert.throws(() => compileFleetUI({ ...snapshot, routes: [{ ...snapshot.routes[0], observedAt: "2026-10-08T00:00:00Z" }] }));
});
