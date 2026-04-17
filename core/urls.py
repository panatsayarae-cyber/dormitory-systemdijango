from django.urls import path
from app import views
from app.admin import admin_site
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home),
    path('login/', views.login_view),
    path('logout/', views.logout_view),

    path('dashboard/', views.dashboard),
    path('bills/', views.bills),
    path('repair/', views.repair),

    path('admin/', admin_site.urls),

    path('rooms/', views.rooms),
    path('room/<int:room_id>/', views.room_detail),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)