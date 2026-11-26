#!/usr/bin/env python3
"""visual_verify.py — the visual verify gate (Claude Design reversal, Module 4).

A standing pre-delivery step for visual artifacts (Spaces, decks, site
builds): render the surface, screenshot it, review it against a loaded
design package, and file the findings as evidence — machine-measured
findings as *observed*, visual-review findings as *inferred* prose, the
repo's own evidence rule. Nothing ships to Dave before this gate runs.

This tool lives OUTSIDE the deterministic compiler on purpose:
tools/nougendesigns.py stays pixel-free (its stated limit — screenshots
there register binary hashes only). This gate is the layer the repo
left open: it consumes a rendered surface and a package, never mutates
either, and emits a findings log.

Stdlib only. The screenshot itself is produced by an operator-supplied
renderer command, so the gate works with whatever renderer a lane has:

  # Chromium-compatible headless binary:
  python3 tools/visual_verify.py \
      --package designs/nougenai-brand \
      --html path/to/surface.html \
      --out verify-out \
      --screenshot-cmd "chrome --headless --no-sandbox \
          --screenshot={png} --window-size=1280,1000 {url}"

  # WeasyPrint (pure-python renderer):
  python3 tools/visual_verify.py \
      --package designs/nougenai-brand --html surface.html \
      --out verify-out \
      --screenshot-cmd "weasyprint {html} {png}"

  # Or bring a screenshot taken elsewhere:
  python3 tools/visual_verify.py --package designs/nougenai-brand \
      --html surface.html --screenshot already.png --out verify-out

{screenshot placeholders: {png} output path, {url} file:// URL of the
surface, {html} the surface path.}

After viewing the screenshot, the reviewing agent files its visual
findings as inferred prose and merges them in:

  python3 tools/visual_verify.py --package designs/nougenai-brand \
      --html surface.html --screenshot shot.png --out verify-out \
      --visual-findings visual.json   # [{"selector": ".hero",
                                      #   "severity": "warn",
                                      #   "statement": "...",
                                      #   "recommendation": "..."}]

Exit code: 1 when any finding has severity "fail", else 0.
Outputs in --out: findings.json, findings.md, screenshot.png (copy).
"""

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
VAR_RE = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")
IMG_RE = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)
LINK_RE = re.compile(r"""<link[^>]+href=["']([^"']+\.css)["']""", re.IGNORECASE)
STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
SHADOW_RE = re.compile(r"box-shadow\s*:\s*([^;}]+)", re.IGNORECASE)
RADIUS_RE = re.compile(r"border-radius\s*:\s*([0-9.]+)px", re.IGNORECASE)


# ---------------------------------------------------------------- tokens

def parse_tokens_css(text):
    """Return {token: value} from the :root block of a tokens.css."""
    root = re.search(r":root\s*\{(.*?)\}", text, re.DOTALL)
    if not root:
        return {}
    return {m.group(1): m.group(2).strip() for m in VAR_RE.finditer(root.group(1))}


def package_tokens(package):
    """(base tokens, spec). Base = the compiled tokens.css :root set
    overlaid with design.json's tokens — the default (dark) theme.
    Theme overrides are NOT merged in: they belong to their theme,
    and merging them would silently replace base values."""
    tokens = {}
    css = package / "tokens.css"
    if css.exists():
        tokens.update(parse_tokens_css(css.read_text()))
    spec = json.loads((package / "design.json").read_text())
    tokens.update(spec.get("tokens", {}))
    return tokens, spec


def themed_tokens(base, spec):
    """{theme name: token set} — 'base' plus each named theme with its
    overrides applied onto the base set."""
    out = {"base": dict(base)}
    for name, overrides in spec.get("themes", {}).items():
        merged = dict(base)
        merged.update(overrides)
        out[name] = merged
    return out


def palette_hexes(tokens):
    out = set()
    for value in tokens.values():
        for hit in HEX_RE.findall(str(value)):
            out.add(hit.lower())
    return out


# ---------------------------------------------------------------- checks

def _finding(check, severity, selector, statement, recommendation, evidence="observed"):
    return {
        "check": check,
        "evidence": evidence,
        "severity": severity,
        "selector": selector,
        "statement": statement,
        "recommendation": recommendation,
    }


