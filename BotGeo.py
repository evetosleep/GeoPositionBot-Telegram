import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# логи
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# делимся позицией с написавшим
geolocations = {}

# старт бота и приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет. Я могу поделиться твоей геолокацией. Используй /geolocations для этого.')

# локации нет
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not geolocations:
        await update.message.reply_text('Нет доступных местоположений.')
        return

    keyboard = []
    for user_id, info in geolocations.items():
        keyboard.append([InlineKeyboardButton(info['nickname'], callback_data=f"loc_{user_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите пользователя:', reply_markup=reply_markup)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    sender = update.message.from_user
    user_id = sender.id
    nickname = sender.username if sender.username else f"{sender.first_name} {sender.last_name}".strip()

    geolocations[user_id] = {
        'location': (location.latitude, location.longitude),
        'nickname': nickname
    }

    await update.message.reply_text('Геолокация сохранена.')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split('_')[1])
    if user_id in geolocations:
        location = geolocations[user_id]['location']
        nickname = geolocations[user_id]['nickname']
        await query.message.reply_location(latitude=location[0], longitude=location[1])
        await query.message.reply_text(f"Отправлено: {nickname}")
    else:
        await query.message.reply_text("Извините, местоположение больше недоступно.")

def main():
    # токен сюда
    application = ApplicationBuilder().token('токен').build()

    # команды
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('getlocation', get_location))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()