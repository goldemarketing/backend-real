from django.contrib import admin
from .models import (
    Developer, Location, Amenity, Compound, Property, 
    PropertyImage, BlogPost, Author, Partner, Testimonial, ContactFormSubmission, CompoundImage
)

# 1. Developer Admin
@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ('name', 'projects_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# 2. Location Admin
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# 3. Amenity Admin
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# --- تعريف الـ Inlines (الصور المتعددة) ---
# يجب تعريفها قبل استخدامها داخل الكلاسات الرئيسية

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class CompoundImageInline(admin.TabularInline):
    model = CompoundImage
    extra = 1

# 5. Compound Admin (تم إصلاح الأخطاء هنا)
@admin.register(Compound)
class CompoundAdmin(admin.ModelAdmin):
    # ربط صور الجاليري
    inlines = [CompoundImageInline]

    # القوائم التي تظهر في الجدول الخارجي
    list_display = ('name', 'developer', 'location', 'min_price', 'min_area', 'delivery_date', 'status', 'is_featured')
    
    # خيارات الفلترة والبحث
    list_filter = ('developer', 'location', 'status', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    # ترتيب الحقول داخل صفحة التعديل (تم دمج الحقول الناقصة)
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'developer', 'location', 'status', 'is_featured')
        }),
        ('Financial & Specs', {
            'fields': ('min_price', 'min_area', 'max_installment_years', 'delivery_date')
        }),
        ('Media & Details', {
            'fields': ('main_image', 'video_url', 'description', 'amenities')
        }),
    )
    
    # لتسهيل اختيار الـ Amenities الكثيرة
    filter_horizontal = ('amenities',)

# 6. Property Admin
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline]
    
    list_display = ('title', 'compound', 'price', 'property_type', 'is_featured')
    list_filter = ('property_type', 'is_featured', 'is_new_launch', 'compound', 'location')
    search_fields = ('title', 'compound__name', 'location__name')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('amenities',)

# 7. Blog & Author Admin
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'publish_date')
    list_filter = ('status', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

# 8. Other Admins
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'rating')

@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'submitted_at')
    readonly_fields = ('name', 'email', 'phone', 'message', 'submitted_at')
    list_filter = ('submitted_at',)