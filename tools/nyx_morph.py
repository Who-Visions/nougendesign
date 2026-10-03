"""
NouGen Design - Nyx UI Cyberpunk Component Dialect Morph Tool
Translates and verifies design tokens against Nyx UI motion & aesthetic primitives
(cyberpunk card, light trails, glitch controls, HUD telemetry, scanline matrix).
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DESIGNS_DIR = REPO_ROOT / "designs"


def generate_nyx_morph(package_name: str) -> Dict[str, Any]:
    pkg_dir = DESIGNS_DIR / package_name
    if not pkg_dir.exists():
        raise FileNotFoundError(f"Design package '{package_name}' not found at {pkg_dir}")

    design_json = pkg_dir / "design.json"
    with open(design_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    tokens = data.get("tokens", {})
    colors = tokens.get("color", {})

    # Extract 60-30-10 palette
    bg = colors.get("background", {}).get("value", "#120b10")
    panel = colors.get("panel", {}).get("value", "#28111b")
    panel_card = colors.get("panel-card", {}).get("value", "#381725")
    primary = colors.get("primary", {}).get("value", "#fcd1d7")
    secondary = colors.get("secondary", {}).get("value", "#e9b1cd")
    rose = colors.get("rose", {}).get("value", "#c3829e")
    text = colors.get("text", {}).get("value", "#ffe7de")
    text_muted = colors.get("text-muted", {}).get("value", "#d8b2c2")

    nyx_dialect = {
        "package": package_name,
        "nyx_version": "1.0.0-cyber",
        "aesthetic_dialect": "Cyberpunk-Nocturnal-Matrix",
        "surfaces": {
            "canvas": bg,
            "card_substrate": panel_card,
            "glass_ambient": panel,
            "specular_rim": f"inset 0 1px 0 rgba(255, 255, 255, 0.12)",
        },
        "light_trail": {
            "gradient": f"conic-gradient(from 0deg, transparent 0deg, {rose} 90deg, {secondary} 180deg, {primary} 270deg, transparent 360deg)",
            "glow_spread": f"0 0 28px -4px {secondary}80",
            "border_width": "1px",
        },
        "glitch": {
            "channel_red": primary,
            "channel_cyan": secondary,
            "displacement_px": "2px",
            "cycle_ms": 180,
        },
        "hud_telemetry": {
            "label_color": text_muted,
            "meter_bg": f"{bg}cc",
            "meter_fill": f"linear-gradient(90deg, {rose} 0%, {secondary} 60%, {primary} 100%)",
            "meter_glow": f"0 0 12px {primary}aa",
        },
        "typography": {
            "heading": text,
            "body": text,
            "caption": text_muted,
            "mono_code": primary,
        },
    }

    return nyx_dialect


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nyx_morph.py <package_name> [--export]")
        sys.exit(1)

    pkg = sys.argv[1]
    export_flag = "--export" in sys.argv

    try:
        morph = generate_nyx_morph(pkg)
        formatted = json.dumps(morph, indent=2)

        if export_flag:
            target = DESIGNS_DIR / pkg / "nyx_dialect.json"
            with open(target, "w", encoding="utf-8") as f:
                f.write(formatted)
            print(f"[OK] Exported Nyx UI morph dialect to: {target}")
        else:
            print(formatted)

    except Exception as e:
        print(f"[ERROR] Failed to generate Nyx morph: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
