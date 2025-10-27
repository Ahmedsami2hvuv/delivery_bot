# الملف: bot.py (تم التعديل عليه)

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os # لإدارة بيئة التشغيل

# ************************************************
# 🔴 التوكن اللي خليته هو:
# ************************************************
TOKEN = "6725354032:AAoHfE3AOkdeJXasufshXhxt600b8sw0g" 


# دالة (Function) مهمة: تهيئة متصفح السيلينيوم
def setup_selenium_driver():
    """تهيئة متصفح Chrome للعمل بوضع Headless (بدون واجهة) بالريلوي."""
    
    # خيارات تشغيل الكروم (Headless mode)
    chrome_options = Options()
    chrome_options.add_argument("--headless") # تشغيل بدون واجهة (مهم بالريلوي)
    chrome_options.add_argument("--no-sandbox") # مهم للسيرفرات (الريلوي)
    chrome_options.add_argument("--disable-dev-shm-usage") # مهم للسيرفرات

    # ننصب الكروم درايفر ونشغله مباشرة
    service = Service(ChromeDriverManager().install())
    
    # ننشئ المتصفح
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


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

# دالة استقبال ضغطات الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() 

    data = query.data
    
    # *** المنطق الجديد: تجربة السيلينيوم عند الضغط على زر إضافة طلب ***
    if data == 'add_order':
        await query.edit_message_text(text="جاري محاولة الدخول للموقع... إنتظر رجاءً.")
        
        try:
            # تشغيل المتصفح الآلي (Selenium)
            driver = setup_selenium_driver()
            
            # مجرد تجربة بسيطة (مثلاً فتح جوجل)
            driver.get("https://www.google.com")
            
            # التأكد من نجاح الدخول
            title = driver.title
            
            # سد المتصفح
            driver.quit()
            
            await query.edit_message_text(f"✅ تم تشغيل المتصفح بنجاح! عنوان الصفحة اللي دخلتها: {title}")

        except Exception as e:
            await query.edit_message_text(f"❌ صار خطأ بمحاولة تشغيل المتصفح: {e}")

    # باقي الأزرار
    elif data == 'search_by_id':
        await query.edit_message_text(text="تمام! للبحث برقم الطلب، يرجى إرسال الرقم الآن.")
    elif data == 'search_by_name':
        await query.edit_message_text(text="تمام! للبحث باسم الزبون، يرجى إرسال الاسم الآن.")


def main() -> None:
    # تهيئة البوت
    application = Application.builder().token(TOKEN).build()

    # تسجيل الأوامر (Handlers)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # تشغيل البوت
    print("البوت بدأ العمل.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
