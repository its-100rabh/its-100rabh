#!/usr/bin/env python3
"""Builds the static SVG assets for the profile README.

Edit CONFIG / IDENTITY / STACK / LINKS below, then run:

    python scripts/build_assets.py

Output goes to ./assets/. Live (API-driven) visuals are produced separately by
scripts/generate_stats.py.
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from design import *  # noqa: F401,F403

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# ── Content (edit me) ──────────────────────────────────────────────────────
CONFIG = dict(
    handle="its-100rabh",
    role="Software Engineer",
    tagline="Designing reliable systems and the interfaces people touch.",
    pillars="BACKEND  ·  MOBILE  ·  INFRASTRUCTURE",
)

IDENTITY = [
    ("handle", "its-100rabh"),
    ("role", "Software Engineer"),
    ("focus", "Full-stack products · API design · Mobile"),
    ("principle", "Ship small. Measure. Refine."),
    ("currently", "Shipping production systems"),
]

# Familiarity: 1 exploring · 3 proficient · 5 daily driver
STACK = {
    "LANGUAGES": [("TypeScript", 4), ("JavaScript", 4), ("Python", 3), ("C++", 2), ("SQL", 3)],
    "FRONTEND": [("React", 4), ("Next.js", 3), ("React Native", 4), ("HTML / CSS", 4), ("Tailwind", 3)],
    "BACKEND": [("Node.js", 4), ("Express", 4), ("NestJS", 3), ("FastAPI", 3), ("REST APIs", 4)],
    "DATABASES": [("PostgreSQL", 4), ("MySQL", 3), ("MongoDB", 3), ("Redis", 3), ("Firebase", 3)],
    "AI / ML": [("TensorFlow", 2), ("OpenCV", 2), ("YOLO", 2), ("Pandas", 3), ("Prompt design", 3)],
    "CLOUD / DEVOPS": [("AWS", 3), ("Docker", 3), ("GitHub Actions", 3), ("Linux", 3), ("Cloudflare", 2)],
}
TOOLS = [
    ("Git", 4), ("GitHub", 4), ("Postman", 4),
    ("Swagger", 3), ("Jest", 3), ("Playwright", 2),
]

LINKS = [  # (file slug, LABEL, descriptor)
    ("email", "EMAIL", "saurabhmahapatra03@gmail.com"),
    ("linkedin", "LINKEDIN", "YOUR_LINKEDIN_URL"),
]

SECTIONS = [  # (file slug, number, TITLE, tag)
    ("identity", "01", "IDENTITY", "WHO"),
    ("stack", "02", "STACK", "CAPABILITY MAP"),
    ("activity", "03", "ACTIVITY", "GITHUB TELEMETRY"),
    ("contributions", "04", "CONTRIBUTIONS", "LAST 12 MONTHS"),
    ("connect", "05", "CONNECT", "CHANNELS"),
]


def write(name, content):
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / name).write_text(content, encoding="utf-8")
    print("wrote", ASSETS / name)


# ── Hero ───────────────────────────────────────────────────────────────────
def hero():
    W, H = 900, 340
    handle = CONFIG["handle"].upper()
    size = min(96, int((760 / len(handle) - 10) / 0.6))
    defs = f"""
<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
  <path d="M30 0H0V30" fill="none" stroke="{LINE}" stroke-width="1"/>
</pattern>
<radialGradient id="glow" cx="50%" cy="0%" r="80%">
  <stop offset="0" stop-color="{ACCENT}" stop-opacity=".17"/>
  <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="fade" x1="0" x2="0" y1="0" y2="1">
  <stop offset="0" stop-color="{BG}" stop-opacity="0"/>
  <stop offset="1" stop-color="{BG}" stop-opacity="1"/>
</linearGradient>
<linearGradient id="ink" x1="0" x2="0" y1="0" y2="1">
  <stop offset="0" stop-color="#ffffff"/>
  <stop offset="1" stop-color="#9fb4c4"/>
</linearGradient>
<linearGradient id="beam" x1="0" x2="1" y1="0" y2="0">
  <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{ACCENT}" stop-opacity=".6"/>
  <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
</linearGradient>"""
    css = """
