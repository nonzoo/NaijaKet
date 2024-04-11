from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import TemplateView
from core.views import frontpage
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/',include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('robots.txt', TemplateView.as_view(template_name='core/robots.txt', content_type='text/plain')),
    path('', include('userprofile.urls')),
    path('', include('store.urls')),
    path('',frontpage,name='frontpage'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''urlpatterns = [
    
    path('admin/', admin.site.urls),]

urlpatterns += i18n_patterns (
    path('robots.txt', TemplateView.as_view(template_name='core/robots.txt', content_type='text/plain')),
    path('', include('userprofile.urls')),
    path('', include('store.urls')),
    path('',frontpage,name='frontpage'),
    prefix_default_language=False
    
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)'''