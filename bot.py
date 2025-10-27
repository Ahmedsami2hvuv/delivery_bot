import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ************************************************
# 🔴 معلومة مهمة: غير هذا الرمز (TOKEN) بالرمز مالتك اللي اخذته من BotFather
# ************************************************
TOKEN = "8215940523:AAGrHjks3aDn0KOjesuhuOxa5GDB6wBR0Vg" 

# دالة (Function) البداية: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # الأزرار اللي راح تطلع للمستخدم 
    keyboard = [
        [
            InlineKeyboardButton("➕ إضافة طلب جديد", callback_data='add_order'),
            InlineKeyboardButton("🔎 بحث برقم الطلب", callback_data='search_by_id'),
        ],
        [
            InlineKeyboardButton("👤 بحث باسم الزبون", callback_data='search_by_name'),
        ]
    ]

    # تهيئة لوحة المفاتيح (الكيبورد) 
    reply_markup = InlineKeyboardMarkup(keyboard)

    # إرسال الرسالة مع الأزرار 
    await update.message.reply_text(
        'أهلاً بك يا أبو الأكبر في بوت خدمة التوصيل الشامل.\nإختر العملية المطلوبة:',
        reply_markup=reply_markup
    )

# دالة استقبال ضغطات الأزرار (CallbackQueryHandler)
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() 

    data = query.data
    
    # هنا راح نبدي نضيف المنطق البرمجي لكل زر:
    if data == 'add_order':
        await query.edit_message_text(text="تمام! لإضافة طلب جديد، نحتاج ندخل للموقع... (قريباً راح نبرمج الدخول للموقع)")
    elif data == 'search_by_id':
        await query.edit_message_text(text="تمام! للبحث برقم الطلب، يرجى إرسال الرقم الآن. (قريباً راح نبرمج عملية البحث)")
    elif data == 'search_by_name':
        await query.edit_message_text(text="تمام! للبحث باسم الزبون، يرجى إرسال الاسم الآن. (قريباً راح نبرمج عملية البحث)")


def main() -> None:
    # تهيئة البوت
    application = Application.builder().token(TOKEN).build()

    # تسجيل الأوامر (Handlers)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # تشغيل البوت
    print("البوت بدأ العمل محلياً. دوس Ctrl+C حتى توقفه.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
