from django.contrib import admin
from django.urls import path
from reviews import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main, name='main'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='reviews/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.log_out, name='logout'),

    path('create_ticket', views.create_ticket, name="create_ticket"),
    path('ticket/<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
    path('ticket/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),

    path('create_ticket_and_review', views.create_ticket_and_review, name="create_ticket_and_review"),
    path('review/<int:ticket_id>/create_review/', views.create_review, name='create_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    path('follow-users/', views.follow_users, name='follow_users'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),

    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock-user/<int:user_id>/', views.unblock_user, name='unblock_user'),

    path('posts/', views.posts, name='posts'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
