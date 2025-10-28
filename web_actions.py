# الملف: web_actions.py (التعديل النهائي لزر إضافة طلبية)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys # لاستخدام زر Enter مثلاً
import time

# (دالة setup_selenium_driver تبقى كما هي)
def setup_selenium_driver():
    """تهيئة متصفح Chrome للعمل بوضع Headless (بدون واجهة) بالريلوي."""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=ar") 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # نحدد وقت انتظار للصفحة بشكل عام
    driver.implicitly_wait(10)
    
    return driver

# دالة تنفيذ عملية إضافة الطلب
def perform_add_order(order_details: list, delivery_url: str):
    driver = None
    try:
        # 1. تهيئة وتشغيل المتصفح
        driver = setup_selenium_driver()
        driver.get(delivery_url)
        
        # الانتظار لحد ما الحقول تظهر (50 ثانية كحد أقصى)
        wait = WebDriverWait(driver, 50) 
        
        # تفاصيل الطلب حسب الترتيب اللي حددناه:
        item_type = order_details[0].strip()    # النوع (مسواك)
        price = order_details[1].strip()        # السعر (12)
        area_name = order_details[2].strip()    # المنطقة (جيكور)
        phone_number = order_details[3].strip() # الرقم (077...)
        time_text = order_details[4].strip()    # الوقت (هسه)
        
        # **********************************************************************************
        # 2. ملء حقول النصوص (باستخدام XPATH التخميني اللي صار دقيق)
        # **********************************************************************************
        
        # حقل نوع الطلبية (Type of Order) - (الحقل الأول)
        type_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='نوع الطلبية *']/following-sibling::input")))
        type_input.send_keys(item_type)
        
        # حقل سعر الطلبية بدون التوصيل (Price) - (الحقل الثاني)
        price_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='سعر الطلبية بدون التوصيل']/following-sibling::input")))
        price_input.send_keys(price)

        # **********************************************************************************
        # 3. التعامل مع خانة المنطقة
        # **********************************************************************************
        
        # أ. إيجاد حقل البحث عن المنطقة (المكتوب بي 'اختر للبحث عن المنطقة')
        area_search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='اختر للبحث عن المنطقة']")))
        area_search_input.send_keys(area_name) 
        
        # ب. الانتظار لظهور خيار المنطقة (يظهر بخط عريض، مثلاً 'جيكور')
        # نستخدم الـ XPATH اللي يبحث عن العنصر النصي اللي يحمل اسم المنطقة
        # ممكن يكون العنصر اللي يظهر هو (li) أو (div) فنجربه على li بالبداية
        area_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[text()='{area_name}']")))
        area_option.click() # اختيار المنطقة
        
        # **********************************************************************************
        # 4. ملء باقي الحقول
        # **********************************************************************************
        
        # حقل رقم الهاتف
        phone_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='رقم الهاتف *']/following-sibling::input")))
        phone_input.send_keys(phone_number)
        
        # حقل وقت الطلبية
        time_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='وقت الطلبية *']/following-sibling::input")))
        time_input.send_keys(time_text)
        
        # **********************************************************************************
        # 5. النقر على زر الإضافة
        # **********************************************************************************
        
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='إضافة الطلبية']")))
        submit_button.click()
        
        # 6. انتظار رسالة التأكيد (ممكن يحول لصفحة سجل الطلبات)
        # بما إننا ما نعرف بالضبط شنو اللي يصير بعد الضغط، نرجع رسالة نجاح مبدئية
        # إذا فشل، الـ wait راح يفشل ويطلع الـ Except
        
        success_message = "✅ تم محاولة إضافة الطلب بنجاح. يرجى مراجعة الموقع للتأكد." 
        
        return success_message

    except Exception as e:
        return f"❌ صار خطأ أثناء إدخال الطلب (XPath/انتظار): {e}"
        
    finally:
        if driver:
            driver.quit()

# دالة dummy للمحافظة على بنية الكود (سنحتاجها للزر الثاني)
def perform_order_action():
    return "هذه الدالة موجودة فقط للحفاظ على الربط بـ bot.py. سنستخدم دالة perform_add_order."
