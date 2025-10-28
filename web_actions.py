# الملف: web_actions.py (إلغاء تسجيل الدخول والتركيز على العميل)

import requests
from bs4 import BeautifulSoup
import time
import os

# 🔴 لم نعد نحتاج بيانات تسجيل الدخول
# LOGIN_URL = os.environ.get("LOGIN_URL", "https://d.ksebstor.site/login")
# WEB_USERNAME = os.environ.get("WEB_USERNAME")
# WEB_PASSWORD = os.environ.get("WEB_PASSWORD")

# قاموس لتحديد ID المنطقة بناءً على الاسم 
AREA_IDS = {
    "تقاطع جلاب": "1", "الاسمدة": "2", "محيلة السوق": "3", "جسر محيلة": "4", 
    "جيكور": "5", "ابو مغيرة": "6", "محيلة طريق المحطة": "7", "محيلة شارع الاندلس": "8", 
    "محيلة صفحة الشط": "9", "جيكور حزبة 1": "10", "جيكور حزبة .2": "11", "باب ميدان": "12", 
}


# ************************************************
# 🔴 دالة تنفيذ عملية إضافة الطلب (مع محاكاة العميل فقط)
# ************************************************
# دالة تسجيل الدخول محذوفة!
def perform_add_order(order_details: list, delivery_url: str):
    
    # البيانات الأساسية للطلب
    item_type = order_details[0].strip()    
    price = order_details[1].strip()        
    area_name = order_details[2].strip()    
    phone_number = order_details[3].strip() 
    time_text = order_details[4].strip()    
    city_id = AREA_IDS.get(area_name, "") 

    session = requests.Session()
    
    try:
        # 1. المرحلة الأولى: الحصول على الصفحة و CSRF Token
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36', 
        }
        
        # 🔴 فتح رابط العميل مباشرة (بدون تسجيل دخول)
        response_get = session.get(delivery_url, headers=headers)
        soup = BeautifulSoup(response_get.text, 'html.parser')
        
        # 2. استخراج CSRF Token من صفحة العميل
        # البحث عن أي حقل إدخال مخفي (input type=hidden) في الصفحة
        csrf_token_tag = soup.find('input', {'type': 'hidden'})
        
        if not csrf_token_tag:
             csrf_token_value = ""
             csrf_token_name = "_token" 
        else:
             csrf_token_value = csrf_token_tag.get('value', "")
             csrf_token_name = csrf_token_tag.get('name', "_token") 
        
        # 3. إرسال الطلب (POST Request)
        payload = {
            csrf_token_name: csrf_token_value,    
            'order_type': item_type,       
            'price': price,                
            'city_id': city_id,            
            'phone': phone_number,         
            'date_note': time_text,        
            
            # الحقول الثانوية
            'is_paid': "0", 'phone2': "", 'pic': "", 'note': "",                   
            
            # زر الإضافة
            'addnew': 'اضافة الطلبية'      
        }
        
        # إرسال البيانات
        response_post = session.post(delivery_url, data=payload, headers=headers)
        
        # 4. فحص الرد:
        if response_post.status_code == 200:
            if response_post.url != delivery_url and "client_order" in response_post.url:
                return "✅ تم إضافة الطلب بنجاح (تم التحويل بعد الإرسال)."
            
            else:
                return f"❌ فشل صامت: تم قبول الرد (200) لكن الطلب لم يُسجل. السبب غالباً: فشل CSRF أو بيانات مطلوبة."
        else:
            return f"❌ فشل الإرسال. حالة الرد: {response_post.status_code}. "

    except Exception as e:
        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
