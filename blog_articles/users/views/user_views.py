from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from blog_articles.users.models import Profile

class UserCreateView(UserPassesTestMixin, TemplateView):
    template_name = 'users/user_form.html'

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user)
            return redirect('users:admin_dashboard')
        except Exception as e:
            return render(request, self.template_name, {'error': str(e)})

class UserEditView(UserPassesTestMixin, TemplateView):
    template_name = 'users/user_form.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = User.objects.get(id=self.kwargs['id'])
        return context

    def post(self, request, id):
        user = User.objects.get(id=id)
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        try:
            user.save()
            return redirect('users:admin_dashboard')
        except Exception as e:
            return render(request, self.template_name, {'error': str(e), 'user': user})

class UserDeleteView(UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, id):
        try:
            User.objects.get(id=id).delete()
            return redirect('users:admin_dashboard')
        except User.DoesNotExist:
            return redirect('users:admin_dashboard')

class UserDetailView(UserPassesTestMixin, TemplateView):
    template_name = 'users/user_detail.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = User.objects.get(id=self.kwargs['id'])
        return context