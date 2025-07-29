from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('help/', views.help, name='help'),
    path('result/<int:upload_id>/', views.result_page, name='result_page'),
    path('templates/', views.templates, name='templates'),
    path('history/', views.history, name='history'),
    path('upload/', views.handle_upload, name='handle_upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #path('generate/', views.generate_code, name='generate_code'),
    path('logout/', views.user_logout, name='logout'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
