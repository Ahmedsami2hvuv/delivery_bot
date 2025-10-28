# الملف: web_actions.py (النسخة النهائية لـ Requests)

import requests
from bs4 import BeautifulSoup
import json
import time

# ************************************************
# 🔴 دالة تنفيذ عملية إضافة الطلب (باستخدام Requests)
# ************************************************
def perform_add_order(order_details: list, delivery_url: str):
    
    # تفاصيل الطلب اللي تجينا من التليجرام:
    item_type = order_details[0].strip()    # النوع (مسواك)
    price = order_details[1].strip()        # السعر (12)
    area_name = order_details[2].strip()    # المنطقة (جيكور)
    phone_number = order_details[3].strip() # الرقم (077...)
    time_text = order_details[4].strip()    # الوقت (هسه)
    
    # *******************************************************************
    # 1. المرحلة الأولى: الحصول على كود المنطقة (ضروري للتطبيق)
    # *******************************************************************
    try:
        # 🔴 لازم نسوي طلب بحث خاص حتى نعرف الكود (ID) مال المنطقة
        # حالياً، ما نكدر نعرف رابط البحث، لذلك راح نفترض إن الموقع يحتاج اسم المنطقة فقط.
        # إذا فشل، نحتاج رابط API الموقع. حالياً: نفترض إنه ما يحتاج API.
        
        # بما إن الروابط ثابتة، الموقع يطلب ID خاص بالمنطقة
        # لكن للتجربة المبدئية، راح نستخدم اسم المنطقة مباشرة في حقل Area_Name
        
        # 🔴 نحتاج نحدد ID الحقيقي للمنطقة. بما إننا ما عندنا API، راح نفترض ID افتراضي مؤقتاً
        # (اذا فشل الكود، سنحتاج منك تفاصيل أكثر عن المنطقة)
        area_id = area_name 

    except Exception as e:
         return f"❌ فشل: لم يتمكن من تحديد كود المنطقة. (الخطوة رقم 102)"

    # *******************************************************************
    # 2. المرحلة الثانية: إرسال الطلب (POST Request)
    # *******************************************************************
    
    # 🔴 هذا هو الرابط اللي راح نرسل عليه البيانات (غالباً هو نفسه رابط الصفحة)
    # 🔴 غالباً الطلب يكون على رابط آخر، لكن نفترض إنه رابط الصفحة مؤقتاً
    post_url = delivery_url 
    
    # 🔴 البيانات اللي لازم يرسلها البوت للموقع:
    # (هاي الأسماء هي تخمينية للحقول، لازم تتغير للأسماء الحقيقية اللي يستخدمها الموقع)
    payload = {
        'order_type': item_type,       # نوع الطلبية
        'price_delivery_less': price,  # السعر بدون توصيل
        'area_search': area_id,        # اسم/كود المنطقة
        'customer_phone': phone_number, # رقم الزبون
        'order_time': time_text,       # وقت الطلب
        'submit_button': 'إضافة الطلبية' # زر التأكيد (اسم الزر الحقيقي)
        # ممكن نحتاج نضيف حقول مخفية (csrf tokens) إذا الموقع يتطلب أمان
    }
    
    # إرسال البيانات
    try:
        response = requests.post(post_url, data=payload)
        
        # فحص الرد:
        if response.status_code == 200:
            # 🔴 البحث عن رسالة النجاح في محتوى الصفحة اللي رجعت
            soup = BeautifulSoup(response.text, 'html.parser')
            success_div = soup.find('div', class_='success-message') # تخميني
            
            if success_div or "سجل الطلبات" in response.text:
                return "✅ تم إضافة الطلب بنجاح. (تم الإرسال عبر requests)"
            else:
                return f"⚠️ تم إرسال الطلب، لكن لم يتم التأكد من نجاح الإضافة. حالة الرد: {response.status_code}. \nمحتوى الرد: {response.text[:100]}..."
        else:
            return f"❌ فشل الإرسال. حالة الرد: {response.status_code}. "

    except Exception as e:
        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
