"""
GitHub activity fetcher — utils/ingest/github_activity.py
Fetches commit cadence, contributor count, open PR count via GitHub REST API.
"""
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

log = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com"
_TIMEOUT    = 10


def fetch_github_activity(repo: str, weeks: int = 12, mock: bool = False) -> dict:
    """
    Fetch GitHub repo activity metrics.

    Args:
        repo:  "owner/repo" format (e.g. "metadaoproject/metadao")
        weeks: How many weeks of commit history to fetch
        mock:  If True, return hardcoded mock data

    Returns:
        {commits_per_week, total_commits, contributors, open_prs, last_push,
         stars, forks, is_active}
    """
    if mock or not os.getenv("GITHUB_TOKEN"):
        log.info(f"[GitHub] Mock mode | repo={repo}")
        return _mock_activity(repo)

    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
               "Accept": "application/vnd.github+json"}
    try:
        # Repo metadata
        r = requests.get(f"{_GITHUB_API}/repos/{repo}", headers=headers, timeout=_TIMEOUT)
        r.raise_for_status()
        meta = r.json()

        # Weekly commit activity (last 52 weeks)
        r2 = requests.get(f"{_GITHUB_API}/repos/{repo}/stats/commit_activity",
                          headers=headers, timeout=_TIMEOUT)
        weekly = r2.json() if r2.status_code == 200 else []
        recent_weeks = weekly[-weeks:] if weekly else []
        commits_per_week = [w.get("total", 0) for w in recent_weeks]
        total_commits = sum(commits_per_week)

        # Contributors
        r3 = requests.get(f"{_GITHUB_API}/repos/{repo}/contributors",
                          headers=headers, timeout=_TIMEOUT, params={"per_page": 10})
        contributors = len(r3.json()) if r3.status_code == 200 else 0

        # Open PRs
        r4 = requests.get(f"{_GITHUB_API}/repos/{repo}/pulls",
                          headers=headers, timeout=_TIMEOUT,
                          params={"state": "open", "per_page": 1})
        open_prs = int(r4.headers.get("X-Total-Count", len(r4.json()))) if r4.status_code == 200 else 0

        avg_weekly = total_commits / max(len(commits_per_week), 1)
        is_active  = avg_weekly >= 1.0

        result = {
            "repo":           repo,
            "commits_per_week": commits_per_week,
            "avg_commits_per_week": round(avg_weekly, 1),
            "total_commits":  total_commits,
            "contributors":   contributors,
            "open_prs":       open_prs,
            "stars":          meta.get("stargazers_count", 0),
            "forks":          meta.get("forks_count", 0),
            "last_push":      meta.get("pushed_at", ""),
            "is_active":      is_active,
        }
        log.info(f"[GitHub] Fetched | repo={repo} avg_commits={avg_weekly:.1f}/wk "
                 f"contributors={contributors}")
        return result

    except Exception as exc:
        log.warning(f"[GitHub] Fetch failed: {exc} — returning mock")
        return _mock_activity(repo)


def _mock_activity(repo: str) -> dict:
    return {
        "repo":                 repo,
        "commits_per_week":     [8, 12, 7, 15, 11, 9, 13, 10, 6, 14, 11, 8],
        "avg_commits_per_week": 10.3,
        "total_commits":        124,
        "contributors":         7,
        "open_prs":             4,
        "stars":                1240,
        "forks":                89,
        "last_push":            datetime.now(timezone.utc).isoformat(),
        "is_active":            True,
    }
