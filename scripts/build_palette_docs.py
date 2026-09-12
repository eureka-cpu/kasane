#!/usr/bin/env python3
"""Generate docs/*.html from themes/*.conf.

Color values are parsed from the .conf files (single source of truth).
Names, taglines, and per-accent notes are hand-authored below since the
.conf header comments are written for kitty users, not this page's prose.

Run after editing any themes/*.conf: python3 scripts/build_palette_docs.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = ROOT / "themes"
DOCS_DIR = ROOT / "docs"


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


THEMES = {
    "shibui": {
        "label": "shibui",
        "tagline": "A cool, dark ground with every accent at the edge of restraint.",
        "summary": "shibui (渋い) names the Japanese aesthetic of subdued, unobtrusive beauty. "
        "It is the quality of something that deepens the longer you look without ever "
        "announcing itself. The ground is a cool blue-black, the six accents are "
        "desaturated and muted, and nothing in the palette claims priority over the text.",
        "accents": [
            (
                "color1",
                "color9",
                "Beni",
                "seal red",
                "The calligraphy scroll's cinnabar stamp — quiet warmth, not alarm.",
            ),
            (
                "color2",
                "color10",
                "Cha",
                "tea-sage",
                "The tatami weave — dry sage, neutral and grounding.",
            ),
            (
                "color3",
                "color11",
                "Kin",
                "gilt",
                "The scroll's gold-leaf border, aged and quieted.",
            ),
            (
                "color4",
                "color12",
                "Ai",
                "indigo",
                "The kimono's cool cloth — the hero hue of this palette.",
            ),
            (
                "color5",
                "color13",
                "Fuji",
                "wisteria",
                "Mixed from Beni and Ai, sitting between scroll and cloth.",
            ),
            (
                "color6",
                "color14",
                "Mizu",
                "water",
                "Cha and Ai mixed — tatami green meets kimono blue.",
            ),
        ],
    },
    "obi": {
        "label": "obi",
        "tagline": "A near-black ashy ground from the kimono's sash, with six accents spanning the full wheel.",
        "summary": "obi (帯) is the sash of a kimono: darker and plainer than the cloth, the thing "
        "that holds everything together without drawing the eye. The ground is near-black "
        "with only a trace of cool. The six accents span the full warmth of the wheel, "
        "from coral to cherry blossom to sage to water, each one held at the same "
        "restraint. Blue survives as the quietest member of the set.",
        "accents": [
            (
                "color1",
                "color9",
                "Beni",
                "seal red",
                "The calligraphy scroll's cinnabar stamp.",
            ),
            (
                "color2",
                "color10",
                "Cha",
                "tea-sage",
                "The tatami weave — dry sage, unchanged.",
            ),
            (
                "color3",
                "color11",
                "Kaki",
                "persimmon",
                "Ferra's warm coral-salmon — the yellow slot reads as ripe fruit, not gilt.",
            ),
            (
                "color4",
                "color12",
                "Ai",
                "indigo, whispered",
                "Demoted from hero to the quietest accent — lighter and less saturated.",
            ),
            (
                "color5",
                "color13",
                "Sakura",
                "cherry blossom",
                "Ferra's pink opened up — deeper plum in shibui, blossom here.",
            ),
            ("color6", "color14", "Mizu", "water", "Cha and Ai mixed — unchanged."),
        ],
    },
}

ORDER = ["shibui", "obi"]


def hero(colors):
    return colors.get("color12", colors["foreground"])


def root_vars(colors):
    return f"""
    --sumi:         {colors['color0']};
    --bg:           {colors['background']};
    --bg-raised:    {colors.get('active_tab_background', colors['background'])};
    --bg-select:    {colors.get('selection_background', colors['background'])};
    --nezumi:       {colors['color8']};
    --washi-dim:    {colors['color8']};
    --washi:        {colors['color7']};
    --washi-bright: {colors['color15']};
    --fg:           {colors['foreground']};
    --accent-hero:      {hero(colors)};
    --accent-green-b:   {colors['color10']};
    --accent-gold-b:    {colors['color11']};
    --accent-pink-b:    {colors['color13']};
    --accent-red-b:     {colors['color9']};
    --serif: "Iowan Old Style", "Hoefler Text", Georgia, "Songti SC", serif;
    --sans: -apple-system, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    --mono: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
    """


def nav(current):
    links = [("index.html", "Overview")] + [(f"{t}.html", t) for t in ORDER]
    parts = []
    for i, (href, label) in enumerate(links):
        cls = (
            ' class="current"'
            if (current == "index" and href == "index.html")
            or href == f"{current}.html"
            else ""
        )
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
        if i < len(links) - 1:
            parts.append('<span class="sep">/</span>')
    return '<nav class="top">' + "".join(parts) + "</nav>"


def page_shell(title, description, vars_css, body, current):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="description" content="{description}">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<style>:root {{{vars_css}}}</style>
</head>
<body>
<main>
{nav(current)}
{body}
</main>
</body>
</html>
"""


