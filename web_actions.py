# الملف: web_actions.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# هاي الدالة تهيئ المتصفح حتى يشتغل على الريلوي
def setup_selenium_driver():
    """تهيئة متصفح Chrome للعمل بوضع Headless (بدون واجهة) بالريلوي."""
    
    # خيارات تشغيل الكروم
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # ننصب الكروم درايفر ونشغله مباشرة
    service = Service(ChromeDriverManager().install())
    
    # ننشئ المتصفح
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

# دالة الدخول للموقع الهدف (المفروض هنا تخلي اليوزر والباسوورد)
def login_and_get_title(username, password, login_url):
    driver = None
    try:
        # 1. تشغيل المتصفح
        driver = setup_selenium_driver()
        driver.get(login_url) # يفتح صفحة الدخول
        
        # 🔴 ملاحظة: هنا لازم نكتب كود خاص حتى يملي حقول اليوزر والباسوورد ويدوس زر الدخول. 
        # (راح نبرمجه بالتفصيل ورا ما نتأكد إن البوت اشتغل)
        
        # مثال على قراءة العنوان:
        title = driver.title 
        
        return f"✅ تم الدخول بنجاح. عنوان الصفحة: {title}"

    except Exception as e:
        return f"❌ فشل الدخول أو صار خطأ: {e}"
        
    finally:
        # التأكد من سد المتصفح حتى لا تتراكم العمليات بالريلوي
        if driver:
            driver.quit()

# ممكن نضيف هنا دوال ثانية مثل:
# def add_new_order(driver, details):
#    # ... كود إضافة طلب ...
# def search_order_by_id(driver, order_id):
#    # ... كود البحث ...
# ... إلخ

