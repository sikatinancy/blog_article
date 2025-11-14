# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views import defaults as default_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from blog_articles.users.views.home_view import HomeView

urlpatterns = [
    # Route racine
    path('', HomeView.as_view(), name='home'),

    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),

    # === USERS : PAGES HTML + ACTIVATION + API LOGIN ===
    path('users/', include('blog_articles.users.urls')),  # /users/activate/... + /users/api/login/

    # === BLOG ===
    path('api/blog/', include(('blog_articles.blog.urls', 'blog_api'), namespace='blog_api')),
    path('blog/', include(('blog_articles.blog.urls', 'blog'), namespace='blog')),

    # === AUTRES APPS ===
    path('api/contact/', include('blog_articles.contact.urls')),
    path('newsletter/', include('blog_articles.newsletter.urls')),

    # === API DOCS ===
    path("api/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema", permission_classes=[AllowAny]), name="api-docs"),
]

# === MÉDIAS EN DEBUG ===
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# === PAGES D’ERREURS ===
if settings.DEBUG:
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]

# === DEBUG TOOLBAR ===
if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]