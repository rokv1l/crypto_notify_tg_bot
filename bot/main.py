import threading
from time import sleep

import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import Filters
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler

import config

FIRST_STEP, SECOND_STEP, LAST_STEP = range(3)


def notify(updater):
    while True:
        sleep(120)
        data = requests.get(f'http://{config.API_IP}:{config.API_PORT}').json()
        if data:
            for chat_id in data:
                for name in data[chat_id]:
                    info = data[chat_id][name]
                    message = f'{name}\n' \
                              f'Цена сейчас {info.get("now")}\n' \
                              f'{info.get("12_hours")}\n' \
                              f'{info.get("7_days")}\n'
                    try:
                        updater.bot.send_message(chat_id, message)
                    except Exception as e:
                        print(e)


def start(update, _):
    update.message.reply_text(f'Здравствуйте {update.effective_chat.first_name}.\n'
                              'Я могу уведомлять вас об изменениях выбранной вами криптовалюты.\n'
                              'Вы можете использовать такие комманды как:\n'
                              '/coin - выбрать новую криптовалюту для оповещения\n'
                              '/time - установить как часто вам будут приходить оповещения\n'
                              '/cancel - остановить диалог выбора времени или криптовалюты')


def init_dialog_handler(update, _):
    update.message.reply_text('Напишите полное название криптовалюты информацию о который вы хотите получать.')
    return FIRST_STEP


def crypto_name_handler(update, context):
    crypto_name = update.message.text
    context.user_data['name'] = crypto_name
    comfirm_handler(update, context)
    return SECOND_STEP


def api_add_coin(update, context):
    if context.user_data.get('chat_id'):
        json_data = {'chat_id': context.user_data['chat_id'], 'name': context.user_data.get('name'), 'time': 1}
    else:
        context.user_data['chat_id'] = str(update.effective_chat.id)
        json_data = {'chat_id': context.user_data['chat_id'], 'name': context.user_data.get('name'), 'time': 'None'}
    requests.post(f'http://{config.API_IP}:{config.API_PORT}', json=json_data)
    update.message.reply_text(f'Вы будете получать информацию о "{context.user_data["name"]}" '
                              f'если такая криптовалюта существует')
    return ConversationHandler.END


def comfirm_handler(update, context):
    reply_keyboard = [['Продолжить', 'Назад']]
    update.message.reply_text(f'Вы хотите отслеживать {context.user_data["name"]}?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def time_question(update, _):
    update.message.reply_text('Как часто вы хотите получать информацию?\n'
                              'Введите время в часах')
    return FIRST_STEP


def time_handler(update, context):
    time = update.message.text
    if time.isdigit() and int(time) > 0:
        context.user_data['time'] = time
    else:
        update.message.reply_text('Введено некорректное значение времени, оно должно являться цифрой и быть больше нуля.')
        return FIRST_STEP
    context.user_data['chat_id'] = str(update.effective_chat.id)
    json_data = {'chat_id': context.user_data['chat_id'], 'name': 'None', 'time': context.user_data.get('time')}
    requests.post(f'http://{config.API_IP}:{config.API_PORT}', json=json_data)
    update.message.reply_text(f'Теперь вы будете получать оповещения раз в {context.user_data.get("time")}ч')
    return ConversationHandler.END


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Неопознаная команда')


def cancel(update, _):
    update.message.reply_text('Ок')
    return ConversationHandler.END


def main():
    updater = Updater(token=config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # fallbacks в ConversationHandler не работают, разобраться почему, на каждом шаге временно размещен cancel
    coin_name_handler = ConversationHandler(
        entry_points=[CommandHandler('coin', init_dialog_handler)],
        states={FIRST_STEP: [CommandHandler('cancel', cancel),
                             MessageHandler(Filters.text, crypto_name_handler)],
                SECOND_STEP: [CommandHandler('cancel', cancel),
                              MessageHandler(Filters.regex('Продолжить'), api_add_coin),
                              MessageHandler(Filters.regex('Назад'), init_dialog_handler)]},
        fallbacks=[]
    )
    coin_time_handler = ConversationHandler(
        entry_points=[CommandHandler('time', time_question)],
        states={FIRST_STEP: [CommandHandler('cancel', cancel),
                             MessageHandler(Filters.text, time_handler)]},
        fallbacks=[]
    )
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(coin_name_handler)
    dispatcher.add_handler(coin_time_handler)
    dispatcher.add_handler(MessageHandler(Filters.all, unknown))
    threading.Thread(target=notify, args=[updater, ]).start()
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
