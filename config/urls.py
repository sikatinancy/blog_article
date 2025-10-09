from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views import defaults as default_views
# from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny


from blog_articles.users.views.home_view import HomeView
# from rest_framework.authtoken.views import obtain_auth_token



urlpatterns = [
# Route racine utilisant HomeView
    path('', HomeView.as_view(), name='home'),
    # path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),

    # Django Admin

    # Gestion des utilisateurs
    # path("users/", include("blog_articles.users.urls")),
    # path("accounts/", include("allauth.urls")),
    # API routes
    path(settings.ADMIN_URL, admin.site.urls),
    path('api/', include('blog_articles.users.urls')),
    path('api/blog/', include('blog_articles.blog.urls')),
    path('api/contact/', include('blog_articles.contact.urls')),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="api-schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="api-schema",
            permission_classes=[AllowAny],
 
            ),
        name="api-docs",
    ),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# Pages d’erreurs en DEBUG
if settings.DEBUG:
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
