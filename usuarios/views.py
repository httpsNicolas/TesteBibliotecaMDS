from django.shortcuts import render
from django.http import HttpResponse
from .models import Usuario
from django.shortcuts import redirect
from hashlib import sha256

URL_HOME = "/livro/home"

def login(request):
    if request.session.get('usuario'):
        return redirect(URL_HOME)
    status = request.GET.get('status')
    return render(request, 'login.html', {'status': status})

def cadastro(request):
    if request.session.get('usuario'):
        return redirect(URL_HOME)
    status = request.GET.get('status')
    return render(request, 'cadastro.html', {'status': status})


def valida_cadastro(request):
    nome = request.POST.get('nome')
    senha = request.POST.get('senha')
    email = request.POST.get('email')

    usuario = Usuario.objects.filter(email = email)

    if len(nome.strip()) == 0 or len(email.strip()) == 0:
        return redirect('/auth/cadastro/?status=1')

    if len(senha) < 8:
        return redirect('/auth/cadastro/?status=2')

    if len(usuario) > 0:
        return redirect('/auth/cadatro/?status=3')

    try:
        senha = sha256(senha.encode()).hexdigest()
        usuario = Usuario(nome = nome,
                          senha = senha,
                          email = email)
        usuario.save()

        return redirect('/auth/cadastro/?status=0')
    except Exception:
        return redirect('/auth/cadastro/?status=4')


def validar_login(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')

    if not email or not senha:
        return redirect('/auth/login/?status=1')

    senha_hash = sha256(senha.encode()).hexdigest()

    usuario = Usuario.objects.filter(email=email, senha=senha_hash).first()

    if not usuario:
        return redirect('/auth/login/?status=1')

    request.session['usuario'] = usuario.id
    return redirect(URL_HOME)


def sair(request):
    request.session.flush()
    return redirect('/auth/login/')