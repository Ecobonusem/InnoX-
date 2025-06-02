from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, ConversationHandler
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

DISTRICT, NAME, PHONE, PROJECT_NAME, PRESENTATION, TABLET, PHOTO = range(7)
user_data = {}

@app.route('/')
def home():
    return "InnoX bot server ishlayapti!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

def start(update, context):
    update.message.reply_text("Assalomu alaykum! Iltimos, tumaningizni tanlang:",
        reply_markup=context.bot.build_reply_keyboard([["Angor", "Bandixon", "Boysun"],
                                                        ["Denov", "Jarqo‘rg‘on", "Muzrabot"],
                                                        ["Oltinsoy", "Qiziriq", "Qumqo‘rg‘on"],
                                                        ["Sariosiyo", "Sherobod", "Sho‘rchi"],
                                                        ["Termiz", "Uzun"]]))
    return DISTRICT

def get_district(update, context):
    user_data[update.effective_chat.id] = {'district': update.message.text}
    update.message.reply_text("Ism familyangizni yuboring:")
    return NAME

def get_name(update, context):
    user_data[update.effective_chat.id]['name'] = update.message.text
    update.message.reply_text("Telefon raqamingizni yuboring:")
    return PHONE

def get_phone(update, context):
    user_data[update.effective_chat.id]['phone'] = update.message.text
    update.message.reply_text("Loyihangiz nomini yozing:")
    return PROJECT_NAME

def get_project(update, context):
    user_data[update.effective_chat.id]['project'] = update.message.text
    update.message.reply_text("Loyiha prezentatsiyasi faylini yuboring:")
    return PRESENTATION

def get_presentation(update, context):
    user_data[update.effective_chat.id]['presentation'] = update.message.document.file_id
    update.message.reply_text("Endi loyiha planshet faylini yuboring:")
    return TABLET

def get_tablet(update, context):
    user_data[update.effective_chat.id]['tablet'] = update.message.document.file_id
    update.message.reply_text("Endi shaxsiy 3x4 rasmingizni yuboring:")
    return PHOTO

def get_photo(update, context):
    uid = update.effective_chat.id
    user_data[uid]['photo'] = update.message.photo[-1].file_id

    info = user_data[uid]
    bot.send_message(chat_id=ADMIN_ID,
        text=f"📥 Yangi ro'yxatdan o'tuvchi:\n"
             f"📍 Tuman: {info['district']}\n"
             f"👤 Ism: {info['name']}\n"
             f"📞 Tel: {info['phone']}\n"
             f"📌 Loyiha: {info['project']}")
    bot.send_document(chat_id=ADMIN_ID, document=info['presentation'], caption="📎 Prezentatsiya")
    bot.send_document(chat_id=ADMIN_ID, document=info['tablet'], caption="📎 Planshet")
    bot.send_photo(chat_id=ADMIN_ID, photo=info['photo'], caption="🖼 3x4 rasm")

    update.message.reply_text("✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Rahmat!")
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        DISTRICT: [MessageHandler(Filters.text & ~Filters.command, get_district)],
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
        PROJECT_NAME: [MessageHandler(Filters.text & ~Filters.command, get_project)],
        PRESENTATION: [MessageHandler(Filters.document, get_presentation)],
        TABLET: [MessageHandler(Filters.document, get_tablet)],
        PHOTO: [MessageHandler(Filters.photo, get_photo)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

dispatcher.add_handler(conv_handler)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
