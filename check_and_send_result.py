from bot import send_message, ms
from models import Task


if __name__ == '__main__':
    ready_tasks = Task.select().where(Task.ready is True and Task.sent is False)
    for task in ready_tasks:
        if task.ok:
            send_message(task.user, ms.REPORT_READY, attachment=task.result_file_dir)
        else:
            send_message(task.user, ms.REPORT_FAILED)
    



class Task(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='user_task')
    url = CharField()
    result_file_dir = CharField(default='')
    ok = BooleanField(default=False)
    comment = CharField(default='')
    ready = BooleanField(default=False)