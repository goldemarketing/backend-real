from rest_framework import viewsets, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .filters import CompoundFilter
import os
import uuid

# استدعاء الموديلات
from .models import (
    Developer, Location, Amenity, Compound, Property, PropertyImage,
    Author, BlogPost, Partner, Testimonial, ContactFormSubmission
)

# استدعاء السيريالايزر (تأكد أن ملف serializers.py تم حفظه)
from .serializers import (
    DeveloperSerializer, LocationSerializer, AmenitySerializer,
    CompoundSerializer, CompoundWriteSerializer, CompoundListSerializer,
    PropertySerializer, PropertyImageSerializer, PropertyListSerializer,
    AuthorSerializer, BlogPostSerializer, BlogPostListSerializer,
    PartnerSerializer, TestimonialSerializer, ContactFormSubmissionSerializer,
    UserSerializer, AuthTokenSerializer,
    PublicPropertySerializer, PublicCompoundSerializer, 
    PublicDeveloperSerializer, PublicBlogPostSerializer
)

# --- دالة رفع الصور ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def image_upload_view(request):
    uploaded_images = []
    if 'images' in request.FILES:
        image_files = request.FILES.getlist('images')
        image_type = request.POST.get('type', 'general')
        for image_file in image_files:
            try:
                result = process_image_upload(image_file, image_type)
                uploaded_images.append(result)
            except Exception as e:
                return JsonResponse({'error': f'Failed: {str(e)}'}, status=400)
    elif 'image' in request.FILES:
        image_file = request.FILES['image']
        image_type = request.POST.get('type', 'general')
        try:
            result = process_image_upload(image_file, image_type)
            uploaded_images.append(result)
        except Exception as e:
            return JsonResponse({'error': f'Failed: {str(e)}'}, status=400)
    else:
        return JsonResponse({'error': 'No image files provided'}, status=400)

    return JsonResponse({'message': 'Success', 'images': uploaded_images})

def process_image_upload(image_file, image_type):
    file_extension = os.path.splitext(image_file.name)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    upload_path = f"uploads/{image_type}/{unique_filename}"
    saved_path = default_storage.save(upload_path, ContentFile(image_file.read()))
    image_url = f"{settings.MEDIA_URL}{saved_path}".replace('//', '/')
    return {'id': str(uuid.uuid4()), 'image': image_url}

# --- ViewSets ---

class DeveloperViewSet(viewsets.ModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'])
    def compounds(self, request, pk=None):
        developer = self.get_object()
        compounds = developer.compound_set.all()
        serializer = CompoundListSerializer(compounds, many=True, context={'request': request})
        return Response(serializer.data)

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CompoundViewSet(viewsets.ModelViewSet):
    queryset = Compound.objects.all()
    serializer_class = CompoundSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = CompoundFilter
    search_fields = ['name']
    ordering_fields = ['min_price', 'delivery_date', 'id']
    ordering = ['-id']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompoundWriteSerializer
        return CompoundSerializer

    @action(detail=True, methods=['get'])
    def properties(self, request, pk=None):
        compound = self.get_object()
        properties = compound.property_set.all()
        serializer = PropertyListSerializer(properties, many=True, context={'request': request})
        return Response(serializer.data)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.select_related('compound', 'developer', 'location')
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['compound', 'developer', 'location', 'property_type', 'is_featured']
    search_fields = ['title']
    ordering_fields = ['price', 'area']

    def get_queryset(self):
        queryset = super().get_queryset()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price: queryset = queryset.filter(price__gte=min_price)
        if max_price: queryset = queryset.filter(price__lte=max_price)
        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = self.get_queryset().filter(is_featured=True)
        serializer = PropertyListSerializer(featured, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_launches(self, request):
        new = self.get_queryset().filter(is_new_launch=True)
        serializer = PropertyListSerializer(new, many=True, context={'request': request})
        return Response(serializer.data)

class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['property']

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['author', 'status']
    search_fields = ['title']

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ContactFormSubmissionViewSet(viewsets.ModelViewSet):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSubmissionSerializer
    permission_classes = [IsAdminUser]

# --- Public ViewSets ---

class PublicPropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.filter(is_new_launch=False) # Example filter
    serializer_class = PublicPropertySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_launches(self, request):
        new = Property.objects.filter(is_new_launch=True)
        serializer = self.get_serializer(new, many=True)
        return Response(serializer.data)

class PublicCompoundViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Compound.objects.all()
    serializer_class = PublicCompoundSerializer
    permission_classes = [AllowAny]

class PublicDeveloperViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = PublicDeveloperSerializer
    permission_classes = [AllowAny]

class PublicBlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogPost.objects.filter(status='Published')
    serializer_class = PublicBlogPostSerializer
    permission_classes = [AllowAny]

class PublicContactFormSubmissionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSubmissionSerializer
    permission_classes = [AllowAny]

# --- Auth Views ---

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]