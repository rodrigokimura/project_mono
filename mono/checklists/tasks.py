from background_task import background

from .models import Task


@background(schedule=60)
def remind(task_id):
    task = Task.objects.get(pk=task_id)
    task.remind()
