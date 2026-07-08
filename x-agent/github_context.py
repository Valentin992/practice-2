import os
from datetime import datetime, timedelta, timezone


def get_recent_commits(repos: list[str], days: int = 7) -> str:
    """Return a plain-text summary of commits from the last `days` days."""
    try:
        from github import Github
    except ImportError:
        return ""

    token = os.getenv("GITHUB_TOKEN")
    g = Github(token) if token else Github()

    since = datetime.now(timezone.utc) - timedelta(days=days)
    lines = []

    for repo_name in repos:
        try:
            repo = g.get_repo(repo_name)
            for commit in repo.get_commits(since=since)[:10]:
                msg = commit.commit.message.split("\n")[0]
                date_str = commit.commit.author.date.strftime("%b %d")
                lines.append(f"[{repo_name}] {date_str}: {msg}")
        except Exception:
            continue

    return "\n".join(lines)
