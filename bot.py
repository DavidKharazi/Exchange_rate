import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters


# API для получения курса доллара (например, с exchangerate-api)
API_URL = "https://api.exchangerate-api.com/v4/latest/USD"

# Константы для состояний бота
ASKING_NAME, FINISHED = range(2)

# Кнопка для старта
keyboard = [['Начать']]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


# Стартовая команда (показываем кнопку "Начать")
async def start(update: Update, context):
    await update.message.reply_text("Добрый день! Нажмите 'Начать', чтобы продолжить", reply_markup=reply_markup)


# Обработка нажатия кнопки "Начать" и запроса имени
async def ask_name(update: Update, context):
    await update.message.reply_text("Добрый день! Как вас зовут?", reply_markup=ReplyKeyboardMarkup([[]], one_time_keyboard=True))
    return ASKING_NAME


# Получаем имя и отправляем курс доллара
async def handle_name(update: Update, context):
    name = update.message.text
    # Получаем курс доллара
    response = requests.get(API_URL)
    data = response.json()
    # Допустим, нам нужен курс к рублю (RUB)
    rate = data['rates'].get('RUB', 'Не удалось получить курс')

    await update.message.reply_text(f"Рад знакомству, {name}! Курс доллара сегодня {rate}р.")

    # Завершаем диалог
    return FINISHED


# Завершаем чат
async def stop(update: Update, context):
    await update.message.reply_text("Чат завершен. Вы можете начать снова, нажав 'Начать'.", reply_markup=reply_markup)
    return ConversationHandler.END


# Основная функция
def main():
    # Инициализация приложения с вашим токеном
    app = ApplicationBuilder().token("7251328238:AAFYVI9XW9pEXOvOM46cuB5Us1yomjiGkNw").build()

    # Создаем ConversationHandler для управления состояниями
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(Начать)$'), ask_name)],
        states={
            ASKING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)
            ],
            FINISHED: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, stop)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex('^(Начать)$'), ask_name)]
    )

    # Обработчик команды /start для первого запуска
    app.add_handler(CommandHandler("start", start))

    # Добавляем ConversationHandler
    app.add_handler(conv_handler)

    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    main()


