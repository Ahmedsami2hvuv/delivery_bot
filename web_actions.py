# الملف: web_actions.py (الإصدار النهائي والمدقق لـ CSRF)

import requests
from bs4 import BeautifulSoup
import json
import time

# قاموس لتحديد ID المنطقة بناءً على الاسم (باقي كما هو)
AREA_IDS = {
    "تقاطع جلاب": "1", "الاسمدة": "2", "محيلة السوق": "3", "جسر محيلة": "4", 
    "جيكور": "5", "ابو مغيرة": "6", "محيلة طريق المحطة": "7", "محيلة شارع الاندلس": "8", 
    "محيلة صفحة الشط": "9", "جيكور حزبة 1": "10", "جيكور حزبة .2": "11", "باب ميدان": "12", 
}

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
        # 1. المرحلة الأولى: الحصول على الصفحة و CSRF Token
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36', 
        }
        
        response_get = session.get(delivery_url, headers=headers)
        soup = BeautifulSoup(response_get.text, 'html.parser')
        
        # 🔴 البحث عن أي حقل إدخال مخفي (input type=hidden) في الصفحة
        csrf_token_tag = soup.find('input', {'type': 'hidden'})
        
        if not csrf_token_tag:
             # في حال عدم وجود حقل مخفي، نخمن الاسم "_token"
             csrf_token_value = ""
             csrf_token_name = "_token" 
        else:
             csrf_token_value = csrf_token_tag.get('value', "")
             # ⬅️ الحصول على الاسم الحقيقي للحقل المخفي (مثل: 'csrf-token' أو '_token')
             csrf_token_name = csrf_token_tag.get('name', "_token") 
        
        # 2. المرحلة الثانية: إرسال الطلب (POST Request)
        
        # البيانات اللي لازم يرسلها البوت للموقع:
        payload = {
            # 🔴 استخدام اسم الحقل المستخرج (أو _token كتخمين)
            csrf_token_name: csrf_token_value,    
            
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
        response_post = session.post(delivery_url, data=payload, headers=headers)
        
        # فحص الرد:
        if response_post.status_code == 200:
            # 🔴 التحقق الأكيد من النجاح: إذا تم التحويل (Redirect) إلى صفحة أخرى بعد الإرسال
            if response_post.url != delivery_url:
                return "✅ تم إضافة الطلب بنجاح (تم رصد تحويل في الرابط)."

            # إذا لم يتم التحويل، هذا يعني فشل بالرغم من الرد 200
            if "CSRF token mismatch" in response_post.text:
                return f"❌ فشل: CSRF Token غير مطابق. يرجى مراجعة المبرمج."
            
            # 🔴 إذا كان الرد 200 ولا يوجد تحويل، ووجد رسالة نجاح، فهذا فشل صامت
            elif "location.replace" in response_post.text or "تمت العملية بنجاح" in response_post.text:
                return f"❌ فشل صامت: الموقع رد برسالة نجاح ({response_post.status_code}) لكن لم يتم إنشاء الطلب. السبب غالباً: حقل بيانات مفقود."
            
            else:
                return f"❌ فشل الإرسال: الرد 200 لكن لا توجد إشارة نجاح أو تحويل. هذا يعني فشل في التحقق من البيانات."

        else:
            return f"❌ فشل الإرسال. حالة الرد: {response_post.status_code}. "

    except Exception as e:
        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
