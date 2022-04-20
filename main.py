from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import set_webhook
from aiohttp import web

import config
from web_app import routes as webapp_routes


async def on_startup(dp: Dispatcher):
    await dp.bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown(dp: Dispatcher):
    await dp.bot.delete_webhook()


async def cmd_start(message: types.Message):
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Order Food",
                    web_app=types.WebAppInfo(url=f'https://{config.WEBHOOK_HOST}'),
                )
            ]
        ]
    )
    await message.answer("<b>Hey!</b>\nYou can order food here!", reply_markup=markup)


async def ordered(message: types.Message):
    await message.reply('<b>Thank you for your order!</b>\n(It will not be delivered)')


def main():
    bot = Bot(config.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot)
    app = web.Application()
    app["bot"] = bot
    app.add_routes(webapp_routes)
    app.router.add_static(prefix='/static', path='static')
    set_webhook(
        dispatcher=dp,
        webhook_path=config.WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        web_app=app,
    )
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(ordered, lambda message: message.via_bot)
    web.run_app(app, port=config.WEBAPP_PORT, host=config.WEBAPP_HOST)


if __name__ == "__main__":
    main()
