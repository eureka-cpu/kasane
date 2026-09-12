#!/usr/bin/env python3
"""
apply_dim_offset.py

Updates raw conf files to account for a uniform compositor dim offset.
The offset (-1R, -1G, 0B) was measured by comparing gamma-corrected values
to wl-color-picker readings taken on an unfocused (dimmed) browser window.
The dimmed appearance is preferred, so we bake it in.

For each raw color X:
  adjusted_gc = ICC(X) + DIM          # new gamma-corrected target
  new_raw     = ICC_inverse(adjusted_gc)  # raw value that browser renders as adjusted_gc

After running this, run gen_gamma.py to regenerate all gamma-corrected files.
"""

import os
import re

CALIB_R = [
    (14, 22),
    (24, 29),
    (29, 34),
    (36, 40),
    (93, 90),
    (139, 134),
    (187, 182),
    (213, 206),
]
CALIB_G = [
    (15, 22),
    (25, 30),
    (30, 34),
    (37, 41),
    (95, 92),
    (100, 98),
    (180, 174),
    (204, 197),
]
CALIB_B = [
    (16, 23),
    (27, 32),
    (32, 36),
    (40, 43),
    (101, 98),
    (103, 101),
    (169, 164),
    (175, 169),
]

CALIB_R_INV = sorted((y, x) for x, y in CALIB_R)
CALIB_G_INV = sorted((y, x) for x, y in CALIB_G)
CALIB_B_INV = sorted((y, x) for x, y in CALIB_B)

DIM = (-1, -1, 0)


def pl(calib, x):
    xs = [p[0] for p in calib]
    ys = [p[1] for p in calib]
    x = float(x)
    if x <= xs[0]:
        slope = (ys[1] - ys[0]) / (xs[1] - xs[0])
        return round(ys[0] + slope * (x - xs[0]))
    if x >= xs[-1]:
        slope = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
        return round(ys[-1] + slope * (x - xs[-1]))
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return round(ys[i] + t * (ys[i + 1] - ys[i]))
    return round(x)


def icc(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (
        max(0, min(255, pl(CALIB_R, r))),
        max(0, min(255, pl(CALIB_G, g))),
        max(0, min(255, pl(CALIB_B, b))),
    )


def icc_inv(r, g, b):
    return (
        max(0, min(255, pl(CALIB_R_INV, r))),
        max(0, min(255, pl(CALIB_G_INV, g))),
        max(0, min(255, pl(CALIB_B_INV, b))),
    )


def new_raw(hex_color):
    r, g, b = icc(hex_color)
    r2 = max(0, min(255, r + DIM[0]))
    g2 = max(0, min(255, g + DIM[1]))
    b2 = max(0, min(255, b + DIM[2]))
    ri, gi, bi = icc_inv(r2, g2, b2)
    return f"#{ri:02x}{gi:02x}{bi:02x}"


HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
THEMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "themes")
BASE_THEMES = ["shibui", "obi", "shibui-raised", "obi-raised"]


def verify():
    print("Spot checks (old_raw -> adjusted_gc, new_raw -> adjusted_gc):")
    cases = [
        ("#28292b", "#2b2c2e"),  # obi-raised background
        ("#1d1e20", "#212124"),  # obi background
        ("#d5cca9", "#cdc4a4"),  # obi foreground
        ("#bb6467", "#b56164"),  # obi beni dull
    ]
    for old, expected_gc in cases:
        r, g, b = icc(old)
        r2, g2, b2 = r + DIM[0], g + DIM[1], b + DIM[2]
        actual_gc = (
            f"#{max(0,min(255,r2)):02x}{max(0,min(255,g2)):02x}{max(0,min(255,b2)):02x}"
        )
        nr = new_raw(old)
        ri, gi, bi = icc(nr)
        gc_from_new = f"#{ri:02x}{gi:02x}{bi:02x}"
        print(
            f"  {old} -> gc {actual_gc} ({'OK' if actual_gc == expected_gc else 'FAIL'})"
            f"  new_raw {nr} -> gc {gc_from_new} ({'OK' if gc_from_new == expected_gc else 'FAIL'})"
        )


def update_conf(base):
    path = os.path.join(THEMES_DIR, f"{base}.conf")
    with open(path) as f:
        content = f.read()
    updated = HEX_RE.sub(lambda m: new_raw(m.group(0)), content)
    with open(path, "w") as f:
        f.write(updated)
    print(f"  updated {base}.conf")


def main():
    verify()
    print()
    print("Updating raw conf files:")
    for base in BASE_THEMES:
        update_conf(base)
    print("\nDone. Run gen_gamma.py to regenerate gamma-corrected files.")


if __name__ == "__main__":
    main()
