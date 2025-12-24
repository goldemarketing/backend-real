import time
import re
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests

from realestate.models import Developer

class Command(BaseCommand):
    help = 'سحب المطورين بناءً على نمط الروابط الجديد (ID-Name)'

    def handle(self, *args, **kwargs):
        # إعدادات المتصفح (يفتح أمامك لترى النتائج)
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        
        # المصدر: الصفحة الرئيسية هي أغنى مكان بروابط المطورين
        url = "https://www.nawy.com/developer/"

        try:
            self.stdout.write(f"1. فتح الموقع: {url}")
            driver.get(url)

            self.stdout.write("2. جاري التمرير (Scroll) لتحميل كل الشعارات...")
            # نقوم بالنزول تدريجياً لأسفل الصفحة لتحميل الصور (Lazy Loading)
            for i in range(1, 5):
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/5});")
                time.sleep(2)

            # البحث عن كل الروابط في الصفحة
            all_links = driver.find_elements(By.TAG_NAME, "a")
            self.stdout.write(f"3. فحص {len(all_links)} رابط...")

            count = 0
            processed_ids = set()

            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    
                    # الفلتر الذكي: نبحث عن النمط /developer/رقم-اسم
                    # Regex: يطابق /developer/ متبوعاً بأرقام ثم شرطة
                    if href and re.search(r'/developer/\d+-', href):
                        
                        # استخراج الـ ID والاسم من الرابط
                        # مثال: https://www.nawy.com/developer/8-sodic
                        parts = href.split('/developer/')[-1].split('-')
                        dev_id = parts[0]  # الرقم 8 (يمكنك تخزينه إذا أردت)
                        
                        # محاولة جلب الاسم والصورة
                        try:
                            img = link.find_element(By.TAG_NAME, "img")
                            img_src = img.get_attribute("src")
                            name = img.get_attribute("alt") # عادة يكون الاسم هنا "Sodic Logo"
                        except:
                            # لو مفيش صورة، نتجاهل الرابط
                            continue

                        # إذا لم نجد اسماً في الـ alt، نستخرجه من الرابط
                        if not name:
                            raw_slug = href.split(f'{dev_id}-')[-1] # يأخذ ما بعد الرقم
                            name = raw_slug.replace('-', ' ').title()

                        # تنظيف البيانات
                        name = name.replace("Logo", "").replace("logo", "").strip()
                        if not name or not img_src: continue

                        # إنشاء Slug نظيف (بدون الـ ID) ليكون موقعك أنت أجمل من ناوي
                        # موقعك سيكون: /developer/sodic (بدون رقم 8)
                        slug = slugify(name)

                        if slug in processed_ids: continue
                        processed_ids.add(slug)

                        # الحفظ في قاعدة البيانات
                        developer, created = Developer.objects.get_or_create(
                            slug=slug,
                            defaults={'name': name}
                        )

                        if created:
                            self.stdout.write(f"   [+] تم العثور على: {name} (ID في ناوي: {dev_id})")
                            
                            # تحميل اللوجو
                            try:
                                r = requests.get(img_src, timeout=10)
                                if r.status_code == 200:
                                    # تحديد الامتداد
                                    ext = "jpg"
                                    if "svg" in img_src: ext = "svg"
                                    elif "png" in img_src: ext = "png"
                                    
                                    file_name = f"{slug}.{ext}"
                                    developer.logo.save(file_name, ContentFile(r.content), save=True)
                            except Exception as img_err:
                                self.stdout.write(self.style.WARNING(f"فشل تحميل صورة {name}"))

                            count += 1

                except Exception:
                    continue

            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"تم بنجاح! تمت إضافة {count} مطور من الصفحة الرئيسية."))
            else:
                self.stdout.write(self.style.WARNING("العدد 0. ربما يحتاج الموقع لوقت تحميل أطول، أو الروابط تغيرت."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"خطأ: {e}"))
        
        finally:
            driver.quit()