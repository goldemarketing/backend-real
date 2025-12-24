from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# استيراد الموديلات (تأكد أن اسم التطبيق listings)
from realestate.models import Developer, Compound, Location

class Command(BaseCommand):
    help = 'Scrape Developers and Compounds from Nawy'

    def handle(self, *args, **kwargs):
        # إعدادات المتصفح
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            # سنزور صفحة البحث لأنها تحتوي على فلاتر وقوائم كثيرة
            url = "https://www.nawy.com/search"
            print(f"1. Opening {url}...")
            driver.get(url)

            print("2. Waiting for page to load (scrolling to get more data)...")
            time.sleep(5)
            
            # نقوم بعمل Scroll لتحميل المزيد من البيانات في الصفحة
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            # ---------------------------------------------------------
            # أولاً: جلب المطورين (Developers)
            # ---------------------------------------------------------
            print("\n🔍 Scanning for Developers...")
            # نبحث عن الروابط التي تحتوي على كلمة developer في الرابط
            dev_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/real-estate-developer/']")
            
            for link in dev_links:
                try:
                    name = link.text.strip()
                    if name:
                        # حفظ المطور
                        dev_obj, created = Developer.objects.get_or_create(
                            name=name,
                            defaults={'description': f"Imported from Nawy. Link: {link.get_attribute('href')}"}
                        )
                        if created:
                            print(f"   ✅ New Developer: {name}")
                        else:
                            print(f"   Note: Developer {name} exists.")
                except:
                    pass

            # ---------------------------------------------------------
            # ثانياً: جلب الكمبوندات (Compounds)
            # ---------------------------------------------------------
            print("\n🔍 Scanning for Compounds...")
            # نبحث عن الروابط التي تحتوي على كلمة compound في الرابط
            comp_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/compound/']")
            
            # نحتاج لمطور افتراضي لربط الكمبوند به لو معرفناش نجيب المطور بتاعه
            default_dev, _ = Developer.objects.get_or_create(name="Unknown Developer")
            # نحتاج لموقع افتراضي
            default_loc, _ = Location.objects.get_or_create(name="Cairo")

            for link in comp_links:
                try:
                    name = link.text.strip()
                    href = link.get_attribute('href')
                    
                    if name and "compound" not in name.lower(): # تنظيف بسيط
                        # حفظ الكمبوند
                        # هنا بنربطه بمطور افتراضي مؤقتاً لحد ما ندخل نعدله
                        comp_obj, created = Compound.objects.get_or_create(
                            name=name,
                            defaults={
                                'developer': default_dev,
                                'location': default_loc,
                                'description': f"Compound imported from Nawy: {href}"
                            }
                        )
                        if created:
                            print(f"   ✅ New Compound: {name}")
                        else:
                            print(f"   Note: Compound {name} exists.")
                except:
                    pass

        except Exception as e:
            print(f"Fatal Error: {e}")
        
        finally:
            print("\nDone. Closing browser...")
            driver.quit()