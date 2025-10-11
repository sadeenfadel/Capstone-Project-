from django.contrib import admin
from .models import Flower, Bouquet, BouquetFlower

# Inline لربط BouquetFlower مع Bouquet
class BouquetFlowerInline(admin.TabularInline):
    model = BouquetFlower
    extra = 1  # عدد الصفوف الفارغة لبدء الإضافة
    min_num = 1
    can_delete = True

@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    inlines = [BouquetFlowerInline]
    list_display = ('name', 'user', 'total_price')

    # عرض الباقات حسب المستخدم العادي أو الكل للـ superuser
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    # التحكم في صلاحيات التعديل والحذف
    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.user == request.user
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.user == request.user
        return request.user.is_superuser

    # تلقائيًا تعيين المستخدم صاحب الباقة عند الإضافة
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
