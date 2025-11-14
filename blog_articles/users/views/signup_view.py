# users/views/signup_view.py
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from users.api.serializers import SignupSerializer

User = get_user_model()


# === PAGE D'INSCRIPTION (GET) ===
class SignupPageView(TemplateView):
    template_name = 'users/register.html'


# === API D'INSCRIPTION (POST) ===
class SignupAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            # Créer l'utilisateur désactivé
            user = serializer.save(is_active=False)

            # Générer UID + TOKEN
            current_site = get_current_site(request)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # LIEN CORRIGÉ : /users/activate/...
            activation_link = (
                f"{request.scheme}://{current_site.domain}/users/activate/{uidb64}/{token}/"
            )

            # Email HTML
            subject = "Activez votre compte BlogApp"
            html_message = render_to_string('users/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': uidb64,
                'token': token,
                'activation_link': activation_link,  # Lien complet
            })

            # Envoi email
            send_mail(
                subject=subject,
                message="",
                from_email=None,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({
                'success': True,
                'message': 'Inscription réussie ! Vérifiez votre email pour activer votre compte.'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# === ACTIVATION DE COMPTE (UNIQUE & SÉCURISÉE) ===
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.info(request, "Votre compte est déjà activé. Connectez-vous.")
            return redirect('users:login')
        else:
            user.is_active = True
            user.save()
            messages.success(request, "Compte activé avec succès ! Connectez-vous.")
            return redirect('users:login')
    else:
        messages.error(request, "Lien d'activation invalide ou expiré.")
        return render(request, 'users/activation_failed.html')