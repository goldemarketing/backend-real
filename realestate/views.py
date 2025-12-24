from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth.models import User 
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, mixins , permissions
from rest_framework.views import APIView                  # <--- (1) هام
from rest_framework.permissions import IsAuthenticated    # <--- (2) هام
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters 
from rest_framework.decorators import action

from .models import (
    Compound, Developer, Location, Property, PropertyImage,
    BlogPost, Author, Amenity, ContactFormSubmission,
    Testimonial, Partner
)
from .serializers import (
    CompoundSerializer, DeveloperSerializer, LocationSerializer, 
    PropertySerializer, PropertyImageSerializer, BlogPostSerializer, 
    AuthorSerializer, AmenitySerializer, ContactFormSubmissionSerializer,
    TestimonialSerializer, PartnerSerializer, UserSerializer
)
from .filters import CompoundFilter 

# ==========================================
#  0. Authentication Views (Login & Current User)
# ==========================================

# 1. Login View
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# 2. Current User View (التي كانت ناقصة) 👇👇
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# ==========================================
#  1. Admin / Full Access ViewSets
# ==========================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CompoundViewSet(viewsets.ModelViewSet):
    queryset = Compound.objects.all()
    serializer_class = CompoundSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = CompoundFilter
    ordering_fields = ['min_price', 'delivery_date', 'id']
    ordering = ['-id']
@action(detail=True, methods=['get'])
def related(self, request, pk=None):
        current_compound = self.get_object()
        related = Compound.objects.filter(
            location=current_compound.location
        ).exclude(id=current_compound.id)

        if current_compound.min_price:
            min_range = current_compound.min_price * 0.8
            max_range = current_compound.min_price * 1.2
            related = related.filter(
                min_price__gte=min_range, 
                min_price__lte=max_range
            ) | related.filter(min_price__isnull=True)

        related = related.distinct()[:4]
        serializer = self.get_serializer(related, many=True)
        return Response(serializer.data)
class DeveloperViewSet(viewsets.ModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['name']

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = {
        'location': ['exact'],
        'property_type': ['exact'],
        'price': ['gte', 'lte'],
        'bedrooms': ['gte'],
        'compound': ['exact'],
        'developer': ['exact'],
        'is_featured': ['exact'],
        'is_new_launch': ['exact'],
    }
    search_fields = ['title', 'description', 'location__name', 'compound__name']

class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.filter(status='Published')
    serializer_class = BlogPostSerializer
    filter_backends = [drf_filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    filterset_fields = ['author']

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer

class ContactFormSubmissionViewSet(viewsets.ModelViewSet):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSubmissionSerializer
class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

# ==========================================
#  2. Public ViewSets (Read Only & Submission)
# ==========================================

class PublicPropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = PropertyViewSet.filter_backends
    filterset_fields = PropertyViewSet.filterset_fields
    search_fields = PropertyViewSet.search_fields

class PublicCompoundViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Compound.objects.all()
    serializer_class = CompoundSerializer
    filter_backends = CompoundViewSet.filter_backends
    filterset_class = CompoundViewSet.filterset_class
    ordering_fields = CompoundViewSet.ordering_fields
    ordering = CompoundViewSet.ordering
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        current_compound = self.get_object()
        related = Compound.objects.filter(
            location=current_compound.location
        ).exclude(id=current_compound.id) # استبعاد المشروع الحالي
        # 2. فلتر حسب السعر (اختياري: مثلاً في نطاق 20% زيادة أو نقصان)
        if current_compound.min_price:
            min_range = current_compound.min_price * 0.8  # أقل بـ 20%
            max_range = current_compound.min_price * 1.2  # أزيد بـ 20%
            
            # هات المشروعات اللي سعرها في الرينج ده، أو المشروعات اللي سعرها مش محدد (عشان منخسرش داتا)
            related = related.filter(
                min_price__gte=min_range, 
                min_price__lte=max_range
            ) | related.filter(min_price__isnull=True)

        # 3. خد أول 4 نتايج فقط عشان الصفحة متطولش
        related = related.distinct()[:5]

        serializer = self.get_serializer(related, many=True)
        return Response(serializer.data)

class PublicDeveloperViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer
    filter_backends = DeveloperViewSet.filter_backends
    search_fields = DeveloperViewSet.search_fields

class PublicLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class PublicBlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogPost.objects.filter(status='Published')
    serializer_class = BlogPostSerializer
    filter_backends = BlogPostViewSet.filter_backends
    search_fields = BlogPostViewSet.search_fields
    filterset_fields = BlogPostViewSet.filterset_fields

class PublicAuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class PublicTestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

class PublicPartnerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

class PublicAmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer

class PublicContactFormSubmissionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSubmissionSerializer
    permission_classes = [permissions.AllowAny]
# ==========================================
#  3. Utilities
# ==========================================
@csrf_exempt
def image_upload_view(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']
        file_name = default_storage.save(f"uploads/{upload.name}", upload)
        url = default_storage.url(file_name)
        return JsonResponse({'url': url, 'uploaded': True})
    
    return JsonResponse({'uploaded': False, 'error': {'message': 'Upload failed'}})