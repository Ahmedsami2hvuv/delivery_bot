# الملف: bot.py (تم التعديل للربط بـ web_actions.py)

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
# 🔴 استيراد الدوال من الملف الجديد
from web_actions import login_and_get_title 


# ************************************************
# 🔴 التوكن اللي خليته هو:
# ************************************************
TOKEN = "8215940523:AAEVr2jEg8Uxh4zJAFq4kFzKw1-kjKvByUg" 

# اليوزر نيم والباسوورد والموقع الهدف (راح نخليهم ثابتين للتجربة)
# 🔴 يرجى تغييرها بمعلوماتك الحقيقية للموقع الهدف
USER_NAME = "ابو_الاكبر_يوزر" 
PASS_WORD = "ابو_الاكبر_باسورد" 
LOGIN_PAGE = "https://www.google.com" # 🔴 غير هذا العنوان بعنوان الموقع اللي بيه حسابك

# دالة (Function) البداية: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # الأزرار (نفس الأزرار السابقة)
    keyboard = [
        [
            InlineKeyboardButton("➕ إضافة طلب جديد", callback_data='add_order'),
            InlineKeyboardButton("🔎 بحث برقم الطلب", callback_data='search_by_id'),
        ],
        [
            InlineKeyboardButton("👤 بحث باسم الزبون", callback_data='search_by_name'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'أهلاً بك يا أبو الأكبر في بوت خدمة التوصيل الشامل.\nإختر العملية المطلوبة:',
        reply_markup=reply_markup
    )

# دالة استقبال ضغطات الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() 

    data = query.data
    
    if data == 'add_order':
        await query.edit_message_text(text="جاري محاولة الدخول للموقع... إنتظر رجاءً.")
        
        # 🔴 هنا نستدعي الدالة من ملف web_actions.py
        result_message = login_and_get_title(USER_NAME, PASS_WORD, LOGIN_PAGE)
        
        await query.edit_message_text(result_message)

    # باقي الأزرار (ما تتغير)
    elif data == 'search_by_id':
        await query.edit_message_text(text="تمام! للبحث برقم الطلب، يرجى إرسال الرقم الآن.")
    elif data == 'search_by_name':
        await query.edit_message_text(text="تمام! للبحث باسم الزبون، يرجى إرسال الاسم الآن.")


def main() -> None:
    # تهيئة وتشغيل البوت (نفس الشي)
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    
    print("البوت بدأ العمل.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
