# الملف: web_actions.py

import requests
from bs4 import BeautifulSoup
import time
import os

# 🔴 قراءة بيانات الدخول والرابط من متغيرات البيئة
LOGIN_URL = os.environ.get("LOGIN_URL", "https://d.ksebstor.site/login")
WEB_USERNAME = os.environ.get("WEB_USERNAME")
WEB_PASSWORD = os.environ.get("WEB_PASSWORD")
DELIVERY_URL = os.environ.get("URL") # رابط العميل

# قاموس لتحديد ID المنطقة بناءً على الاسم 
AREA_IDS = {
    "تقاطع جلاب": "1", "الاسمدة": "2", "محيلة السوق": "3", "جسر محيلة": "4", 
    "جيكور": "5", "ابو مغيرة": "6", "محيلة طريق المحطة": "7", "محيلة شارع الاندلس": "8", 
    "محيلة صفحة الشط": "9", "جيكور حزبة 1": "10", "جيكور حزبة .2": "11", "باب ميدان": "12", 
    # ... نكدر نضيف باقي المناطق حسب الحاجة
}


# ************************************************
# 1. دالة تسجيل الدخول والحصول على جلسة عمل قوية
# ************************************************
def login_user(session, username, password, login_url):
    
    # 1. الحصول على CSRF Token
    headers = {'User-Agent': 'Mozilla/5.0'}
    response_get = session.get(login_url, headers=headers)
    soup = BeautifulSoup(response_get.text, 'html.parser')
    
    # 🔴 استخراج CSRF Token (البحث داخل الـ formAuthentication)
    form_tag = soup.find('form', id='formAuthentication')
    csrf_tag = form_tag.find('input', {'type': 'hidden'}) if form_tag else None 
    
    csrf_token = csrf_tag.get('value', "") if csrf_tag else ""
    csrf_name = csrf_tag.get('name', "_token") if csrf_tag else "_token"
    
    # 2. إرسال بيانات الدخول
    login_payload = {
        csrf_name: csrf_token,             
        'username': username,             # ⬅️ الاسم الحقيقي المستخرج
        'password': password,             # ⬅️ الاسم الحقيقي المستخرج
        'btn_login': 'دخول'               # ⬅️ اسم الزر الحقيقي
    }
    
    # 3. محاولة الدخول
    response_post = session.post(login_url, data=login_payload, headers=headers, allow_redirects=False)

    # 4. فحص نجاح الدخول: الرد 302 وتحويل للوحة القيادة
    if response_post.status_code == 302 and 'dashboard' in response_post.headers.get('Location', ''):
        return True
    else:
        # إذا رجع 200 أو فشل التحويل (وهو فشل)
        return False
        
# ************************************************
# 2. دالة تنفيذ عملية إضافة الطلب (مع جلسة الإدارة)
# ************************************************
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
        # 1. تسجيل الدخول أولاً (الحصول على الكوكيز القوية)
        if not login_user(session, WEB_USERNAME, WEB_PASSWORD, LOGIN_URL):
             return "❌ فشل الدخول: لم يتمكن البوت من تسجيل الدخول (يرجى مراجعة اليوزر والباسوورد)."

        # 2. المرحلة الثانية: استخدام الجلسة القوية لإ        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
