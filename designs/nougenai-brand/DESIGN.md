---
name: "nougenai-brand"
version: "0.1.0"
description: "The public NouGenAI brand surface: green-led, gold-highlighted, shards purple as the named secondary system."
colors: {"--accent": "#d4af37", "--accent-2": "#73fd7c", "--bg": "#0a0c0a", "--brand": "#73fd7c", "--brand-deep": "#1fae4e", "--control-ink": "#0a0c0a", "--danger": "#ff9d94", "--focus": "#d4af37", "--line": "#55654f", "--line-glow": "#55654f", "--muted": "#b9c2b2", "--panel": "#121711", "--panel-2": "#1a211a", "--panel-hover": "#242e24", "--panel-solid": "#121711", "--shard": "#a78bfa", "--shard-deep": "#7c5cd6", "--status-conflict-border": "#ff9d94", "--status-conflict-text": "#ff9d94", "--status-offline-border": "#55654f", "--status-offline-text": "#b9c2b2", "--status-pending-border": "#d4af37", "--status-pending-text": "#d4af37", "--status-sim-border": "#55654f", "--status-sim-text": "#b9c2b2", "--status-verified-border": "#73fd7c", "--status-verified-text": "#73fd7c", "--text": "#f0f3ec", "--warn": "#d4af37"}
---

# nougenai-brand

## referenceWorld

Broadcast newsroom identity, embroidered patch and enamel pin material culture, precision instrument labelling. This package governs the public brand surfaces — the NouGenAI channel, public sites, decks, one-pagers and Hotel Visions materials — not the fleet workbench, which stays under nougen-core.

## antiPatterns

Reject decorative gradients, glass, giant pills, sparkles, confetti colour and rainbow accent sprawl: do not mardi gras it. Green leads; gold is a highlight, never a field; purple belongs to the shards system alone and never mixes decoratively with gold. Glow is rejected as a CSS effect everywhere — no glow box-shadows, no neon text-shadow, no halo filters. The single scoped exception is the N pin mark itself: its glow is intrinsic to the pinned asset file (assets/n-pin.webp, sha256-pinned in evidence), and surfaces place those pinned bytes as-is. The exception covers the mark only; it never licenses recreating, redrawing, filtering or approximating the mark or its glow in CSS, canvas or generation, and it does not weaken the workbench dialect in nougen-core, where glow stays rejected without exception.

## materiality

Use deep green-tinted near-black grounds and opaque panels. The mark's material is the embroidered patch: a saturated green letterform with a stitched dark border on black. Gold reads as metal — rules, ticks, numerals and keylines — never as a wash. Purple appears only as the shards material: shard bodies, memory surfaces and relay identity.

## density

Public surfaces breathe more than the workbench: one message per region, generous separation between identity, message and action. Restraint is the density rule — if a region needs a third accent colour to work, the composition is wrong, not the palette. Keep sustained reading near 65ch; metadata and tables may use the page width.

## motionGrammar

Use short deliberate state transitions. The mark never pulses, breathes or animates its glow; the pinned asset is static by rule. Disable nonessential motion when reduced motion is requested.

## interactionPhysics

Inputs respond immediately; asynchronous work exposes progress, cancellation and recovery. Every public call to action states its destination before it is followed. Assistant suggestions show their evidence and wait for approval, and approved actions are logged.

## informationHierarchy

Brand green marks identity and the primary action of a region; gold marks emphasis inside content — a figure, a rule, a highlight — and nothing else; shards purple marks memory and shard content wherever it appears. Each region has one primary reading. Settle the page composition (regions, space budget, the primary reading of each region) before detailing components. Text stays live text on its own layer, never baked into an image.

## responsiveBehavior

Stack regions at narrow widths; allow document scrolling and wrap toolbars. Use rem type and spacing. Full-width regions use their container width rather than 100vw. Long identifiers wrap without losing content. Choose columns from available container width. At 320px and split-pane widths, independently meaningful regions must not touch or overlap. The mark keeps its aspect and its black ground at every size; it is never cropped into a decorative texture.

## Accessibility

Body text must meet 4.5:1 and focus/status indicators 3:1. Preserve labels and keyboard access. Measured default text on ground: 17.51:1; muted on panel: 9.88:1; focus on ground: 9.33:1. Light theme: text on ground 15.62:1; muted on panel 7.31:1; focus on ground 4.93:1. These are declared token pairs, not a complete application audit. Inputs have explicit accessible names. Controls have a 24px minimum target and 44px touch target. Reflow at 320px and text-size growth are verification requirements. Colour alone never conveys meaning; the mark is always paired with the NouGenAI name in text at first use on a surface.

## brandVoice

Use concrete verbs, technical accuracy and concise recovery instructions. Keep the same term for the same action. Public copy is plain, confident and receipts-first: claims carry numbers, dates and sources. Generic AI-slop phrasing is rejected the way generic visuals are — defaults are slop in words too.

## iconography

The glowing green N pin is the logo, at one-to-one parity with the pinned asset; it is placed, never redrawn, re-rendered, recoloured or approximated, by any tool, including generative ones. Supporting icons are consistent monochrome line icons paired with labels where unfamiliar. Purple iconography is reserved for shards surfaces.

## dataViz

Use labelled axes and text status; color alone never conveys meaning. Series order is fixed: brand green first, gold for the highlighted series, shards purple only for shard or memory data. Preserve data-bearing bar lengths, baselines, scales and area encodings. Pair each series with a visible label and provide a keyboard-accessible data table. Missing evidence is unavailable, not zero.

## stateGrammar

Specify default, hover, focus, selected, disabled, loading, empty, offline, success and error states. Verified, pending, conflict, offline and simulated are distinct states with distinct token triples; sample values are labeled illustrative and never presented as live telemetry. Stale and unsynchronized views are marked explicitly. A planned or gated surface states what is missing and who can enable it.

## provenance

Authored 2026-11-25 as Slice 1 of the Claude Design reversal build spec (brief: claude-design-reversal.md; Google Doc 1SbbZuwbMzUvpjGXHB_Vu0WbfkxpMvV6dIotbk4KfPE4; fleet shard 30224@db4). Palette relationships are Dave's standing locks: NouGenAI green with gold highlights and shards purple (ruling 2026-11-23), restraint as an explicit rule, and the glowing green N pin as the logo at one-to-one parity (ruling 2026-11-22, set as the NouGenAI channel profile picture). The brand green token is measured from the pinned mark itself. Every other specific value in this package is an invented candidate for Dave's review, listed as such in the evidence and in the pull request; nothing here is settled doctrine until he rules. First consumer: the next fleet visual build after approval — dav1d.nougenai.com is the named first surface.
