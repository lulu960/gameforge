from django.contrib import admin
from django.urls import path, include
from games.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('games/', include(('games.urls', 'games'), namespace='games')),
]

from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
