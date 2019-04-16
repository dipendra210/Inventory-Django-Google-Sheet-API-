from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('getBarcode/', views.ajaxGetBarcode, name='getBarcode'),
    path('getUOMs/', views.getUOMs, name='getUOMs'),
    path('add/', views.add, name='add'),
    # path('logout/', views.logout, name='logout'),
    # path('inventory/updateSheet/', views.updateSheet, name='updateSheet'),

]
 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)