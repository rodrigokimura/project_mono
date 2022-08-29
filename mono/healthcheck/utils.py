"""Utility functions for healthcheck."""
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Iterable, List

from django.conf import settings
from git import Commit, Repo


def _int_to_date(i: int):
    """Convert integer to date."""
    return datetime.fromtimestamp(time.mktime(time.localtime(i))).date()


def format_to_heatmap(
    commits: List[Any],
) -> Dict[str, List[Dict[str, int]]]:
    """Format data to heatmap."""
    temp_date = datetime.today() - timedelta(weeks=52)
    initial_date = datetime.fromisocalendar(
        year=temp_date.isocalendar()[0],
        week=temp_date.isocalendar()[1],
        day=1,
    ) - timedelta(days=1)
    days = (datetime.today() - initial_date).days

    context_data = {f"data_{i}": {} for i in range(7)}
    for i in range(days + 1):
        date = (initial_date + timedelta(days=i)).date()
        context_data[f"data_{i % 7}"][date.isoformat()] = 0

    for commit in commits:
        commit_date = _int_to_date(commit.committed_date)
        if initial_date.date() <= commit_date <= datetime.today().date():
            i = (commit_date - initial_date.date()).days
            context_data[f"data_{i % 7}"][commit_date.isoformat()] += 1
    return context_data


def get_commits_context():
    """Get commits context."""
    commits = Repo(settings.BASE_DIR.parent).iter_commits(
        "--all",
        since="365.days.ago",
    )
    context_data = format_to_heatmap(commits)
    return context_data


def get_commits_by_date(date: datetime.date):
    """Get commits context."""
    repo = Repo(settings.BASE_DIR.parent)
    commits: Iterable[Commit] = repo.iter_commits("--all")
    return map(
        lambda commit: {
            "hexsha": commit.hexsha,
            "author": commit.author.name,
            "date": commit.authored_date,
            "message": commit.message,
        },
        filter(
            lambda commit: _int_to_date(commit.committed_date) == date, commits
        ),
    )
