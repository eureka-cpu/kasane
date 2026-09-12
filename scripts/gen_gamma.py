#!/usr/bin/env python3
"""Generate gamma-corrected kitty theme variants using piecewise linear ICC calibration.

Usage: python3 scripts/gen_gamma.py
Reads themes/{shibui,obi,shibui-raised,obi-raised}.conf
Writes themes/{...}-gamma.conf
"""

import os
import re

# Calibration: (raw_conf_value, browser_displayed_value) per channel
# Measured with wl-color-picker on the obi docs page (wide-gamut P3 display, Wayland).
# Raw values are exact conf hex; browser values are what the ICC-managed browser shows.
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


def piecewise_linear(calib, x):
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


def icc(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r2 = max(0, min(255, piecewise_linear(CALIB_R, r)))
    g2 = max(0, min(255, piecewise_linear(CALIB_G, g)))
    b2 = max(0, min(255, piecewise_linear(CALIB_B, b)))
    return f"#{r2:02x}{g2:02x}{b2:02x}"


HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")

GAMMA_BLURB_PREFIX = (
    "## blurb: Gamma-corrected variant -- ICC-shifted so kitty renders the same\n"
    "##   perceived values as the browser shows for the base theme on a wide-gamut\n"
    "##   display. Base: "
)


def transform_conf(src_path, dst_path, base_name):
    with open(src_path) as f:
        lines = f.readlines()

    out = []
    for line in lines:
        if line.startswith("## name:"):
            out.append(f"## name: {base_name} gamma\n")
            continue
        if line.startswith("## blurb:"):
            orig_text = line[len("## blurb: ") :]
            out.append(GAMMA_BLURB_PREFIX + orig_text)
            continue
        out.append(HEX_RE.sub(lambda m: icc(m.group(0)), line))

    with open(dst_path, "w") as f:
        f.writelines(out)
    print(f"  wrote {os.path.basename(dst_path)}")


def verify():
    cases = [
        ("#0e0f10", "#161617"),
        ("#18191b", "#1d1e20"),
        ("#1d1e20", "#222224"),
        ("#242528", "#28292b"),
        ("#5d5f65", "#5a5c62"),
        ("#bb6467", "#b66265"),
        ("#d5cca9", "#cec5a4"),
        ("#8bb4af", "#86aea9"),
    ]
    ok = True
    for raw, expected in cases:
        got = icc(raw)
        status = "OK" if got == expected else f"FAIL -- expected {expected}"
        print(f"  {raw} -> {got}  {status}")
        if got != expected:
            ok = False
    return ok


THEMES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "themes", "kitty"
)
BASE_THEMES = ["shibui", "obi", "shibui-raised", "obi-raised"]


def main():
    print("Calibration check:")
    if not verify():
        print("Calibration failed -- aborting.")
        return
    print()
    print("Generating gamma themes:")
    for base in BASE_THEMES:
        src = os.path.join(THEMES_DIR, f"{base}.conf")
        dst = os.path.join(THEMES_DIR, f"{base}-gamma.conf")
        transform_conf(src, dst, base)
    print("\nDone.")


if __name__ == "__main__":
    main()
