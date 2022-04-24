from aiogram import Bot, types
from aiohttp import web
from aiohttp.web_fileresponse import FileResponse

import config
from utils import parse_init_data

routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
    return FileResponse("static/index.html")


@routes.post('/submitOrder')
async def submit_order(request):
    data = await request.json()
    init_data = parse_init_data(token=config.BOT_TOKEN, raw_init_data=data['initData'])
    if init_data is False:
        return False

    bot: Bot = request.app['bot']
    query_id = init_data['query_id']

    result_text = "<b>Order summary:</b>\n\n"
    for item in data['items']:
        name, price, amount = item.values()
        result_text += f"{name} x{amount} — <b>{price}</b>\n"
    result_text += '\n' + data["totalPrice"]

    result = types.InlineQueryResultArticle(
        id=query_id,
        title='Order',
        input_message_content=types.InputTextMessageContent(message_text=result_text))
    await bot.answer_web_app_query(query_id, result)
