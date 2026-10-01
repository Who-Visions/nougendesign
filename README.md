# nougendesign

NouGenDesigns: reviewed design specifications (`design.json`) compiled deterministically into `DESIGN.md`, `tokens.css`, `manifest.json` and `mutations.json`. See `designs/README.md` for commands and `designs/nougen-core/` for the canonical workbench package.

```sh
python tools/nougendesigns.py check designs/nougen-core/design.json designs/nougen-core
python -m pytest tests -q
```

## Provenance

Split from Who-Visions/NouGenShards on 2026-10-01 as a fresh import of `designs/`, `tools/nougendesigns.py`, `tools/nougendesign_discover.py`, their tests and workflow, at branch `feat/nougendesigns-morph-three-papers` (commit d9d16e5, PR #638 at the time). Earlier history stays in NouGenShards. `ui/src/styles.css` is a snapshot of that repo's workbench stylesheet, used only by the lint step. NouGenShards still carries its own copy until #638 merges and the two are reconciled.

## Staying in sync

NouGenShards is the source of truth; this repo is a mirror. A scheduled "Drift check" workflow goes red when they differ (the organization does not allow Actions to open PRs, so syncing stays a manual PR) of `designs/` and the compiler. Edit there, then:

```sh
python tools/sync_from_shards.py <NouGenShards checkout> --check   # exit 1 on drift
python tools/sync_from_shards.py <NouGenShards checkout>           # copy
```
