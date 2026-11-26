---
name: "nougenai-site"
version: "1.0.0"
description: "The canon design tokens of nougenai.com, reversed from the live site's own theme: obsidian ground, carbon panels, ivory text, gold accent, emerald signal, Inter + Syne. Nou's Desk on /news is its first recorded surface."
colors: {"--accent": "#CFAF5A", "--accent-2": "#8B5E34", "--bg": "#111111", "--brand": "#2F8F79", "--control-ink": "#111111", "--danger": "#C44E3A", "--focus": "#CFAF5A", "--muted": "#A6A29C", "--panel": "#1C1C1C", "--panel-solid": "#1C1C1C", "--text": "#F4F1EA"}
---

# nougenai-site

## referenceWorld

The live nougenai.com: a dark newsroom surface — obsidian ground, carbon panels, ivory text, one gold accent, a muted emerald for live and status signals, copper and terracotta as warm data accents. Inter carries text; Syne carries display. This package governs nougenai.com and its surfaces, including Nou's Desk on /news. It is the reversed record of a look that already ships, not a proposal.

## antiPatterns

Do not re-skin the site from another package's candidates: on nougenai.com these tokens are canon, and other packages' values (including nougenai-brand's pin green #73fd7c and gold #d4af37) do not apply here. No light theme exists on the site and none is to be invented in its name. Gold stays an accent — pills, rules, keylines, focus — never a field. No decorative gradients, no glass beyond the established carbon/40 blur cards, no accent sprawl: the site's restraint is part of the record.

## materiality

Obsidian #111111 is the ground; carbon #1C1C1C at 40% with backdrop blur is the card material, edged in white at 5%. Ivory #F4F1EA is the reading text; stone #A6A29C is metadata. Gold #CFAF5A reads as metal: rules, ticks, numerals, pills. Emerald #2F8F79 is the live signal — dots, labels, the Desk's edition tags. Copper #8B5E34 and terracotta #C44E3A appear only as warm data accents.

## density

The news page breathes at an 87.5rem measure (max-w-[1400px] at 2xl) inside a 95% frame, widening on the ultra-wide breakpoints. Cards sit in 2rem grid gaps. One lead per zone; the Desk takes exactly one card above the wire.

## motionGrammar

Tickers move: horizontal marquee 30s linear infinite, vertical marquee 60s, slide-progress 6s for the hero carousel. Content itself does not animate beyond short hover transitions. Reduced motion is honoured by the compiled sheet's policy block.

## interactionPhysics

Cards are links and read as links: borders warm to gold at 30% on hover, titles turn gold. Focus is a 2px gold outline at 2px offset, everywhere, from the base layer. Asynchronous regions (weather, tickers) degrade to a labelled fallback rather than blocking the page.

## informationHierarchy

Gold marks the brand and the primary emphasis; emerald marks live/status and edition identity; ivory is the reading layer; stone is metadata and time. Each zone has one lead: the Desk's latest edition above the wire, then the hero carousel, then the stream.

## responsiveBehavior

Stack at narrow widths; the frame is 95% to 2xl, then fixed measures widen through the ultra-wide breakpoints (3xl 120rem, 4xl 160rem, 5xl 240rem, 8k 480rem). The Desk card collapses to one column, image below text. Type and spacing stay rem-based.

## Accessibility

Measured with the compiler's WCAG ratios on the declared pairs: text on ground 16.74:1; text on panel 15.11:1; muted on panel 6.71:1; muted on ground 7.44:1; gold on ground 8.93:1; control ink on gold 8.93:1. Emerald on ground measures 4.79:1 — above the text floor, recorded as a UI pair because the site uses it for labels and signals. Terracotta (4.04:1) and copper (3.37:1) clear only the 3:1 UI floor: they are never body text. These are declared token pairs from the reversed theme, not a full application audit.

## brandVoice

The site's voice is the newsroom's: plain, confident, receipts-first. Labels are short uppercase with wide tracking ('Updated Regularly', 'Stories & Insights for Everyone'). Nou's Desk speaks as Nou: 'Reports by Nou', 'Listen — Nou reads this edition'.

## iconography

Monochrome line icons (lucide) paired with labels; the gold NEWS in the NOUGENNEWS wordmark is type, not an image. The glowing N pin belongs to the brand package and the channel; the site's own mark is its wordmark.

## dataViz

Market and chart accents use gold first, emerald for live series, terracotta for negative movement, copper as the warm secondary. Colour is always paired with a label or a figure; missing data is unavailable, not zero.

## stateGrammar

Live regions mark themselves: the emerald dot pulses on 'Updated Regularly'; a stale wire is labelled, never hidden. The Desk states its empty state by absence — no card until the first edition publishes. Weather shows its fallback's name ('desk location') when it is not the viewer's own.

## provenance

Reversed 2026-11-26 from the live site's own code at Dave's ruling ('reverse the site's design tokens into Nougendesign so that it's canon'). Every value is observed from Who-Visions/nougenai-next (globals.css @theme at ea8229ee; the news components) except the dialect slot mapping, recorded as inferred in the evidence. Nothing in this package is invented; where the site has no value (a light theme, a mono font), the package records the absence instead of filling it.
