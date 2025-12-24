import django_filters
from .models import Compound

class CompoundFilter(django_filters.FilterSet):
    # 1. البحث بالاسم (بحث مرن)
    search = django_filters.CharFilter(method='filter_search')

    # 2. فلترة السعر (Price Range)
    # min_price: المستخدم عايز مشاريع تبدأ من سعر كذا (أكبر من أو يساوي)
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    # max_price: المستخدم معه ميزانية قصوى، عايز مشاريع سعر بدايتها أقل من ميزانيته
    max_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='lte')

    # 3. سنوات التقسيط (Installments)
    # المستخدم محتاج قسط على 8 سنين، فبنجيب المشاريع اللي الـ Max بتاعها 8 أو أكتر
    min_installment_years = django_filters.NumberFilter(field_name='max_installment_years', lookup_expr='gte')

    # 4. سنة الاستلام (Delivery Year)
    # بنفلتر بالسنة فقط من التاريخ الكامل
    delivery_year = django_filters.NumberFilter(field_name='delivery_date', lookup_expr='year')
    
    # فلترة الاستلام: "استلام فوري" أو قبل سنة معينة (أقل من أو يساوي السنة)
    delivery_year_lte = django_filters.NumberFilter(field_name='delivery_date', lookup_expr='year__lte')
    min_area = django_filters.NumberFilter(field_name='min_area', lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name='min_area', lookup_expr='lte')

    class Meta:
        model = Compound
        fields = ['location', 'developer']

    def filter_search(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(name__icontains=value) |
            Q(location__name__icontains=value) |
            Q(developer__name__icontains=value)
        )