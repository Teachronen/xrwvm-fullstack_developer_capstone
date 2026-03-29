from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from . import views


app_name = 'djangoapp'


urlpatterns = [
    path(route='login', view=views.login_user, name='login'),
    path(route='logout', view=views.logout_request, name='logout'),

    path('register/', views.registration, name='register'),
    path(
        'register/',
        TemplateView.as_view(template_name="index.html"),
    ),

    path(route='get_cars', view=views.get_cars, name='getcars'),

    path(
        'get_dealers',
        views.get_dealers,
        name='get_dealers',
    ),
    path(
        'get_dealer/<int:id>',
        views.get_dealer,
        name='get_dealer',
    ),
    path(
        'get_reviews/dealer/<int:id>',
        views.get_reviews,
        name='get_reviews',
    ),

    path(route='add_review', view=views.add_review, name='add_review'),
] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
