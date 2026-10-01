"""Shared design tokens and SVG helpers.

Every generated visual (static and live) imports from this module so the whole
profile reads as one system: one palette, one typeface stack, one set of
primitives (panel, corner brackets, segmented indicators).
"""
from xml.sax.saxutils import escape as esc

# ── Palette ────────────────────────────────────────────────────────────────
BG = "#070a0f"        # page-level background
PANEL = "#0b1017"     # raised surface
LINE = "#18212d"      # hairlines, grids
LINE_HI = "#2a3748"   # emphasised hairlines, empty indicator cells
FG = "#e6edf3"        # primary text
MUTED = "#8593a6"     # secondary text
DIM = "#4b596b"       # tertiary text, ticks
ACCENT = "#7df9ff"    # the single accent (electric cyan)
ACCENT_MID = "#2fb4c2"
ACCENT_LOW = "#0f4b55"

# Intensity ramp (0..4) used by indicators and the contribution matrix
HEAT = ["#0e141b", "#0f4b55", "#188a97", "#4fd0dc", "#7df9ff"]
RAMP5 = ["#188a97", "#2fb4c2", "#4fd0dc", "#6ee9f2", "#7df9ff"]

# GitHub renders SVG via <img>, which blocks web fonts. This stack picks the
# best installed monospace on the viewer's machine.
FONT = "'JetBrains Mono','SF Mono','Cascadia Code','Roboto Mono',Consolas,'Liberation Mono',monospace"

# Respect reduced-motion everywhere.
BASE_CSS = """
@media (prefers-reduced-motion: reduce){*{animation:none!important;opacity:1!important}}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
"""


def svg(w, h, body, defs="", css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}" role="img">\n'
        f"<defs>{defs}<style>{BASE_CSS}{css}</style></defs>\n"
        # Opaque background so every asset stays legible on GitHub's light theme too.
        f'<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}\n</svg>\n'
    )


def brackets(x, y, w, h, s=12, color=ACCENT, sw=1.5, opacity=1):
    """Four L-shaped corner marks. The signature border of this design system."""
    d = (
        f"M{x},{y + s} V{y} H{x + s} "
        f"M{x + w - s},{y} H{x + w} V{y + s} "
        f"M{x + w},{y + h - s} V{y + h} H{x + w - s} "
        f"M{x + s},{y + h} H{x} V{y + h - s}"
    )
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" '
        f'opacity="{opacity}"/>'
    )


def panel(x, y, w, h, title=None, tag=None):
    """Surface with hairline border, corner brackets and an optional header."""
    out = [
        f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" '
        f'fill="{PANEL}" stroke="{LINE}"/>',
        brackets(x, y, w, h),
    ]
    if title:
        out.append(
            f'<text x="{x + 18}" y="{y + 23}" font-size="10.5" font-weight="700" '
            f'letter-spacing="3" fill="{MUTED}">{esc(title)}</text>'
        )
        out.append(
            f'<path d="M{x + 18},{y + 36.5} H{x + w - 18}" stroke="{LINE}"/>'
        )
    if tag:
        out.append(
            f'<text x="{x + w - 18}" y="{y + 23}" font-size="10" letter-spacing="2" '
            f'text-anchor="end" fill="{DIM}">{esc(tag)}</text>'
        )
    return "\n".join(out)


def segments(x, y, level, total=5, w=14, h=6, gap=3, delay=0.0):
    """Segmented familiarity indicator, left to right, with a staggered fade-in."""
    out = []
    for i in range(total):
        filled = i < level
        fill = RAMP5[i] if filled else "#141c26"
        d = delay + i * 0.05
        out.append(
            f'<rect class="s" x="{x + i * (w + gap)}" y="{y}" width="{w}" height="{h}" '
            f'fill="{fill}" style="animation-delay:{d:.2f}s"/>'
        )
    return "".join(out)


SEG_W = 5 * 14 + 4 * 3  # rendered width of segments()
