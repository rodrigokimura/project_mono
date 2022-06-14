from background_task import background


@background(schedule=60)
def remind(task_id):
    from .models import Task
    task: Task = Task.objects.get(pk=task_id)
    task.remind()


@background(schedule=60)
def create_next_task(task_id):
    from .models import Task
    task: Task = Task.objects.get(pk=task_id)
    task.create_next_task()
