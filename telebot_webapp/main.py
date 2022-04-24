from flask import Flask, request, abort, send_file
from telebot import TeleBot, types

import config
from utils import parse_init_data

bot = TeleBot(config.BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__, static_url_path='/static')


@app.post(config.WEBHOOK_PATH)
def process_webhook_post():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@app.get('/')
def index():
    return send_file('static/index.html')


@app.post('/submitOrder')
def submit_order():
    data = request.json
    init_data = parse_init_data(token=config.BOT_TOKEN, raw_init_data=data['initData'])
    if init_data is False:
        return False

    query_id = init_data['query_id']

    result_text = "<b>Order summary:</b>\n\n"
    for item in data['items']:
        name, price, amount = item.values()
        result_text += f"{name} x{amount} — <b>{price}</b>\n"
    result_text += '\n' + data["totalPrice"]

    result = types.InlineQueryResultArticle(
        id=query_id,
        title='Order',
        input_message_content=types.InputTextMessageContent(message_text=result_text, parse_mode='HTML'))
    bot.answer_web_app_query(query_id, result)
    return ''


@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message):
    markup = types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Order Food",
                    web_app=types.WebAppInfo(url=f'https://{config.WEBHOOK_HOST}'),
                )
            ]
        ]
    )
    bot.send_message(message.from_user.id, "<b>Hey!</b>\nYou can order food here!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.via_bot)
def ordered(message: types.Message):
    bot.reply_to(message, '<b>Thank you for your order!</b>\n(It will not be delivered)')


def main():
    bot.delete_webhook()
    bot.set_webhook(config.WEBHOOK_URL)

    app.run(host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)


if __name__ == "__main__":
    main()
