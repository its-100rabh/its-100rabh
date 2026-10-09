#!/usr/bin/env python3
"""Live GitHub telemetry -> SVG, in the same design system as the static assets.

Produces three files in assets/generated/:
  stats.svg          headline counters + streaks
  languages.svg      top languages by bytes across your owned, non-fork repos
  contributions.svg  12-month contribution matrix

Usage:
  GH_TOKEN=... GH_USER=yourname python scripts/generate_stats.py
  python scripts/generate_stats.py --demo      # synthetic data, no network
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from design import *  # noqa: F401,F403

OUT = Path(__file__).resolve().parent.parent / "assets" / "generated"
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

REPO_QUERY = """
query($login:String!, $cursor:String!){
  user(login:$login){
    repositories(ownerAffiliations:OWNER, isFork:false, first:100, after:$cursor, orderBy:{field:PUSHED_AT, direction:DESC}){
      pageInfo { hasNextPage endCursor }
      nodes{
        stargazerCount
        languages(first:100, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } }
      }
    }
  }
}
"""

QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!){
  user(login:$login){
    followers{ totalCount }
    repositories(ownerAffiliations:OWNER, isFork:false, first:100, orderBy:{field:PUSHED_AT, direction:DESC}){
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes{
        stargazerCount
        languages(first:100, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } }
      }
    }
    contributionsCollection(from: $from, to: $to){
      startedAt
      endedAt
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      totalRepositoriesWithContributedPullRequests
      totalRepositoriesWithContributedPullRequestReviews
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount contributionLevel } }
      }
    }
  }
}
"""


