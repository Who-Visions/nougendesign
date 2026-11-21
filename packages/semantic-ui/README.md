# Semantic UI compiler (experimental)

Evidence-aware, deterministic TypeScript fleet compiler with a narrowly scoped federation adapter and allowlisted React presentation components.

**Ownership:** This package lives outside the legacy NouGenShards → NouGenDesigns mirror sync paths. The existing `designs/nougen-core/design.json` remains the authority for visual tokens. No changes to `main`, no runtime deployment, and no automated application-side mutations are implied by this package.

## Invariants

- An unverified route cannot be displayed as healthy or down.
- A **Cloudflare tunnel failure** describes the route, **not the underlying computer**.
- Status is evaluated against an injected `asOf` timestamp and a bounded `maxAgeMs` policy. Stale status becomes **Unverified**, with its original evidence and timestamp visible.
- Empty responses display **Unavailable**, not a misleading 0/0 green ratio.
- Compiler output is pure and stable for identical snapshots and policy inputs. Records are ordered by stable IDs, not locale-specific sorting.
- Output is a typed, allowlisted UI specification, not executable HTML or arbitrary JSX from a model.
- React renders data as text. There is no `dangerouslySetInnerHTML`, dynamic evaluation, or direct host mutation.
- Styles consume NouGenDesign's established generated tokens. A dark/light theme is selected by the existing `data-theme` mechanism.

## Install and local validation (no CI required)

```sh
cd packages/semantic-ui
npm install
npm run typecheck
npm test
```

The existing Python design compiler has a separate check, from the repository root:

```sh
python tools/nougendesigns.py check designs/nougen-core/design.json designs/nougen-core
python tools/nougendesigns.py lint designs/nougen-core/design.json --css ui/src/styles.css
```

## Integration

```tsx
import { adaptFederation } from "./src/federation-adapter";
import { compileFleetUI } from "./src/compiler";
import { SemanticUI } from "./src/renderer";
import "../../designs/nougen-core/tokens.css"; // resolve relative to host app
import "./src/styles.css";

const snapshot = adaptFederation(federationResponse, "federation-check-001");
const spec = compileFleetUI(snapshot, {
  asOf: knownEvaluationTime, // provided externally; no implicit Date.now()
  maxAgeMs: 60_000 // explicit product policy, not a measured universal threshold
});
return <SemanticUI spec={spec} />;
```

The example is deliberately **not wired to a live endpoint**. A host app must authenticate and fetch federation telemetry, establish valid `asOf` semantics, and manage polling and error states. Do not use a hardcoded screenshot or a stale cached response as a live health claim.

## Validation scope and follow-ups

Local isolated verification of the exact compiled compiler and federation adapter passed ten focused Node tests on 2026-10-07. Git blob hashes were checked against the branch contents. Full `npm test`, React typecheck, accessibility testing, browser screenshots, and true end-to-end source-to-render validation have **not** been completed. There is no required CI service.

Next tasks: browser tests at 320px/390px/desktop, dark/light and zoom; stale cache/fetch failure behavior; WCAG contrast testing across themes; schema validation at untrusted JSON boundaries; and a provider-neutral registry for other semantic UI domains (jobs, design reviews).
