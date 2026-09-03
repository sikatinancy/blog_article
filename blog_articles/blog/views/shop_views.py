from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from blog_articles.blog.models import Article, CartItem, Order, OrderItem


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = CartItem.objects.filter(user=self.request.user).select_related('article')
        context['cart_items'] = items
        context['cart_total'] = sum((item.subtotal for item in items), Decimal('0.00'))
        return context


class CartAddView(LoginRequiredMixin, TemplateView):
    def post(self, request, id):
        article = get_object_or_404(Article, id=id, published=True)
        item, created = CartItem.objects.get_or_create(user=request.user, article=article)
        if not created:
            item.quantity += 1
            item.save(update_fields=['quantity'])
        return redirect(request.POST.get('next') or 'blog:cart')


class CartDecreaseView(LoginRequiredMixin, TemplateView):
    def post(self, request, id):
        item = get_object_or_404(CartItem, id=id, user=request.user)
        if item.quantity > 1:
            item.quantity -= 1
            item.save(update_fields=['quantity'])
        else:
            item.delete()
        return redirect('blog:cart')


class CartRemoveView(LoginRequiredMixin, TemplateView):
    def post(self, request, id):
        get_object_or_404(CartItem, id=id, user=request.user).delete()
        return redirect('blog:cart')


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = CartItem.objects.filter(user=self.request.user).select_related('article')
        context['cart_items'] = items
        context['cart_total'] = sum((item.subtotal for item in items), Decimal('0.00'))
        return context

    def post(self, request):
        items = list(CartItem.objects.filter(user=request.user).select_related('article'))
        if not items:
            messages.error(request, 'Votre panier est vide.')
            return redirect('blog:cart')
        if request.POST.get('payment_method') == 'online':
            messages.error(request, 'Le paiement en ligne sera disponible prochainement.')
            return render(request, self.template_name, {'cart_items': items, 'cart_total': sum((i.subtotal for i in items), Decimal('0.00'))})
        required = ('city', 'neighborhood', 'location')
        if any(not request.POST.get(field, '').strip() for field in required):
            messages.error(request, 'Veuillez renseigner la ville, le quartier et le lieu.')
            return render(request, self.template_name, {'cart_items': items, 'cart_total': sum((i.subtotal for i in items), Decimal('0.00'))})
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                city=request.POST['city'].strip(),
                neighborhood=request.POST['neighborhood'].strip(),
                location=request.POST['location'].strip(),
                payment_method='cod',
                total=sum((item.subtotal for item in items), Decimal('0.00')),
            )
            OrderItem.objects.bulk_create([
                OrderItem(order=order, article=item.article, title=item.article.title, unit_price=item.article.price, quantity=item.quantity)
                for item in items
            ])
            CartItem.objects.filter(user=request.user).delete()
        return redirect('blog:order_success', id=order.id)


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/order_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs['id'], user=self.request.user)
        return context


class OrderStatusView(UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, id, status):
        order = get_object_or_404(Order, id=id)
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save(update_fields=['status'])
        return redirect('users:admin_dashboard')
