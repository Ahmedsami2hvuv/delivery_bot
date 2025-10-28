# الملف: bot.py

import os 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters 

# 🔴 إستيراد دالة perform_add_order
from web_actions import perform_add_order


# ************************************************
# قراءة البيانات من متغيرات بيئة التشغيل في Render
# ************************************************
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
USER_NAME = os.environ.get("WEB_USERNAME") 
PASS_WORD = os.environ.get("WEB_PASSWORD") 
DELIVERY_URL = os.environ.get("URL") 


# ************************************************
# 1. دالة (Function) البداية: /start
# ************************************************
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['state'] = 'READY' 
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

# ************************************************
# 2. دالة استقبال ضغطات الأزرار
# ************************************************
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() 

    data = query.data
    
    if data == 'add_order':
        context.user_data['state'] = 'AWAITING_ORDER_DETAILS' 
        await query.edit_message_text(
            "تم إختيار إضافة طلب جديد. يرجى إرسال تفاصيل الطلب على شكل سطور بالترتيب:\n"
            "**مثال:**\n"
            "مسواك\n"
            "12\n"
            "جيكور\n"
            "07733921468\n"
            "هسه"
        )

    # باقي الأزرار
    elif data == 'search_by_id':
        await query.edit_message_text(text="تمام! للبحث برقم الطلب، يرجى إرسال الرقم الآن.")
    elif data == 'search_by_name':
        await query.edit_message_text(text="تمام! للبحث باسم الزبون، يرجى إرسال الاسم الآن.")


# ************************************************
# 3. دالة معالجة الرسائل النصية الجديدة
# ************************************************
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

        # استدعاء دالة السيلينيوم الحقيقية
        result_message = perform_add_order(order_details, DELIVERY_URL) 
        
        # إرسال نتيجة العملية للمستخدم
        await update.message.reply_text(result_message)

    else:
        await update.message.reply_text("إختر أمر من الأزرار أو إكتب /start.")


# ************************************************
# 4. دالة التشغيل الرئيسية (Main)
# ************************************************
def main() -> None:
    if not TOKEN:
        print("❌ خطأ: التوكن غير موجود. يرجى إضافته كمتغير بيئة (TELEGRAM_TOKEN) في Render.")
        return 
        
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start)) 
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت بدأ العمل.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
