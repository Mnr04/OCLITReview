from django.contrib import admin
from django.urls import path
from reviews import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.main, name='main'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='reviews/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.log_out, name='logout'),
]
