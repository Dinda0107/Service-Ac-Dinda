from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Harga, User, Teknisi, Service

# Harga
@admin.register(Harga)
class HargaAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_ac') 
    search_fields = ('service_ac',) 
    fields = ('service_ac',) 


# User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role', 'alamat', 'nomor_hp') 
    list_filter = ('role',) 
    search_fields = ('username', 'nomor_hp') 
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role')}),
        ('Personal Info', {'fields': ('alamat', 'nomor_hp')}),
    )
    # readonly_fields = ('password',) 

    def save_model(self, request, obj, form, change):
        """
        Saat menyimpan model User:
        - Jika password diubah, maka akan dienkripsi.
        """
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        - Jika superuser, bisa melihat semua user.
        """
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            return queryset.exclude(role='admin')
        return queryset

    def has_change_permission(self, request, obj=None):
        """
        - Hanya superuser yang bisa mengubah user dengan role 'admin'.
        """
        if obj and obj.role == 'admin' and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        - Hanya superuser yang bisa menghapus user dengan role 'admin'.
        """
        if obj and obj.role == 'admin' and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


# Teknisi
@admin.register(Teknisi)
class TeknisiAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'nomor_hp', 'spesialisasi') 
    search_fields = ('nama', 'nomor_hp') 
    list_filter = ('spesialisasi',) 


# Service
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'teknisi', 'tanggal_servis', 'status', 'harga')
    list_filter = ('status', 'tanggal_servis')
    search_fields = ('user__username', 'teknisi__nama')
    raw_id_fields = ('user', 'teknisi') 
    fieldsets = (
        (None, {'fields': ('user', 'teknisi', 'tanggal_servis', 'location', 'harga', 'status', 'deskripsi')}),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            return queryset.filter(user__role='user')
        return queryset

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser and obj.status == 'selesai':
            return False
        return super().has_change_permission(request, obj)
