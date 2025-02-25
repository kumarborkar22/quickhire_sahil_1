from django.urls import path
from .views import (
    create_superadmin, login, create_admin, create_user, 
    forgot_password, reset_password, get_all_departments, dashboard, 
    superadmin_dashboard, logout_view, admin_dashboard,profile_image_view, attendance_4,user_dashboard ,home, index,attendance_records,download_attendance_csv,capture_image, attendance1,attendance3, video_feed,start_camera,stop_camera
)
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('', index , name ="index"),
    path('home/', home, name='home'),
    path('create-superadmin/', create_superadmin, name='create_superadmin'),
    path('login/', login, name='login'),
    path('create-admin/', create_admin, name='create_admin'),
    path('create-user/', create_user, name='create_user'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('departments/', get_all_departments, name='get_all_departments'),
    path('dashboard/', dashboard, name='dashboard'),
    path('superadmin-dashboard/', superadmin_dashboard, name='superadmin_dashboard'),
    path('logout/', logout_view, name='logout_view'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path('attendance1/', attendance1, name='attendance1'),
    path('video_feed/', video_feed, name='video_feed'),
    path("start_camera/", start_camera, name="start_camera"),
    path("stop_camera/", stop_camera, name="stop_camera"),
    path('capture_image/', capture_image, name='capture_image'),
    path('records/', attendance_records, name='attendance_records'),
    path('download/', download_attendance_csv, name='download_csv'),
    path('attendance3/', attendance3, name='attendance3'),
    path('attendance_4/', attendance_4, name='attendance_4'),
    path("profile-image/", profile_image_view, name="profile_image"),
    path('attendance4/', views.attendance4, name='attendance4'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)