.r{opacity:0;animation:rise .9s cubic-bezier(.2,.7,.2,1) forwards}
.f{opacity:0;animation:fade 1.4s ease forwards}
.b{animation:blink 2.4s ease-in-out infinite}
.scan{animation:scan 7s linear infinite}
@keyframes scan{0%{transform:translateY(-4px);opacity:0}8%{opacity:1}92%{opacity:1}100%{transform:translateY(344px);opacity:0}}
"""
    ticks = "".join(
        f"M{x},296 v{8 if (x - 40) % 100 == 0 else 4} " for x in range(40, 861, 20)
    )
    body = f"""
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)" opacity=".55"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<rect y="190" width="{W}" height="150" fill="url(#fade)"/>
{brackets(16, 16, W - 32, H - 32, s=18, opacity=.9)}
<text x="40" y="38" font-size="10" letter-spacing="4" fill="{DIM}">// DEVELOPER IDENTITY</text>
<circle class="b" cx="860" cy="34" r="3" fill="{ACCENT}"/>
<text x="848" y="38" font-size="10" letter-spacing="3" text-anchor="end" fill="{MUTED}">ONLINE</text>

<text class="f" x="{450 + 5 + 4}" y="{170 + 4}" text-anchor="middle" font-size="{size}" font-weight="800"
      letter-spacing="10" fill="none" stroke="{ACCENT}" stroke-width="1" opacity=".5"
      style="animation-delay:.25s">{esc(handle)}</text>
<text class="r" x="455" y="170" text-anchor="middle" font-size="{size}" font-weight="800"
      letter-spacing="10" fill="url(#ink)">{esc(handle)}</text>
<text class="r" x="456" y="216" text-anchor="middle" font-size="17" font-weight="600"
      letter-spacing="12" fill="{ACCENT}" style="animation-delay:.2s">{esc(CONFIG['role'].upper())}</text>
<text class="r" x="450" y="250" text-anchor="middle" font-size="13.5" fill="{MUTED}"
      style="animation-delay:.4s">{esc(CONFIG['tagline'])}</text>

<path d="M40,296 H860" stroke="{LINE_HI}"/>
<path d="{ticks}" stroke="{LINE_HI}" fill="none"/>
<path d="M40,296 H140" stroke="{ACCENT}" stroke-width="2"/>
<text class="r" x="452" y="324" text-anchor="middle" font-size="10" letter-spacing="4" fill="{DIM}"
      style="animation-delay:.6s">{esc(CONFIG['pillars'])}</text>
<rect class="scan" x="0" y="0" width="{W}" height="2" fill="url(#beam)"/>"""
    return svg(W, H, body, defs, css)


# ── Identity card ──────────────────────────────────────────────────────────
def identity():
    W, H = 900, 214
    cx, cy = 770, 118
    rows = []
    for i, (k, v) in enumerate(IDENTITY):
        y = 74 + i * 28
        rows.append(
            f'<text class="r" x="40" y="{y}" font-size="10.5" letter-spacing="3" fill="{DIM}" '
            f'style="animation-delay:{i * .08:.2f}s">{esc(k.upper())}</text>'
            f'<text class="r" x="170" y="{y}" font-size="14" fill="{FG if i else ACCENT}" '
            f'font-weight="{700 if i == 0 else 400}" style="animation-delay:{i * .08:.2f}s">{esc(v)}</text>'
        )
    css = ".r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) forwards}.b{animation:blink 2.4s ease-in-out infinite}"
    body = f"""
{panel(0, 0, W, H, "IDENTITY.SYS", "ID-01")}
{''.join(rows)}
<g>
  <circle cx="{cx}" cy="{cy}" r="74" fill="none" stroke="{LINE_HI}" stroke-dasharray="2 6">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="52" fill="none" stroke="{ACCENT_LOW}" stroke-width="1.5" stroke-dasharray="40 14 8 14">
    <animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="40s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{ACCENT_MID}" stroke-width="1" stroke-dasharray="3 5">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/>
  </circle>
  <path d="M{cx - 84},{cy} H{cx - 20} M{cx + 20},{cy} H{cx + 84} M{cx},{cy - 84} V{cy - 20} M{cx},{cy + 20} V{cy + 84}" stroke="{LINE_HI}"/>
  <circle class="b" cx="{cx}" cy="{cy}" r="4" fill="{ACCENT}"/>
</g>"""
    return svg(W, H, body, "", css)


# ── Section header / divider / footer ──────────────────────────────────────
def section(num, title, tag):
    W, H = 900, 46
    body = f"""
<text x="0" y="26" font-size="13" font-weight="800" fill="{ACCENT}">{num}</text>
<text x="30" y="26" font-size="13" fill="{DIM}">/</text>
<text x="48" y="26" font-size="13" font-weight="700" letter-spacing="6" fill="{FG}">{esc(title)}</text>
<text x="900" y="26" font-size="10" letter-spacing="3" text-anchor="end" fill="{DIM}">{esc(tag)}</text>
<path d="M0,38.5 H900" stroke="{LINE}"/>
<path d="M0,38.5 H48" stroke="{ACCENT}" stroke-width="2"/>
<path d="M899.5,34 V43" stroke="{LINE_HI}"/>"""
    return svg(W, H, body)


def divider():
    W, H = 900, 22
    defs = f"""<linearGradient id="d" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="{LINE_HI}" stop-opacity="0"/><stop offset=".5" stop-color="{LINE_HI}"/>
<stop offset="1" stop-color="{LINE_HI}" stop-opacity="0"/></linearGradient>"""
    body = f"""
<path d="M0,11 H900" stroke="url(#d)"/>
<path d="M426,11 H440 M460,11 H474" stroke="{ACCENT_MID}"/>
<rect x="446" y="7" width="8" height="8" transform="rotate(45 450 11)" fill="none" stroke="{ACCENT}"/>
<rect class="b" x="448.5" y="9.5" width="3" height="3" transform="rotate(45 450 11)" fill="{ACCENT}"/>"""
    return svg(W, H, body, defs, ".b{animation:blink 2.4s ease-in-out infinite}")


def footer():
    W, H = 900, 44
    year = datetime.date.today().year
    body = f"""
<path d="M0,8.5 H900" stroke="{LINE}"/>
<path d="M0,8.5 H48" stroke="{ACCENT}" stroke-width="2"/>
<text x="450" y="31" font-size="10" letter-spacing="4" text-anchor="middle" fill="{DIM}">// END OF FILE  ·  {year}</text>"""
    return svg(W, H, body)


# ── Stack ──────────────────────────────────────────────────────────────────
def stack():
    W = 900
    pw, gap, ph = 288, 18, 200
    css = ".s{opacity:0;animation:fade .5s ease forwards}"
    body = []

    for i, (name, items) in enumerate(STACK.items()):
        col, row = i % 3, i // 3
        x, y = col * (pw + gap), row * (ph + gap)
        body.append(panel(x, y, pw, ph, name, f"{len(items):02d}"))
        for j, (label, lvl) in enumerate(items):
            ry = y + 66 + j * 27
            body.append(
                f'<text x="{x + 18}" y="{ry}" font-size="12.5" fill="{FG}">{esc(label)}</text>'
            )
            body.append(segments(x + pw - 18 - SEG_W, ry - 8, lvl, delay=(i * 5 + j) * 0.04))

    # Full-width tools panel, items in 3 columns
    ty = 2 * (ph + gap)
    th = 124
    body.append(panel(0, ty, W, th, "DEVELOPER TOOLS", f"{len(TOOLS):02d}"))
    colw = 288
    for k, (label, lvl) in enumerate(TOOLS):
        c, r = k % 3, k // 3
        x = 18 + c * (colw + 18) - (0 if c == 0 else 0)
        ry = ty + 66 + r * 27
        body.append(f'<text x="{x}" y="{ry}" font-size="12.5" fill="{FG}">{esc(label)}</text>')
        body.append(segments(x + colw - 18 - SEG_W - 18, ry - 8, lvl, delay=(30 + k) * 0.04))

    # Legend
    ly = ty + th + 24
    legend = [(1, "EXPLORING", 0), (3, "PROFICIENT", 172), (5, "DAILY DRIVER", 352)]
    for lvl, text, lx in legend:
        for s in range(5):
            fill = RAMP5[s] if s < lvl else "#141c26"
            body.append(f'<rect x="{lx + s * 10}" y="{ly - 7}" width="8" height="5" fill="{fill}"/>')
        body.append(
            f'<text x="{lx + 58}" y="{ly - 1}" font-size="10" letter-spacing="2" fill="{DIM}">{text}</text>'
        )
    H = ly + 12
    return svg(W, H, "\n".join(body), "", css)


# ── Link pills ─────────────────────────────────────────────────────────────
def link_pill(label, sub):
    W, H = 200, 48
    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="{PANEL}" stroke="{LINE_HI}"/>
<rect x="0" y="0" width="3" height="{H}" fill="{ACCENT}"/>
<text x="20" y="21" font-size="12" font-weight="700" letter-spacing="3" fill="{FG}">{esc(label)}</text>
<text x="20" y="37" font-size="10.5" fill="{MUTED}">{esc(sub)}</text>
<path d="M{W - 32},{H - 17} L{W - 18},{H - 31} M{W - 30},{H - 31} H{W - 18} V{H - 19}"
      fill="none" stroke="{ACCENT}" stroke-width="1.5"/>"""
    return svg(W, H, body)


def main():
    write("hero.svg", hero())
    write("identity.svg", identity())
    write("divider.svg", divider())
    write("footer.svg", footer())
    write("stack.svg", stack())
    for slug, num, title, tag in SECTIONS:
        write(f"section-{slug}.svg", section(num, title, tag))
    for slug, label, sub in LINKS:
        write(f"link-{slug}.svg", link_pill(label, sub))


if __name__ == "__main__":
    main()
