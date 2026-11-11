# Stitch DESIGN.md — Obsidian Singularity Shards

## 1. Brand Identity & Theme
- **Name**: Obsidian Singularity (NouGenDesign Core v1.0)
- **Concept**: Gravitational black hole singularity collapsing and exploding outward into faceted obsidian crystal shards with cosmic ultraviolet/purple event-horizon rim lighting.
- **Aesthetic**: Hyper-premium, cosmic dark-mode, high photopic contrast, tactile glassmorphism.

## 2. Color Palette (OKLCH & HEX)
- **Background Primary (Obsidian Void)**: `#050508` (`oklch(0.12 0.02 280)`)
- **Background Secondary (Deep Void)**: `#090611` (`oklch(0.15 0.04 290)`)
- **Accretion Surface**: `#180c2e` (`oklch(0.20 0.09 300)`)
- **Shard Base (Volcanic Glass)**: `#0a0714` (`oklch(0.14 0.03 295)`)
- **Shard Specular Reflection**: `#2e1065` (`oklch(0.25 0.16 300)`)
- **Shard Rim Glow / Neon Violet**: `#a855f7` (`oklch(0.65 0.25 305)`)
- **Relativistic Flare / Hotspot**: `#d8b4fe` (`oklch(0.82 0.12 305)`)
- **Doppler Accretion Core**: `#9333ea` (`oklch(0.58 0.28 302)`)
- **Stardust Spark**: `#f5f3ff` (`oklch(0.97 0.02 300)`)
- **Foreground Text Primary**: `#f8fafc` (18.5:1 contrast against obsidian void)
- **Foreground Text Muted**: `#c4b5fd` (8.2:1 contrast)
- **Border / Glass Divider**: `rgba(168, 85, 247, 0.24)`

## 3. Elevation & Surfaces (Glassmorphic L0-L3)
- **L0 (Backdrop Canvas)**: `#050508` pure obsidian void with radial cosmic nebula gradients.
- **L1 (Accretion Field)**: 60fps WebGL/Canvas with 180+ crystalline shards, Doppler accretion ribbons, and relativistic lensing ring.
- **L2 (Glassmorphic Cards)**: `background: rgba(13, 8, 26, 0.68)`, `backdrop-filter: blur(18px)`, `border: 1px solid rgba(168, 85, 247, 0.22)`, `box-shadow: 0 12px 40px rgba(5, 5, 8, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.08)`.
- **L3 (Active Glow / Controls)**: `box-shadow: 0 0 25px -4px rgba(168, 85, 247, 0.45)`.

## 4. Motion & Physics Grammar
- **Gravitational Well**: Inward Newtonian pull `(G * M) / r^2` decaying at event horizon radius (55px).
- **Accretion Orbit**: Tangential angular velocity with Doppler asymmetry (approaching quadrant flares white-violet).
- **Explosion Shockwave**: Outward relativistic burst `cubic-bezier(0.16, 1, 0.3, 1)` with radial displacement and faceted 3D polygon tumbling.
- **Micro-transitions**: 150ms ease-out on all UI interactive controls.

## 5. Typography
- **Headings**: `Space Grotesk`, -apple-system, sans-serif (700 weight, tight tracking).
- **Telemetry & Numbers**: `JetBrains Mono`, `Consolas`, monospace (aligned tabular data).
- **Body**: 14px floor, 1.6 line height, high readability.

## 6. Do's and Don'ts
- **DO**: Maintain pure obsidian void (`#050508`) as the foundational floor to allow vibrant purple/violet shards to pop with 18:1 contrast.
- **DO**: Use faceted, angular polygon shard geometry with distinct dark body vs. glowing purple specular edges.
- **DON'T**: Use muddy grayish purples or flat linear gradients across cards.
- **DON'T**: Render low-contrast sub-12px micro-text.
