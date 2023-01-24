import typing
import telebot

from models import User, Tariff

ZERO_TARIFF, _ = Tariff.get_or_create(
    id=0,
    defaults={
        'name': 'Отсутствие тарифа',
        'by_date': False,
        'total': 0,
        'id': 0,
        'price': 0
    }
)


def get_refovod(msg: telebot.types.Message | telebot.types.CallbackQuery) -> User | None:
    """ Возвращает рефовода из бд, если его нет - None """
    if not isinstance(msg, telebot.types.Message):
        return
    ref_id = msg.text.split(' ')[-1].strip()
    if not ref_id.isdigit():
        return
    refovod = User.select().where(User.telegram_id == int(ref_id)).first()
    if not refovod:
        return
    # тут нужно дать бонус рефоводу
    # FIXME: тут должно быть что то другое
    # также именно тут наверное нужно проверять, достиг ли пользователь нужного
    # количества рефералов и давать бонус
    refovod.balance += 1
    refovod.save()
    return refovod


def get_user(func: typing.Callable):
    def wrapper_get_user(msg: telebot.types.Message | telebot.types.CallbackQuery):
        user = User.select().where(User.telegram_id == msg.from_user.id).first()

        if not user:
            refovod = get_refovod(msg)
            User.insert(
                telegram_id=msg.from_user.id,
                username=msg.from_user.username,
                tariff=ZERO_TARIFF,
                ref=refovod
            ).execute()
            user = User.select().where(User.telegram_id == msg.from_user.id).first()

        func(msg, user)
    return wrapper_get_user
