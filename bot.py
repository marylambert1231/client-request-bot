import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

NAME, NUMBER = range(2) 

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.from_user.id
    keyboard = [
        ["📅 Записаться", "🕐 График"],
        ["ℹ️ О нас", "📍 Адрес"]
        ]
    if user_id == ADMIN_ID:
        keyboard.append(["🧹 Очистить записи", " 📤 Заявки"])
    reply_markup = ReplyKeyboardMarkup (keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f"Здравствуйте, {update.effective_user.first_name}! Чем могу помочь?", reply_markup=reply_markup)


async def adress(update: Update, context):
    await update.message.reply_text("Мы располагаемся по адресу ул. Красоты, д. 1")

async def worktime(update: Update, context):
    await update.message.reply_text("Мы работаем ежедневно с 10:00 до 20:00")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ О нашем салоне красоты ✨\n"
        "\n"
        "Мы создаем красоту и уверенность в каждом образе! 💇‍♀️💅💄\n"
        "\n"
        "🔹 Профессиональные мастера с многолетним опытом\n"
        "🔹 Только качественные материалы и премиальная косметика\n"
        "🔹 Уютная атмосфера и индивидуальный подход\n"
        "🔹 Современные технологии для безупречного результата\n"
        "\n"
        "Доверьте свою красоту нам — и будьте неотразимы! 💖\n"
        "\n"
        "Ждем вас в нашем салоне! 🏩"
    )

async def appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        await update.message.reply_text("Администратор скоро свяжется")
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Как администратор может к Вам обращатся?",
            reply_markup=ReplyKeyboardRemove(),
            )
        return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data['name'] = name
    await update.message.reply_text(
        f"{name}, укажите номер телефона для связи:"
    )
    return NUMBER

async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    number = update.message.text
    user_data[user_id] = {
        'name' : context.user_data['name'],
        'number' : number
    }
    context.user_data.pop('name', None)
    await update.message.reply_text("Спасибо, с вами свяжется администратор!")
    return ConversationHandler.END

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if not user_data:
            await update.message.reply_text("Нет заявок для записи")
        else:
            message = "Данные пациентов для записи \n"
            for uid, data in user_data.items():
                message += f"ID: {uid}, Имя: {data['name']}, Номер телефона: {data['number']} \n"
            await update.message.reply_text(message)
    else:
        await update.message.reply_text("Доступ ограничен. Нужны права администратора")

async def clear_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        user_data.clear()
        await update.message.reply_text("Все записи успешно удалены 🧹")
    else:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancel")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("appointment", appointment),
            MessageHandler(filters.Regex(r'^📅 Записаться$'), appointment)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^ℹ️ О нас$'), info))
    app.add_handler(MessageHandler(filters.Regex(r'^📍 Адрес$'), adress))
    app.add_handler(MessageHandler(filters.Regex(r'^🕐 График$'), worktime))
    app.add_handler(MessageHandler(filters.Regex(r'^🧹 Очистить записи$'), clear_users))
    app.add_handler(MessageHandler(filters.Regex(r'^📤 Заявки$'), admin))
    app.add_handler(conv_handler)

    print("Бот готов к работе!!")
    app.run_polling()

if __name__ == "__main__":
    main()
