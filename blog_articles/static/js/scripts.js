function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

async function viewArticle(id) {
    const response = await fetch(`/api/blog/articles/${id}/`, {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    const article = await response.json();
    alert(`Titre: ${article.title}\nDescription: ${article.description}\nPublié: ${article.published ? 'Oui' : 'Non'}`);
}

async function editArticle(id) {
    const response = await fetch(`/api/blog/articles/${id}/`, {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    const article = await response.json();
    document.querySelector('#articleForm [name="id"]').value = article.id;
    document.querySelector('#articleForm [name="title"]').value = article.title;
    document.querySelector('#articleForm [name="description"]').value = article.description;
    document.querySelector('#articleForm [name="published"]').checked = article.published;
    openModal('articleModal');
}

async function deleteArticle(id) {
    if (confirm('Voulez-vous supprimer cet article ?')) {
        await fetch(`/api/blog/articles/${id}/`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });
        location.reload();
    }
}

async function editComment(id) {
    const response = await fetch(`/api/blog/comments/${id}/`, {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    const comment = await response.json();
    document.querySelector('#commentForm [name="id"]').value = comment.id;
    document.querySelector('#commentForm [name="article"]').value = comment.article;
    document.querySelector('#commentForm [name="content"]').value = comment.content;
    document.querySelector('#commentForm [name="published"]').checked = comment.published;
    openModal('commentModal');
}

async function deleteComment(id) {
    if (confirm('Voulez-vous supprimer ce commentaire ?')) {
        await fetch(`/api/blog/comments/${id}/`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });
        location.reload();
    }
}

async function viewUser(id) {
    const response = await fetch(`/api/users/${id}/`, {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    const user = await response.json();
    alert(`Utilisateur: ${user.username}\nEmail: ${user.email}`);
}

async function editUser(id) {
    const response = await fetch(`/api/users/${id}/`, {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    const user = await response.json();
    document.querySelector('#userForm [name="id"]').value = user.id;
    document.querySelector('#userForm [name="username"]').value = user.username;
    document.querySelector('#userForm [name="email"]').value = user.email;
    openModal('userModal');
}

async function deleteUser(id) {
    if (confirm('Voulez-vous supprimer cet utilisateur ?')) {
        await fetch(`/api/users/${id}/`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });
        location.reload();
    }
}

async function viewMessage(id) {
    const response = await fetch(`/api/contact/messages/${id}/`, {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    const message = await response.json();
    alert(`Sujet: ${message.subject}\nMessage: ${message.message}\nLu: ${message.is_read ? 'Oui' : 'Non'}`);
}

async function replyMessage(id) {
    const reply = prompt('Entrez votre réponse :');
    if (reply) {
        await fetch(`/api/contact/messages/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ reply: reply })
        });
        location.reload();
    }
}

async function deleteMessage(id) {
    if (confirm('Voulez-vous supprimer ce message ?')) {
        await fetch(`/api/contact/messages/${id}/`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });
        location.reload();
    }
}