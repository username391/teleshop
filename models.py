from config import CONFIG
from peewee import (
    PostgresqlDatabase,
    Model,
    IntegerField,
    BooleanField,
    CharField,
    FloatField,
    DateTimeField,
    PrimaryKeyField,
    ForeignKeyField,
)
from flask_login import UserMixin

db = PostgresqlDatabase(**CONFIG['database'])


class BaseModel(Model):
    class Meta:
        database = db


class Admin(UserMixin, BaseModel):
    email = CharField(unique=True)
    password_hash = CharField()

    @property
    def is_active(self) -> bool:
        return True


class Tariff(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    by_date = BooleanField(default=False)
    total = IntegerField()
    price = IntegerField()


class User(BaseModel):
    telegram_id = IntegerField(unique=True)
    username = CharField(default='', null=True)
    balance = FloatField(default=0.0)
    has_trial = BooleanField(default=True)
    ref = ForeignKeyField('self', related_name='ref', null=True)
    has_key = BooleanField(default=False)
    tariff = ForeignKeyField(Tariff, related_name='user_tariff')
    reports_left = IntegerField(default=0)
    expire_at = DateTimeField(default=None, null=True)


class Task(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='user_task')
    url = CharField()
    result_file_dir = CharField(default='')
    ok = BooleanField(default=False)
    comment = CharField(default='')
    ready = BooleanField(default=False)


class Setting(BaseModel):
    key = CharField(unique=True)
    value = CharField(default='')


if __name__ == '__main__':
    with db:
        tables = [Admin, User, Task]
        # tables = [Tariff]
        tables = [Setting]
        db.drop_tables(tables)
        db.create_tables(tables)

        # create settings
        # YOOMONEY_TOKEN, RECIEVER
        Setting.insert(key='yoomoney_token').execute()
        Setting.insert(key='yoomoney_reciever').execute()
        Setting.insert(key='yoomoney_success_url').execute()
        Setting.insert(key='server_domain', value='http://localhost:5000').execute()