CORRECTION_NOTE = (
    "Swatches are rendered through the browser\u2019s color management pipeline. "
    "On some displays the chips may appear as slightly different values than the hex "
    "codes shown \u2014 minor adjustment may be needed when applying these to terminals "
    "or other applications that bypass color management."
)


def ground_grid(colors):
    rows = [
        ("Sumi", "color0", colors["color0"]),
        ("Ground", "background", colors["background"]),
        (
            "Raised",
            "panel / tab",
            colors.get("active_tab_background", colors["background"]),
        ),
        ("Wash", "selection", colors.get("selection_background", colors["background"])),
        ("Nezumi", "color8 / comment", colors["color8"]),
        ("Washi", "color7", colors["color7"]),
        ("Paper", "foreground", colors["foreground"]),
        ("Washi, bright", "color15", colors["color15"]),
    ]
    cards = []
    for name, role, hexv in rows:
        cards.append(f"""      <div class="swatch">
        <div class="chip" style="background:{hexv}"></div>
        <div class="swatch-meta">
          <div class="swatch-name">{name} <span class="role">{role}</span></div>
          <div class="swatch-hex">{hexv}</div>
        </div>
      </div>""")
    return '<div class="grid">\n' + "\n".join(cards) + "\n    </div>"


def accent_grid(colors, accents):
    cards = []
    for dull_key, bright_key, name, subtitle, source in accents:
        dull, bright = colors[dull_key], colors[bright_key]
        cards.append(f"""      <div class="pair">
        <div class="pair-chips">
          <div style="background:{dull}"></div>
          <div style="background:{bright}"></div>
        </div>
        <div class="pair-meta">
          <div class="pair-name">{name} &middot; {subtitle}</div>
          <div class="pair-source">{source}</div>
          <div class="pair-hex"><span>{dull}</span><span>{bright}</span></div>
        </div>
      </div>""")
    return '<div class="pair-grid">\n' + "\n".join(cards) + "\n    </div>"


def terminal_preview(theme_key):
    return f"""<!-- prettier-ignore -->
<div class="term">~/scrolls <span class="comment"># {theme_key}</span>
<span class="kw">&#10095;</span> cat {theme_key}.theme

<span class="comment"># palette</span>
<span class="kw">def</span> <span class="fn">accent</span>(name: <span class="kw">str</span>) -&gt; tuple[<span class="kw">int</span>, <span class="kw">int</span>, <span class="kw">int</span>]:
    <span class="kw">match</span> name:
        <span class="kw">case</span> <span class="str">"hero"</span>:
            <span class="kw">return</span> (<span class="num">0x9e</span>, <span class="num">0xa7</span>, <span class="num">0xba</span>)
        <span class="kw">case</span> _:
            <span class="kw">raise</span> <span class="err">ValueError(<span class="str">"no such accent"</span>)</span>
<span class="kw">&#10095;</span> <span class="cursor-blk"> </span></div>"""


def build_theme_page(key):
    data = THEMES[key]
    colors = parse_conf(THEMES_DIR / f"{key}.conf")
    title = f"{data['label']} — palette study"
    body = f"""  <p class="eyebrow">{data['label']} &middot; palette study</p>
  <h1>{data['tagline']}</h1>
  <p class="lede">{data['summary']}</p>

  <section>
    <h2>Ground</h2>
    <p class="section-note">{CORRECTION_NOTE}</p>
    {ground_grid(colors)}
  </section>

  <section>
    <h2>Accents</h2>
    {accent_grid(colors, data['accents'])}
  </section>

  <section>
    <h2>In place</h2>
    {terminal_preview(key)}
  </section>

  <footer>
    Example implementations can be found at <a href="https://github.com/eureka-cpu/kasane/tree/master/themes">themes/</a> &middot;
    see the <a href="index.html">overview</a> for how {data['label']} compares to its siblings.
  </footer>
"""
    return page_shell(title, data["tagline"], root_vars(colors), body, key)


