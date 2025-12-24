from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# تأكد من اسم التطبيق (listings)
from realestate.models import Location

class Command(BaseCommand):
    help = 'Scrape all Locations from Nawy Area Page'

    def handle(self, *args, **kwargs):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_argument("--headless") # شيل العلامة لو عايز تخفي المتصفح
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            url = "https://www.nawy.com/area"
            self.stdout.write(f"🌍 Opening Locations Page: {url}")
            driver.get(url)
            time.sleep(5)

            # سكرول عشان يحمل كل المناطق
            self.stdout.write("📜 Scrolling to load all areas...")
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # البحث عن كروت المناطق
            # المناطق في الصفحة دي عادة بتكون جوه روابط href="/area/..."
            area_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/area/']")
            
            self.stdout.write(f"🔎 Found {len(area_links)} potential areas.")
            
            count = 0
            for link in area_links:
                try:
                    name = link.text.strip()
                    href = link.get_attribute('href')

                    # تنظيف الاسم: أحياناً الاسم بيجي معاه عدد الكمبوندات (مثلاً: New Cairo 231 Compounds)
                    # إحنا عايزين الاسم بس، فبناخد أول سطر أو بنفصل عند الأرقام
                    if "\n" in name:
                        name = name.split("\n")[0]
                    
                    # فلترة إضافية
                    if name and len(name) > 2 and "Compounds" not in name:
                        obj, created = Location.objects.get_or_create(
                            name=name,
                            defaults={'map_url': href} # بنحفظ رابط المنطقة في الـ map_url مؤقتاً
                        )
                        if created:
                            self.stdout.write(f"   ✅ Added: {name}")
                            count += 1
                        else:
                            self.stdout.write(f"   ⚠️ Exists: {name}")
                except Exception as e:
                    pass

            self.stdout.write(self.style.SUCCESS(f"🎉 Done! Added {count} new locations."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Fatal Error: {e}"))
        
        finally:
            driver.quit()