# ── Data ───────────────────────────────────────────────────────────────────
def fetch(login, token):
    now = dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(days=365)
    variables = {
        "login": login,
        "from": start.isoformat().replace("+00:00", "Z"),
        "to": now.isoformat().replace("+00:00", "Z")
    }
    def _post(q, v):
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": q, "variables": v}).encode(),
            headers={
                "Authorization": f"bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "profile-readme-generator",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)

    payload = _post(QUERY, variables)
        
    print("--- GITHUB API RAW RESPONSE LOG ---")
    print(json.dumps(payload, indent=2))
    print("-----------------------------------")
    
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise SystemExit("GitHub API error: " + json.dumps(payload.get("errors", payload))[:600])
        
    u = payload["data"]["user"]
    
    # Fetch remaining repository pages if total exceeds 100
    page_info = u["repositories"]["pageInfo"]
    while page_info.get("hasNextPage"):
        next_v = {"login": login, "cursor": page_info["endCursor"]}
        next_payload = _post(REPO_QUERY, next_v)
        if next_payload.get("errors"):
            print("Warning: Error fetching next page of repositories:", next_payload.get("errors"))
            break
        next_repos = next_payload["data"]["user"]["repositories"]
        u["repositories"]["nodes"].extend(next_repos["nodes"])
        page_info = next_repos["pageInfo"]
        
    cc = u["contributionsCollection"]
    
    print("\n--- TELEMETRY SUMMARY ---")
    print(f"startedAt: {cc.get('startedAt')}")
    print(f"endedAt: {cc.get('endedAt')}")
    print(f"totalContributions: {cc['contributionCalendar']['totalContributions']}")
    print(f"totalCommitContributions: {cc['totalCommitContributions']}")
    print(f"totalPullRequestContributions: {cc['totalPullRequestContributions']}")
    print(f"totalPullRequestReviewContributions: {cc['totalPullRequestReviewContributions']}")
    print(f"totalIssueContributions: {cc['totalIssueContributions']}")
    print(f"followers: {u['followers']['totalCount']}")
    actual_fetched_repos = len(u['repositories']['nodes'])
    total_matching_repos = u['repositories']['totalCount']
    print(f"repository count (fetched via pagination / total matching filter): {actual_fetched_repos} / {total_matching_repos}")
    print("Filter used: ownerAffiliations:OWNER, isFork:false")
    print("-------------------------\n")
    
    # Force the returned 'totalCount' to match the actual dataset aggregated
    u['repositories']['totalCount'] = actual_fetched_repos
    
    return u


def normalize(u):
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = [
        [(d["date"], d["contributionCount"], LEVELS.get(d["contributionLevel"], 0)) for d in w["contributionDays"]]
        for w in cal["weeks"]
    ]
    nodes = u["repositories"]["nodes"]
    langs = {}
    for n in nodes:
        for e in n["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return dict(
        weeks=weeks,
        total=cal["totalContributions"],
        commits=cc["totalCommitContributions"],
        prs=cc["totalPullRequestContributions"],
        reviews=cc["totalPullRequestReviewContributions"],
        issues=cc["totalIssueContributions"],
        repos_with_commits=cc.get("totalRepositoriesWithContributedCommits", 0),
        repos_with_prs=cc.get("totalRepositoriesWithContributedPullRequests", 0),
        repos_with_reviews=cc.get("totalRepositoriesWithContributedPullRequestReviews", 0),
        stars=sum(n["stargazerCount"] for n in nodes),
        followers=u["followers"]["totalCount"],
        repos=u["repositories"]["totalCount"],
        langs=langs,
    )


def demo():
    today = dt.date.today()
    start = today - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    weeks, day, week = [], start, []
    while day <= today:
        week.append((day.isoformat(), 0, 0))
        if len(week) == 7:
            weeks.append(week)
            week = []
        day += dt.timedelta(days=1)
    if week:
        weeks.append(week)
    return dict(
        weeks=weeks, total="—", commits="—", prs="—", reviews="—", issues="—",
        stars="—", followers="—", repos="—",
        langs={},
    )


def streaks(weeks):
    days = [c for w in weeks for _, c, _ in w]
    longest = run = 0
    for c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    cur, i = 0, len(days) - 1
    if i >= 0 and days[i] == 0:  # today may simply not have happened yet
        i -= 1
    while i >= 0 and days[i] > 0:
        cur += 1
        i -= 1
    return cur, longest


# ── Renderers ──────────────────────────────────────────────────────────────
def render_stats(d):
    W, H = 440, 256
    cur, longest = streaks(d["weeks"])
    metrics = [
        ("CONTRIBUTIONS · 1Y", d["total"]), ("COMMITS", d["commits"]),
        ("PULL REQUESTS", d["prs"]), ("CODE REVIEWS", d["reviews"]),
        ("STARS EARNED", d["stars"]), ("FOLLOWERS", d["followers"]),
    ]
    out = [panel(0, 0, W, H, "TELEMETRY", "LIVE")]
    for i, (label, val) in enumerate(metrics):
        col, row = i % 2, i // 2
        x, y = 18 + col * 206, 80 + row * 52
        val_str = f"{val:,}" if isinstance(val, int) else str(val)
        out.append(
            f'<text class="r" x="{x}" y="{y}" font-size="26" font-weight="800" fill="{FG}" '
            f'style="animation-delay:{i * .07:.2f}s">{val_str}</text>'
            f'<text class="r" x="{x}" y="{y + 17}" font-size="9.5" letter-spacing="2" fill="{DIM}" '
            f'style="animation-delay:{i * .07:.2f}s">{label}</text>'
        )
    out.append(f'<path d="M18,214.5 H{W - 18}" stroke="{LINE}"/>')
    cur_str = f"{cur}D" if isinstance(d["total"], int) else "—"
    longest_str = f"{longest}D" if isinstance(d["total"], int) else "—"
    out.append(
        f'<text x="18" y="238" font-size="10" letter-spacing="2" fill="{MUTED}">CURRENT STREAK</text>'
        f'<text x="146" y="238" font-size="13" font-weight="800" fill="{ACCENT}">{cur_str}</text>'
        f'<text x="224" y="238" font-size="10" letter-spacing="2" fill="{MUTED}">LONGEST</text>'
        f'<text x="296" y="238" font-size="13" font-weight="800" fill="{ACCENT}">{longest_str}</text>'
    )
    css = ".r{opacity:0;animation:rise .7s cubic-bezier(.2,.7,.2,1) forwards}"
    return svg(W, H, "\n".join(out), "", css)


def render_languages(d):
    W, H = 440, 256
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in langs) or 1
    top = langs[:6]
    colors = ["#7df9ff", "#4fd0dc", "#2fb4c2", "#188a97", "#157582", "#0f4b55"]
    out = [panel(0, 0, W, H, "LANGUAGES", "BY BYTES")]
    bw = W - 36
    for i, (name, size) in enumerate(top):
        y = 66 + i * 30
        pct = size / total * 100
        out.append(
            f'<text x="18" y="{y}" font-size="12" fill="{FG}">{esc(name)}</text>'
            f'<text x="{W - 18}" y="{y}" font-size="11" text-anchor="end" fill="{MUTED}">{pct:.1f}%</text>'
            f'<rect x="18" y="{y + 7}" width="{bw}" height="4" fill="#111823"/>'
            f'<rect class="g" x="18" y="{y + 7}" width="{max(2, bw * pct / 100):.1f}" height="4" '
            f'fill="{colors[i]}" style="animation-delay:{i * .1:.1f}s"/>'
        )
    if not top:
        out.append(f'<text x="18" y="80" font-size="12" fill="{DIM}">No language data available yet</text>')
    
    repos_str = f'{d["repos"]} ' if isinstance(d["repos"], int) else ""
    out.append(
        f'<text x="18" y="244" font-size="9.5" letter-spacing="2" fill="{DIM}">'
        f'{repos_str}OWNED REPOS · FORKS EXCLUDED</text>' if d["repos"] != "—" else
        f'<text x="18" y="244" font-size="9.5" letter-spacing="2" fill="{DIM}">DATA PENDING · FORKS EXCLUDED</text>'
    )
    css = ".g{transform-box:fill-box;transform-origin:left;animation:grow 1s cubic-bezier(.2,.7,.2,1) both}@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    return svg(W, H, "\n".join(out), "", css)


