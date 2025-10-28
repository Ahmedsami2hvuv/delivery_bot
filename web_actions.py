# الملف: web_actions.py (الإصدار النهائي مع CSRF Token)

import requests
from bs4 import BeautifulSoup
import json
import time

# قاموس لتحديد ID المنطقة بناءً على الاسم (مطلوب لـ Select Box)
AREA_IDS = {
    "تقاطع جلاب": "1", "الاسمدة": "2", "محيلة السوق": "3", "جسر محيلة": "4", 
    "جيكور": "5", "ابو مغيرة": "6", "محيلة طريق المحطة": "7", "محيلة شارع الاندلس": "8", 
    "محيلة صفحة الشط": "9", "جيكور حزبة 1": "10", "جيكور حزبة .2": "11", "باب ميدان": "12", 
    # 🔴 يرجى إضافة باقي المناطق لاحقاً إذا احتجتها
}

# ************************************************
# 🔴 دالة تنفيذ عملية إضافة الطلب (باستخدام Requests و CSRF)
# ************************************************
def perform_add_order(order_details: list, delivery_url: str):
    
    # البيانات الأساسية
    item_type = order_details[0].strip()    # نوع الطلبية
    price = order_details[1].strip()        # السعر
    area_name = order_details[2].strip()    # المنطقة
    phone_number = order_details[3].strip() # الرقم
    time_text = order_details[4].strip()    # الوقت
    city_id = AREA_IDS.get(area_name, "") 

    session = requests.Session()
    
    try:
        # 1. المرحلة الأولى: الحصول على الصفحة و CSRF Token
        headers = {
            'User-Agent': 'Mozilla/5.0', # 🔴 استخدام User-Agent يحاكي متصفح حقيقي
        }
        
        # 🔴 نحصل على الصفحة أولاً للحصول على الكود السري (Token)
        response_get = session.get(delivery_url, headers=headers)
        soup = BeautifulSoup(response_get.text, 'html.parser')
        
        # 🔴 البحث عن حقل CSRF Token (عادةً يكون input type="hidden")
        # هذا التخمين شائع جداً لمواقع الـ PHP والـ Laravel
        csrf_token_tag = soup.find('input', {'name': '_token'}) 
        
        if not csrf_token_tag:
             # إذا لم نجد التوكن، نعتبره غير موجود ونستمر
             csrf_token_value = ""
        else:
             csrf_token_value = csrf_token_tag.get('value', "")
        
        # 2. المرحلة الثانية: إرسال الطلب (POST Request) مع الكود السري
        
        # 🔴 البيانات اللي لازم يرسلها البوت للموقع:
        payload = {
            # 🔴 الكود السري للامان
            '_token': csrf_token_value,    
            
            # الحقول الأساسية
            'order_type': item_type,       
            'price': price,                
            'city_id': city_id,            
            'phone': phone_number,         
            'date_note': time_text,        
            
            # الحقول الثانوية
            'is_paid': "0",                 
            'phone2': "",                   
            'pic': "",                      
            'note': "",                     
            
            # زر الإضافة
            'addnew': 'اضافة الطلبية'      
        }
        
        # إرسال البيانات
        post_headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': delivery_url, # 🔴 مهم: نحدد صفحة المرجع لأمان الموقع
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response_post = session.post(delivery_url, data=payload, headers=post_headers)
        
        # فحص الرد:
        if response_post.status_code == 200:
            if "location.replace" in response_post.text or response_post.url != delivery_url:
                return "✅ تم إضافة الطلب بنجاح (الكود والبيانات صحيحة)."
            else:
                return f"❌ فشل: تم رفض البيانات أو CSRF Token غير صحيح. \n محتوى الرد: {response_post.text[:100]}..."
        else:
            return f"❌ فشل الإرسال. حالة الرد: {response_post.status_code}. "

    except Exception as e:
        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
