# الملف: web_actions.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# تم حذف استيراد webdriver_manager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
import time

# ************************************************
# 🔴 دالة تهيئة المتصفح باستخدام المسار اليدوي 
# ************************************************
def setup_selenium_driver():
    """تهيئة متصفح Chrome للعمل بوضع Headless (بدون واجهة) على الريلوي باستخدام مسار يدوي."""
    
    # 🔴 المسار اللي ينصّب بيه أمر البناء الطويل الـ ChromeDriver
    CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver" 
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=ar") 
    
    # 🔴 استخدام المسار اليدوي
    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.implicitly_wait(10) # انتظار ضمني
    
    return driver

# ************************************************
# 🔴 دالة تنفيذ عملية إضافة الطلب (باستخدام XPATH الحقيقي)
# ************************************************
def perform_add_order(order_details: list, delivery_url: str):
    driver = None
    try:
        # 1. تهيئة وتشغيل المتصفح
        driver = setup_selenium_driver()
        driver.get(delivery_url)
        
        # الانتظار لحد ما الحقول تظهر (50 ثانية كحد أقصى)
        wait = WebDriverWait(driver, 50) 
        
        # تفاصيل الطلب اللي تجينا من التليجرام:
        item_type = order_details[0].strip()    # النوع (مسواك)
        price = order_details[1].strip()        # السعر (12)
        area_name = order_details[2].strip()    # المنطقة (جيكور)
        phone_number = order_details[3].strip() # الرقم (077...)
        time_text = order_details[4].strip()    # الوقت (هسه)
        
        # 2. ملء حقول النصوص (باستخدام XPATH الدقيق من الصور)
        
        # حقل نوع الطلبية (Type of Order) 
        type_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='نوع الطلبية *']/following-sibling::input")))
        type_input.send_keys(item_type)
        
        # حقل سعر الطلبية بدون التوصيل (Price) 
        price_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='سعر الطلبية بدون التوصيل']/following-sibling::input")))
        price_input.send_keys(price)

        # 3. التعامل مع خانة المنطقة
        
        # أ. إيجاد حقل البحث عن المنطقة (المكتوب بي 'اختر للبحث عن المنطقة')
        area_search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='اختر للبحث عن المنطقة']")))
        area_search_input.send_keys(area_name) 
        
        # ب. الانتظار لظهور خيار المنطقة والنقر عليه
        # (نبحث عن عنصر بالقائمة يحمل النص بالكامل)
        area_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[text()='{area_name}']")))
        area_option.click() 
        
        # 4. ملء باقي الحقول
        
        # حقل رقم الهاتف
        phone_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='رقم الهاتف *']/following-sibling::input")))
        phone_input.send_keys(phone_number)
        
        # حقل وقت الطلبية
        time_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='وقت الطلبية *']/following-sibling::input")))
        time_input.send_keys(time_text)
        
        # 5. النقر على زر الإضافة
        
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='إضافة الطلبية']")))
        submit_button.click()
        
        # 6. رسالة نجاح مبدئية
        success_message = "✅ تم محاولة إضافة الطلب بنجاح. يرجى مراجعة الموقع للتأكد." 
        
        return success_message

    except Exception as e:
        # إذا صار خطأ، نرجع رسالة الخطأ
        return f"❌ صار خطأ أثناء إدخال الطلب (XPath/انتظار): {e}"
        
    finally:
        if driver:
            driver.quit() # إغلاق المتصفح

# دالة dummy للمحافظة على بنية الكود (سنحتاجها للزر الثاني)
def perform_order_action():
    return "هذه الدالة موجودة فقط للحفاظ على الربط بـ bot.py. سنستخدم دالة perform_add_order."
