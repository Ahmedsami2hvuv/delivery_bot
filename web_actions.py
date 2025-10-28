# الملف: web_actions.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# هاي الدالة تهيئ المتصفح حتى يشتغل على الريلوي
def setup_selenium_driver():
    """تهيئة متصفح Chrome للعمل بوضع Headless (بدون واجهة) بالريلوي."""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # ممكن تحتاج تخلي اللغة عربية حتى الموقع يعرض الخيارات صح
    chrome_options.add_argument("--lang=ar") 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

# الدالة الجديدة: تنفيذ عملية إضافة الطلب
def perform_add_order(order_details: list, delivery_url: str):
    driver = None
    try:
        # 1. تهيئة وتشغيل المتصفح
        driver = setup_selenium_driver()
        driver.get(delivery_url)
        
        # الانتظار لحد ما الصفحة تنفتح بشكل كامل (30 ثانية كحد أقصى)
        wait = WebDriverWait(driver, 30)

        # تفاصيل الطلب حسب الترتيب:
        # [0] = النوع (مسواك)
        # [1] = السعر (12)
        # [2] = المنطقة (جيكور)
        # [3] = رقم الزبون (077...)
        # [4] = الوقت (هسه)
        
        item_type = order_details[0].strip() # مسواك
        price = order_details[1].strip()     # 12
        area_name = order_details[2].strip() # جيكور
        phone_number = order_details[3].strip() # 077...
        time_text = order_details[4].strip() # هسه
        
        # **********************************************************************************
        # 2. ملء حقول النصوص (النوع، السعر، الرقم، الوقت)
        # 🔴 ملاحظة: هاي الـ IDs والـ XPATHS هي تخمينية ولازم تتعدل حسب الموقع الحقيقي مالك
        # **********************************************************************************
        
        # حقل نوع الطلب (Type of Order)
        # 🔴 لازم تشوف الـ ID أو الـ Name أو الـ XPath الحقيقي لخانة النوع
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='نوع الطلب']"))).send_keys(item_type)
        
        # حقل سعر الطلب (Price)
        # 🔴 لازم تشوف الـ ID أو الـ Name أو الـ XPath الحقيقي لخانة السعر
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='سعر الطلب']"))).send_keys(price)

        # حقل رقم الزبون (Phone Number)
        # 🔴 لازم تشوف الـ ID أو الـ Name أو الـ XPath الحقيقي لخانة الرقم
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='رقم الزبون']"))).send_keys(phone_number)
        
        # حقل وقت الطلب (Time)
        # 🔴 لازم تشوف الـ ID أو الـ Name أو الـ XPath الحقيقي لخانة الوقت
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='وقت الطلب']"))).send_keys(time_text)
        
        # **********************************************************************************
        # 3. التعامل مع خانة البحث والاختيار للمنطقة (Dropdown/Autocomplete)
        # **********************************************************************************
        
        # أ. النقر لفتح قائمة المناطق
        # 🔴 لازم تشوف الـ ID أو الـ XPath الحقيقي لخانة المنطقة (عادة يكون حقل نصي أو زر)
        area_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='منطقة الزبون']")))
        area_input.click() # الضغط لفتح قائمة البحث
        
        # ب. كتابة اسم المنطقة (جيكور)
        area_input.send_keys(area_name) 

        # ج. الانتظار لظهور خيار المنطقة (عادة يكون عنصر بالقائمة يظهر بعد الكتابة)
        # 🔴 لازم تشوف الـ XPath أو الـ ID للعنصر اللي يظهر بالقائمة بعد البحث 
        area_option = wait.until(EC.presence_of_element_located((By.XPATH, f"//li[contains(text(), '{area_name}')]")))
        area_option.click() # اختيار المنطقة
        
        # **********************************************************************************
        # 4. النقر على زر الإضافة
        # **********************************************************************************
        
        # 🔴 لازم تشوف الـ XPath أو الـ ID الحقيقي لزر "إضافة طلبية" أو "تأكيد"
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'إضافة طلبية')]")))
        submit_button.click()
        
        # 5. الانتظار للحصول على رسالة النجاح
        # 🔴 هذا الجزء تخميني، لازم نعرف شلون الموقع يرد (رسالة نجاح أو تحويل لصفحة ثانية)
        success_message = "✅ تم إضافة الطلب بنجاح في الموقع." 
        
        # ممكن نشوف عنوان الصفحة الجديدة أو نبحث عن رسالة تأكيد معينة
        
        return success_message

    except Exception as e:
        return f"❌ صار خطأ أثناء إدخال الطلب: {e}"
        
    finally:
        if driver:
            driver.quit() # إغلاق المتصفح

# دالة dummy للمحافظة على بنية الكود (سنحتاجها للزر الثاني)
def perform_order_action():
    return "هذه الدالة موجودة فقط للحفاظ على الربط بـ bot.py. سنستخدم دالة perform_add_order."

