"""Refresh the live parts of the profile from GitHub: the development board and the status panel.

Run by .github/workflows/refresh-status.yml (daily, on demand, and when these scripts change).
It touches only assets/board.svg and assets/status.svg, and only when something real changed.

What is read live
  - Opspilot's roadmap table (its README) -> "Week N of 7", the version, and what is next
  - the recorded-demo URL of Agent Blackbox -> is it still up?
  - the last push date of every featured repo -> the "Latest" row

What stays hand-written: the project list, tags and descriptions (scripts/generate_assets.py).

Usage:  python scripts/refresh_status.py [--dry-run]
"""
import datetime
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_assets as g  # noqa: E402

OWNER = "Shubham261299"
DEMO_URL = "https://shubham261299.github.io/agent-blackbox/"
REPOS = {
    "01": "agentic-case-routing-orchestrator",
    "02": "enterprise-mcp-layer",
    "03": "agentic-tool-orchestrator",
    "04": "opspilot",
    "05": "self-healing-invoice-automation",
    "06": "daybook",
    "07": "sop-assistant",
    "08": "decision-intelligence-lab",
    "09": "agent-blackbox",
    "10": "the-last-witness",
}
ASSETS = HERE.parent / "assets"


def fetch(url, accept="application/vnd.github+json", method="GET", tries=3):
    headers = {"Accept": accept, "User-Agent": "profile-status-refresh"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429:
                return e.code, ""
            last = e
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"could not reach {url}: {last}")


def parse_roadmap(readme):
    """Rows like '| 6 ✅ | v0.4 | Policy search ... |' -> (done_count, total, last_done_version, next_desc, next_version)."""
    rows = re.findall(r"^\|\s*(\d+)\s*(✅)?\s*\|\s*(v[\w.]+)\s*\|\s*([^|]+?)\s*\|", readme, re.M)
    if not rows:
        return None
    done = [r for r in rows if r[1]]
    pending = [r for r in rows if not r[1]]
    last_version = done[-1][2] if done else None
    nxt = pending[0] if pending else None
    return len(done), len(rows), last_version, (nxt[3] if nxt else None), (nxt[2] if nxt else None)


def pushed_at(repo):
    status, body = fetch(f"https://api.github.com/repos/{OWNER}/{repo}")
    if status != 200:
        return None
    m = re.search(r'"pushed_at"\s*:\s*"([^"]+)"', body)
    return datetime.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")) if m else None


def today():
    d = datetime.datetime.now(datetime.timezone.utc)
    return f"{d.day} {d:%b %Y}"


def main(dry_run):
    rows = [list(r) for r in g.BOARD]
    status_kw = {"projects": len(rows)}

    # Opspilot roadmap -> board row 04 and the "currently building" panel
    code, readme = fetch(f"https://api.github.com/repos/{OWNER}/opspilot/readme", accept="application/vnd.github.raw")
    road = parse_roadmap(readme) if code == 200 else None
    if road and road[0] and road[2]:
        week, total, version, nxt, nxt_v = road
        status_kw.update(week=week, total=total, version=version)
        if nxt:
            status_kw["next_text"] = f"{nxt.lower()} ({nxt_v})"
            stage = f"Week {week} of {total} done ({version}) · {nxt.lower()} next"
        else:
            status_kw["next_text"] = "all weeks done"
            stage = f"All {total} weeks done ({version})"
        next(r for r in rows if r[0] == "04")[3] = stage
    else:
        print("note: could not read Opspilot's roadmap; keeping the written values")

    # Is the Agent Blackbox recorded demo still up?
    demo_ok = fetch(DEMO_URL, method="HEAD")[0] == 200
    stage = "Recorded demo live · Docker stack · MIT" if demo_ok else "Docker stack · MIT · recorded demo offline"
    next(r for r in rows if r[0] == "09")[3] = stage

    # Latest = most recently pushed featured repo
    stamps = {}
    for num, repo in REPOS.items():
        when = pushed_at(repo)
        if when:
            stamps[num] = when
    if stamps:
        num = max(stamps, key=stamps.get)
        name = next(r for r in rows if r[0] == num)[1]
        d = stamps[num]
        status_kw["latest"] = f"{name} · updated {d.day} {d:%b}"
    else:
        print("note: no push dates found; keeping the written 'Latest' value")

    rows = [tuple(r) for r in rows]
    changed = []

    # board: keep the existing date unless something else changed
    path = ASSETS / "board.svg"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    m = re.search(r"Status as of ([^<]+)<", old)
    new = g.board_svg(rows, m.group(1) if m else None)
    if new != old:
        new = g.board_svg(rows, today())
        changed.append((path, new))

    path = ASSETS / "status.svg"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    new = g.status_svg(**status_kw)
    if new != old:
        changed.append((path, new))

    if not changed:
        print("no changes")
        return 0
    for path, content in changed:
        print(("would update " if dry_run else "updated ") + path.name)
        if not dry_run:
            path.write_text(content, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main("--dry-run" in sys.argv))
