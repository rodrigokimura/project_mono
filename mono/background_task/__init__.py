"""Set alias for main decorator"""


def background(*arg, **kwargs):
    from background_task.tasks import tasks

    return tasks.background(*arg, **kwargs)
