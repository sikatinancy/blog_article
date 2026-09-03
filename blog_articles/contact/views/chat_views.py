from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)


from ..models import Conversation





@login_required
def user_chat_room(request):
    """
    Page chat côté utilisateur
    """


    # Recherche d'une conversation existante
    conversation = (
        Conversation.objects
        .filter(
            participants=request.user
        )
        .first()
    )


    # Création si aucune conversation
    if conversation is None:

        conversation = Conversation.objects.create()

        conversation.participants.add(
            request.user
        )



    messages = (
        conversation.messages
        .all()
        .order_by(
            "created_at"
        )
    )


    return render(
        request,
        "contact/chat_room.html",
        {
            "conversation": conversation,
            "messages": messages,
        }
    )







def is_admin(user):
    """
    Vérifie si l'utilisateur est administrateur
    """

    return (
        user.is_authenticated
        and user.is_staff
    )







@login_required
@user_passes_test(is_admin)
def admin_chat_list(request):
    """
    Liste des conversations côté admin
    """


    conversations = (
        Conversation.objects
        .prefetch_related(
            "participants",
            "messages"
        )
        .all()
        .order_by(
            "-updated_at"
        )
    )


    return render(
        request,
        "contact/admin_chat_list.html",
        {
            "conversations": conversations,
        }
    )








@login_required
@user_passes_test(is_admin)
def admin_chat_room(
    request,
    conversation_id
):

    """
    Discussion complète côté admin
    """


    conversation = get_object_or_404(
        Conversation,
        id=conversation_id
    )



    # Envoi message admin

    if request.method == "POST":


        content = request.POST.get(
            "message"
        )


        if content:


            conversation.messages.create(
                sender=request.user,
                content=content
            )


            conversation.save()



        return redirect(
            "contact:admin_chat_room",
            conversation_id=conversation.id
        )





    messages = (
        conversation.messages
        .all()
        .order_by(
            "created_at"
        )
    )



    return render(
        request,
        "contact/admin_chat_room.html",
        {
            "conversation": conversation,
            "messages": messages,
        }
    )