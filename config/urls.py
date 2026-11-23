
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('skills/', include('skills.urls')),
    path('analyzer/', include('analyzer.urls')),
    path('roadmap/', include('roadmap.urls')),
    path('progress/', include('progress.urls')),
]