def _rel_luminance(hexcolor):
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast_ratio(fg, bg):
    """WCAG contrast ratio between two hex colours."""
    l1, l2 = _rel_luminance(fg), _rel_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def check_contrast(spec, base_tokens):
    findings = []
    for theme, tokens in themed_tokens(base_tokens, spec).items():
        for pair in spec.get("contrastPairs", []):
            ink, ground = pair.get("ink"), pair.get("ground")
            if ink not in tokens or ground not in tokens:
                findings.append(_finding(
                    "contrast", "warn", f"{ink} on {ground} [{theme}]",
                    f"Declared contrast pair references a missing token ({ink} / {ground}).",
                    "Resolve the token names in design.json or tokens.css."))
                continue
            ratio = contrast_ratio(str(tokens[ink]), str(tokens[ground]))
            role = pair.get("role", "text")
            minimum = 3.0 if role == "ui" else 4.5
            severity = "info" if ratio >= minimum else "fail"
            findings.append(_finding(
                "contrast", severity, f"{ink} on {ground} [{theme}]",
                f"Contrast {ratio:.2f}:1 (declared pair, role {role}, minimum {minimum}:1).",
                "Within the package minimum." if severity == "info"
                else "Adjust the ink or ground token until the pair clears its minimum."))
    return findings


def check_asset_parity(spec, package, surface_html, surface_dir):
    findings = []
    pinned = [e["asset"] for e in spec.get("evidence", []) if "asset" in e]
    for asset in pinned:
        path, want = asset["path"], asset["sha256"]
        own = package / path
        if not own.exists():
            findings.append(_finding(
                "asset-parity", "fail", path,
                "Pinned asset is missing from the package itself.",
                "Restore the pinned bytes; never re-render the mark."))
            continue
        digest = hashlib.sha256(own.read_bytes()).hexdigest()
        findings.append(_finding(
            "asset-parity", "info" if digest == want else "fail", path,
            f"Package copy of the pinned asset hashes to {digest[:12]}… "
            f"(pin {want[:12]}…).",
            "Byte parity holds." if digest == want else
            "The pinned bytes changed. This is a lock event, not an edit: stop and surface it."))
        # If the surface references the asset, the referenced bytes must be the pin.
        name = Path(path).name
        for src in IMG_RE.findall(surface_html):
            if Path(src).name != name:
                continue
            ref = (surface_dir / src).resolve()
            if not ref.exists():
                findings.append(_finding(
                    "asset-parity", "fail", f'img[src="{src}"]',
                    "Surface references the pinned mark but the file does not resolve.",
                    "Point the surface at the package's pinned asset file."))
                continue
            ref_digest = hashlib.sha256(ref.read_bytes()).hexdigest()
            findings.append(_finding(
                "asset-parity", "info" if ref_digest == want else "fail",
                f'img[src="{src}"]',
                f"Surface's mark hashes to {ref_digest[:12]}… (pin {want[:12]}…).",
                "The surface places the pinned bytes as-is." if ref_digest == want else
                "The surface is serving a redrawn or re-encoded mark. Replace it with the pinned asset."))
    return findings


def surface_css_text(surface_html, surface_dir):
    chunks = list(STYLE_RE.findall(surface_html))
    inline = re.findall(r"""style=["']([^"']+)["']""", surface_html, re.IGNORECASE)
    chunks.extend(inline)
    for href in LINK_RE.findall(surface_html):
        css = (surface_dir / href).resolve()
        if css.exists() and css.suffix == ".css":
            chunks.append(css.read_text())
    return "\n".join(chunks)


def check_off_palette(css_text, base_tokens, spec):
    allowed = set()
    for tokens in themed_tokens(base_tokens, spec).values():
        allowed |= palette_hexes(tokens)
    findings, seen = [], set()
    for hit in HEX_RE.findall(css_text):
        colour = hit.lower()
        if colour in allowed or colour in seen:
            continue
        seen.add(colour)
        findings.append(_finding(
            "off-palette", "warn", colour,
            f"Surface uses {colour}, which is not a value of any token in the package.",
            "Replace with the nearest package token, or propose a token through design review."))
    return findings


def check_anti_patterns(css_text):
    findings = []
    low = css_text.lower()
    if "linear-gradient" in low or "radial-gradient" in low:
        findings.append(_finding(
            "anti-pattern", "fail", "gradient",
            "Surface CSS declares a gradient; the package rejects decorative gradients.",
            "Replace the gradient with a flat token ground."))
    if "backdrop-filter" in low or re.search(r"filter\s*:[^;]*blur\(", low):
        findings.append(_finding(
            "anti-pattern", "fail", "glass/blur",
            "Surface CSS blurs (glass); the package rejects blur glass.",
            "Use a solid panel token instead of a blurred ground."))
    for shadow in SHADOW_RE.findall(css_text):
        nums = [float(n) for n in re.findall(r"([0-9.]+)px", shadow)]
        if nums and max(nums) >= 12:
            findings.append(_finding(
                "anti-pattern", "fail", "box-shadow",
                f"box-shadow blur/spread reaches {max(nums):.0f}px — a glow-scale shadow; "
                "the package rejects glow shadows outside the pinned mark itself.",
                "Keep shadows tight (under 12px) or drop them."))
            break
    for radius in RADIUS_RE.findall(css_text):
        if float(radius) >= 24:
            findings.append(_finding(
                "anti-pattern", "fail", "border-radius",
                f"border-radius of {radius}px is a giant pill; the package rejects giant pill radii.",
                "Use the package radius tokens (sm/md/lg)."))
            break
    return findings


