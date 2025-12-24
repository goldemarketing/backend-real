from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # 1. Admin ViewSets
    UserViewSet, CompoundViewSet, DeveloperViewSet, LocationViewSet,
    PropertyViewSet, PropertyImageViewSet, BlogPostViewSet, AuthorViewSet,
    AmenityViewSet, ContactFormSubmissionViewSet, TestimonialViewSet, PartnerViewSet,

    # 2. Public ViewSets
    PublicCompoundViewSet, PublicDeveloperViewSet, PublicLocationViewSet,
    PublicPropertyViewSet, PublicBlogPostViewSet, PublicAuthorViewSet,
    PublicAmenityViewSet, PublicTestimonialViewSet, PublicPartnerViewSet,
    PublicContactFormSubmissionViewSet,

    # 3. Auth & Utils
    CustomAuthToken, CurrentUserView, image_upload_view
)

router = DefaultRouter()

# ==============================
# 1. ADMIN ROUTES
# ==============================
router.register(r'admin/users', UserViewSet)
router.register(r'admin/compounds', CompoundViewSet)
router.register(r'admin/developers', DeveloperViewSet)
router.register(r'admin/locations', LocationViewSet)
router.register(r'admin/properties', PropertyViewSet)
router.register(r'admin/property-images', PropertyImageViewSet)
router.register(r'admin/blog-posts', BlogPostViewSet)
router.register(r'admin/authors', AuthorViewSet)
router.register(r'admin/amenities', AmenityViewSet)
router.register(r'admin/contact-submissions', ContactFormSubmissionViewSet)
router.register(r'admin/testimonials', TestimonialViewSet)
router.register(r'admin/partners', PartnerViewSet)

# ==============================
# 2. PUBLIC ROUTES
# ==============================
router.register(r'public/compounds', PublicCompoundViewSet, basename='public-compound')
router.register(r'public/developers', PublicDeveloperViewSet, basename='public-developer')
router.register(r'public/locations', PublicLocationViewSet, basename='public-location')
router.register(r'public/properties', PublicPropertyViewSet, basename='public-property')
router.register(r'public/blog-posts', PublicBlogPostViewSet, basename='public-blogpost')
router.register(r'public/authors', PublicAuthorViewSet, basename='public-author')
router.register(r'public/amenities', PublicAmenityViewSet, basename='public-amenity')
router.register(r'public/testimonials', PublicTestimonialViewSet, basename='public-testimonial')
router.register(r'public/partners', PublicPartnerViewSet, basename='public-partner')
router.register(r'public/contact-submissions', PublicContactFormSubmissionViewSet, basename='public-contact-submission')

urlpatterns = [
    path('', include(router.urls)),
    
    # 👇👇 (1) رابط تسجيل الدخول
    path('auth/login/', CustomAuthToken.as_view(), name='auth_login'),
    
    # 👇👇 (2) الرابط الناقص الذي يسبب المشكلة (جلب بيانات المستخدم)
    path('auth/me/', CurrentUserView.as_view(), name='auth_me'),

    # روابط خدمية أخرى
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('current-user/', CurrentUserView.as_view(), name='current_user'),
    path('upload/', image_upload_view, name='image_upload'),
]