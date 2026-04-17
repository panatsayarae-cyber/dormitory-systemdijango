from django.urls import path
from app import views
from app.admin import admin_site
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home),                # 🔥 หน้าเลือก
    path('login/', views.login_view),
    path('logout/', views.logout_view),

    path('dashboard/', views.dashboard),  # 🔥 dashboard
    path('bills/', views.bills, name='bills'),
    path('repair/', views.repair),

    path('upload-slip/', views.upload_slip),
    path('qr/<int:bill_id>/', views.generate_qr),
    path('bill-pdf/<int:bill_id>/', views.bill_pdf),

    path('admin/', admin_site.urls),

    path('rooms/', views.rooms),
    path('room/<int:room_id>/', views.room_detail),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)