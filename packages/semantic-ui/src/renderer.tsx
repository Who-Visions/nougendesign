import * as React from "react";
import type { UISpec, UINode, Health } from "./compiler";

const healthLabel: Record<Health, string> = {
  healthy: "Healthy", degraded: "Degraded", down: "Down", unknown: "Unverified"
};
const healthClass: Record<Health, string> = {
  healthy: "ng-ui--healthy", degraded: "ng-ui--degraded",
  down: "ng-ui--down", unknown: "ng-ui--unknown"
};
function Node({ node }: { node: UINode }) {
  switch (node.type) {
    case "heading": return <h2 className="ng-ui__heading">{node.text}</h2>;
    case "metric": return <section className="ng-ui__metric" aria-label={node.label}>
      <strong className="ng-ui__value">{node.value}</strong>
      <span className="ng-ui__label">{node.label}</span>
    </section>;
    case "status": return <section className="ng-ui__status" aria-label={node.label}>
      <div className="ng-ui__status-main"><strong>{node.label}</strong>
        <span className={`ng-ui__pill ${healthClass[node.value]}`}>{healthLabel[node.value]}</span>
      </div>
      {node.detail && <p className="ng-ui__detail">{node.detail}</p>}
      {node.evidence !== "verified" && <small className="ng-ui__evidence">Evidence: {node.evidence}</small>}
    </section>;
    default: return assertNever(node);
  }
}
function assertNever(value: never): never { throw new Error(`Unsupported UI node: ${JSON.stringify(value)}`); }
export function SemanticUI({ spec }: { spec: UISpec }) {
  if (spec.schemaVersion !== "0.1.0") throw new Error("Unsupported UI schema version");
  const metrics = spec.nodes.filter(n => n.type === "metric");
  const others = spec.nodes.filter(n => n.type !== "metric");
  return <article className="ng-ui" aria-label="NouGen fleet status" data-source={spec.sourceSnapshot}>
    {others.filter(n => n.type === "heading").map(n => <Node key={n.id} node={n} />)}
    <div className="ng-ui__metrics">{metrics.map(n => <Node key={n.id} node={n} />)}</div>
    <div className="ng-ui__routes">{others.filter(n => n.type === "status").map(n => <Node key={n.id} node={n} />)}</div>
    <footer className="ng-ui__footer">Snapshot: <time dateTime={spec.generatedFrom}>{spec.generatedFrom}</time></footer>
  </article>;
}
