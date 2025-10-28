# الملف: web_actions.py

import requests
from bs4 import BeautifulSoup
import json
import time

# قاموس لتحديد ID المنطقة بناءً على الاسم (مطلوب لـ Select Box)
AREA_IDS = {
    "تقاطع جلاب": "1", "الاسمدة": "2", "محيلة السوق": "3", "جسر محيلة": "4", 
    "جيكور": "5", "ابو مغيرة": "6", "محيلة طريق المحطة": "7", "محيلة شارع الاندلس": "8", 
    "محيلة صفحة الشط": "9", "جيكور حزبة 1": "10", "جيكور حزبة .2": "11", "باب ميدان": "12", 
}

def perform_add_order(order_details: list, delivery_url: str):
    
    # البيانات الأساسية
    item_type = order_details[0].strip()    # نوع الطلبية
    price = order_details[1].strip()        # السعر
    area_name = order_details[2].strip()    # المنطقة
    phone_number = order_details[3].strip() # الرقم
    time_text = order_details[4].strip()    # الوقت
    city_id = AREA_IDS.get(area_name, "") # ID المنطقة
    
    session = requests.Session()
    
    try:
        # 1. المرحلة الأولى: الحصول على الصفحة و CSRF Token
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36', 
        }
        
        # 🔴 الحصول على الصفحة لإنشاء الجلسة واستخراج التوكن
        response_get = session.get(delivery_url, headers=headers)
        soup = BeautifulSoup(response_get.text, 'html.parser')
        
        # 🔴 البحث عن أي حقل إدخال مخفي (input type=hidden) في الصفحة
        csrf_token_tag = soup.find('input', {'type': 'hidden'})
        
        if not csrf_token_tag:
             csrf_token_value = ""
        else:
             csrf_token_value = csrf_token_tag.get('value', "")
        
        # 2. المرحلة الثانية: إرسال الطلب (POST Request) مع الكود السري
        
        # البيانات اللي لازم يرسلها البوت للموقع:
        payload = {
            # 🔴 الكود السري للامان (نرسله باسم _token)
            '_token': csrf_token_value,    
            
            # الحقول الأساسية (الأسماء الحقيقية)
            'order_type': item_type,       
            'price': price,                
            'city_id': city_id,            # 🔴 نرسل ID المنطقة فقط (الحل النهائي)
            'phone': phone_number,         
            'date_note': time_text,        
            
            # الحقول الثانوية (التي يجب إرسالها بقيمة)
            'is_paid': "0",                 # كل شيء واصل؟ (لا)
            'phone2': "",                   # رقم هاتف ثاني
            'pic': "",                      # صورة الطلبية
            'note': "",                     # ملاحظات
            
            # زر الإضافة
            'addnew': 'اضافة الطلبية'      
        }
        
        # إرسال البيانات (بدون headers إضافية غير User-Agent)
        response_post = session.post(delivery_url, data=payload, headers=headers)
        
        # فحص الرد:
        if response_post.status_code == 200:
            if "location.replace" in response_post.text or "تمت العملية بنجاح" in response_post.text:
                return "✅ تم إضافة الطلب بنجاح (الكود والبيانات صحيحة)."
            else:
                # إذا فشل الـ Token، الموقع يرد برسالة فشل تحتوي على كود خطأ (مثل 419)
                if "CSRF token mismatch" in response_post.text:
                     return f"❌ فشل: CSRF Token غير مطابق. يرجى مراجعة المبرمج."
                else:
                    return f"❌ فشل: تم رفض البيانات من قبل الموقع. يرجى مراجعة بياناتك."
        else:
            return f"❌ فشل الإرسال. حالة الرد: {response_post.status_code}. "

    except Exception as e:
        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
