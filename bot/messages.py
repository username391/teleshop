from telebot.types import ReplyKeyboardMarkup


def get_form(words: list[str], num: int) -> int:
    last_digit = num % 10
    previous_digit = num // 10 % 10

    if previous_digit == 1:
        return words[0]
    if last_digit == 1:
        return words[1]
    if last_digit in [2, 3, 4]:
        return words[2]
    return words[0]


def day_form(days: int) -> str:
    return get_form(['дней', 'день', 'дня'], days)


def report_form(count: int) -> str:
    return get_form(['отчетов', 'отчет', 'отчета'], count)


MAIN_MESSAGE = 'Hello!'

CHECK_OUR_SERVICE_FOR_FREE = 'Протеструйте наш сервис сбора статистики бесплатно!'

SEND_AVITO_URL = 'Для получения отчёта, отправьте ссылку на поисковую выдачу \
Авито. При формировании выдачи, не забудьте отметить фильтры: "Только в \
названии" и "Только из ..."\n\
Ваш отчёт начнёт формироваться в 23:00 по МСК.'

NO_TARIFF = 'На данный момент у вас нет активного тарифа. \
Чтобы подготовить отчёт, выберите подходящий тариф.'

NO_TARIFF_BUT_TRIAL = '🤷‍♂️ *На данный момент у вас нет активного тарифа,* \
но вам доступен 1 бесплатный отчёт. Нажмите: *ПОЛУЧИТЬ ОТЧЕТ* и \
отправьте боту ссылку на поисковую выдачу.'

NO_TARIFF_BUY_IMM = 'Также вы можете сразу приобрести подходящий тариф:'

YOUR_TARIFF_DAYS = 'Ваш тариф: {days}.\nДата окончания: {ends}'
YOUR_TARIFF_COUNT = 'Ваш тариф: {total}.\nЕще доступно: {left}'
PAYMENT_CHECKING = 'Проверяю...'
PAYMENT_SUCCESS = '✅ Оплата прошла успешно!\nВаш тариф: *{tariff}*.\n\
Хотите подготовить отчет?'
# PAYMENT_SUCCESS = 'Благодарим за оплату!\nВаш тариф: {tariff}.\nХотите подготовить отчёт?'
PAYMENT_FAILED = 'Платеж не найден. Если вы оплатили - обратитесь в техподдержку'

REF = '🤝 *Пригласи в сервис трёх друзей* по реферальной ссылке. Вы и ваши друзья \
получат бонусные дни бесплатного использования или доступные отчёты в \
зависимости от тарифа.\nВаша ссылка 👇\n{url}\nКоличество рефералов: {count}'

UNKNOWN_MESSAGE = 'Нераспознанный запрос'
WRONG_URL = '🙅‍♂️ *Запрос не соответствует формату*'
ORDER_IN_PROGRESS = '👌 *Ваш заказ принят,* ожидайте получения отчёта.'

SUPPORT = 'По всем вопросам пишите: @durov'

MAIN = 'меню'

WHAT_CAN_BOT_DO = 'Что умеет этот бот?'

YOU_ARE_REF = '*Вас пригласили по реферальной ссылке* и после \
активации любого из тарифов, вам будут доступны наши бонусы.\n\
🎉 Также вам доступен 1 бесплатный отчёт. Нажмите: *ПОЛУЧИТЬ ОТЧЕТ* \
и отправьте боту ссылку на поисковую выдачу.\n\n\
👇Затем выберите подходящий тариф, чтобы получить реферальные бонусы'


# кнопки
GET_REPORT_BTN = 'ПОЛУЧИТЬ ОТЧЕТ'
MY_TARIFF_BTN = 'МОЙ ТАРИФ'
REF_BTN = 'РЕФКА'
SUPPORT_BTN = 'ПОДДЕРЖКА'

CANCEL_BTN = 'Отмена'

GET_REPORT_KB = ReplyKeyboardMarkup(True, True)
GET_REPORT_KB.add(GET_REPORT_BTN)

MAIN_KB = ReplyKeyboardMarkup(True, one_time_keyboard=False)
MAIN_KB.add(GET_REPORT_BTN)
MAIN_KB.add(MY_TARIFF_BTN)
MAIN_KB.row(REF_BTN, SUPPORT_BTN)
# MAIN_KB.add(REF_BTN)
# MAIN_KB.add(SUPPORT_BTN)

CANCEL_KB = ReplyKeyboardMarkup(True, True)
CANCEL_KB.add(CANCEL_BTN)
