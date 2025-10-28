# الملف: web_actions.py (الإصدار النهائي لحل CSRF)

import requests
from bs4 import BeautifulSoup
import json
import time

# قاموس لتحديد ID المنطقة بناءً على الاسم (مطلوب لـ Select Box)
AREA_IDS = {
    # ... (باقي المناطق) ...
    "تقاطع جلاب": "1", "الاسمدة": "2", "محيلة السوق": "3", "جسر محيلة": "4", 
    "جيكور": "5", "ابو مغيرة": "6", "محيلة طريق المحطة": "7", "محيلة شارع الاندلس": "8", 
    "محيلة صفحة الشط": "9", "جيكور حزبة 1": "10", "جيكور حزبة .2": "11", "باب ميدان": "12", 
}

def perform_add_order(order_details: list, delivery_url: str):
    
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
            'User-Agent': 'Mozilla/5.0', 
        }
        
        response_get = session.get(delivery_url, headers=headers)
        soup = BeautifulSoup(response_get.text, 'html.parser')
        
        # 🔴 البحث الأكيد عن CSRF Token ضمن الـ FORM
        # البحث عن أي input مخفي داخل الـ form اللي method=POST (هذا هو الأصح)
        csrf_token_tag = soup.find('form', method='POST').find('input', {'type': 'hidden'})
        
        if not csrf_token_tag:
             # إذا لم نجد الـ token، نفترض أنه قد يكون ضمن name=_token (التخمين القديم)
             csrf_token_tag = soup.find('input', {'name': '_token'}) 
             if not csrf_token_tag:
                 csrf_token_value = ""
             else:
                 csrf_token_value = csrf_token_tag.get('value', "")
        else:
            # 🔴 إذا وجدنا الـ input المخفي، نأخذ القيمة مالته
             csrf_token_value = csrf_token_tag.get('value', "")

        # 2. المرحلة الثانية: إرسال الطلب (POST Request) مع الكود السري
        
        payload = {
            # 🔴 الكود السري للامان (نرسله باسم _token)
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
            'Referer': delivery_url,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response_post = session.post(delivery_url, data=payload, headers=post_headers)
        
        # فحص الرد:
        if response_post.status_code == 200:
            if "location.replace" in response_post.text:
                return "✅ تم إضافة الطلب بنجاح (الكود والبيانات صحيحة)."
            else:
                # 🔴 إذا الـ Token فشل، الموقع يرد برسالة فشل تحتوي على كود خطأ (مثل 419)
                if "CSRF token mismatch" in response_post.text:
                     return f"❌ فشل: CSRF Token غير مطابق. يرجى مراجعة المبرمج."
                elif response_post.url != delivery_url:
                     return "✅ تم إضافة الطلب بنجاح (الكود والبيانات صحيحة)."
                else:
                    return f"❌ فشل: تم رفض البيانات من قبل الموقع. يرجى مراجعة بياناتك."
        else:
            return f"❌ فشل الإرسال. حالة الرد: {response_post.status_code}. "

    except Exception as e:
        return f"❌ صار خطأ أثناء إرسال الطلب: {e}"
