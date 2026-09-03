from django.conf import settings
from blog_articles.blog.models import CartItem


def allauth_settings(request):
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }


def cart_context(request):
    if not request.user.is_authenticated:
        return {"cart_item_count": 0}
    return {
        "cart_item_count": sum(
            item.quantity for item in CartItem.objects.filter(user=request.user)
        )
    }
