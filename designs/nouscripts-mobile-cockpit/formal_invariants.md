# Formal Proving Invariants: Generative Design SDK Client

### 1. Keymaker Secret Isolation (Non-Interference / Memory Safety)
**Invariant:** *The semantic value of any `KeymasterSecret` $s \in \mathcal{S}$ is provably absent from all observable output channels $\mathcal{O}$ and persistent storage $\mathcal{P}$ reachable from the SDK client process boundary $\partial C$, for all execution traces $\tau$.*

$$\forall \tau \in \text{Traces}(C),\ \forall s \in \mathcal{S},\ \forall o \in \mathcal{O} \cup \mathcal{P} : \Big( \text{Read}_\tau(o) \Big) \perp\!\!\!\perp \Big( \text{Value}_\tau(s) \Big) \ \land \ \Big( \text{Addr}_\tau(s) \in \text{Enclave}(\text{Keymaker}) \Big) \ \land \ \Big( \text{Zeroize}_\tau(s) \prec \text{Free}_\tau(s) \Big)$$

---

### 2. Authenticated Fetch Proxying (Integrity & Origin Binding)
**Invariant:** *Every outbound network request $r_{out}$ emitted by the client proxy $\mathcal{P}_{sdk}$ is cryptographically bound to a specific, authorized user intent $I_u$ via an unforgeable capability token $\kappa$, and the proxy enforces strict egress policy $\Pi_{egress}$ such that no request reaches the network interface $\mathcal{N}$ without valid attestation.*

$$\forall r_{out} \in \text{Emitted}(\mathcal{P}_{sdk}) : \exists! \kappa \in \mathcal{K}_{valid} : \text{Verify}_{PK_{auth}}(\kappa, r_{out}) = \top \ \land \ \text{PolicyCheck}(\Pi_{egress}, r_{out}) = \top \ \land \ \text{Bind}(\kappa, I_u) \land \text{NonceFresh}(\kappa.\text{nonce})$$

---

### 3. Schema Parameter Repair (Idempotent Conformance)
**Invariant:** *The repair function $\mathcal{R}: \mathcal{D}_{raw} \to \mathcal{D}_{valid}$ is a total, idempotent projection operator onto the valid schema domain $\mathcal{D}_{valid} \subseteq \mathcal{D}_{raw}$, preserving the semantic intent of the user input $d_u$ under a defined distance metric $\delta$, and never inventing structural keys absent from the schema $\Sigma$.*

$$\forall d_{raw} \in \mathcal{D}_{raw} : \mathcal{R}(d_{raw}) \in \mathcal{D}_{valid} \ \land \ \mathcal{R}(\mathcal{R}(d_{raw})) = \mathcal{R}(d_{raw}) \ \land \ \text{Keys}(\mathcal{R}(d_{raw})) \subseteq \text{Keys}(\Sigma)$$
