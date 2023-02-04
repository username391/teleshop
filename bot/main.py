import typing
import telebot

from datetime import datetime as dt
from datetime import timedelta
# import sys; sys.path.append('..')

from . import messages as ms

from models import User, Tariff, Task
from .decorators import get_user
from config import CONFIG

from payment import new_payment, check_payment

bot = telebot.TeleBot(CONFIG['bot']['token'], parse_mode='html')

BOT_URL = ''

# FIXES:
# 1) стоит изменить провеку has_key на проверку id текущего тарифа

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


def on_start() -> None:
    global BOT_URL
    me = bot.get_me()

    BOT_URL = f'https://t.me/{me.username}'
    print('Бот запущен.\n')
    print(f'Username: @{me.username}')
    print(BOT_URL)
    print(f'Название: {me.first_name}\n')


def apply_tariff(user: User, tariff: Tariff) -> None:
    """ Применяет заданный тариф к заданному пользователю """
    user.tariff = tariff
    user.has_key = True
    if tariff.by_date:
        user.expire_at = dt.now() + timedelta(days=tariff.total)
    else:
        user.reports_left += tariff.total
    user.save()


def apply_tariff_if_correct(label: str, amount: float) -> None:
    """ Получает на вход метку платежа и его сумму. Если все верно - применяет тариф """
    print(label)
    try:
        uid, tid, _ = label.split('-')
        uid, tid = int(uid), int(tid)
    except ValueError:
        print('value error')
        return
    user = User.select().where(User.telegram_id == uid).first()
    if not user:
        print('no user')
        return
    tariff = Tariff.select().where(Tariff.id == tid).first()
    if not tariff:
        print('no such tariff')
        return
    if tariff.price <= amount:
        apply_tariff(user, tariff)
        send_message(user, ms.PAYMENT_SUCCESS)
    else:
        print('пользователь заплатил не ту цену')


def end_tariff(user: User) -> None:
    """ Удаляем закончившийся тариф """
    user.tariff = ZERO_TARIFF
    user.expire_at = None
    user.reports_left = 0
    user.save()


def send_message(
    user: User,
    text: str,
    kb: telebot.types.ReplyKeyboardMarkup | telebot.types.InlineKeyboardMarkup | None = None,
    callback: typing.Callable | None = None,
    attachment: str | None = None,
    parse_mode: str = 'markdown'
) -> None:
    """ Отправляет пользователю сообщение и регистрирует callback """
    uid = user.telegram_id
    callback = callback if callback else handle_keyboard
    if not attachment:
        bot.send_message(uid, text, reply_markup=kb, parse_mode=parse_mode)
    else:
        with open(attachment, 'rb') as f:
            # bot.send_video(uid, f, caption=text, reply_markup=kb)
            bot.send_animation(uid, f, caption=text, reply_markup=kb)
    bot.register_next_step_handler_by_chat_id(uid, callback)
    # clear handlers
    bot.next_step_backend.handlers[uid] = [bot.next_step_backend.handlers[uid][-1]]


def create_task(user: User, url: str, trial: bool = True) -> bool:
    """ Создает задачу на выполнение отчета в базе данных """
    Task.insert(user=user, url=url).execute()


def is_allowed(user: User) -> bool:
    """ True, если у пользователя есть возможность запросить отчет, False - если нет """
    print('Is allowed?')
    if user.has_trial:
        return True
    if not user.tariff or user.tariff.id == 0:
        return False
    if user.tariff.by_date and not user.expire_at:
        # странный фикс странного бага
        return False
    if user.tariff.by_date and user.expire_at > dt.now():
        return True
    if not user.tariff.by_date and user.reports_left:
        return True
    user.tariff = ZERO_TARIFF
    user.save()
    return False


def handle_tariff(user: User) -> None:
    """ Изменяем данные о тарифе и пробнике с учетом того, что пользователь заказ 1 отчет """
    if user.has_trial:
        user.has_trial = False
    elif not user.tariff.by_date and user.reports_left:
        user.reports_left -= 1
    user.save()

    # проверяем закончился ли тариф
    if not is_allowed(user):
        end_tariff(user)


