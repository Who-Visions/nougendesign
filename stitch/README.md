# NouGen Stitch SDK Integration

Official integration of the Google Stitch SDK (`@google/stitch-sdk`) into the NouGenDesign and NouScripts ecosystem.

## Capabilities

- **Keymaker Vault Grounded**: Resolves `STITCH_API_KEY` directly from the local Keymaker vault (`shards_secrets.db`) with zero secret leakage in CLI parameters, environment files, or git commits.
- **Authenticated Fetch Interceptor**: Injects `X-Goog-Api-Key` headers dynamically into all Stitch API calls and download endpoints (`https://stitch.googleapis.com/...`).
- **Complete Project & Screen Orchestration**:
  - List all Stitch projects and inspect screen hierarchies.
  - Download complete projects including self-contained HTML (`code.html`), screenshots (`screen.png`), assets, and Material You / Stitch `DESIGN.md`.
  - Generate brand new UI screens using Gemini 3 in Stitch.
  - Create design variants (`variants`) with controllable creative ranges and aspect focus.
- **NouGenDesign Compiler Export**:
  - Exports Stitch screens directly into `nougendesign/designs/<slug>/`.
  - Generates `nougendesigns/v0` `design.json` token specifications.
  - Automatically verifies 100% WCAG AAA contrast and anti-slop rules via `nougendesigns.py lint`.

## Usage

### Run Unit Tests
```bash
bun test
```

### CLI Commands

```bash
# List all Stitch projects
bun run stitch projects

# List all screens in a project
bun run stitch screens <projectId>

# Download entire project (HTML, images, DESIGN.md)
bun run stitch download <projectId> [outDir]

# Download single screen assets
bun run stitch get-screen <projectId> <screenId> [outDir]

# Generate a new screen with Gemini in Stitch
bun run stitch generate <projectId> "<prompt>" [outDir]

# Export screen directly into NouGenDesign and run linter
bun run stitch export-to-nougen <projectId> <screenId> <slug>
```
