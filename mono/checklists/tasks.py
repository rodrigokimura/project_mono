"""Background tasks for Checklists app"""
from background_task import background

# pylint: disable=import-outside-toplevel, cyclic-import


@background(schedule=60)
def remind(task_id):
    """Call remind method"""
    from .models import Task as MonoTask

    task: MonoTask = MonoTask.objects.get(pk=task_id)
    task.remind()


@background(schedule=60)
def create_next_task(task_id):
    """Call create_next_task method"""
    from .models import Task as MonoTask

    task: MonoTask = MonoTask.objects.get(pk=task_id)
    task.create_next_task()