def build_index_page():
    colors = parse_conf(THEMES_DIR / "obi.conf")
    cards = []
    for key in ORDER:
        data = THEMES[key]
        tcolors = parse_conf(THEMES_DIR / f"{key}.conf")
        swatch_keys = [
            "background",
            "color1",
            "color2",
            "color3",
            "color4",
            "color5",
            "color6",
            "color7",
        ]
        row = "".join(
            f'<span style="background:{tcolors[k]}"></span>' for k in swatch_keys
        )
        cards.append(f"""    <a class="theme-card" href="{key}.html">
      <div class="swatch-row">{row}</div>
      <h3>{data['label']}</h3>
      <p>{data['tagline']}</p>
    </a>""")

    compare_rows = []
    for label, keyname in [
        ("background", "background"),
        ("foreground", "foreground"),
        ("Beni &middot; red", "color1"),
        ("Cha &middot; green", "color2"),
        ("Ai &middot; blue", "color4"),
    ]:
        cells = []
        for key in ORDER:
            tcolors = parse_conf(THEMES_DIR / f"{key}.conf")
            hexv = tcolors.get(keyname, "—")
            cells.append(
                f'<td><span class="chip-inline" style="background:{hexv}"></span>{hexv}</td>'
            )
        compare_rows.append(f"<tr><th>{label}</th>{''.join(cells)}</tr>")

    body = f"""  <p class="eyebrow">kasane &middot; palette study</p>
  <h1>Two quiet rooms</h1>
  <p class="lede">
    <em>Kasane</em> (重ね) means layering. In kimono culture it names the practice of combining
    garments so that carefully paired colors show at the sleeves and collar, each layer
    individually restrained, together creating depth without noise. Two dark, muted terminal
    themes, each available as a ground variant, a raised surface variant, and a gamma-corrected
    variant for wide-gamut displays.
  </p>
  <p class="lede">
    Both themes were designed with accessibility in mind. The author is color-blind and has
    dyslexia, and rotates regularly between themes like ferra, gruvbox, meliora, kanagawa, and ayu. All
    are beautiful. All eventually tire in a specific way: a single accent that reads the wrong
    hue for color-deficient eyes, or a palette so uniform the eyes adjust to it and reading
    becomes harder, prompting a theme change to reset. kasane tries to thread that needle. No
    accent is bright enough to demand attention or cause eye strain, but no two adjacent tones
    are close enough to collapse into each other. The foreground is warm parchment against a
    near-black ground, providing strong contrast without the fatigue of white on black.
  </p>
  <p class="lede">
    The visual language comes from three Japanese material references: a calligraphy scroll
    (sumi ink, seal red, gilt), a kimono (dark cool cloth and its sash), and tatami (the
    sage-olive weave underfoot). Colors represent the intent of those references, dark, muted,
    and considered, not literal pixel samples.
  </p>

  <section>
    <h2>The themes</h2>
    <div class="theme-cards">
{chr(10).join(cards)}
    </div>
  </section>

  <section>
    <h2>At a glance</h2>
    <p class="section-note">Key values compared across both themes.</p>
    <div class="wide-table-wrap">
    <table class="compare">
      <tr><th>&nbsp;</th>{"".join(f"<th>{k}</th>" for k in ORDER)}</tr>
      {chr(10).join(compare_rows)}
    </table>
    </div>
  </section>

  <footer>
    Shaped by time with <a href="https://github.com/casperstorm/ferra">ferra</a>, gruvbox, meliora, kanagawa, and ayu.
  </footer>
"""
    return page_shell(
        "kasane &middot; shibui / obi",
        "Two muted colour palettes for calm, accessible reading.",
        root_vars(colors),
        body,
        "index",
    )


def main():
    (DOCS_DIR / "index.html").write_text(build_index_page())
    for key in ORDER:
        (DOCS_DIR / f"{key}.html").write_text(build_theme_page(key))
    print("wrote docs/index.html and", ", ".join(f"docs/{k}.html" for k in ORDER))


if __name__ == "__main__":
    main()
