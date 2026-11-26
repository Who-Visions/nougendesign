# nougendesign shell — Tauri (Rust) scaffold

The workbench shell ruled in **ADR 0001** (`docs/adr-0001-tauri-shell.md`):
Tauri (Rust) around the system webview. This is a **scaffold**, not the
finished workbench — the smallest skeleton that proves the ruled
architecture end to end.

## The contract

The shell stays a shell. Its whole job is:

1. **Load package** — read a compiled design package
   (`designs/nougenai-brand`: `design.json` + `manifest.json`) read-only.
2. **Render surface** — show one real surface styled by the package
   (the Fleet Boards verify-proof surface, `ui/surface/brand-surface.html`,
   token-styled from the package's compiled `tokens.css`).
3. **Explore tweaks** — list the bounded dimensions declared by the
   package's tweaks manifest (`tweaks/manifest.json`, dialect `tweaks/v1`).
   Exploring changes nothing; settling produces a candidate variant plan.
4. **Variant plans** — list the stored plans under `variants/`. Plans are
   inert candidates. There is deliberately **no apply command**: a plan
   takes effect only when Dave names it as locked, through the
   reviewed-spec flow.
5. **Verify** — the gate of record is the **headless reference renderer**
   (`tools/visual_verify.py`), never the shell's webview (OS webviews
   differ per platform; the shell's render is advisory). The Verify panel
   states this and prints the gate command; it does not grade its own
   renders.

The shell **never edits package sources** and holds no design state of
its own. Sources live in the shards; packages compile through
`tools/nougendesigns.py`.

## Layout

```
shell/
  Cargo.toml            workspace (core + src-tauri)
  core/                 nougendesign-shell-core: read-only package loading
    src/lib.rs            (design package, tweaks manifest, variant plans)
    src/bin/shell-data.rs emits the frontend data snapshot as JSON
    tests/                fixture + real-package integration tests
  src-tauri/            the Tauri v2 app (one read-only command:
                        load_package; capabilities: core:default only)
  ui/                   static frontend (no build step)
    index.html            four verb panels + surface frame; the markup
                          mirrors the bundled snapshot so the page is
                          meaningful without JS
    app.js                Tauri invoke -> bundled snapshot fallback
    shell-data.json       snapshot generated from the real package
    surface/              vendored copy of the verify-proof surface
                          (brand-surface.html + tokens.css + n-pin.webp)
```

## Run

Prerequisites: a Rust toolchain, and on Linux the Tauri v2 system
libraries (`libwebkit2gtk-4.1-dev`, `libgtk-3-dev`, `libsoup-3.0-dev`,
`librsvg2-dev`, `libayatana-appindicator3-dev`).

```sh
cd shell
cargo test -p nougendesign-shell-core   # core gates (no webview needed)
cargo run  -p nougendesign-shell        # the app (from the repo root it
                                        # finds designs/nougenai-brand by
                                        # walking up; or set
                                        # NOUGENDESIGN_PACKAGE_DIR)
```

Regenerate the frontend's bundled snapshot after the package changes:

```sh
cd shell
cargo run -p nougendesign-shell-core --bin shell-data -- \
  ../designs/nougenai-brand > ui/shell-data.json
```

Standalone frontend (no Tauri): serve `ui/` statically
(`python3 -m http.server -d ui`) — panels hydrate from
`shell-data.json`.

## Scaffold scope — what is NOT here yet

- No tweaks *controls*: the panel lists the manifest's dimensions; the
  exploration widgets are the next slice.
- No variant apply/lock action, by design (see contract above).
- No verify execution from the shell: the gate stays headless.
- One wired package (`nougenai-brand`); package switching is a later
  slice.
