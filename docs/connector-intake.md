# Connector intake — Stitch and Figma methods for the morph pipeline

**Status:** distilled 2026-11-25 from the first live passes (Stitch generation +
Figma read proof), companion to ADR 0001 and the tooling brief
(`~/workspace/nougendesign-tooling-brief.md`). Candidates, not locks: this doc
records the method; the packages remain the canon.

External design tools feed the pipeline as **evidence**, never as canon.
Everything a connector returns is labeled (observed / inferred / invented),
morphed into a package change or a stored variant plan, gated, and locked by
Dave before it takes effect. No connector writes canon directly.

## Google Stitch — generation intake

- Connector: `custom.google-stitch` (official MCP server at
  `https://stitch.googleapis.com/mcp`, API key in the `X-Goog-Api-Key` header,
  carried only through the connector's surrogate exchange — never in a file,
  an environment variable, or the repo's Keymaker).
- Client: `~/workspace/custom-connectors/custom.google-stitch/bin/client.py`
  (`list-tools`, `call-tool`). Allowed tools are allow-listed in the client;
  a tool the server adds later stays blocked until reviewed.
- Verb sequence: `create_project` → `generate_screen_from_text` →
  `download_file` (HTML + native screenshot) → morph by hand or via the
  `stitch/` CLI export → Slice 3 verify gate → variant plan candidate →
  Dave's lock.
- The repo's `stitch/` CLI is the SDK path: it resolves `STITCH_API_KEY`
  from the local Keymaker and injects the header itself. The connector
  credential Dave entered on 2026-11-25 lives in the connector store, NOT
  in Keymaker, so `export-to-nougen` cannot run keyed until the key also
  lands in Keymaker. Until then the morph steps run by hand (see the
  pass-1 record) and the hand-off point is stated in the plan.
- Evidence rule: a generated screen is **inferred** (its layout and styling
  choices) with **invented** data (names, counts, sizes). The first pass
  proved why: the generator drew its own N logo instead of the pinned
  asset, and its two urgent counts disagreed (3 vs 2). Both defects are
  recorded in the candidate plan, never copied.
- First live pass (2026-11-25): project `6226010854277612569`, screen
  "Fleet Boards - Operations" (`a7d674207f9e41519a13262dfcbe0c26`),
  distilled into `designs/nougenai-brand/variants/boards-stitch-pass1-layout.json`.

## Figma — designed-work intake and review export

- Connector: the Figma connector (`/opt/hatch/bin/figma`), wrapping the
  official remote MCP server (`https://mcp.figma.com/mcp`, OAuth). Dave
  completed the OAuth connection on 2026-11-25.
- Verb sequence (intake): `get_design_context` + `get_variable_defs` for a
  frame → variables map to package tokens → the frame's structure becomes
  **observed** evidence rows in a morph candidate → compiler emits the
  package → verify gate files Figma-vs-compiled deltas as findings.
- Verb sequence (review export): a locked package is written back with
  `use_figma` so a human reviews the real canvas; comments land on real
  nodes and are read back as findings.
- Boundary, measured: every substantive read (`get_design_context`,
  `get_variable_defs`, `get_libraries`, `search_design_system`) requires a
  file key. The 2026-11-25 proof ran `whoami` (account "NouGenAi",
  team "NouGenAi's team", Starter tier, View seat) and confirmed
  `search_design_system` refuses without `fileKey`. The intake therefore
  starts from a Figma file link supplied by Dave or a contributor; there
  is no file-less browse of the account's files through this server.
- Pool reality: Starter/View seats get roughly 6 MCP calls per month, so
  Figma is a deliberate intake, not a polling source. Spend calls on
  frames that will actually morph.

## Evidence labeling for connector output

- Figma frames, variables and components: **observed** (a human designed
  them; the connector measured them).
- Stitch screens: **inferred** layout/styling, **invented** data and any
  asset the generator drew (logos especially — the pinned-asset rule in
  the brand package is the check).
- Nothing from either connector is promoted past candidate without a
  package morph, the verify gate, and Dave's lock.

## Friction log — measured 2026-11-25, fixes equated from the runs

1. **NO_PROXY bracket trap (known fleet quirk, re-bitten).** The VM's
   `NO_PROXY` carries bracketed IPv6 entries; httpx/urllib paths choke.
   Fix applied on every connector call tonight: strip `[` `]` from
   `NO_PROXY`/`no_proxy` before invoking the client. (Stitch list-tools
   run 1 also timed out at 47 s against a cold path; the identical retry
   completed in 3.3 s — a cold-start, not a credential fault. Rule: one
   identical retry is justified after a transport timeout on a read;
   never after a 401/403.)
2. **Generation outruns the MCP template's 45 s timeout.**
   `generate_screen_from_text` completed server-side in ~45 s; the stock
   template client would have cut it off mid-write. Fix: the Stitch
   client copy carries a `LONG_TOOLS` set (generate/edit/variants) with a
   600 s read timeout; all other tools keep 45 s. After any timed-out
   write, check state (`list_screens`) before retrying — pass 1 verified
   the project empty before its retry, so the retry was safe.
3. **Two key paths, one key.** The connector credential (Dave's secure
   entry) and the repo CLI's Keymaker lookup are separate stores. The
   CLI's `export-to-nougen` stays unkeyed until the key is also in
   Keymaker; the connector path works today. Any brief that says "run
   export-to-nougen" without naming the store is wrong.
4. **Figma's CLI takes arguments inline.** `figma call-tool` wants
   `--arguments-json '<json>'`, not `--arguments-file` (the Stitch and
   shards clients take the file). One failed call tonight; the fix is
   knowing the shape per client.
5. **Local rendering is approximate for generated HTML.** The Stitch
   screen is Tailwind/grid; WeasyPrint (the verify gate's local renderer)
   cannot lay it out — its render is a degraded text flow, while
   Stitch's native screenshot is faithful. Rule: for connector-generated
   screens, file the native screenshot as the visual evidence and label
   the WeasyPrint render as renderer-limited, exactly as ADR 0001's
   webview caveat implies. A verify finding about layout requires a
   webview-class renderer, not WeasyPrint.
6. **Figma pool ceiling.** Starter/View ≈ 6 MCP calls/month (per the
   tooling brief's verified plan facts). `whoami` + one probe cost 2 of
   the month's calls. Budget Figma calls like design-pool spend
   (Module 18): know the pool before the step.
