from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms import TextInput, Textarea
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import (
    Developer, Location, Amenity, Compound, Property, PropertyImage, 
    Author, BlogPost, Partner, Testimonial, ContactFormSubmission
)

# Inline classes for related objects
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'alt_text')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"

class PropertyInline(admin.TabularInline):
    model = Property
    extra = 0
    fields = ('title', 'property_type', 'price', 'area', 'bedrooms', 'bathrooms', 'is_featured', 'is_new_launch')
    readonly_fields = ('title', 'property_type', 'price', 'area', 'bedrooms', 'bathrooms')

# Developer Admin
@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'projects_count', 'description_preview')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    list_filter = ('name',)
    readonly_fields = ('slug', 'projects_count', 'logo_preview')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.logo
            )
        return "No logo"

    def description_preview(self, obj):
        if obj.description:
            return obj.description[:100] + "..." if len(obj.description) > 100 else obj.description
        return "No description"

    def projects_count(self, obj):
        return obj.compound_set.count()
    projects_count.short_description = "Projects"

# Location Admin
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'map_url')
    list_display_links = ('name',)
    search_fields = ('name',)
    readonly_fields = ('slug',)
# Compund  Admin
@admin.register(Compound)
class CompoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'location', 'min_price', 'delivery_date')
    list_filter = ('developer', 'location', 'delivery_date')
    search_fields = ('name', 'developer__name')
    
    # تنظيم الحقول في مجموعات (Fieldsets) عشان شكلها يبقى حلو
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'developer', 'location', 'status')
        }),
        ('Financial & Delivery', {
            'fields': ('min_price', 'max_installment_years', 'delivery_date')
        }),
        ('Details', {
            'fields': ('main_image', 'description', 'amenities')
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
# Amenity Admin
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Compound Admin
#@admin.register(Compound)
#class CompoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'location', 'status', 'delivery_date', 'main_image_preview', 'properties_count')
    list_display_links = ('name',)
    list_filter = ('status', 'location', 'developer', 'delivery_date')
    search_fields = ('name', 'description')
    raw_id_fields = ('location', 'developer')
    readonly_fields = ('slug', 'main_image_preview', 'properties_count')
    inlines = [PropertyInline]
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }

    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.main_image.url
            )
        return "No image"

    def properties_count(self, obj):
        return obj.property_set.count()
    properties_count.short_description = "Properties"

# Property Admin
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'compound', 'property_type', 'price', 'area', 'bedrooms', 'bathrooms', 
                   'main_image_preview', 'is_featured', 'is_new_launch', 'created_at')
    list_display_links = ('title',)
    list_filter = ('property_type', 'compound', 'developer', 'location', 'bedrooms', 'bathrooms', 
                  'is_featured', 'is_new_launch')
    search_fields = ('title', 'description')
    raw_id_fields = ('compound', 'developer', 'location')
    readonly_fields = ('slug', 'main_image_preview', 'floor_plan_preview', 'map_preview')
    inlines = [PropertyImageInline]
    list_per_page = 20
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'compound', 'developer', 'location', 'property_type')
        }),
        ('Property Details', {
            'fields': ('price', 'area', 'bedrooms', 'bathrooms', 'description')
        }),
        ('Images', {
            'fields': ('main_image', 'main_image_preview', 'floor_plan_image', 'floor_plan_preview', 
                      'map_image', 'map_preview')
        }),
        ('Features', {
            'fields': ('is_new_launch', 'is_featured', 'amenities')
        }),
    )

    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.main_image.url
            )
        return "No image"

    def floor_plan_preview(self, obj):
        if obj.floor_plan_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.floor_plan_image.url
            )
        return "No floor plan"

    def map_preview(self, obj):
        if obj.map_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.map_image.url
            )
        return "No map"

    def created_at(self, obj):
        return obj.id  # Using ID as a proxy for creation order
    created_at.short_description = "ID"

# Property Image Admin
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image_preview', 'alt_text')
    list_filter = ('property',)
    raw_id_fields = ('property',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"

# Author Admin
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'picture_preview')
    search_fields = ('name',)
    readonly_fields = ('picture_preview',)

    def picture_preview(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.picture.url
            )
        return "No picture"

# Blog Post Admin
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish_date', 'status', 'image_preview')
    list_filter = ('status', 'author', 'publish_date')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish_date'
    readonly_fields = ('slug', 'publish_date', 'image_preview')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Publishing', {
            'fields': ('publish_date',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.image
            )
        return "No image"

# Partner Admin
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview')
    search_fields = ('name',)
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: contain;" />',
                obj.logo
            )
        return "No logo"

# Testimonial Admin
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'rating', 'quote_preview', 'avatar_preview')
    list_filter = ('rating',)
    search_fields = ('client_name', 'quote')
    readonly_fields = ('avatar_preview',)

    def quote_preview(self, obj):
        if obj.quote:
            return obj.quote[:100] + "..." if len(obj.quote) > 100 else obj.quote
        return "No quote"

    def avatar_preview(self, obj):
        if obj.client_avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.client_avatar
            )
        return "No avatar"

# Contact Form Submission Admin
@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'submitted_at', 'message_preview')
    list_filter = ('submitted_at',)
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('submitted_at', 'message_preview')
    list_per_page = 20

    def message_preview(self, obj):
        if obj.message:
            return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message
        return "No message"

    def has_add_permission(self, request):
        return False  # Contact submissions are created via the form

# Customize admin site
admin.site.site_header = "4 Seasons Real Estate - Admin"
admin.site.site_title = "Real Estate Admin"
admin.site.index_title = "Welcome to Real Estate Administration"