# ---------------------------------------------------------------- render

def png_dimensions(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def take_screenshot(cmd_template, html_path, png_path):
    url = html_path.resolve().as_uri()
    cmd = (cmd_template.replace("{png}", str(png_path))
                       .replace("{url}", url)
                       .replace("{html}", str(html_path)))
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0 or not png_path.exists():
        raise SystemExit(f"screenshot command failed ({proc.returncode}): "
                         f"{(proc.stderr or proc.stdout).strip()[:400]}")
    return cmd


# ---------------------------------------------------------------- report

def render_markdown(record):
    lines = [
        f"# Visual verify — {record['surface']}",
        "",
        f"- Package: `{record['package']}`",
        f"- Surface: `{record['surface']}`",
        f"- Screenshot: `{record['screenshot']['path']}` "
        f"(sha256 {record['screenshot']['sha256'][:16]}…, "
        f"{record['screenshot']['dimensions']})",
        f"- Verdict: **{record['verdict']}** — "
        f"{record['counts']['fail']} fail, {record['counts']['warn']} warn, "
        f"{record['counts']['info']} info",
        "",
        "Evidence kinds follow the repo rule: *observed* = machine-measured "
        "by this gate; *inferred* = visual-review prose filed by the "
        "reviewing agent after viewing the screenshot. Findings are input "
        "to review, never spec by themselves.",
        "",
        "## Findings",
        "",
    ]
    for i, f in enumerate(record["findings"], 1):
        lines += [
            f"### {i}. [{f['severity']}] {f['check']} — `{f['selector']}` ({f['evidence']})",
            "",
            f["statement"],
            "",
            f"Recommendation: {f['recommendation']}",
            "",
        ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--package", type=Path, required=True,
                        help="design package dir (design.json + tokens.css)")
    parser.add_argument("--html", type=Path, required=True, help="rendered surface (HTML)")
    parser.add_argument("--out", type=Path, required=True, help="findings output dir")
    parser.add_argument("--screenshot", type=Path, help="existing screenshot PNG")
    parser.add_argument("--screenshot-cmd",
                        help="renderer command template ({png} {url} {html})")
    parser.add_argument("--visual-findings", type=Path,
                        help="JSON list of inferred visual-review findings to merge")
    args = parser.parse_args()

    package, surface = args.package, args.html
    tokens, spec = package_tokens(package)
    surface_html = surface.read_text()
    surface_dir = surface.resolve().parent

    args.out.mkdir(parents=True, exist_ok=True)
    shot_path = args.out / "screenshot.png"
    render_cmd = None
    if args.screenshot_cmd:
        render_cmd = take_screenshot(args.screenshot_cmd, surface, shot_path)
    elif args.screenshot:
        shot_path.write_bytes(args.screenshot.read_bytes())
    else:
        raise SystemExit("provide --screenshot-cmd or --screenshot")

    findings = []
    findings += check_contrast(spec, tokens)
    findings += check_asset_parity(spec, package, surface_html, surface_dir)
    css_text = surface_css_text(surface_html, surface_dir)
    findings += check_off_palette(css_text, tokens, spec)
    findings += check_anti_patterns(css_text)

    if args.visual_findings:
        for vf in json.loads(args.visual_findings.read_text()):
            findings.append(_finding(
                vf.get("check", "visual-review"), vf.get("severity", "warn"),
                vf.get("selector", "(surface)"), vf["statement"],
                vf.get("recommendation", "Reviewer's call."),
                evidence="inferred"))

    dims = png_dimensions(shot_path)
    counts = {sev: sum(1 for f in findings if f["severity"] == sev)
              for sev in ("fail", "warn", "info")}
    record = {
        "package": str(package),
        "surface": str(surface),
        "render_cmd": render_cmd,
        "screenshot": {
            "path": str(shot_path),
            "sha256": hashlib.sha256(shot_path.read_bytes()).hexdigest(),
            "dimensions": f"{dims[0]}x{dims[1]}" if dims else "unknown (not a PNG)",
        },
        "counts": counts,
        "verdict": "FAIL" if counts["fail"] else "PASS",
        "findings": findings,
    }
    (args.out / "findings.json").write_text(json.dumps(record, indent=2) + "\n")
    (args.out / "findings.md").write_text(render_markdown(record))
    print(f"visual verify: {record['verdict']} — {counts['fail']} fail, "
          f"{counts['warn']} warn, {counts['info']} info → {args.out}/findings.md")
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
