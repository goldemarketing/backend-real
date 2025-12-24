from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

# تأكد من اسم التطبيق (listings أو realestate)
from realestate.models import Property, Location, Developer 

class Command(BaseCommand):
    help = 'Scrape Nawy and Save to DB'

    def handle(self, *args, **kwargs):
        # إعدادات المتصفح
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
        # chrome_options.add_argument("--headless") # شيل الشباك لو عايز المتصفح مخفي
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            url = "https://www.nawy.com/search"
            print(f"1. Opening {url}...")
            driver.get(url)

            print("2. Waiting for data to load...")
            time.sleep(10) # انتظار التحميل

            # البحث عن الكروت (بناءً على الروابط لأن الكلاسات متغيرة)
            # بنجيب كل الروابط اللي بتودي على صفحة مشروع أو عقار
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/compound/'], a[href*='/property/']")
            
            print(f"-> Found {len(links)} items. Starting save process...")
            
            saved_count = 0
            
            # نستخدم set لمنع التكرار
            processed_urls = set()

            for link in links:
                try:
                    href = link.get_attribute('href')
                    title = link.text.strip()
                    
                    # لو الرابط مكرر أو العنوان فاضي (صورة مثلاً)، نتجاهله
                    if href in processed_urls or not title:
                        continue
                        
                    processed_urls.add(href)

                    # --- مرحلة الحفظ في قاعدة البيانات ---
                    # بنستخدم get_or_create عشان لو العقار موجود ميكرروش
                    property_obj, created = Property.objects.get_or_create(
                        title=title[:200], # نقص العنوان لو طويل اوي
                        defaults={
                            'price': random.randint(1000000, 5000000), # سعر تقريبي (لأننا مش عارفين نجيبه من بره)
                            'area': random.randint(100, 300),          # مساحة تقريبية
                            'bedrooms': random.randint(2, 4),
                            'bathrooms': random.randint(1, 3),
                            'property_type': 'Apartment',
                            'description': f"Unit from Nawy. Link: {href}",
                            'is_featured': False,
                            'is_new_launch': True
                        }
                    )

                    if created:
                        print(f"✅ Saved New: {title}")
                        saved_count += 1
                    else:
                        print(f"⚠️ Exists: {title}")

                except Exception as e:
                    print(f"Error saving item: {e}")

            print(f"------------------------------------------------")
            print(f"Job Done! Successfully saved {saved_count} properties.")

        except Exception as e:
            print(f"Fatal Error: {e}")
        
        finally:
            driver.quit()