def render_matrix(d):
    W = 900
    weeks = d["weeks"]
    n = len(weeks)
    left, right = 46, 20
    pitch = (W - left - right) / n
    cell = pitch - 3
    top = 66
    H = 216
    total_str = f'{d["total"]:,}' if isinstance(d["total"], int) else str(d["total"])
    out = [panel(0, 0, W, H, "CONTRIBUTION MATRIX", f'{total_str} IN THE LAST 12 MONTHS')]

    # month labels
    marks, last_m = [], None
    for wi, w in enumerate(weeks):
        first = dt.date.fromisoformat(w[0][0])
        if first.month != last_m:
            marks.append((wi, first.strftime("%b").upper()))
            last_m = first.month
    # Drop a label when the next month starts within 3 weeks (avoids "SEPOCT" collisions),
    # and drop a trailing label with no room to render.
    keep = [m for i, m in enumerate(marks) if i == len(marks) - 1 or marks[i + 1][0] - m[0] >= 3]
    keep = [m for m in keep if m[0] <= n - 3]
    for wi, label in keep:
        out.append(f'<text x="{left + wi * pitch:.1f}" y="{top - 8}" font-size="9" letter-spacing="1.5" fill="{DIM}">{label}</text>')
    # weekday labels
    for di, name in ((1, "MON"), (3, "WED"), (5, "FRI")):
        out.append(f'<text x="18" y="{top + di * pitch + cell - 2:.1f}" font-size="8.5" letter-spacing="1" fill="{DIM}">{name}</text>')
    # cells
    for wi, w in enumerate(weeks):
        cells = []
        for di, (date, count, lvl) in enumerate(w):
            cells.append(
                f'<rect x="{left + wi * pitch:.1f}" y="{top + di * pitch:.1f}" width="{cell:.1f}" '
                f'height="{cell:.1f}" fill="{HEAT[lvl]}"><title>{count} on {date}</title></rect>'
            )
        out.append(f'<g class="c" style="animation-delay:{wi * 0.018:.2f}s">{"".join(cells)}</g>')
    # legend
    ly = top + 7 * pitch + 22
    lx = W - 18 - 5 * 14 - 34
    out.append(f'<text x="{lx - 8}" y="{ly + 8}" font-size="9" letter-spacing="2" text-anchor="end" fill="{DIM}">LESS</text>')
    for i in range(5):
        out.append(f'<rect x="{lx + i * 14}" y="{ly}" width="10" height="10" fill="{HEAT[i]}"/>')
    out.append(f'<text x="{lx + 5 * 14 + 4}" y="{ly + 8}" font-size="9" letter-spacing="2" fill="{DIM}">MORE</text>')
    css = ".c{opacity:0;animation:fade .6s ease forwards}"
    return svg(W, H, "\n".join(out), "", css)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if "--demo" in sys.argv:
        data = demo()
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        login = os.environ.get("GH_USER")
        if not token or not login:
            raise SystemExit("Set GH_TOKEN and GH_USER (or pass --demo).")
        data = normalize(fetch(login, token))
    (OUT / "stats.svg").write_text(render_stats(data), encoding="utf-8")
    (OUT / "languages.svg").write_text(render_languages(data), encoding="utf-8")
    (OUT / "contributions.svg").write_text(render_matrix(data), encoding="utf-8")
    print("wrote 3 files to", OUT)


if __name__ == "__main__":
    main()
