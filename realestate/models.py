from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

# Create your models here.

class Developer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='developers/logos/', blank=True, null=True)
    description = RichTextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def projects_count(self):
        return self.compound_set.count()

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    map_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Compound(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    main_image = models.ImageField(upload_to='compounds/main_images/', blank=True, null=True)
    description = RichTextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    min_area = models.PositiveIntegerField(null=True, blank=True, help_text="Starting area in square meters")
    map_image = models.ImageField(upload_to='compounds/map_images/', blank=True, null=True)
    is_new_launch = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    video_url = models.URLField(blank=True, null=True, verbose_name="Video URL (YouTube)")
    # ===== الحقول الجديدة للفلاتر =====
    # 1. السعر المبدئي للمشروع
    min_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Starting price for the project")
    
    # 2. أقصى عدد سنوات تقسيط
    max_installment_years = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum installment years available")
    
    # 3. تاريخ الاستلام (تم تغييره لـ DateField لسهولة الفلترة)
    delivery_date = models.DateField(null=True, blank=True, help_text="Expected delivery date") 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Property(models.Model):
    PROPERTY_TYPES = [
        ('Apartment', 'Apartment'),
        ('Villa', 'Villa'),
        ('Chalet', 'Chalet'),
        ('Duplex', 'Duplex'),
        ('Studio', 'Studio'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    compound = models.ForeignKey(Compound, on_delete=models.SET_NULL, null=True, blank=True)
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    area = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    description = RichTextField()
    main_image = models.ImageField(upload_to='properties/main_images/', blank=True, null=True)
    floor_plan_image = models.ImageField(upload_to='properties/floor_plans/', blank=True, null=True)
    map_image = models.ImageField(upload_to='properties/map_images/', blank=True, null=True)
    is_new_launch = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    amenities = models.ManyToManyField(Amenity, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
class CompoundImage(models.Model):
    compound = models.ForeignKey(Compound, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='compounds/gallery/')

    def __str__(self):
        return f"Image for {self.compound.name}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='properties/gallery_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.property.title}"

class Author(models.Model):
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='authors/pictures/', blank=True, null=True)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('Published', 'Published'),
        ('Draft', 'Draft'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField()
    content = RichTextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Draft')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Partner(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/logos/')

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    client_avatar = models.ImageField(upload_to='testimonials/avatars/', blank=True, null=True)
    rating = models.PositiveIntegerField()
    quote = models.TextField()

    def __str__(self):
        return f"Testimonial by {self.client_name}"


class ContactFormSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact form submission from {self.name}"