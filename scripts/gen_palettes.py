#!/usr/bin/env python3
"""Generate palettes/{theme}.json from themes/*.conf.

Reads all 8 theme conf files (base + raised + gamma variants).
Writes a flat JSON object of color key->hex value per theme.
Run after gen_gamma.py so the *-gamma.conf files exist.

Usage: python3 scripts/gen_palettes.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = ROOT / "themes" / "kitty"
PALETTES_DIR = ROOT / "palettes"

THEMES = [
    "shibui",
    "obi",
    "shibui-raised",
    "obi-raised",
    "shibui-gamma",
    "obi-gamma",
    "shibui-raised-gamma",
    "obi-raised-gamma",
]

RENAMES = {
    "color0": "black",
    "color1": "red",
    "color2": "green",
    "color3": "yellow",
    "color4": "blue",
    "color5": "magenta",
    "color6": "cyan",
    "color7": "white",
    "color8": "black-bright",
    "color9": "red-bright",
    "color10": "green-bright",
    "color11": "yellow-bright",
    "color12": "blue-bright",
    "color13": "magenta-bright",
    "color14": "cyan-bright",
    "color15": "white-bright",
}


def parse_conf(path):
    text = path.read_text()
    colors = {}
    for line in text.splitlines():
        m = re.match(
            r"^(cursor|foreground|background|selection_foreground|selection_background|"
            r"color\d{1,2}|active_tab_foreground|active_tab_background|"
            r"inactive_tab_foreground|inactive_tab_background)\s+(#[0-9a-fA-F]{6})",
            line,
        )
        if m:
            colors[m.group(1)] = m.group(2)
    return colors


def main():
    PALETTES_DIR.mkdir(exist_ok=True)
    for theme in THEMES:
        conf = THEMES_DIR / f"{theme}.conf"
        raw = parse_conf(conf)
        colors = {RENAMES.get(k, k): v for k, v in raw.items()}
        out = PALETTES_DIR / f"{theme}.json"
        out.write_text(json.dumps(colors, indent=2) + "\n")
        print(f"  wrote palettes/{theme}.json")
    print("Done.")


if __name__ == "__main__":
    main()
