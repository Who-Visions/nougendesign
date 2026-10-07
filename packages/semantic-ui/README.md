# Semantic UI compiler (experimental)

Pure typed fleet compiler, federation adapter, and React renderer. This package is isolated from the existing Python design compiler and does not change production routes.

## Local validation

```sh
cd packages/semantic-ui
npm install
npm run typecheck
npm test
```

## Usage

```tsx
import { adaptFederation } from "./src/federation-adapter";
import { compileFleetUI } from "./src/compiler";
import { SemanticUI } from "./src/renderer";
import "./src/styles.css";

const snapshot = adaptFederation(federationResponse, "federation-check-001");
const spec = compileFleetUI(snapshot);
return <SemanticUI spec={spec} />;
```

The adapter classifies Cloudflare tunnel failures as *route degraded*, not *machine down*. Only explicitly verified healthy routes count toward the healthy metric. Missing evidence becomes unknown. The React renderer is allowlisted and contains no dynamic HTML injection.

Next: actual test execution, accessible screenshots at mobile and desktop breakpoints, stale-observation policy, and compatibility with the existing design token compiler.
