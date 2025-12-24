from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
import time

from .models import (
    Compound, Developer, Location, Property, PropertyImage,
    BlogPost, Author, Amenity, ContactFormSubmission,
    Testimonial, Partner, CompoundImage
)

# ==========================================
#  Helper Function: Build Absolute URL
# ==========================================
def get_full_image_url(image_field, request):
    if image_field and hasattr(image_field, 'url') and request:
        return request.build_absolute_uri(image_field.url)
    return None

# ==========================================
#  User & Helpers Serializers
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

# ==========================================
#  Developer Serializer (UPDATED)
# ==========================================
class DeveloperSerializer(serializers.ModelSerializer):
    # جعل الـ Slug اختياري لنتفادى خطأ 400
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = Developer
        fields = '__all__'

    # إصلاح روابط الصور
    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if hasattr(instance, 'logo') and instance.logo:
             response['logo'] = get_full_image_url(instance.logo, request)
        if hasattr(instance, 'image') and instance.image:
             response['image'] = get_full_image_url(instance.image, request)
        return response

    # توليد الـ Slug تلقائياً
    def to_internal_value(self, data):
        mutable_data = data.copy()
        if 'name' in mutable_data and not mutable_data.get('slug'):
             mutable_data['slug'] = slugify(mutable_data['name'], allow_unicode=True)
        return super().to_internal_value(mutable_data)

class AuthorSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if hasattr(instance, 'image') and instance.image:
             response['image'] = get_full_image_url(instance.image, request)
        return response
    class Meta:
        model = Author
        fields = '__all__'

class PartnerSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if hasattr(instance, 'logo') and instance.logo:
             response['logo'] = get_full_image_url(instance.logo, request)
        return response
    class Meta:
        model = Partner
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if hasattr(instance, 'image') and instance.image:
             response['image'] = get_full_image_url(instance.image, request)
        return response
    class Meta:
        model = Testimonial
        fields = '__all__'

class ContactFormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormSubmission
        fields = '__all__'

# ==========================================
#  Compound Serializer (Existing Fix)
# ==========================================
class CompoundImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CompoundImage
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        return get_full_image_url(obj.image, request)

class CompoundSerializer(serializers.ModelSerializer):
    images = CompoundImageSerializer(many=True, read_only=True)
    
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    # Make slug optional so validation passes, we generate it later
    slug = serializers.SlugField(required=False, allow_blank=True)
    
    # Use PrimaryKey for writing (saving IDs)
    amenities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Amenity.objects.all(), required=False
    )

    class Meta:
        model = Compound
        fields = '__all__'

    # 🔥 FIX: Override data processing BEFORE validation
    def to_internal_value(self, data):
        # Create a mutable copy of the data
        mutable_data = data.copy()

        # 1. Handle Amenities (Convert list of strings to list of integers)
        if 'amenities' in mutable_data:
            # Check if it's a list or needs distinct getlist (for FormData)
            items = mutable_data.getlist('amenities') if hasattr(mutable_data, 'getlist') else mutable_data.get('amenities')
            if items:
                # Filter and convert to integers
                valid_ids = [int(x) for x in items if str(x).isdigit()]
                mutable_data.setlist('amenities', valid_ids)

        # 2. Auto-generate Slug if missing
        if 'name' in mutable_data and not mutable_data.get('slug'):
            base_slug = slugify(mutable_data['name'], allow_unicode=True)
            if not base_slug: # If name implies empty slug (e.g. strict Arabic chars sometimes)
                 base_slug = f"compound-{int(time.time())}"
            mutable_data['slug'] = base_slug

        return super().to_internal_value(mutable_data)

    # 🔥 FIX: Override representation for Frontend Display
    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')

        # 1. Fix Image URLs
        if instance.main_image:
            response['main_image'] = get_full_image_url(instance.main_image, request)
        if hasattr(instance, 'map_image') and instance.map_image:
            response['map_image'] = get_full_image_url(instance.map_image, request)

        # 2. Return full Amenity objects instead of just IDs
        if instance.amenities.exists():
            response['amenities'] = AmenitySerializer(instance.amenities.all(), many=True).data
        else:
            response['amenities'] = []

        # 3. Expand related fields
        if instance.developer:
            response['developer'] = DeveloperSerializer(instance.developer, context=self.context).data
        if instance.location:
            response['location'] = LocationSerializer(instance.location).data

        return response

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        amenities = validated_data.pop('amenities', []) 

        compound = Compound.objects.create(**validated_data)

        if amenities:
            compound.amenities.set(amenities)

        for image in uploaded_images:
            CompoundImage.objects.create(compound=compound, image=image)
        
        return compound

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        amenities = validated_data.pop('amenities', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if amenities is not None:
            instance.amenities.set(amenities)

        for image in uploaded_images:
            CompoundImage.objects.create(compound=instance, image=image)
            
        return instance

# ==========================================
#  Property & Blog Serializers (Standard)
# ==========================================
class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'alt_text']
    def get_image(self, obj):
        request = self.context.get('request')
        return get_full_image_url(obj.image, request)

class PropertySerializer(serializers.ModelSerializer):
    gallery_images = PropertyImageSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'compound', 'developer', 'location',
            'property_type', 'price', 'area', 'bedrooms', 'bathrooms',
            'description', 'main_image', 'floor_plan_image', 'map_image',
            'is_new_launch', 'is_featured', 'amenities', 'gallery_images'
        ]
    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if instance.main_image: response['main_image'] = get_full_image_url(instance.main_image, request)
        if instance.floor_plan_image: response['floor_plan_image'] = get_full_image_url(instance.floor_plan_image, request)
        if instance.map_image: response['map_image'] = get_full_image_url(instance.map_image, request)
        
        if instance.compound:
            response['compound'] = {'id': instance.compound.id, 'name': instance.compound.name, 'slug': instance.compound.slug}
        if instance.developer:
            response['developer'] = DeveloperSerializer(instance.developer, context=self.context).data
        if instance.location:
            response['location'] = LocationSerializer(instance.location).data
        if instance.amenities.exists():
            response['amenities'] = AmenitySerializer(instance.amenities.all(), many=True).data
        return response

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        request = self.context.get('request')
        if hasattr(instance, 'image') and instance.image:
             response['image'] = get_full_image_url(instance.image, request)
        elif hasattr(instance, 'main_image') and instance.main_image:
             response['main_image'] = get_full_image_url(instance.main_image, request)
        if instance.author:
            response['author'] = AuthorSerializer(instance.author, context=self.context).data
        return response