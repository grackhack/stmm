from telegram.ext import Updater, CommandHandler, Job, MessageHandler, Filters, BaseFilter
import telegram
import logging
import datetime
import filters

# Keyboards for anything menu
from tbot import cfg
from tbot.botkeyboard import BotKeyboard

start_kb = BotKeyboard.SetKb('/start', '|', '/unset', '|', '/set 10')

TOKEN = cfg.TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    first_name = update.message.from_user.first_name
    user_id = update.message.from_user.id
    welcome_text = 'Привет! Батя! ' if user_id == cfg.BOT_FATHER else 'Привет, ' + first_name + '! '
    welcome_text += '\nСегодня ' + datetime.datetime.today().strftime("%d/%m/%Y %H:%M")
    start_kb = BotKeyboard.SetKb('Домой', 'Статистика', '|', 'Результаты', 'Помощь')
    bot.send_message(chat_id=update.message.chat_id,
                     text=welcome_text,
                     parse_mode="HTML",
                     reply_markup=start_kb)


def echo(bot, update):
    command_text = update.message.text
    try:
        func_menu[command_text](bot, update)
    except Exception:
        bot.send_message(update.message.chat_id, text=command_text)


def later(bot, update):
    caption = "Давай через:"
    later_kb = BotKeyboard.SetKb('Домой', '10 мин', '30 мин', '|', '1 час :-)', 'завтра', '30 мин')
    bot.send_message(chat_id=update.message.chat_id,
                     text=caption,
                     parse_mode="HTML",
                     reply_markup=later_kb)


def stat(bot, update):
    # games = parse.parse_game(parse.get_html(Cfg.ROOT_LNK))
    # res = parse.get_games(games)
    res = 'Тестовое сообщение'
    start_kb = BotKeyboard.SetKb('Домой', 'Статистика', '|', 'Результаты', 'Чемпионаты')
    logging.info("chat msg: {}".format(update.message.chat_id))
    bot.send_message(chat_id=update.message.chat_id,
                     text=res,
                     parse_mode="HTML",
                     reply_markup=start_kb)


def resgame(bot, update):
    # games = parse.parse_game(parse.get_html(Cfg.ROOT_LNK))
    # res = parse.get_res(games)
    res = 'Тестовый результат'
    start_kb = BotKeyboard.SetKb('Домой', 'Статистика', '|', 'Результаты', 'Помощь')
    bot.send_message(chat_id=update.message.chat_id,
                     text=res,
                     parse_mode="HTML",
                     reply_markup=start_kb)


def home(bot, update):
    res = 'Главное меню'
    start_kb = BotKeyboard.SetKb('Домой', 'Статистика', '|', 'Результаты', 'Помощь')
    bot.send_message(chat_id=update.message.chat_id,
                     text=res,
                     parse_mode="HTML",
                     reply_markup=start_kb)


def chemp(bot, update):
    res = 'Чемпионаты'
    start_kb = BotKeyboard.SetKb('Домой', 'Статистика', '|', 'Результаты', 'Помощь')
    bot.send_message(chat_id=update.message.chat_id,
                     text=res,
                     parse_mode="HTML",
                     reply_markup=start_kb)


def alarm(bot, job):
    """Function to send the alarm message"""
    bot.sendMessage(job.context, text='Напоминаю!!!')


def set(bot, update, args, job_queue, chat_data):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = Job(alarm, due, repeat=False, context=chat_id)
        chat_data['job'] = job
        job_queue.put(job)

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(bot, update, chat_data):
    """Removes the job if the user changed their mind"""

    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


func_menu = {'Помощь': start, 'Позже': later}

CN = False


def main():
    REQUEST_KWARGS = {
        'proxy_url': 'https://192.162.241.92:1080',
        # Optional, if you need authentication:
        # 'urllib3_proxy_kwargs': {
        #     'username': 'PROXY_USER',
        #     'password': 'PROXY_PASS',
        # }
    }
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", home))

    # dp.add_handler(MessageHandler(filters.chemp_filter, chemp))
    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # dp.add_handler(CommandHandler("set", set,
    #                               pass_args=True,
    #                               pass_job_queue=True,
    #                               pass_chat_data=True))
    # dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # ОБработка Статистики
    dp.add_handler(MessageHandler(filters.stat_filter, stat))
    # dp.add_handler(MessageHandler(filters.res_filter, resgame))
    # dp.add_handler(MessageHandler(filters.home_filter, home))

    # log all errors
    dp.add_error_handler(error)


    # Start the Bot
    updater.start_polling()
    # try:
    #     updater.send_message(chat_id=39356158, text='some text to post')
    # except Exception as e:
    #     logging.exception("Message")

    # if not CN:
    #     CN = True
    #     dp.send_message(chat_id=39356158, text='some text to post')

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def test_msg():
    for i in range(5):
        proxy_list = [
            'https://195.201.43.199:3128',
            'https://195.208.172.70:8080',
            'https://145.249.106.107:8118',
            'https://51.255.168.125:9999',
            'https://144.76.62.29:3128',
        ]
        try:
            REQUEST_KWARGS = {
                # 'proxy_url': 'https://192.162.241.92:1080',
                'proxy_url': proxy_list[i],
                # Optional, if you need authentication:
                # 'urllib3_proxy_kwargs': {
                #     'username': 'PROXY_USER',
                #     'password': 'PROXY_PASS',
                # }
            }

            updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)
            country = 'ПОЛЬША'
            chemp = 'Первый дивизион'
            info = """<a href="http://t.myscore.ru/#!/match/{}/match-summary">Подробности</a>""".format('v73jbxUI')
            message = """<b>{}</b>\n {} {} \n{} - {} dog:{}\n <i> Счет: {} Время:{}</i>\n <i> Кэфы:{} {} {}</i>\n{} """.format(
                'СТАВКА П1', country, chemp, 'Друтекс-Бытовия', 'Хробры Глогув', '2', '0-1', '30',
                '1.21', '3.54', '6.52', info)

            updater.bot.send_message(chat_id=cfg.BOT_FATHER,
                             text=message,
                             parse_mode='HTML',
                             disable_web_page_preview=True)
        except Exception as e:
            print(e)
        else:
            break

if __name__ == '__main__':
    # main()
    test_msg()