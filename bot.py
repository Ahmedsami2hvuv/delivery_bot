# الملف: bot.py (التعديل الأخير)

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
# 🔴 إستيراد دالة perform_add_order الجديدة 
from web_actions import perform_add_order


# ************************************************
# 🔴 قراءة البيانات من متغيرات الريلوي (أمان)
# ************************************************
# ... (TOKEN و USER_NAME و PASS_WORD تبقى كما هي)
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
USER_NAME = os.environ.get("WEB_USERNAME") 
PASS_WORD = os.environ.get("WEB_PASSWORD") 
DELIVERY_URL = "https://d.ksebstor.site/client/8757c7dd6c4df11bbb435093" 


# ... (دالة start و دالة button تبقى كما هي) ...

# 🔴 دالة معالجة الرسائل النصية الجديدة (تم التعديل)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('state') == 'AWAITING_ORDER_DETAILS':
        
        context.user_data['state'] = 'READY' 

        order_details = update.message.text.split('\n')
        
        if len(order_details) < 5:
            await update.message.reply_text(
                "❌ فشل: يجب أن تكون الرسالة بخمسة سطور (النوع، السعر، المنطقة، الرقم، الوقت). يرجى المحاولة مرة أخرى أو إرسال /start."
            )
            return

        await update.message.reply_text("⏳ جاري محاولة إضافة الطلب في الموقع... إنتظر رجاءً.")

        # 🔴 1. استدعاء دالة السيلينيوم الحقيقية
        # هاي الدالة راح ترجع رسالة النجاح أو الخطأ
        result_message = perform_add_order(order_details, DELIVERY_URL) 
        
        # 🔴 2. إرسال نتيجة العملية للمستخدم
        await update.message.reply_text(result_message)

    else:
        await update.message.reply_text("إختر أمر من الأزرار أو إكتب /start.")


def main() -> None:
    # تهيئة وتشغيل البوت (نفس الشي)
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    
    print("البوت بدأ العمل.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
