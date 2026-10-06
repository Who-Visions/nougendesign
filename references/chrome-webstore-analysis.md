# NouGenDesign Pattern Analysis: Chrome Web Store (N=200, ≥4.5★)

## 1. What the Data Supports
* **Neutral & Blue Icon Dominance:** Neutral tones (51/200) and blue (43/200) make up 47% of dominant icon hues; warm accents (yellow 6, pink 4) are rare.
* **Light-Mode Marketing Default:** Listing primary screenshots skew light (85 light, 68 mid vs. 47 dark; median luminance 0.59).
* **Image volume: NOT measured.** The pull capped `image_urls` at 8 per listing, so the apparent median of 8 is the cap, not data.
* **Structured, Compact Copy:** 43% (86/200) format their title with an explicit separator (`:`, `-`, `|`). Copy is concise: median name length is 28 characters; median short description is 99 characters.
* **Low Direct AI Labeling:** Only 11% (22/200) explicitly mention "AI" in their primary metadata.
* **Mid-to-High Scale Distribution:** 82% (164/200) hold 100k+ users (67 with 1M+), concentrated in practical utility domains (shopping 20, privacy 15, developer 15, tools 15).

---

## 2. What the Data Does NOT Support
* **Actual In-App Theme Preference:** First-screenshot luminance measures store promotional framing, not user preference or extension dark-mode toggle adoption.
* **Icon Composition or Contrast:** Dominant hue (128px pixel average) collapses gradients, outlines, glyphs, and white-space into a single bucket. A black glyph on white space evaluates as neutral/gray.
* **Typography, Spatial Density & Layout:** Font scales, whitespace, margin rhythm, corner radii, and element hierarchies are unmeasured.
* **Conversion Causality:** The dataset captures high-rated listings (≥4.5) across 20 distinct categories, not conversion lift, retention, or global install rankings.

---

## 3. Concrete Design Rules for NouGenDesign

1. **Title Architecture: `Brand: Function` Under 30 Chars** `[SUPPORTED]`  
   Structure display names with a distinct separator (`:`, ` - `, or `|`), targeting a ~28-character envelope (e.g., `NouGen: Context Navigator`).

2. **Ultra-Concise Hook at ~100 Characters** `[SUPPORTED]`  
   Restrict primary store summary descriptions to 90–110 characters, focusing strictly on core utility.

3. **Screenshot count** `[UNSUPPORTED]` - not derivable from this pull (image list was capped at 8); re-pull uncapped before setting a target.

4. **Default Hero Assets to High-Luminance Canvas (>0.58)** `[INFERENCE]`  
   Render primary marketing screenshots on clean, light backgrounds to align with the cohort's dominant presentation baseline (median 0.59).

5. **Icon Anchor: Neutral Core with High-Confidence Cool Accents** `[INFERENCE]`  
   Favor neutral monochromatic foundations with blue/cyan signature accents; avoid yellow/pink dominant palettes.

6. **Feature Utility Over "AI" Hype in Primary Surface Copy** `[INFERENCE]`  
   Omit gratuitous "AI" badges from titles/descriptions; lead with functional output (89% of top-rated cohort avoids explicit AI naming).


---
Source: `chrome-webstore-top200.json` (200 extensions, rating >= 4.5, top by users from 20 category listings; not a global ranking). Draft written by the agy CLI from measured counts; corrected by phoebus on 2026-10-05 (image-count claim removed: capped at 8 by the pull). Icon hue and screenshot luminance are 1x1 average-colour proxies.
