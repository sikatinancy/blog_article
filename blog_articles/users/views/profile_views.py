from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from blog_articles.users.models import Profile


class ProfileEditView(LoginRequiredMixin, View):
    template_name = 'users/profile_edit.html'

    def get(self, request):
        return render(request, self.template_name, {'profile': request.user.profile})

    def post(self, request):
        user = request.user
        user.username = request.POST.get('username', '').strip()
        user.email = request.POST.get('email', '').strip().lower()
        if request.POST.get('password'):
            user.set_password(request.POST['password'])
        user.save()
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.birth_date = request.POST.get('birth_date') or None
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES['profile_image']
        profile.save()
        messages.success(request, 'Profil modifié avec succès.')
        return redirect('users:dashboard')
