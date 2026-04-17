from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import Room, Tenant, Contract, Bill, Maintenance
from django import forms
from django.utils.html import format_html
from django.contrib.auth import logout
from django.shortcuts import redirect


class BillForm(forms.ModelForm):
    MONTH_CHOICES = [(i, f"เดือน {i}") for i in range(1, 13)]
    month = forms.ChoiceField(choices=MONTH_CHOICES)

    class Meta:
        model = Bill
        fields = '__all__'


class RoomAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        rooms = Room.objects.all().order_by('room_number')

        floors = {}
        for room in rooms:
            floor = room.room_number[0]
            floors.setdefault(floor, []).append(room)

        context = self.admin_site.each_context(request)
        context['floors'] = floors

        return TemplateResponse(request, "admin/rooms.html", context)


class BillAdmin(admin.ModelAdmin):
    form = BillForm
    exclude = ('total', 'room_price', 'water_total', 'electric_total')
    readonly_fields = ('year',)

    def save_model(self, request, obj, form, change):
        from datetime import datetime
        obj.year = datetime.now().year
        super().save_model(request, obj, form, change)


class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'room', 'status', 'image_preview')
    readonly_fields = ('image', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200">', obj.image.url)
        return "ไม่มีรูป"


class CustomAdminSite(admin.AdminSite):
    site_header = "Dormitory Admin"

    def logout(self, request, extra_context=None):
        logout(request)
        request.session.flush()
        return redirect('/')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('rooms-view/', self.admin_view(self.rooms_view)),
        ]
        return custom_urls + urls

    def rooms_view(self, request):
        rooms = Room.objects.all().order_by('room_number')

        floors = {}
        for room in rooms:
            floor = room.room_number[0]
            floors.setdefault(floor, []).append(room)

        context = self.each_context(request)
        context['floors'] = floors

        return TemplateResponse(request, "admin/rooms.html", context)


admin_site = CustomAdminSite(name='custom_admin')

admin_site.register(Room, RoomAdmin)
admin_site.register(Tenant)
admin_site.register(Contract)
admin_site.register(Bill, BillAdmin)
admin_site.register(Maintenance, MaintenanceAdmin)