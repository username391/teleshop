import os.path
import pathlib

from bot import send_message, ms
from models import Task

current_dir = pathlib.Path(__file__).parent.resolve()


if __name__ == '__main__':
    ready_tasks = Task.select().where(Task.ready == True, Task.sent == False)
    for task in ready_tasks:
        print(task.url)
        if task.ok:
            send_message(
                task.user,
                ms.REPORT_READY,
                # attachment=os.path.join(current_dir, task.result_file_dir))
                attachment=task.result_file_dir
            )
        else:
            send_message(task.user, ms.REPORT_FAILED)
        task.sent = True
        task.save()
