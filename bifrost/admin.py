from django.contrib import admin
from .models import CustomerUser
from .models import UploadHistory
from django.utils.html import format_html

admin.site.register(CustomerUser)
# Register your models here.

# This will show the UploadHistory model in Django admin
@admin.register(UploadHistory)
class UploadHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_conversion_option', 'get_uploaded_image', 'created_at')
    list_filter = ('framework_type', 'css_style', 'created_at')
    search_fields = ('user__username', 'framework_type', 'css_style')
    readonly_fields = ('created_at', 'get_uploaded_image', 'get_conversion_option')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'created_at')
        }),
        ('Conversion Options', {
            'fields': ('framework_type', 'css_style')
        }),
        ('Image', {
            'fields': ('cloud_image_url', 'get_uploaded_image')
        }),
        ('Generated Code', {
            'fields': ('html_code', 'css_code', 'js_code', 'ocr_text'),
            'classes': ('collapse',)
        }),
    )

    def get_uploaded_image(self, obj):
        return format_html('<img src="{}" width="100" style="border:1px solid #ddd"/>', obj.cloud_image_url)
    get_uploaded_image.short_description = 'Uploaded Image'
    get_uploaded_image.allow_tags = True

    def get_conversion_option(self, obj):
        return f"{obj.get_framework_type_display()} - {obj.get_css_style_display()}"
    get_conversion_option.short_description = 'Conversion Option'