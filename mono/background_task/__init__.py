"""Set alias for main decorator"""


def background(*arg, **kwargs):
    """Set alias for main decorator"""
    # pylint: disable=import-outside-toplevel
    from background_task.tasks import all_tasks

    return all_tasks.background(*arg, **kwargs)
