#!/usr/bin/env python3
"""Generate assets/stats.svg — an FPV-OSD-styled GitHub stats card.

Pulls stars/repos/followers/languages from the GitHub REST API and renders
a card that matches assets/banner.svg (same palette, mono font, OSD outline).
Runs in GitHub Actions with GITHUB_TOKEN; locally with `gh auth token`.
"""
import json
import os
import subprocess
import urllib.request

USER = "LongXL6"
API = "https://api.github.com"

BG = "#0d131c"
BORDER = "#223041"
FG = "#e9f1f4"
MUTED = "#9fb0bc"
DIM = "#c9d5de"
TEAL = "#53d7c8"
AMBER = "#e8b84b"
OUTLINE = "#070a0e"
LANG_COLORS = [TEAL, AMBER, FG, MUTED, "#246a5f", "#33475c"]


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def get(path: str):
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {token()}",
        "Accept": "application/vnd.github+json",
        "User-Agent": USER,
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    user = get(f"/users/{USER}")
    repos = get(f"/users/{USER}/repos?per_page=100")
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)

    lang_bytes: dict[str, int] = {}
    for r in own:
        for lang, n in get(f"/repos/{USER}/{r['name']}/languages").items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + n
    total = sum(lang_bytes.values()) or 1
    top = sorted(lang_bytes.items(), key=lambda kv: -kv[1])[:5]
    rest = total - sum(n for _, n in top)
    if rest > 0:
        top.append(("OTHER", rest))

    metrics = [
        ("STARS", stars),
        ("REPOS", user["public_repos"]),
        ("FOLLOWERS", user["followers"]),
        ("LANGS", len(lang_bytes)),
    ]

    o = (f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
         f'stroke="{OUTLINE}" paint-order="stroke" stroke-linejoin="round"')

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="190" viewBox="0 0 900 190" '
        f'role="img" aria-label="GitHub stats for {USER}">',
        f'<rect width="900" height="190" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="899" height="189" fill="none" stroke="{BORDER}"/>',
        f'<text x="34" y="40" font-size="12" letter-spacing="3" fill="{MUTED}" stroke-width="2.5" {o}>GITHUB TELEMETRY</text>',
        f'<text x="866" y="40" text-anchor="end" font-size="12" letter-spacing="1.5" fill="{TEAL}" stroke-width="2.5" {o}>@{USER}</text>',
    ]

    for i, (label, value) in enumerate(metrics):
        cx = 34 + i * 210
        parts += [
            f'<text x="{cx}" y="92" font-size="30" font-weight="700" letter-spacing="2" fill="{FG}" stroke-width="5" {o}>{value}</text>',
            f'<text x="{cx}" y="114" font-size="11" letter-spacing="2.5" fill="{DIM}" stroke-width="2" {o}>{label}</text>',
        ]

    x = 34.0
    bar_w = 832.0
    for i, (lang, n) in enumerate(top):
        w = bar_w * n / total
        color = LANG_COLORS[i % len(LANG_COLORS)]
        parts.append(f'<rect x="{x:.1f}" y="136" width="{max(w - 3, 1):.1f}" height="8" fill="{color}"/>')
        pct = 100 * n / total
        if w > 52:
            parts.append(
                f'<text x="{x:.1f}" y="168" font-size="10.5" letter-spacing="1" fill="{MUTED}" stroke-width="2" {o}>'
                f'{esc(lang.upper())} {pct:.0f}%</text>')
        x += w

    parts.append("</svg>")

    os.makedirs("assets", exist_ok=True)
    with open("assets/stats.svg", "w") as f:
        f.write("\n".join(parts) + "\n")
    print(f"stars={stars} repos={user['public_repos']} followers={user['followers']} langs={list(lang_bytes)}")


if __name__ == "__main__":
    main()