def my_tariff(user: User) -> None:
    """
        отправляет пользователю сообщение с описанием его текущего тарифа
        предполагается, что сюда попадают пользователи, у которых
        есть оплаченный тариф
    """
    # проверяем закончился ли тариф
    if not is_allowed(user):
        end_tariff(user)
        return show_tariffes(user)

    if user.tariff.by_date:
        days = f'{user.tariff.total} {ms.day_form(user.tariff.total)}'
        return send_message(
            user=user,
            text=ms.YOUR_TARIFF_DAYS.format(
                days=days,
                ends=user.expire_at
            ),
            kb=ms.MAIN_KB
        )
    left = f'{user.reports_left} {ms.report_form(user.reports_left)}'
    send_message(
        user=user,
        text=ms.YOUR_TARIFF_COUNT.format(
            total=user.tariff.total,
            left=left
        ),
        kb=ms.MAIN_KB
    )


def get_tariffes_keyboard(user: User) -> telebot.types.InlineKeyboardMarkup:
    tariffes = Tariff.select().where(Tariff.id != 0)
    tariffes_ = []

    for i in range(len(tariffes) // 2 + 1):
        buttons_row = []
        for tariff in tariffes[i*2:i*2+2]:
            pay_url = new_payment(user, tariff)
            button = telebot.types.InlineKeyboardButton(
                tariff.name,
                url=pay_url
            )

            buttons_row.append(button)
        tariffes_.append(buttons_row)

        # FIXME: delete this
        # pay_url, label = new_payment(user, tariff)

        # tariffes_.append([
        #     telebot.types.InlineKeyboardButton(t.name, callback_data=f'tariff_{t.id}')
        #     for t in tariffes[i*2:i*2+2]])

    return telebot.types.InlineKeyboardMarkup(tariffes_, 2)


def show_tariffes(user: User) -> None:
    """ Отправляет пользователю инлайн клавиатуру со списком
        тарифов, которые можно купить
    """
    if user.tariff.id != 0:
        return my_tariff(user)

    # тут пользователю показывается куча тарифов и предлагается
    # что то купить
    kb = get_tariffes_keyboard(user)

    if user.has_trial:
        send_message(user, ms.NO_TARIFF_BUT_TRIAL)
        text = ms.NO_TARIFF_BUY_IMM
    else:
        text = ms.NO_TARIFF
    send_message(user, text, kb=kb)


def show_ref(msg: telebot.types.Message, user: User) -> None:
    """ Отправляет пользователю сообщение с текущим количеством рефов и его реф ссылкой """
    ref_count = len(User.select().where(User.ref == user.id))
    ref_url = f'{BOT_URL}?start={user.telegram_id}'

    send_message(
        user=user,
        text=ms.REF.format(url=ref_url, count=ref_count),
        kb=ms.MAIN_KB,
        parse_mode='html'
    )


@get_user
def handle_order_url(msg: telebot.types.Message, user: User):
    """ Обрабатывает ссылку на авито от пользователя """
    url = msg.text.strip()

    if url == ms.CANCEL_BTN:
        # если пользователь отменил ввод ссылки
        return main(msg)

    if 'avito.ru' not in url:
        return send_message(user, ms.WRONG_URL, ms.CANCEL_KB, callback=handle_order_url)

    # FIXME: Тут он дважды проверяет актуальность тарифа, хотя достаточно одного
    handle_tariff(user)
    create_task(user, url, True)

    send_message(user, ms.ORDER_IN_PROGRESS, kb=ms.MAIN_KB)


def ask_for_url(msg: telebot.types.Message, user: User):
    """ При нажатии на кнопку "ПОЛУЧИТЬ ОТЧЕТ" отправляет пользователю предложение
        отправить ссылку
    """
    if user.tariff.id != 0:
        my_tariff(user)

    if not is_allowed(user):
        # если попали сюда - значит пользователь израсходовал пробник
        # и больше не может использовать бот до оплаты. предлагаем тарифы
        # return send_message(user, ms.NO_TARIFF, ms.MAIN_KB)
        return show_tariffes(user)

    send_message(user, ms.SEND_AVITO_URL, ms.CANCEL_KB, callback=handle_order_url)


@get_user
def handle_keyboard(msg: telebot.types.Message, user: User):
    """ Обрабатывает кнопки из основной клавиатуры """
    text = msg.text.strip()
    if text == ms.GET_REPORT_BTN:
        return ask_for_url(msg, user)
    if text == ms.MY_TARIFF_BTN:
        return show_tariffes(user)
    if text == ms.REF_BTN:
        return show_ref(msg, user)
    if text == ms.SUPPORT_BTN:
        return send_message(user, ms.SUPPORT, kb=ms.MAIN_KB, parse_mode='html')
    return send_message(user, ms.UNKNOWN_MESSAGE, kb=ms.MAIN_KB)


@bot.callback_query_handler(func=lambda msg: msg.data.startswith('tariff'))
@get_user
def buy_handler(msg: telebot.types.CallbackQuery, user: User):
    """ Обрабатывает нажатие на кнопку "Купить тариф" """
    tariff_id = int(msg.data.split('_')[-1])
    tariff = Tariff.select().where(Tariff.id == tariff_id).first()

    pay_url, label = new_payment(user, tariff)
    kb = telebot.types.InlineKeyboardMarkup(
        keyboard=[
            [telebot.types.InlineKeyboardButton('Оплата', pay_url)],
            [telebot.types.InlineKeyboardButton(
                'Я оплатил', callback_data=f'pay_{label}_{tariff.id}'
            )],
        ]
    )
    # FIXME: сообщить пользователю о том, что нужно оплатить и нажать на кнопку
    # перенести текст в messages
    send_message(user, 'Заглушка: Для оплаты нажмите на кнопку', kb=kb)


@bot.callback_query_handler(func=lambda msg: msg.data.startswith('pay'))
@get_user
def check_payment_handler(msg: telebot.types.CallbackQuery, user: User) -> None:
    """ Сюда попадаем, когда пользователь нажал на кнопку "Я оплатил"
        Проверяем оплату, если оплата прошла - пишем пользователю об этом
        и применяем оплаченный тариф.
        Если не прошла - предлагаем обратиться в поддержку
    """
    _, label, tarif_id = msg.data.split('_')
    tariff = Tariff.select().where(Tariff.id == int(tarif_id)).first()

    bot.edit_message_text(
        text=ms.PAYMENT_CHECKING,
        chat_id=user.telegram_id,
        message_id=msg.message.message_id,
    )

    if check_payment(label, tariff.price):
        # оплата прошла
        desc = f'{tariff.total} {"дней" if tariff.by_date else "отчетов"}'
        bot.edit_message_text(
            text=ms.PAYMENT_SUCCESS.format(tariff=desc),
            chat_id=user.telegram_id,
            message_id=msg.message.message_id
        )

        return apply_tariff(user, tariff)

    # оплата не прошла
    kb = telebot.types.InlineKeyboardMarkup(
        keyboard=[
            [telebot.types.InlineKeyboardButton(
                'Я оплатил',
                callback_data=f'pay_{label}_{tariff.id}'
            )],
        ]
    )
    bot.edit_message_text(
        text=ms.PAYMENT_FAILED,
        chat_id=user.telegram_id,
        message_id=msg.message.message_id,
        reply_markup=kb
    )


@bot.message_handler()
@get_user
def main(msg: telebot.types.Message, user: User):
    if not user.has_key and msg.text == '/start':
        # у пользователя нету оплаченного тарифа и он впервые написал боту,
        # предлагаем ему попробовать бесплатно
        if user.ref:
            send_message(user=user, text=ms.WHAT_CAN_BOT_DO, kb=ms.GET_REPORT_KB)
            send_message(
                user=user,
                text=ms.YOU_ARE_REF, kb=get_tariffes_keyboard(user)
            )
        else:
            send_message(
                user=user,
                text=ms.CHECK_OUR_SERVICE_FOR_FREE,
                kb=ms.GET_REPORT_KB
            )
    else:
        # у пользователя есть оплаченный тариф, показываем ему обычное меню
        # либо пользователь уже пользовался ботом
        send_message(user, ms.MAIN, ms.MAIN_KB)

    # DELETE THIS (FIXME:)
    if msg.text == '/change':
        user.has_key = not user.has_key
        user.save()


def run() -> None:
    on_start()
    bot.infinity_polling()


if __name__ == '__main__':
    run()
