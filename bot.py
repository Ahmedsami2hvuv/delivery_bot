# الملف: bot.py (الكود الكامل والصحيح)

import os 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters 
# إستيراد دالة perform_add_order
from web_actions import perform_add_order


# ************************************************
# قراءة البيانات من متغيرات الريلوي (الآن صار يشتغل)
# ************************************************
TOKEN = os.environ.get("TELEGRAM_TOKEN") 
USER_NAME = os.environ.get("WEB_USERNAME") 
PASS_WORD = os.environ.get("WEB_PASSWORD") 
# الرابط: https://d.ksebstor.site/client/8757c7dd6c4df11bbb435093
DELIVERY_URL = os.environ.get("URL") 


# ************************************************
# 1. دالة (Function) البداية: /start
# ************************************************
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # وضع حالة البوت: جاهز لاستقبال الأوامر
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
        # تغيير حالة البوت: الآن ينتظر رسالة الطلب
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
    # فحص حالة البوت: هل ينتظر تفاصيل طلب؟
    if context.user_data.get('state') == 'AWAITING_ORDER_DETAILS':
        
        # 1. إرجاع حالة البوت للحالة الأساسية
        context.user_data['state'] = 'READY' 

        # 2. تقسيم رسالة المستخدم (السطور)
        order_details = update.message.text.split('\n')
        
        if len(order_details) < 5:
            await update.message.reply_text(
                "❌ فشل: يجب أن تكون الرسالة بخمسة سطور (النوع، السعر، المنطقة، الرقم، الوقت). يرجى المحاولة مرة أخرى أو إرسال /start."
            )
            return

        await update.message.reply_text("⏳ جاري محاولة إضافة الطلب في الموقع... إنتظر رجاءً.")

        # 3. استدعاء دالة السيلينيوم الحقيقية
        result_message = perform_add_order(order_details, DELIVERY_URL) 
        
        # 4. إرسال نتيجة العملية للمستخدم
        await update.message.reply_text(result_message)

    else:
        # إذا البوت ما ينتظر شي، يرد بالبداية
        await update.message.reply_text("إختر أمر من الأزرار أو إكتب /start.")


# ************************************************
# 4. دالة التشغيل الرئيسية (Main)
# ************************************************
def main() -> None:
    # التأكد من وجود التوكن
    if not TOKEN:
        print("❌ خطأ: التوكن غير موجود. يرجى إضافته كمتغير بيئة (TELEGRAM_TOKEN) في الريلوي.")
        return 
        
    # تهيئة وتشغيل البوت
    application = Application.builder().token(TOKEN).build()

    # تسجيل الأوامر (Handlers)
    application.add_handler(CommandHandler("start", start)) # الآن 'start' معرفة أعلاه
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت بدأ العمل.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
