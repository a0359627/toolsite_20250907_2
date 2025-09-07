from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('upload/', views.zc_upload_view, name='zc_upload'),
    path('upload/background/', views.upload_background_ajax, name='upload_background_ajax'),
    path('upload/background/delete/<int:bg_id>/', views.delete_background, name='delete_background'),
    path('files/', views.zc_download_view, name='zc_files'),
    path('files/delete/<str:filename>/', views.delete_zip_file, name='delete_zip_file'),
]