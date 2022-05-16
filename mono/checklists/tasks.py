from background_task import background


@background(schedule=60)
def remind(task_id):
    from .models import Task
    task = Task.objects.get(pk=task_id)
    task.remind()
