# الملف: web_actions.py (الإصدار النهائي مع تسجيل الدخول)

import requests
from bs4 import BeautifulSoup
import json
import time

# 🔴 معلومات الدخول (راح نجيبها من متغيرات البيئة)
import os 
LOGIN_URL = os.environ.get("LOGIN_URL", "https://d.ksebstor.site/login")
WEB_USERNAME = os.environ.get("WEB_USERNAME")
WEB_PASSWORD = os.environ.get("WEB_PASSWORD")


# قاموس لتحديد ID المنطقة بناءً على الاسم (باقي كما هو)
AREA_IDS = {
    "تقاطع جلاب": "1", "الاسمدة": "2", "محيلة السوق": "3", "جسر محيلة": "4", 
    "جيكور": "5", "ابو مغيرة": "6", "محيلة طريق المحطة": "7", "محيلة شارع الاندلس": "8", 
    "محيلة صفحة الشط": "9", "جيكور حزبة 1": "10", "جيكور حزبة .2": "11", "باب ميدان": "12", 
}

# ************************************************
# 🔴 دالة جديدة: تسجيل الدخول والحصول على جلسة عمل قوية
# ************************************************
def login_user(session, username, password, login_url):
    
    # 1. المرحلة الأولى: فتح صفحة الدخول للحصول على CSRF Token
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # نفتح الصفحة أولاً للحصول على الكوكيز والـ CSRF Token
    response_get = session.get(login_url, headers=headers)
    soup = BeautifulSoup(response_get.text, 'html.parser')
    
    # 🔴 استخراج CSRF Token من أي حقل مخفي في صفحة الدخول
    csrf_tag = soup.find('input', {'type': 'hidden'})
    csrf_token = csrf_tag.get('value', "") if csrf_tag else ""
    csrf_name = csrf_tag.get('name', "_token") if csrf_tag else "_token"
    
    # 2. المرحلة الثانية: إرسال بيانات الدخول
    login_payload = {
        csrf_name: csrf_token,             # كود الأمان
        'username': username,              # 🔴 اسم حقل اليوزر نيم (تخمين)
        'password': password,              # 🔴 اسم حقل الباسوورد (تخمين)
        'login': 'تسجيل الدخول'            # 🔴 اسم زر الدخول (تخمين)
    }
    
    response_post = session.post(login_url, data=login_payload, headers=headers, allow_redirects=False)

    # 3. فحص نجاح الدخول (عادةً الرد يكون 302 ويحول للوحة القيادة)
    if response_post.status_code == 302 and 'dashboard' in response_post.headers.get('Location', ''):
        return True
    else:
        # إذا رجع 200 أو 302 بس بدون تحويل صحيح، فالدخول فشل
        return False


# ************************************************
# 🔴 دالة تنفيذ عملية إضافة الطلب (مع تسجيل الدخول)
# ************************************************
def perform_add_order(order_details: list, delivery_url: str):
    
    # البيانات الأساسية
    item_type = order_details[0].strip()    
    price = order_details[1].strip()        
    area_name = order_details[2].strip()    
    phone_number = order_details[3].strip() 
    time_text = order_details[4].strip()    
    city_id = AREA_IDS.get(area_name, "") 

    session = requests.Session()
    
    try:
        # 1. تسجيل الدخول أولاً (الحصول على الكوكيز القوية)
        if not login_user(session, WEB_USERNAME, WEB_PASSWORD, LOGIN_URL):
             return "❌ فشل الدخول: لم يتمكن البوت من تسجيل الدخول إلى لوحة القيادة."

        # 2. المرحلة الثانية: الحصول على صفحة الإضافة مع كوكيز الإدارة
        headers = {'User-Agent': 'Mozilla/5.0'}
        response_get = session.get(delivery_url, headers=headers)
        soup = BeautifulSoup(response_get.text, 'html.parser')
        
        # 3. استخراج CSRF Token من صفحة الإضافة (هذه المرة بوجود كوكيز الإدارة)
        csrf_token_tag = soup.find('input', {'type': 'hidden'})
        
        if not csrf_token_tag:
             csrf_token_value = ""
             csrf_token_name = "_token" 
        else:
             csrf_token_value = csrf_token_tag.get('value', "")
             csrf_token_name = csrf_token_tag.get('name', "_token") 
        
        # 4. إرسال الطلب (POST Request)
        
        payload = {
            csrf_token_name: csrf_token_value,    
            'order_type': item_type,       
            'price': price,                
            'city_id': city_id,            
            'phone': phone_number,         
            'date_note': time_text,        
            'is_paid': "0", 'phone2': "", 'pic': "", 'note': "", 'addnew': 'اضافة الطلبية'      
        }
        
        # إرسال البيانات
        response_post = session.post(delivery_url, data=payload, headers=headers)
        
        # فحص الرد:
        if response_post.status_code == 200:
            if response_post.url != delivery_url and "client_order" in response_post.url:
                return "✅ تم إضافة الطلب بنجاح (تم التحقق من خلال جلسة الإدارة)."
            
            else:
                return "❌ فشل: تم قبول الرد (200) لكن الطلب لم يُسجل. يرجى مراجعة أسماء حقول الدخول."
        else:
            return f"❌ فشل الإرسال. حالة الرد: {response_post.status_code}. "

    except Exception as e:
        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
