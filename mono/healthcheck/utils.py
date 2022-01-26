"""Utility functions for healthcheck."""
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from django.conf import settings
from git import Repo


def _int_to_date(i: int):
    """Convert integer to date."""
    return datetime.fromtimestamp(
        time.mktime(
            time.localtime(i)
        )
    ).date()


def format_to_heatmap(
    collection: List[Any],
    get_data_by_date: Callable[[List[Any], datetime.date], int]
) -> Dict[str, List[Dict[str, int]]]:
    """Format data to heatmap."""
    temp_date = datetime.today() - timedelta(weeks=52)
    initial_date = datetime.fromisocalendar(
        year=temp_date.isocalendar()[0],
        week=temp_date.isocalendar()[1],
        day=1,
    ) - timedelta(days=1)
    days = (datetime.today() - initial_date).days

    context_data = {
        f'data_{i}': []
        for i in range(7)
    }
    for i in range(days + 1):
        date = (initial_date + timedelta(days=i)).date()
        data = get_data_by_date(collection, date)
        context_data[f'data_{i % 7}'].append(
            {'d': date, 'c': data}
        )
    return context_data


def get_commits_context():
    """Get commits context."""
    repo = Repo(settings.BASE_DIR.parent)
    commits = repo.iter_commits(
        '--all',
        since='365.days.ago',
    )
    commits = list(map(
        lambda commit: {
            'hexsha': commit.hexsha,
            'dt': _int_to_date(commit.committed_date),
        },
        commits
    ))

    def _get_commits_by_date(commits, date):
        return len(list(filter(lambda commit: commit['dt'] == date, commits)))

    context_data = format_to_heatmap(
        commits,
        _get_commits_by_date
    )
    return context_data


def get_commits_by_date(date: datetime.date):
    """Get commits context."""
    repo = Repo(settings.BASE_DIR.parent)
    commits = repo.iter_commits('--all')
    return list(filter(
        lambda commit: _int_to_date(commit.committed_date) == date,
        commits
    ))
