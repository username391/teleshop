import time
import random

from yoomoney import Quickpay, Client
from config import YOOMONEY_TOKEN, RECIEVER
from models import User, Tariff, Setting


def get_reciever() -> str:
    reciever = Setting.select().where(Setting.key == 'yoomoney_reciever')
    return reciever.first().value_str


def get_success_url() -> str:
    domain = Setting.select().where(Setting.key == 'server_domain')
    domain = domain.first().value_str

    url = Setting.select().where(Setting.key == 'yoomoney_success_url')
    return domain + url.first().value_str


def create_payment_link(amount: int, label: str, title: str) -> str:
    return Quickpay(
        receiver=get_reciever(),
        quickpay_form='shop',
        targets=f'Оплата подписки - {title}',
        paymentType='SB',
        sum=amount,
        label=label,
        successURL=get_success_url()
    ).redirected_url


def new_payment(user: User, tariff: Tariff) -> str:
    label = f'{user.telegram_id}-{tariff.id}-{random.randint(9999, 99999999)}'
    # label = f'{int(time.time())}-{random.randint(9999, 99999999)}'
    payment_url = create_payment_link(tariff.price, label, tariff.name)
    # Payment.insert(user=user, tariff=tariff, label=label).execute()
    return payment_url


def check_payment(label: str, amount: int) -> bool:
    return True
    client = Client(YOOMONEY_TOKEN)
    history = client.operation_history(label=label)

    for operation in history.operations:
        if operation.status == 'success' and operation.amount == amount:
            return True
    return False
