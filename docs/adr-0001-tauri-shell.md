# ADR 0001 — The nougendesign shell is Tauri (Rust)

- **Status:** Accepted — ruled by Dave, 2026-11-25 ~19:37 ET ("tauri rust the shell then it is")
- **Target path in repo:** `docs/adr-0001-tauri-shell.md`
- **Branch plan:** stacked on `nou/verify-variants` (PR #16 head); retarget to `main` once #16 lands, merging after #16 in landing order
- **Scope of this record:** the shell only. The deterministic compiler (`tools/nougendesigns.py`) and the `nougendesigns/v0` package dialect are unchanged by this decision.

## Context

nougendesign compiles reviewed design specs deterministically into portable design packages (`design.json` + compiled outputs). Shards are the source of truth; the repo mirrors them. As of this ruling the pipeline has a brand package with pinned assets (PR #15), a visual verify gate and stored variant mutation plans (PR #16), and a tweaks manifest in flight. What it does not yet have is the workbench: the surface a human (or a lane) opens to load a package, look at a rendered surface, explore tweaks, lock a variant, and run verify. Dave was asked to pick the shell technology: Electron, C, Tauri (Rust), or Kotlin Multiplatform.

## Decision

**Tauri (Rust) is the nougendesign shell.**

The shell's whole job is: load package → render surface → explore tweaks → lock variants → run verify. It holds no state of its own beyond the session; everything it shows or changes is a package, a plan, or a findings log in the existing stores.

## Rationale

1. **The package is the product; shards are the source of truth.** The shell must stay a shell. It must never accrete its own truth — no shell-local design state, no shell-side edits that bypass the compiler. Tauri is a thin native wrapper around a webview plus a Rust backend; there is almost nothing in it to accrete into.
2. **The surfaces are HTML, so the canvas must be a webview.** Packages compile to HTML surfaces. A webview renders the actual surface — real fidelity for tweaks exploration and variant preview — instead of a re-implementation of the surface in a native widget toolkit.
3. **Rust is already a fleet language.** Blade's NGS engine work is Rust. A Tauri backend keeps the shell in a language the fleet already reads, and if the compiler core ever outgrows Python it can be re-implemented in C (the engine language, per the NGS precedent) and sit behind the Rust backend via FFI without changing the shell's contract.
4. **Weight.** Tauri ships a few MB around the OS webview. The fleet's lanes run headless on VMs where a bundled browser is dead weight (see Electron, below).

## Rejected alternatives

- **Electron** — rejected. It bundles Chromium (~150 MB class) into every install, and Electron applications tend to grow their own state and logic until the app *is* the product — the exact failure mode the deterministic-compiler architecture exists to prevent. Receipt from the night of this ruling: the visual verify gate's proof run hit this VM's Chromium-headless refusal and shipped on WeasyPrint instead; a shell that drags a browser around inherits that class of problem everywhere it goes.
- **C** — rejected for the shell, affirmed for engines. C is the fleet's engine language (NGS) and it is winning there. It has no rendering story for HTML surfaces and no GUI plumbing worth spending on; using it here buys nothing and costs a workbench's worth of effort.
- **Kotlin Multiplatform** — rejected. It solves native mobile UI across Android/iOS. That is not this problem: the fleet's phones are agent hosts, the workbench is a desktop tool, and KMP would add a fourth language lane (after C, Rust, Python) for the surface that would be used least.

## Named tradeoff and mitigation

Tauri renders through the **OS webview**, which differs per platform (WebView2 on Windows, WKWebView on macOS, WebKitGTK on Linux), so a surface can render slightly differently per OS and screenshots are not byte-stable across platforms.

**Mitigation, by design:** the verify gate of record remains the **headless reference renderer** (the Slice 3 gate, `tools/visual_verify.py`, with its pinned renderer), never the shell. The shell is for exploration and locking; its renders are advisory. A variant is locked against the package and judged by the reference gate, so webview variance can affect what a human sees while exploring but can never change what passes.

## Consequences

- Shell work, when Dave calls for it, is a Tauri app in this repo that reads packages and plans and writes nothing except through the existing tools (compiler, variant plans, verify gate).
- The tweaks manifest and variant plans are the shell's data contract: exploration state lives in the manifest's declared dimensions, locks live in stored plans. The shell invents no third store.
- Nothing in PRs #15/#16 or the in-flight tweaks slice depends on this decision; all of it is package-level and lands independently.
- If a future surface genuinely needs pixel-identical rendering everywhere (e.g. a kiosk build), that surface gets its own ADR superseding this one for that surface only; the default stands.
